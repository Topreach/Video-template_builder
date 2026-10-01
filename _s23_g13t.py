"""G13-T — is `<n>` in `segment/tracks/<n>/tags/<TAG>` the STREAM INDEX or the TRACK NUMBER?

Matroska distinguishes two things that are easy to conflate:
  * the POSITION of a TrackEntry inside the Tracks element (0-based array index), and
  * the TrackNumber the element declares (0xD7), which players present as 1-based and
    which need not equal the position.

A locator address is only resolvable if `<n>` is the right one. This builds a file
with TWO tracks carrying DISTINCT tags, then reads both identities per track and
reports where each tag physically sits.

Minimal EBML reader: element ID is a VINT with the marker retained; size is a VINT
with the marker stripped. Nothing beyond the elements actually present is parsed.
"""
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402

ID = {
    "Segment": 0x18538067, "Info": 0x1549A966, "Tracks": 0x1654AE6B,
    "TrackEntry": 0xAE, "TrackNumber": 0xD7, "TrackType": 0x83,
    "Tags": 0x1254C367, "Tag": 0x7373, "SimpleTag": 0x67C8,
    "TagName": 0x45A3, "TagString": 0x4487,
}


def read_id(buf, pos):
    first = buf[pos]
    if first == 0:
        return None, pos
    length = 1
    mask = 0x80
    while not (first & mask):
        mask >>= 1
        length += 1
    val = int.from_bytes(buf[pos:pos + length], "big")
    return val, pos + length


def read_size(buf, pos):
    first = buf[pos]
    length = 1
    mask = 0x80
    while not (first & mask):
        mask >>= 1
        length += 1
    val = first & (mask - 1)
    for b in buf[pos + 1:pos + length]:
        val = (val << 8) | b
    return val, pos + length


def children(buf, start, end):
    out, pos = [], start
    while pos < end:
        eid, p1 = read_id(buf, pos)
        if eid is None:
            break
        size, p2 = read_size(buf, p1)
        if size <= 0 or p2 + size > end:
            break
        out.append((eid, p2, p2 + size))
        pos = p2 + size
    return out


def descend(buf, start, end, eid):
    for cid, s, e in children(buf, start, end):
        if cid == eid:
            return s, e
    return None


tmp = tempfile.mkdtemp()
path = os.path.join(tmp, "two_tracks.mkv")
print("=" * 74)
print("Build: video track + audio track, each with a DISTINCT tag")
print("=" * 74)
c = av.open(path, "w")
v = c.add_stream("libx264", rate=10)
v.width, v.height, v.pix_fmt = 160, 120, "yuv420p"
v.metadata["ENCODER"] = "TAG_ON_VIDEO_TRACK"
# pcm_s16le is the audio codec the repo's other fixtures use; `aac` needs an encoder
# that is not guaranteed present, and this measurement is about TRACK IDENTITY, not
# about codec support.
a = c.add_stream("pcm_s16le", rate=48000)
a.layout = av.AudioLayout("stereo")
a.metadata["ENCODER"] = "TAG_ON_AUDIO_TRACK"
c.start_encoding()
for i in range(10):
    f = av.VideoFrame(160, 120, "yuv420p")
    for pl in f.planes:
        pl.update(bytes(pl.buffer_size))
    f.pts = i
    for p in v.encode(f):
        c.mux(p)
for i in range(5):
    af = av.AudioFrame(format="s16", layout="stereo", samples=1024)
    af.sample_rate = 48000
    af.pts = i * 1024
    for p in a.encode(af):
        c.mux(p)
print()
print("=" * 74)

for p in v.encode(None):
    c.mux(p)
for p in a.encode(None):
    c.mux(p)
c.close()
print(f"  wrote {os.path.basename(path)}")

c = av.open(path)
for i, s in enumerate(c.streams):
    tag = dict(s.metadata).get("ENCODER")
    print(f"  PyAV stream[{i}] type={s.type:8s} ENCODER={tag!r}")
c.close()

print()
print("=" * 74)
print("Read the physical identities")
print("=" * 74)
buf = open(path, "rb").read()
seg = descend(buf, 0, len(buf), ID["Segment"])
tracks = descend(buf, seg[0], seg[1], ID["Tracks"])
print(f"  Segment [{seg[0]}..{seg[1]})   Tracks [{tracks[0]}..{tracks[1]})")

entries = [c for c in children(buf, tracks[0], tracks[1])
           if c[0] == ID["TrackEntry"]]
print(f"  {len(entries)} TrackEntry(s), in physical order\n")

