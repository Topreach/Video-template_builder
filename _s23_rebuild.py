"""Can a PRODUCER key be placed at mp4 track scope through an authorised mechanism?

The rebuild of T7 depends on this. A5-W established that `trak/udta/name` exists and
is read back, proving a track-scope metadata mechanism -- but `name` is a TITLE atom,
not a producer identity, so it cannot stand in as the second leg of a producer
conflict.

So the real question: can a producer key (`encoder` / `©too`) be written to, and read
from, `trak/udta`? Three routes are tried, because the earlier hand-injected attempt
came back as `encoder: ''` -- which G13-E now classifies as NOT a valid declaration.

  R1  PyAV writes stream metadata `©too` directly
  R2  byte-injected `trak/udta/©too`, iTunes payload, locale variants
  R3  byte-injected `trak/udta/<key-as-atom-name>` (the shape `title` used)
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


def build(path, stream_tags=None, n=10):
    c = av.open(path, "w")
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    for k, v in (stream_tags or {}).items():
        st.metadata[k] = v
    c.start_encoding()
    for i in range(n):
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


def probe(path, label):
    c = av.open(path)
    for s in c.streams:
        if s.type == "video":
            md = dict(s.metadata)
            c.close()
            print(f"  {label}")
            for k in sorted(md):
                print(f"      {k:16s} = {md[k]!r}")
            return md.get("encoder")
    c.close()
    return None


print("=" * 76)
print("R1 — PyAV writes stream metadata '©too' directly")
print("=" * 76)
r1 = build(os.path.join(tmp, "r1.mp4"), {"©too": "PRODUCER_DIRECT"})
probe(r1, "stream metadata")

print()
print("=" * 76)
print("R2 — byte-injected trak/udta/©too, iTunes payload, locale variants")
print("=" * 76)


def inject_trak_udta(src, dst, value, locale=0, atom=TOO):
    """Insert `atom` into the track's udta (creating udta if needed)."""
    buf = bytearray(open(src, "rb").read())

    def boxes(start, end):
        out, pos = [], start
        while pos + 8 <= end:
            size = struct.unpack(">I", buf[pos:pos + 4])[0]
            btype = buf[pos + 4:pos + 8]
            if size < 8 or pos + size > end:
                break
            out.append((btype, pos, size))
            pos += size
        return out

    moov = buf.find(b"moov") - 4
    msize = struct.unpack(">I", buf[moov:moov + 4])[0]
    trak = next(b for b in boxes(moov + 8, moov + msize) if b[0] == b"trak")
    t_at, t_size = trak[1], trak[2]
    tb = boxes(t_at + 8, t_at + t_size)
    udta = next((b for b in tb if b[0] == b"udta"), None)

    raw = value.encode("utf-8")
    payload = (struct.pack(">I", 16 + len(raw)) + b"data"
               + struct.pack(">I", 1) + struct.pack(">I", locale) + raw)
    box = struct.pack(">I", 8 + len(payload)) + atom + payload

    if udta:
        buf[udta[1] + udta[2]:udta[1] + udta[2]] = box
        grow_at, delta = udta[1], len(box)
    else:
        ubox = struct.pack(">I", 8 + len(box)) + b"udta" + box
        buf[t_at + t_size:t_at + t_size] = ubox
        grow_at, delta = t_at, 8 + len(box)
    buf[grow_at:grow_at + 4] = struct.pack(
        "I", struct.unpack(">I", buf[grow_at:grow_at + 4])[0] + delta)
    cm = struct.unpack(">I", buf[moov:moov + 4])[0]
    buf[moov:moov + 4] = struct.pack("I", cm + delta)
    out, _ = inj._shift_chunk_offsets(bytes(buf), delta, moov + cm + delta)
    open(dst, "wb").write(out)


base = build(os.path.join(tmp, "base.mp4"))
for locale in (0, 1, 0x409):
    p = os.path.join(tmp, f"r2_{locale}.mp4")
    inject_trak_udta(base, p, "PRODUCER_INJECTED", locale=locale)
    probe(p, f"locale={locale}")

print()
print("=" * 76)
print("R3 — byte-injected trak/udta/<key-as-atom-name> (the shape `title` used)")
print("=" * 76)
p = os.path.join(tmp, "r3.mp4")
inject_trak_udta(base, p, "PRODUCER_NAMED", atom=b"encoder")
probe(p, "atom type 'encoder'")

print()
print("=" * 76)
print("VERDICT")
print("=" * 76)
print("  A producer key is only usable if it comes back NON-EMPTY -- an empty")
print("  value is not a declaration (G13-E). Which routes returned a non-empty")
print("  stream 'encoder' is the question the rebuild depends on.")
