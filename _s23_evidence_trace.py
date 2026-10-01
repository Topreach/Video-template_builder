"""A7 CARRIER TRACE — emission -> model -> serialization -> consumers.

Run before choosing a carrier. The question A7 leaves open is: which object is
responsible for emitting the `artifact:` address §2.1.17 (v1.4) defines? That cannot
be answered by preference; it has to be answered from what the repository actually
does today.

Also measures what location information the probe can obtain, because a guessed
atom path would be the same class of fabrication as a sentinel string.
"""
import ast
import io
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402

SRC = os.path.join(os.getcwd(), "src")


def walk_py():
    for root, _dirs, files in os.walk(SRC):
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)


print("=" * 78)
print("1. EMISSION SITES (writes to evidence_refs)")
print("=" * 78)
emitters = []
for path in walk_py():
    src = io.open(path, encoding="utf-8").read()
    for i, line in enumerate(src.split("\n"), 1):
        if "evidence_refs=" in line:
            emitters.append((os.path.relpath(path, SRC), i, line.strip()))
for rel, ln, text in emitters:
    print(f"   {rel}:{ln}  {text[:70]}")
print(f"   -> {len(emitters)} emission site(s)")

print()
print("=" * 78)
print("2. MODEL / SERIALIZATION")
print("=" * 78)
from videotemplate.utils.confidence import ProvenanceEntry  # noqa: E402
f = ProvenanceEntry.model_fields["evidence_refs"]
print(f"   declared on   : {type(ProvenanceEntry).__name__}")
print(f"   annotation    : {f.annotation}")
print(f"   default       : {f.default_factory() if callable(f.default_factory) else f.default}")
# No custom serializer touches it: it is a plain pydantic field, so model_dump()
# emits it verbatim and no transform can reinterpret it.
print("   serialization : plain pydantic field -> model_dump() emits verbatim")
print("                   (no custom serializer exists, so nothing can massage it)")

print()
print("=" * 78)
print("3. CONSUMERS (reads of .evidence_refs)")
print("=" * 78)
consumers = []
for path in walk_py():
    src = io.open(path, encoding="utf-8").read()
    for i, line in enumerate(src.split("\n"), 1):
        if ".evidence_refs" in line and "evidence_refs=" not in line:
            consumers.append((os.path.relpath(path, SRC), i, line.strip()))
if consumers:
    for rel, ln, text in consumers:
        print(f"   {rel}:{ln}  {text[:70]}")
else:
    print("   NONE. No module under src/ ever reads evidence_refs.")
print(f"   -> {len(consumers)} consumer(s) in src/")

print()
print("=" * 78)
print("4. WHAT LOCATION INFORMATION THE PROBE CAN ACTUALLY OBTAIN")
print("=" * 78)
FIX = os.path.join(os.getcwd(), "_s23_fixtures", "conflict_two_scope.mp4")
if os.path.exists(FIX):
    c = av.open(FIX)
    print(f"   container.metadata = {dict(c.metadata)}")
    for s in c.streams:
        if s.type == "video":
            print(f"   stream.metadata    = {dict(s.metadata)}")
    loc_attrs = [a for a in dir(c)
                 if any(k in a.lower() for k in ("offset", "pos", "atom", "path"))]
    print(f"   container attrs suggesting a location: {loc_attrs or 'NONE'}")
    print("   -> PyAV hands the probe a {key: value} dict with NO positional data.")
    print("      It cannot distinguish moov/udta/<x> from moov/meta/ilst/<x>/data.")
    c.close()
else:
    print("   (fixture absent; run _s23_fixture_inject.py first)")
