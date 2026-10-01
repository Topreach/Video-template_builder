"""G13-P — can `moov/udta/<key>` alone produce a readable producer observation?

Question: when the plain `moov/udta/<key>` form is the ONLY physical declaration,
does the demuxer yield a usable value?

The earlier CASE 1 attempt failed silently, so every step is VERIFIED INDEPENDENTLY
before the next runs: the file is re-opened and its box chain re-walked after each
operation. If a step does not do what it claims, the run stops there rather than
continuing from a broken artifact.
"""
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "_inj", os.path.join(os.getcwd(), "_s23_fixture_inject.py"))
inj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inj)

TOO = b"\xa9too"
tmp = tempfile.mkdtemp()
CONTAINERS = (b"moov", b"udta", b"meta", b"ilst")


def build(path, tag="Lavf62.12.102"):
    c = av.open(path, "w")
    if tag:
        c.metadata["encoder"] = tag
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    c.start_encoding()
    for i in range(10):
        f = av.VideoFrame(160, 120, "yuv420p")
        for pl in f.planes:
            pl.update(bytes(pl.buffer_size))
        f.pts = i
        for p in st.encode(f):
            c.mux(p)
    for p in st.encode(None):
        c.mux(p)
    c.close()
    return path


def walk(buf, start, end, prefix="", acc=None):
    """Depth-first box walk that also records where a chain became inconsistent."""
    if acc is None:
        acc = ([], [])
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            acc[1].append((prefix or "/", pos, size, end - pos))
            return acc
        name = btype.decode("latin-1")
        acc[0].append(f"{prefix}/{name}({size})")
        if btype in CONTAINERS:
            skip = 4 if btype == b"meta" else 0
            walk(buf, pos + 8 + skip, pos + size, f"{prefix}/{name}", acc)
        pos += size
    return acc


def verify(label, path, expect):
    """Independently verify the artifact before the next step may proceed."""
    buf = bytearray(open(path, "rb").read())
    names, bad = walk(buf, 0, len(buf))
    toos = [n for n in names if "too" in n]
    c = av.open(path)
    md = dict(c.metadata)
    c.close()
    print(f"\n[{label}]")
    print(f"  (c)too atoms : {len(toos)}  {toos}")
    print(f"  PyAV encoder : {md.get('encoder')!r}")
    if bad:
        print(f"  !! CHAIN BROKEN at {bad}")
    ok = len(toos) == expect and not bad
    print(f"  {'OK ' if ok else '!! '}expected {expect} atom(s), chain intact")
    return ok, len(toos), md.get("encoder")


def moov_range(buf):
    m = buf.find(b"moov") - 4
    return m, struct.unpack(">I", buf[m:m + 4])[0]


def child(buf, start, end, want):
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        if size < 8 or pos + size > end:
            return None
        if buf[pos + 4:pos + 8] == want:
            return pos, size
        pos += size
    return None


def boxes(buf):
    """Every box as (path, offset, size) -- the form `strip_too` needs to patch sizes."""
    out = []

    def rec(start, end, prefix=""):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", buf[pos:pos + 4])[0]
            btype = buf[pos + 4:pos + 8]
            if size < 8 or pos + size > end:
                return
            name = btype.decode("latin-1")
            path = f"{prefix}/{name}"
            out.append((path, pos, size))
            if btype in CONTAINERS:
                skip = 4 if btype == b"meta" else 0
                rec(pos + 8 + skip, pos + size, path)
            pos += size

    rec(0, len(buf))
    return out


