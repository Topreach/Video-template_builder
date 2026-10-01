"""G13-E — distinguishing a GENUINE empty producer value from a DEMUXER DEGRADATION.

G13-P established that this demuxer manufactures `encoder = ''` from a physical
condition where the declaration is NOT observable. That raises the question G13-E
must answer before any state rule can be written:

  Q2  can "" EVER be a legitimate producer declaration value?
  Q3  can a genuine empty declaration be told apart from the degradation?

Method: author BOTH cases and compare what reaches the contract.
  A. genuine empty   -- a real (c)too atom whose value string is ""
  B. degradation     -- the unreadable plain udta sibling (G13-P)
  C. normal          -- the readable meta/ilst form, as a control

If A and B are indistinguishable to the consumer, then "" cannot be trusted in
EITHER case, and any rule must reject it unconditionally rather than trying to
detect the degradation.
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
    "_g", os.path.join(os.getcwd(), "_s23_g13p.py"))
g = importlib.util.module_from_spec(spec)
# load only the helper half (stop before the driver)
src = open("_s23_g13p.py", encoding="utf-8").read().split('print("=" * 74)')[0]
mod = type(spec)  # noqa: E841
ns = {}
exec(compile(src, "g13p_helpers", "exec"), ns)
build, strip_too, add_plain_too = (ns["build"], ns["strip_too"], ns["add_plain_too"])
inj = ns["inj"]
TOO = ns["TOO"]

tmp = tempfile.mkdtemp()


def empty_value_too(src, dst):
    """A genuine (c)too atom whose declared string is EMPTY."""
    buf = bytearray(open(src, "rb").read())
    moov = ns["moov_range"](buf)
    moov, msize = moov
    # iTunes data payload with a zero-length value string
    payload = (struct.pack(">I", 16) + b"data"
               + struct.pack(">I", 1) + struct.pack(">I", 0))
    atom = struct.pack(">I", 8 + len(payload)) + TOO + payload
    hit = ns["child"](buf, moov + 8, moov + msize, b"udta")
    pos, size = hit
    buf[pos + size:pos + size] = atom
    total = len(atom)
    buf[pos:pos + 4] = struct.pack(
        "I", struct.unpack(">I", buf[pos:pos + 4])[0] + total)
    cm = struct.unpack(">I", buf[moov:moov + 4])[0]
    buf[moov:moov + 4] = struct.pack(">I", cm + total)
    out, _ = inj._shift_chunk_offsets(bytes(buf), total, moov + cm + total)
    open(dst, "wb").write(out)


def probe(path, label, runs=3):
    print(f"\n{label}")
    seen = []
    for i in range(runs):
        c = av.open(path)
        md = dict(c.metadata)
        c.close()
        enc = md.get("encoder", "<absent>")
        extra = {k: v for k, v in md.items()
                 if k.startswith("encoder") and k != "encoder"}
        seen.append((enc, tuple(sorted(extra))))
        print(f"  run {i + 1}: encoder={enc!r}   siblings={extra}")
    values = {s[0] for s in seen}
    sibs = {s[1] for s in seen}
    return values, sibs


print("=" * 76)
print("A. GENUINE EMPTY — a real (c)too whose value string is ''")
print("=" * 76)
base = build(os.path.join(tmp, "base.mp4"))
stripped = os.path.join(tmp, "stripped.mp4")
strip_too(base, stripped)
genuine = os.path.join(tmp, "genuine_empty.mp4")
empty_value_too(stripped, genuine)
a_vals, a_sibs = probe(genuine, "A: genuine empty", runs=3)

print()
print("=" * 76)
print("B. DEGRADATION — unreadable plain udta sibling (G13-P)")
print("=" * 76)
deg = os.path.join(tmp, "degraded.mp4")
add_plain_too(base, deg, "PlainOnlyWriter 1.0")
b_vals, b_sibs = probe(deg, "B: degradation", runs=3)

print()
print("=" * 76)
print("C. CONTROL — readable meta/ilst form")
print("=" * 76)
c_vals, c_sibs = probe(base, "C: control", runs=3)

print()
print("=" * 76)
print("VERDICT")
print("=" * 76)
print(f"  A genuine empty  : encoder values={a_vals}  siblings={a_sibs}")
print(f"  B degradation    : encoder values={b_vals}  siblings={b_sibs}")
print()
if a_vals == b_vals:
    print("  A and B are INDISTINGUISHABLE at the contract surface.")
    print("  -> \"\" cannot be trusted in either case; any rule must reject it")
    print("     UNCONDITIONALLY rather than trying to detect the degradation.")
else:
    print("  A and B differ. The distinction may be detectable -- inspect the")
    print("  sibling keys before writing any rule.")
if len(b_sibs) > 1:
    print()
    print("  NOTE: the degradation's sibling keys VARY between runs")
    print("  (", b_sibs, ")")
    print("  -> that is uninitialised memory, not a stable signature, so it")
    print("     cannot be used as a detection signal.")
