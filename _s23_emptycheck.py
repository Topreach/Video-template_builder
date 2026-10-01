"""Does an empty-valued producer tag survive into the contract as a declaration?

The G13-R control shows the demuxer returns `encoder: ''` when the same key is
physically present twice. An empty string is NOT a producer declaration, so this
checks what the CURRENT ingestor does with one -- evidence for the record, not a fix.
"""
import os
import sys
import tempfile
import types

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402
from videotemplate.ingestion.ingestor import Ingestor  # noqa: E402

# load the control module's helpers without running its driver
src = open("_s23_control.py", encoding="utf-8").read().split('print("=" * 74)')[0]
g = types.ModuleType("ctl")
exec(compile(src, "ctl", "exec"), g.__dict__)

tmp = tempfile.mkdtemp()
base = g.build(os.path.join(tmp, "b.mp4"))
dup = os.path.join(tmp, "dup.mp4")
g.add_plain_too(base, dup, "SecondWriter 5.0")

desc = Ingestor(max_duration=30.0).ingest(dup)
decls = desc.container.producer_declarations
print("declarations recorded:", len(decls))
for d in decls:
    print(f"   scope={d.scope:12s} key={d.original_key:14s} "
          f"value={d.original_value!r}")
print("producer_state:", desc.container.producer_state)
print()
empties = [d for d in decls if d.original_value == ""]
print(f"EMPTY-VALUED declarations retained: {len(empties)}")
if empties:
    print("  -> an empty string is being recorded as a producer declaration.")
    print("     That is the same fabrication class as a sentinel: it asserts an")
    print("     observation that was never made.")
else:
    print("  -> empties are already excluded; no change needed.")