def strip_too(src, dst):
    """Remove every (c)too, shrinking ONLY its true ancestors.

    ORDER MATTERS. The first two attempts patched sizes AFTER deleting, which cannot
    work: deleting shortens the buffer, so the un-patched parent now overruns `end`,
    the walker's guard rejects it, and the parent is never patched at all. The step
    verifier caught exactly that (`CHAIN BROKEN at offset 1126`). So sizes are patched
    FIRST, while every original offset is still valid, and only then are the bytes
    removed from the highest offset down.
    """
    buf = bytearray(open(src, "rb").read())
    layout = boxes(buf)
    toos = [(p, o, s) for p, o, s in layout if p.endswith("/©too")]
    if not toos:
        open(dst, "wb").write(bytes(buf))
        return 0
    ancestors = set()
    for path, _o, _s in toos:
        parts = path.split("/")[:-1]
        for n in range(1, len(parts) + 1):
            ancestors.add("/".join(parts[:n]))
    removed = sum(s for _p, _o, s in toos)

    # 1. shrink ancestors while the original offsets are still valid
    for path, off, size in layout:
        if path in ancestors and size - removed >= 8:
            buf[off:off + 4] = struct.pack(">I", size - removed)
    # 2. remove the atoms, highest offset first
    for _p, off, size in sorted(toos, key=lambda t: -t[1]):
        del buf[off:off + size]

    out, _n = inj._shift_chunk_offsets(bytes(buf), -removed, len(buf))
    open(dst, "wb").write(out)
    return removed


def add_plain_too(src, dst, value):
    """Insert `moov/udta/<key>` (plain form, NOT under meta/ilst)."""
    buf = bytearray(open(src, "rb").read())
    moov, msize = moov_range(buf)
    payload = inj._too_payload(value)
    atom = struct.pack(">I", 8 + len(payload)) + TOO + payload
    hit = child(buf, moov + 8, moov + msize, b"udta")
    if hit:
        pos, size = hit
        buf[pos + size:pos + size] = atom
        grow = [(pos, len(atom))]
    else:
        box = struct.pack(">I", 8 + len(atom)) + b"udta" + atom
        buf[moov + msize:moov + msize] = box
        grow = [(moov, 8 + len(atom))]
    total = sum(d for _p, d in grow)
    for pos, _d in grow:
        cur = struct.unpack(">I", buf[pos:pos + 4])[0]
        buf[pos:pos + 4] = struct.pack(">I", cur + total)
    cm = struct.unpack(">I", buf[moov:moov + 4])[0]
    buf[moov:moov + 4] = struct.pack(">I", cm + total)
    out, _ = inj._shift_chunk_offsets(bytes(buf), total, moov + cm + total)
    open(dst, "wb").write(out)


print("=" * 74)
print("STEP 1 — baseline")
print("=" * 74)
base = build(os.path.join(tmp, "base.mp4"))
ok, _n, _e = verify("base", base, 1)
if not ok:
    sys.exit("baseline unexpected -- stopping")

print()
print("=" * 74)
print("STEP 2 — strip the writer's ilst atom")
print("=" * 74)
n1 = os.path.join(tmp, "stripped.mp4")
print(f"  removed {strip_too(base, n1)} byte(s)")
ok, _n, _e = verify("stripped (no (c)too expected)", n1, 0)
if not ok:
    sys.exit("strip produced a broken artifact -- stopping")

print()
print("=" * 74)
print("STEP 3 — add ONLY the plain moov/udta/<key> atom")
print("=" * 74)
c1 = os.path.join(tmp, "c1.mp4")
add_plain_too(n1, c1, "PlainOnlyWriter 1.0")
_ok, atoms, enc = verify("plain udta ONLY", c1, 1)

print()
print("=" * 74)
print("VERDICT")
print("=" * 74)
if atoms == 1 and enc == "PlainOnlyWriter 1.0":
    print("  YES - /moov/udta/<key> alone yields a readable producer observation.")
    print("       -> legitimate locator target; G13-M may include it.")
elif atoms == 1 and enc in ("", None):
    print("  NO  - the atom is present but the demuxer yields no usable value.")
    print("       -> finding bytes there does NOT establish the probe would")
    print("          observe it, so G13-M must EXCLUDE this path.")
else:
    print(f"  INCONCLUSIVE - {atoms} atom(s), encoder={enc!r}. Do not cite.")