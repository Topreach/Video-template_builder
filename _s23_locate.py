"""Where EXACTLY does the two-scope fixture's stream-scope tag live?

The first G13-M pass reported the stream value inside `/moov/trak/mdia/minf`, which
is not a plausible home for a metadata tag and may be a walker artifact. This
locates the literal bytes against every top-level and trak-level box boundary, so
the claim is either substantiated or withdrawn.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())

FIX = os.path.join(os.getcwd(), "_s23_fixtures", "conflict_two_scope.mp4")
raw = open(FIX, "rb").read()

for needle in (b"HandBrake 1.6.0 2023041600", b"SomeOtherTool 9.9.9"):
    at = raw.find(needle)
    print(f"\n{needle.decode()}")
    print(f"  literal bytes at absolute offset: {at}")

# enumerate every box in the file, depth-first, with absolute ranges
boxes = []


def walk(start, end, prefix=""):
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", raw[pos:pos + 4])[0]
        btype = raw[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            return
        name = btype.decode("latin-1", "replace")
        boxes.append((f"{prefix}/{name}", pos, pos + size))
        if btype in (b"moov", b"trak", b"udta", b"meta", b"ilst", b"mdia",
                     b"minf", b"stbl", b"dinf"):
            skip = 4 if btype == b"meta" else 0
            walk(pos + 8 + skip, pos + size, f"{prefix}/{name}")
        pos += size


walk(0, len(raw))
print(f"\n  {len(boxes)} boxes walked")

for label, needle in (("CONTAINER 'HandBrake...'", b"HandBrake 1.6.0 2023041600"),
                      ("STREAM 'SomeOtherTool...'", b"SomeOtherTool 9.9.9")):
    at = raw.find(needle)
    # innermost box whose byte range contains the literal
    cands = [b for b in boxes if b[1] <= at < b[2]]
    cands.sort(key=lambda b: b[2] - b[1])
    print(f"\n  {label} at {at}")
    if cands:
        for p, s, e in cands[:4]:
            print(f"    contains: {p}  [{s}..{e})  width {e - s}")
    else:
        print("    NO BOX contains it -- the value is NOT inside a walked box")

# Any (c)too anywhere in the file, regardless of descent rules?
TOO = b"\xa9too"
idx = raw.find(TOO)
while idx != -1:
    size = struct.unpack(">I", raw[idx - 4:idx])[0] if idx >= 4 else 0
    print(f"\n  (c)too box at {idx - 4} (size field {size}, ends {idx - 4 + size})")
    idx = raw.find(TOO, idx + 1)
