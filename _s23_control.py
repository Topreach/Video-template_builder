"""G13-R CONTROL MATRIX — physical bytes vs. the demuxer's logical metadata.

  1  one declaration (plain moov/udta only, ilst stripped)  -> is the plain form readable?
  2  two declarations, IDENTICAL values                     -> preserved or collapsed?
  3  two declarations, DIFFERENT values                     -> reproduce `encoder: ''`?
  4  two declarations, one malformed                       -> collision vs parser rejection

Case 1 needs a base with NO (c)too atom at all. PyAV's muxer always writes one, so the
atom must be STRIPPED rather than merely not-set.
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


def scan(buf, start, end, path="", out=None):
    """Collect every box as (path, type, offset, size)."""
    if out is None:
        out = []
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            break
        name = btype.decode("latin-1")
        out.append((f"{path}/{name}", btype, pos, size))
        if btype in (b"moov", b"udta", b"meta", b"ilst", b"trak", b"mdia"):
            skip = 4 if btype == b"meta" else 0
            scan(buf, pos + 8 + skip, pos + size, f"{path}/{name}", out)
        pos += size
    return out


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


def add_plain_too(src, dst, value):
    """Insert `moov/udta/<key>` (plain form, NOT under meta/ilst)."""
    buf = bytes(open(src, "rb").read())
    moov, msize = moov_range(buf)
    payload = inj._too_payload(value)
    atom = struct.pack(">I", 8 + len(payload)) + TOO + payload
    udta = child(buf, moov + 8, moov + msize, b"udta")
    if udta:
        pos, size = udta
        out = buf[:pos + size] + atom + buf[pos + size:]
        grow = [(pos, len(atom))]
    else:
        box = struct.pack(">I", 8 + len(atom)) + b"udta" + atom
        out = buf[:moov + msize] + box + buf[moov + msize:]
        grow = [(moov, 8 + len(atom))]
    total = sum(d for _p, d in grow)
    for pos, _d in grow:
        cur = struct.unpack(">I", out[pos:pos + 4])[0]
        out = out[:pos] + struct.pack(">I", cur + total) + out[pos + 4:]
    cm = struct.unpack(">I", out[moov:moov + 4])[0]
    out = out[:moov] + struct.pack(">I", cm + total) + out[moov + 4:]
    out, _ = inj._shift_chunk_offsets(out, total, moov + cm + total)
    open(dst, "wb").write(out)


def strip_too(src, dst):
    """Remove every (c)too atom, repairing ancestor sizes and chunk offsets.

    Three corrections this needed across runs -- each caught by the artifact, not by
    inspection:
      * `bytes` is immutable; the buffer must be a bytearray before slicing;
      * deletion shifts later offsets, so the repair pass must RE-SCAN;
      * only TRUE ANCESTORS may shrink. Shrinking every container (an earlier bug)
        corrupted `stbl`/`minf`/`mdia`, which are not on the removed atom's path, and
        the resulting file was unreadable -- which silently voided CASE 1.
    """
    buf = bytearray(open(src, "rb").read())
    boxes = scan(bytes(buf), 0, len(buf))
    toos = [b for b in boxes if b[1] == TOO]
    if not toos:
        open(dst, "wb").write(bytes(buf))
        return 0

    ancestor_paths = set()
    for path, _t, _o, _s in toos:
        parts = path.split("/")[:-1]
        for n in range(1, len(parts) + 1):
            ancestor_paths.add("/".join(parts[:n]))

    removed = sum(b[3] for b in toos)
    for _p, _t, off, size in sorted(toos, key=lambda b: -b[2]):
        del buf[off:off + size]

    for path, _t, off, _s in scan(bytes(buf), 0, len(buf)):
        if path in ancestor_paths:
            cur = struct.unpack(">I", buf[off:off + 4])[0]
            if cur - removed >= 8:
                buf[off:off + 4] = struct.pack(">I", cur - removed)

    out, _n = inj._shift_chunk_offsets(bytes(buf), -removed, len(buf))
    open(dst, "wb").write(out)
    return removed


def report(label, path):
    raw = open(path, "rb").read()
    toos = [b[0] for b in scan(raw, 0, len(raw)) if b[1] == TOO]
    c = av.open(path)
    md = dict(c.metadata)
    c.close()
    got = md.get("encoder")
    others = {k: v for k, v in md.items()
              if k.startswith("encoder") and k != "encoder"}
    print(f"\n{label}")
    print(f"  physical (c)too atoms : {len(toos)}  {toos}")
    print(f"  PyAV encoder         : {got!r}")
    print(f"  other encoder* keys  : {others}")
    return len(toos), got


print("=" * 74)
print("CASE 1 — one declaration: plain moov/udta/<key>, writer's atom STRIPPED")
print("=" * 74)
base = build(os.path.join(tmp, "base.mp4"))
n1 = os.path.join(tmp, "stripped.mp4")
removed = strip_too(base, n1)
print(f"  stripped {removed} byte(s) of (c)too the muxer had written itself")
c1 = os.path.join(tmp, "c1.mp4")
add_plain_too(n1, c1, "PlainOnlyWriter 1.0")
report("CASE 1", c1)

print()
print("=" * 74)
print("CASE 2 — two declarations, IDENTICAL values")
print("=" * 74)
c2 = os.path.join(tmp, "c2.mp4")
add_plain_too(base, c2, "Lavf62.12.102")     # same string as the ilst atom
report("CASE 2", c2)

print()
print("=" * 74)
print("CASE 3 — two declarations, DIFFERENT values")
print("=" * 74)
c3 = os.path.join(tmp, "c3.mp4")
add_plain_too(base, c3, "SecondWriter 5.0")
report("CASE 3", c3)

print()
print("=" * 74)
print("CASE 4 — two declarations, one MALFORMED payload")
print("=" * 74)
buf = bytes(open(base, "rb").read())
moov, msize = moov_range(buf)
bad = b"\x00\x00\x00\x08data\xff\xff\xff\xff"
atom = struct.pack(">I", 8 + len(bad)) + TOO + bad
upos, usize = child(buf, moov + 8, moov + msize, b"udta")
out4 = buf[:upos + usize] + atom + buf[upos + usize:]
delta = len(atom)
out4 = out4[:upos] + struct.pack(
    "I", struct.unpack(">I", out4[upos:upos + 4])[0] + delta) + out4[upos + 4:]
cm = struct.unpack(">I", out4[moov:moov + 4])[0]
out4 = out4[:moov] + struct.pack(">I", cm + delta) + out4[moov + 4:]
out4, _ = inj._shift_chunk_offsets(out4, delta, moov + cm + delta)
c4 = os.path.join(tmp, "c4.mp4")
open(c4, "wb").write(out4)
report("CASE 4", c4)
