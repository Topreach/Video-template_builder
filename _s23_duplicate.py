"""G13-M/R measurement — can one logical mp4 producer key physically exist TWICE?

The duplicate-location case is the whole of G13-R, so it must be measured rather than
assumed legal. This constructs the situation:

  1. PyAV writes the container `encoder` tag to  moov/udta/meta/ilst/©too
  2. a second ©too atom carrying a DIFFERENT value is injected at moov/udta/©too
  3. the artifact is then re-read

Questions answered by observation:
  - are both atoms physically present?          (is the case constructible)
  - does the demuxer surface one, the other, or a merge?
  - can the probe tell WHICH atom produced the value it saw?
"""
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
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


def find_box(buf, start, end, want, path="", found=None):
    """Depth-first search for a box type, returning its full path."""
    if found is None:
        found = []
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            break
        if btype == want:
            found.append((f"{path}/{btype.decode('latin-1')}", pos, size))
        if btype in (b"moov", b"udta", b"meta", b"ilst", b"trak", b"mdia"):
            skip = 4 if btype == b"meta" else 0
            find_box(buf, pos + 8 + skip, pos + size, want,
                     f"{path}/{btype.decode('latin-1')}", found)
        pos += size
    return found


def inject_plain_too(src, dst, value):
    """Insert a `moov/udta/<key>` atom (NOT under meta/ilst) carrying `value`."""
    buf = bytes(open(src, "rb").read())
    moov = buf.find(b"moov") - 4
    moov_size = struct.unpack(">I", buf[moov:moov + 4])[0]

    def child(start, end, want):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", buf[pos:pos + 4])[0]
            if size < 8 or pos + size > end:
                return None
            if buf[pos + 4:pos + 8] == want:
                return (pos, size)
            pos += size
        return None

    payload = inj._too_payload(value)
    atom = struct.pack(">I", 8 + len(payload)) + TOO + payload

    udta = child(moov + 8, moov + moov_size, b"udta")
    if udta:
        pos, size = udta
        out = buf[:pos + size] + atom + buf[pos + size:]
        grow = [(pos, len(atom))]
        created_udta = False
    else:
        udta_size = 8 + len(atom)
        box = struct.pack(">I", udta_size) + b"udta" + atom
        out = buf[:moov + moov_size] + box + buf[moov + moov_size:]
        grow = [(moov, udta_size)]
        created_udta = True

    total = sum(d for _p, d in grow)
    for pos, _d in grow:
        cur = struct.unpack(">I", out[pos:pos + 4])[0]
        out = out[:pos] + struct.pack(">I", cur + total) + out[pos + 4:]
    cur_moov = struct.unpack(">I", out[moov:moov + 4])[0]
    out = out[:moov] + struct.pack(">I", cur_moov + total) + out[moov + 4:]
    out, _p = inj._shift_chunk_offsets(out, total, moov + moov_size + total)
    open(dst, "wb").write(out)
    return created_udta


base = build(os.path.join(tmp, "base.mp4"))
print("=" * 74)
print("STEP 1 — what PyAV's writer actually produces")
print("=" * 74)
buf = bytes(open(base, "rb").read())
for p, pos, size in find_box(buf, 0, len(buf), TOO):
    print(f"  ©too atom at: {p}   (offset {pos}, size {size})")
c = av.open(base)
print("  PyAV container.metadata:", dict(c.metadata))
c.close()

print()
print("=" * 74)
print("STEP 2 — inject a SECOND ©too at moov/udta/ (plain, not under meta/ilst)")
print("=" * 74)
dup = os.path.join(tmp, "dup.mp4")
created = inject_plain_too(base, dup, "SecondWriter 5.0")
print(f"  udta created: {created}")
buf2 = bytes(open(dup, "rb").read())
paths = find_box(buf2, 0, len(buf2), TOO)
for p, pos, size in paths:
    print(f"  ©too atom at: {p}   (offset {pos}, size {size})")
print(f"  -> {len(paths)} physical ©too atom(s) in ONE artifact")

print()
print("=" * 74)
print("STEP 3 — re-read: what does the demuxer surface?")
print("=" * 74)
c = av.open(dup)
print("  PyAV container.metadata:", dict(c.metadata))
c.close()

vals = []
for p, pos, size in paths:
    vals.append(("Lavf62.12.102" in buf2[pos:pos + size].decode("latin-1", "ignore"),
                 "SecondWriter 5.0" in buf2[pos:pos + size].decode("latin-1", "ignore")))
print()
print("  atom contents:", vals)

c = av.open(dup)
seen = dict(c.metadata).get("encoder")
c.close()
print()
print("  VALUE THE PROBE SEES:", repr(seen))
if len(paths) == 2 and seen is not None:
    matched = [i for i, (a, b) in enumerate(vals) if
               (a and "Lavf" in seen) or (b and "SecondWriter" in seen)]
    print(f"  the probe CANNOT tell which atom it read; "
          f"{len(paths)} atoms exist but one value is observed.")