print(f"  {'pos':>3} {'TrackNumber':>11} {'TrackType':>9}  tags found")
for pos, (eid, s, e) in enumerate(entries):
    tnum, ttype = None, None
    tags = []
    for cid, cs, ce in children(buf, s, e):
        if cid == ID["TrackNumber"]:
            tnum = int.from_bytes(buf[cs:ce], "big")
        elif cid == ID["TrackType"]:
            ttype = int.from_bytes(buf[cs:ce], "big")
        elif cid == ID["Tags"]:
            # SimpleTag -> TagName / TagString
            for tid, ts, te in children(buf, cs, ce):
                if tid != ID["Tag"]:
                    continue
                name, value = None, None
                for sid, ss, se in children(buf, ts, te):
                    if sid == ID["SimpleTag"]:
                        for kid, ks, ke in children(buf, ss, se):
                            if kid == ID["TagName"]:
                                name = buf[ks:ke].decode("utf-8", "replace")
                            elif kid == ID["TagString"]:
                                value = buf[ks:ke].decode("utf-8", "replace")
                if name:
                    tags.append(f"{name}={value!r}")
    print(f"  {pos:>3} {tnum!s:>11} {ttype!s:>9}  {tags}")

print()
print("=" * 74)
print("VERDICT")
print("=" * 74)
nums = [int.from_bytes(
    buf[c[1]:c[2]], "big")
    for e in entries for c in children(buf, e[1], e[2])
    if c[0] == ID["TrackNumber"]]
print(f"  physical positions : 0..{len(entries) - 1}")
print(f"  declared TrackNumbers: {nums}")
if nums == list(range(1, len(entries) + 1)):
    print("  -> TrackNumber is 1-BASED and position is 0-BASED; they DIFFER.")
    print("     An address of `tracks/<n>/tags/<TAG>` resolves ONLY if <n> is the")
    print("     POSITION. Writing TrackNumber there would address the wrong track")
    print("     (or nothing) whenever the two diverge.")
else:
    print(f"  -> TrackNumbers {nums} do not equal 1..n; positions remain the only")
    print("     unambiguous index.")


print("Where do the two literals PHYSICALLY live?")
print("=" * 74)
for label, needle in (("TAG_ON_VIDEO_TRACK", b"TAG_ON_VIDEO_TRACK"),
                      ("TAG_ON_AUDIO_TRACK", b"TAG_ON_AUDIO_TRACK")):
    at = buf.find(needle)
    print(f"\n  {label} at offset {at}")
    # which top-level-ish elements contain it?
    seg_s, seg_e = seg
    for eid, s, e in children(buf, seg_s, seg_e):
        nm = [k for k, v in ID.items() if v == eid]
        nm = nm[0] if nm else hex(eid)
        if s <= at < e:
            print(f"    inside Segment child: {nm} [{s}..{e})")
    if tracks[0] <= at < tracks[1]:
        print("    -> inside the TRACKS element")
        for pos, (eid, s, e) in enumerate(entries):
            if s <= at < e:
                print(f"    -> inside TrackEntry at POSITION {pos} "
                      f"[{s}..{e})")
    if seg[0] <= at < tracks[0]:
        print("    -> before Tracks, i.e. in the Info/global region")

print()
print("=" * 74)
print("G13-T VERDICT")
print("=" * 74)
nums = [int.from_bytes(buf[c[1]:c[2]], "big")
        for e in entries for c in children(buf, e[1], e[2])
        if c[0] == ID["TrackNumber"]]
print(f"  physical positions  : 0..{len(entries) - 1}")
print(f"  declared TrackNumbers: {nums}")
if nums == list(range(1, len(entries) + 1)):
    print("  -> TrackNumber is 1-BASED; position is 0-BASED; THEY DIFFER.")
    print("     `tracks/<n>` resolves ONLY with <n> = POSITION.")
else:
    print(f"  -> TrackNumbers {nums} are not 1..n; POSITION remains the only")
    print("     unambiguous index.")
print()
per_track_tags = 0
for _i, (_eid, s, e) in enumerate(entries):
    per_track_tags += sum(1 for cid, _cs, _ce in children(buf, s, e)
                          if cid == ID["Tags"])
print(f"  Tags elements INSIDE a TrackEntry: {per_track_tags}")
if per_track_tags == 0:
    print("  -> PyAV's mkv muxer did NOT write these tags into TrackEntry/Tags.")
    print("     G13-M row 6 (mkv track Tags ELIGIBLE) must therefore be")
    print("     DOWNGRADED to UNLOCATED until the real location is established.")