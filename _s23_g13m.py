"""G13-M — which artifact structures are ELIGIBLE evidence sources?

Eligibility now means something specific and testable, following G13-E:

    a structure is ELIGIBLE iff the probe can obtain a NON-EMPTY value from it,
    and that value can legitimately become a ProducerDeclaration.

Physical presence is NOT eligibility. G13-P already showed `/moov/udta/<key>` is
physically present yet unreadable, so it is ineligible.

Measures the paths that were previously UNKNOWN -- chiefly the mp4 TRACK-SCOPE one,
which the A7/T7 two-scope fixture actually contains but was never located -- and
confirms the Matroska case by byte offset. Anything not measured here is reported
UNTESTED rather than assumed eligible.
"""
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402

CONTAINERS = (b"moov", b"trak", b"udta", b"meta", b"ilst", b"mdia")


def walk(buf, start, end, prefix="", out=None):
    if out is None:
        out = []
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            return out
        name = btype.decode("latin-1")
        path = f"{prefix}/{name}"
        out.append((path, pos, size))
        if btype in CONTAINERS:
            skip = 4 if btype == b"meta" else 0
            walk(buf, pos + 8 + skip, pos + size, path, out)
        pos += size
    return out


def find_values(path, needle):
    buf = open(path, "rb").read()
    return [(p, o, s) for p, o, s in walk(buf, 0, len(buf))
            if needle.encode("utf-8") in buf[o + 8:o + s]]


print("=" * 78)
print("1. MP4 TRACK-SCOPE — where does the two-scope fixture's stream tag live?")
print("=" * 78)
FIX = os.path.join(os.getcwd(), "_s23_fixtures", "conflict_two_scope.mp4")
if not os.path.exists(FIX):
    sys.exit("fixture missing -- run _s23_fixture_inject.py")
for label, needle in (("container 'HandBrake 1.6.0 2023041600'",
                       "HandBrake 1.6.0 2023041600"),
                      ("stream    'SomeOtherTool 9.9.9'", "SomeOtherTool 9.9.9")):
    hits = find_values(FIX, needle)
    print(f"\n  {label}")
    for p, o, s in hits:
        print(f"    {p}   (offset {o}, size {s})")
    if not hits:
        print("    NOT FOUND by the walker")

c = av.open(FIX)
print(f"\n  probe sees container.encoder = {dict(c.metadata).get('encoder')!r}")
for st in c.streams:
    if st.type == "video":
        print(f"  probe sees stream.encoder    = "
              f"{dict(st.metadata).get('encoder')!r}")
c.close()

print()
print("=" * 78)
print("2. MATROSKA — byte offset of each Tags element relative to its parent")
print("=" * 78)
tmp = tempfile.mkdtemp()
mkv = os.path.join(tmp, "t.mkv")
o = av.open(mkv, "w")
o.metadata["ENCODER"] = "ContainerWriter 1.0"
st = o.add_stream("libx264", rate=10)
st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
st.metadata["ENCODER"] = "TrackWriter 2.0"
o.start_encoding()
for i in range(10):
    f = av.VideoFrame(160, 120, "yuv420p")
    for pl in f.planes:
        pl.update(bytes(pl.buffer_size))
    f.pts = i
    for p in st.encode(f):
        o.mux(p)
for p in st.encode(None):
    o.mux(p)
o.close()

raw = open(mkv, "rb").read()
TAGS = bytes([0x12, 0x54, 0xC3, 0x67])
INFO = bytes([0x15, 0x49, 0xA9, 0x66])
TRACKS = bytes([0x16, 0x54, 0xAE, 0x6B])
info_at = raw.find(INFO)
tracks_at = raw.find(TRACKS)
print(f"  Info element  offset : {info_at}")
print(f"  Tracks element offset: {tracks_at}")
for i in range(raw.count(TAGS)):
    at = raw.find(TAGS, i if i == 0 else prev + 1)
    prev = at
    parent = "Info (global)" if 0 <= at - info_at < 4000 and info_at < at else \
             ("Tracks/TrackEntry" if tracks_at < at else "unknown")
    print(f"  Tags element at {at:6d}  -> nearest parent: {parent}")
    body = raw[at:at + 400]
    which = []
    if b"ContainerWriter 1.0" in body:
        which.append("ContainerWriter 1.0")
    if b"TrackWriter 2.0" in body:
        which.append("TrackWriter 2.0")
    print(f"     values inside: {which or 'none within 400 bytes'}")

c = av.open(mkv)
print(f"\n  probe container ENCODER = {dict(c.metadata).get('ENCODER')!r}")
for s in c.streams:
    if s.type == "video":
        print(f"  probe stream ENCODER    = {dict(s.metadata).get('ENCODER')!r}")
c.close()
