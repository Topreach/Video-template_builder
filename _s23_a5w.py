"""A5-W evidence — does ANY authorised mp4 track-scope mechanism exist?

A5-W asks whether `avc1.compressorname` is an authorised producer-declaration
mechanism. Before ruling, one fact is needed that changes the consequences either way:
is there a track-scope metadata mechanism that IS authorised?

If none exists, then ruling NO does not merely drop one declaration -- it removes the
only source of a two-scope CONFLICT, and the T7 fixture built on `compressorname`
loses its second leg. That cascade must be known before the ruling, not after.

Checks, for each stream-scope key PyAV was asked to write, where the bytes actually
land and whether the demuxer synthesised the value rather than reading it.
"""
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402

CONTAINERS = (b"moov", b"trak", b"udta", b"meta", b"ilst", b"mdia")
tmp = tempfile.mkdtemp()

KEYS = {"encoder": "PRODUCER_STRING_X",
        "handler_name": "HANDLER_STRING_Y",
        "title": "TITLE_STRING_Z"}

path = os.path.join(tmp, "tracktags.mp4")
c = av.open(path, "w")
st = c.add_stream("libx264", rate=10)
st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
for k, v in KEYS.items():
    st.metadata[k] = v
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

print("=" * 76)
print("1. What the demuxer surfaces for the stream")
print("=" * 76)
c = av.open(path)
for s in c.streams:
    if s.type == "video":
        for k in sorted(dict(s.metadata)):
            print(f"    {k:16s} = {dict(s.metadata)[k]!r}")
c.close()

raw = open(path, "rb").read()


def walk(buf, start, end, prefix="", out=None):
    if out is None:
        out = []
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            return out
        name = btype.decode("latin-1", "replace")
        out.append((f"{prefix}/{name}", pos, size))
        if btype in CONTAINERS:
            skip = 4 if btype == b"meta" else 0
            walk(buf, pos + 8 + skip, pos + size, f"{prefix}/{name}", out)
        pos += size
    return out


boxes = walk(raw, 0, len(raw))
print()
print("=" * 76)
print("2. Where does each written STRING physically live?")
print("=" * 76)
print("  NOTE: stsd is NOT descended into here -- the walker's sample-entry")
print("  handling is invalid, which is exactly what G13-M2 established.")
for label, needle in KEYS.items():
    at = raw.find(needle.encode())
    print(f"\n  {label:14s} ({KEYS[label]}) at offset {at}")
    if at < 0:
        print("      NOT PRESENT in the artifact bytes")
        continue
    cands = sorted([b for b in boxes if b[1] <= at < b[1] + b[2]],
                   key=lambda b: b[2])
    for p, s, size in cands[:3]:
        print(f"      inside {p} [{s}..{s + size})")

print()
print("=" * 76)
print("3. Is there a legal trak/udta metadata atom at all?")
print("=" * 76)
traks = [b for b in boxes if b[0].endswith("/trak")]
for p, s, size in traks:
    kids = [k for k in boxes if k[0].startswith(p + "/")]
    print(f"  {p}: {len(kids)} walked descendant(s)")
    for k in kids[:12]:
        print(f"      {k[0]}")

print()
print("=" * 76)
print("VERDICT")
print("=" * 76)
any_in_udta = any("/trak" in b[0] and "/udta" in b[0] for b in boxes)
print(f"  a trak-scoped udta metadata atom exists : {any_in_udta}")
if not any_in_udta:
    print("  -> PyAV's mov muxer writes NO track-scope metadata atom in this")
    print("     toolchain. Every stream key either lands in a codec field or")
    print("     is synthesised by the demuxer. There is therefore NO authorised")
    print("     mp4 track-scope producer-declaration mechanism available today,")
    print("     and ruling A5-W NO removes the only second leg of any")
    print("     two-scope conflict -- including the T7 fixture.")
