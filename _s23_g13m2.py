"""G13-M2 — can the track-scope producer tag be located inside `stsd`?

G13-M left mp4 TRACK SCOPE as UNLOCATED because the generic recursive walker is not
valid through `stsd`. This parses `stsd` the way the format actually defines it, and
then answers one question: is a producer-metadata mechanism present there at all?

Deliberately NOT a general sample-entry parser. It reads only what the fixtures
contain -- the FullBox header, the entry count, and the entry header sizes for the
entry types actually observed -- and reports anything it does not recognise rather
than guessing.

Format, per ISO/IEC 14496-12:
  stsd  : FullBox(version/flags 4B, entry_count 4B) then entry_count SampleEntry
  entry : size(4B) format(4B) reserved(6B) data_ref_index(2B) then
          VisualSampleEntry adds 70B  (pre_defined, reserved, [3x12B], w, h,
                                       hres, vres, reserved, frame_count,
                                       compressorname[32], depth, pre_defined)
          AudioSampleEntry adds 20B
          after which child boxes follow
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())

FIX = os.path.join(os.getcwd(), "_s23_fixtures", "conflict_two_scope.mp4")
NEEDLE = b"SomeOtherTool 9.9.9"

raw = open(FIX, "rb").read()
print(f"file: {os.path.basename(FIX)}   size {len(raw)}")
print(f"literal {NEEDLE.decode()} at absolute offset {raw.find(NEEDLE)}\n")


def child_boxes(start, end):
    """Direct children only -- no descent."""
    out, pos = [], start
    while pos + 8 <= end:
        size = struct.unpack(">I", raw[pos:pos + 4])[0]
        btype = raw[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            break
        out.append((btype, pos, size))
        pos += size
    return out


# 1. Walk moov -> trak -> mdia -> minf -> stbl, taking the FIRST match of each.
def find_box(buf_bytes, start, end, want, descend=(b"moov", b"trak", b"mdia",
                                                  b"minf", b"stbl")):
    """Depth-first to a named box. stsd is excluded from `descend` on purpose."""
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf_bytes[pos:pos + 4])[0]
        btype = buf_bytes[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            return None
        if btype == want:
            return pos, size
        if btype in descend:
            skip = 4 if btype == b"meta" else 0
            hit = find_box(buf_bytes, pos + 8 + skip, pos + size, want, descend)
            if hit:
                return hit
        pos += size
    return None


print("=" * 74)
print("1. Locate stsd via a path-aware walk (stsd never descended into)")
print("=" * 74)
hit = find_box(raw, 0, len(raw), b"stsd")
if not hit:
    sys.exit("stsd not found -- check the walk")
stsd_at, stsd_size = hit
print(f"  stsd at {stsd_at}, size {stsd_size}")

print()
print("=" * 74)
print("2. Parse stsd as a FullBox: version/flags(4) + entry_count(4)")
print("=" * 74)
ver_flags = struct.unpack(">I", raw[stsd_at + 8:stsd_at + 12])[0]
count = struct.unpack(">I", raw[stsd_at + 12:stsd_at + 16])[0]
print(f"  version/flags = 0x{ver_flags:08x}")
print(f"  entry_count   = {count}")

pos = stsd_at + 16
end = stsd_at + stsd_size
entries = []
while pos + 8 <= end and len(entries) < count:
    esize = struct.unpack(">I", raw[pos:pos + 4])[0]
    fmt = raw[pos + 4:pos + 8]
    if esize < 8 or pos + esize > end:
        print(f"  !! entry at {pos} claims size {esize}, overruns")
        break
    entries.append((fmt, pos, esize))
    print(f"  entry: format={fmt.decode('latin-1')} at {pos} size {esize}")
    pos += esize

print()
print("=" * 74)
print("3. Parse each sample entry header, then its child boxes")
print("=" * 74)
VISUAL_EXTRA = 70      # bytes after the 8-byte sample-entry header, before children
AUDIO_EXTRA = 20
for fmt, e_at, e_size in entries:
    hdr = 8                                  # size + format
    body_start = e_at + hdr
    print(f"\n  --- {fmt.decode('latin-1')} ---")
    print(f"  raw bytes of entry header: "
          f"{raw[e_at:min(e_at + 8 + VISUAL_EXTRA, e_at + e_size)].hex()}")
    child_start = body_start + VISUAL_EXTRA
    if child_start > e_at + e_size:
        print(f"  visual header overruns the entry -- not a VisualSampleEntry")
        continue
    for btype, c_at, c_size in child_boxes(child_start, e_at + e_size):
        body = raw[c_at + 8:c_at + c_size]
        hitv = NEEDLE in body
        print(f"    child {btype.decode('latin-1'):10s} at {c_at} size {c_size:4d}"
              f"  contains literal={hitv}")

print()
print("=" * 74)
print("4. Where does the literal actually sit? (exhaustive, no parsing)")
print("=" * 74)
at = raw.find(NEEDLE)
print(f"  literal offset: {at}")
print(f"  stsd range     : [{stsd_at}..{stsd_at + stsd_size})")
print(f"  inside stsd    : {stsd_at <= at < stsd_at + stsd_size}")
for fmt, e_at, e_size in entries:
    print(f"  inside entry {fmt.decode('latin-1')} "
          f"[{e_at}..{e_at + e_size}): "
          f"{e_at <= at < e_at + e_size}")

print()
print("=" * 74)
print("VERDICT")
print("=" * 74)
in_stsd = stsd_at <= at < stsd_at + stsd_size
if in_stsd:
    print("  The literal IS inside stsd -- but no child box of the sample entry")
    print("  contains it, so it is not in a legal metadata mechanism. G13-M2 finds")
    print("  NO producer-metadata mechanism there; track scope stays UNLOCATED.")
else:
    print("  The literal is NOT inside stsd. Track scope remains UNLOCATED and the")
    print("  search must continue elsewhere -- but NOT by widening this parser.")
