import os
import sys
import tempfile
import traceback

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from videotemplate.ingestion.ingestor import Ingestor

tmp = tempfile.mkdtemp()
p = os.path.join(tmp, "unreadable.mp4")
open(p, "wb").write(b"A" * 128)

ing = Ingestor(max_duration=30.0)
try:
    d = ing.ingest(p)
    c = d.container
    print("ingest OK")
    print("  probe_state    =", getattr(c.probe_state, "value", None))
    print("  producer_state =", getattr(c.producer_state, "value", None))
    print("  format         =", getattr(c, "format", None))
except Exception:
    print("RAISED:")
    traceback.print_exc()

# A8's `no_synthetic` condition, per-fixture.
import av

print("\nA8 no_synthetic probe (decls empty AND version None required of EACH):")
cases = {"128 ASCII bytes": p}
p2 = os.path.join(tmp, "trunc.mp4")
c = av.open(p2, "w")
st = c.add_stream("libx264")
st.width, st.height, st.pix_fmt, st.rate = 160, 120, "yuv420p", 24
c.start_encoding()
for i in range(8):
    f = av.VideoFrame(160, 120, "yuv420p")
    for pl in f.planes:
        pl.update(bytes(pl.buffer_size))
    f.pts = i
    c.mux(st.encode(f))
for pk in st.encode(None):
    c.mux(pk)
c.close()
with open(p2, "r+b") as fh:
    fh.truncate(24)
cases["24-byte header"] = p2

p3 = os.path.join(tmp, "novideo.mkv")
c = av.open(p3, "w")
a = c.add_stream("pcm_s16le", rate=48000)
a.layout = av.AudioLayout("stereo")
c.start_encoding()
for i in range(4):
    af = av.AudioFrame(format="s16", layout="stereo", samples=1024)
    af.sample_rate = 48000
    af.pts = i * 1024
    for pk in a.encode(af):
        c.mux(pk)
for pk in a.encode(None):
    c.mux(pk)
c.close()
cases["no video stream"] = p3

for label, path in cases.items():
    d = ing.ingest(path)
    cc = d.container
    decls = list(cc.producer_declarations or [])
    ver = getattr(cc.source, "version", None) if cc.source else None
    ps = getattr(cc.probe_state, "value", None)
    print(f"  {label:18s} probe={ps!s:16s} decls={len(decls)} version={ver!r} "
          f"clean={not decls and ver is None}")
    for dd in decls:
        print(f"       -> {getattr(dd, 'key', None)!r} = "
              f"{getattr(dd, 'value', None)!r} "
              f"origin={getattr(getattr(dd, 'origin', None), 'value', None)!r}")
