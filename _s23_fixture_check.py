"""Is the T-R3b fixture structurally well-formed enough for byte-level research?

R1.1's box walk terminated at `<BROKEN>` on the `©too` item: its declared size
overruns its parent `ilst`. Before drawing any conclusion about address identity, the
artifact itself must be checked -- a byte-resolving locator cannot be researched on a
box chain that does not close.

Compares the BASE file (muxer-written) with the INJECTED file, box by box.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())

F = os.path.join(os.getcwd(), "_s23_fixtures")


def report(path, label):
    raw = open(path, "rb").read()
    print(f"\n{'=' * 74}\n{label}  ({len(raw)} bytes)\n{'=' * 74}")
    problems = []

    def walk(start, end, prefix=""):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", raw[pos:pos + 4])[0]
            btype = raw[pos + 4:pos + 8]
            if size < 8 or pos + size > end:
                problems.append(
                    (f"{prefix}/{btype.decode('latin-1', 'replace')}",
                     pos, size, pos + size, end))
                print(f"    !! OVERRUN  {prefix}/{btype!r} at {pos} "
                      f"size={size} ends={pos + size} but parent ends {end}")
                return
            name = btype.decode("latin-1", "replace")
            print(f"    {prefix}/{name:12s} at {pos:6d} size={size:5d} "
                  f"ends={pos + size}")
            if btype in (b"moov", b"udta", b"ilst"):
                walk(pos + 8, pos + size, f"{prefix}/{name}")
            elif btype == b"meta":
                walk(pos + 12, pos + size, f"{prefix}/{name}")
            pos += size

    moov = raw.find(b"moov") - 4
    walk(moov, moov + struct.unpack(">I", raw[moov:moov + 4])[0])
    print(f"  -> {len(problems)} structural problem(s)")
    return problems


base_problems = report(os.path.join(F, "t1_base.mp4"),
                       "BASE (muxer-written, unmodified)")
inj_problems = report(os.path.join(F, "declared_real.mp4"),
                      "INJECTED (T-R3b container declaration)")

print()
print("=" * 74)
print("The specific inconsistency, quantified")
print("=" * 74)
raw = open(os.path.join(F, "declared_real.mp4"), "rb").read()
at = raw.find(b"\xa9too") - 4
declared = struct.unpack(">I", raw[at:at + 4])[0]
body = raw[at + 8:at + declared]
val_at = body.find(b"HandBrake 1.6.0 2023041600")
value_len = len(b"HandBrake 1.6.0 2023041600")
print(f"  (c)too box at {at}, declared size {declared}")
print(f"  body actually holds the value at body offset {val_at}")
print(f"  value length {value_len}")
print(f"  -> iTunes payload = 8(data hdr) + 4(type) + 4(locale) + "
      f"{value_len}(value) = {16 + value_len} bytes")
print(f"  -> so the box SHOULD be 8 + {16 + value_len} = {24 + value_len} bytes")
print(f"  -> declared {declared}, expected {24 + value_len}, "
      f"DISCREPANCY {declared - (24 + value_len)}")

base = open(os.path.join(F, "t1_base.mp4"), "rb").read()
bat = base.find(b"\xa9too") - 4
bdeclared = struct.unpack(">I", base[bat:bat + 4])[0]
print(f"\n  base (c)too declared size {bdeclared} for value 'Lavf62.12.102' "
      f"({len('Lavf62.12.102')} chars) -> expected "
      f"{24 + len('Lavf62.12.102')}")
print(f"  base box is therefore {'CONSISTENT' if bdeclared == 24 + len('Lavf62.12.102') else 'ALSO INCONSISTENT'}")

print()
print("=" * 74)
print("VERDICT FOR R1.1")
print("=" * 74)
if base_problems == [] and inj_problems:
    print("  The BASE is well-formed; the INJECTED artifact is NOT.")
    print("  The T-R3b injector wrote the (c)too box's size field inconsistently,")
    print("  so the item box overruns ilst by the value-length delta.")
    print("  R1.1 CANNOT be completed on this fixture: a byte-resolving address")
    print("  cannot be researched against a box chain that does not close.")
    print("  The fixture must be rebuilt before R1.2.")
else:
    print("  Both artifacts are structurally sound.")
