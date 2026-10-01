"""Decode the avc1 `compressorname` field that G13-M2 located the literal inside.

G13-M2 found the stream-scope string at offset 1840, inside `stsd` -> `avc1`, and
NOT in any child box. The VisualSampleEntry header layout predicts it is in
`compressorname` (a 32-byte Pascal string: length byte + text). This decodes that
field on both the conflict fixture and the untouched control, so the claim rests on
a structural decode rather than on an offset coincidence.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
FIXDIR = os.path.join(os.getcwd(), "_s23_fixtures")


def stsd_of(path):
    raw = open(path, "rb").read()

    def find(start, end, want, descend=(b"moov", b"trak", b"mdia",
                                         b"minf", b"stbl")):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", raw[pos:pos + 4])[0]
            btype = raw[pos + 4:pos + 8]
            if size < 8 or pos + size > end:
                return None
            if btype == want:
                return pos, size
            if btype in descend:
                hit = find(pos + 8, pos + size, want, descend)
                if hit:
                    return hit
            pos += size
        return None

    hit = find(0, len(raw), b"stsd")
    if not hit:
        return None
    at, size = hit
    esize = struct.unpack(">I", raw[at + 16:at + 20])[0]
    fmt = raw[at + 20:at + 24]
    return raw, at, size, at + 16, fmt, esize


def decode(raw, entry_at, esize):
    """VisualSampleEntry: 8B sample-entry header + 70B, of which compressorname is 32B."""
    # offsets inside the VisualSampleEntry, relative to entry start
    W, H, HRES, VRES, RES, FRAME, COMP, DEPTH = 32, 34, 36, 40, 44, 48, 50, 82
    w = struct.unpack(">H", raw[entry_at + W:entry_at + W + 2])[0]
    h = struct.unpack(">H", raw[entry_at + H:entry_at + H + 2])[0]
    frames = struct.unpack(">H", raw[entry_at + FRAME:entry_at + FRAME + 2])[0]
    cname = raw[entry_at + COMP:entry_at + COMP + 32]
    depth = struct.unpack(">H", raw[entry_at + DEPTH:entry_at + DEPTH + 2])[0]
    n = cname[0]
    text = cname[1:1 + n].decode("latin-1") if 0 < n <= 31 else "<invalid len>"
    return {"width": w, "height": h, "frame_count": frames, "depth": depth,
            "compressorname_raw": cname[:16].hex(),
            "compressorname_len": n, "compressorname": text}


for name in ("conflict_two_scope.mp4", "t1_base.mp4", "declared_real.mp4"):
    p = os.path.join(FIXDIR, name)
    if not os.path.exists(p):
        print(f"\n{name}: MISSING")
        continue
    got = stsd_of(p)
    print(f"\n{'=' * 70}\n{name}\n{'=' * 70}")
    if not got:
        print("  stsd not located")
        continue
    raw, s_at, s_size, e_at, fmt, esize = got
    print(f"  stsd [{s_at}..{s_at + s_size})  entry {fmt.decode('latin-1')} "
          f"at {e_at} size {esize}")
    d = decode(raw, e_at, esize)
    for k, v in d.items():
        print(f"    {k:22s} {v!r}")

print(f"\n{'=' * 70}")
print("INTERPRETATION")
print("=" * 70)
print("  If `compressorname` carries producer text on the conflict fixture but a")
print("  normal codec name on the controls, then PyAV's mov muxer wrote a stream")
print("  metadata tag into the SAMPLE DESCRIPTION, not into a metadata box.")
print("  That makes track scope UNLOCATED as a metadata mechanism -- and it is")
print("  itself worth recording as an anomaly.")
