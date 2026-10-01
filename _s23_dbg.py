"""Can the probe HONESTLY produce an `artifact:` locator?

A7 requires the probe to emit an address that identifies evidence inside the
artifact. Before choosing a carrier, establish whether PyAV exposes enough
information to build one without guessing. A guessed atom path is the same class
of fabrication as a sentinel string, and v1.4 exists to forbid it.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402

FIX = os.path.join(os.getcwd(), "_s23_fixtures", "conflict_two_scope.mp4")

c = av.open(FIX)
print("container.metadata :", dict(c.metadata))
for s in c.streams:
    if s.type == "video":
        print("stream.metadata    :", dict(s.metadata))

# Does the demuxer expose a byte offset / location for any tag?
print()
print("container attributes that might carry a location:")
for attr in sorted(dir(c)):
    if any(k in attr.lower() for k in ("offset", "path", "pos", "index",
                                        "tag", "atom", "meta")):
        try:
            v = getattr(c, attr)
            print(f"   {attr:28s} {type(v).__name__}")
        except Exception as exc:
            print(f"   {attr:28s} <{type(exc).__name__}>")

print()
print("stream attributes that might carry a location:")
s = next(x for x in c.streams if x.type == "video")
for attr in sorted(dir(s)):
    if any(k in attr.lower() for k in ("offset", "pos", "tag", "atom", "meta")):
        try:
            v = getattr(s, attr)
            print(f"   {attr:28s} {type(v).__name__}")
        except Exception as exc:
            print(f"   {attr:28s} <{type(exc).__name__}>")
c.close()

# Compare with a Matroska file, whose tag locations are flat by spec.
tmp = tempfile.mkdtemp()
mkv = os.path.join(tmp, "t.mkv")
o = av.open(mkv, "w")
o.metadata["ENCODER"] = "Lavf62.12.102"
st = o.add_stream("libx264", rate=10)
st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
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
o = av.open(mkv)
print()
print("mkv container.metadata:", dict(o.metadata))
print("mkv exposes a location attribute:",
      [a for a in dir(o) if "offset" in a.lower() or "pos" in a.lower()])
o.close()
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402
from videotemplate.ingestion.ingestor import Ingestor  # noqa: E402

tmp = tempfile.mkdtemp()
ing = Ingestor(max_duration=30.0)


def val(x):
    return getattr(x, "value", x)


def show(label, path, ingestor=None):
    try:
        d = (ingestor or ing).ingest(path)
    except BaseException as exc:
        print(f"{label:24s} RAISED {type(exc).__name__}: {exc}")
        return
    c = d.container
    print(f"{label:24s} probe_state={str(val(c.probe_state)):18s} "
          f"producer_state={str(val(c.producer_state)):12s} "
          f"format={str(c.format):12s} "
          f"decls={len(c.producer_declarations or [])} "
          f"src_version={getattr(c.source, 'version', None)!r}")
    print(f"{'':24s} groups never reached: "
          f"video_stream={d.video_stream is None} "
          f"fps={d.fps_actual is None} cfr={d.cfr_vfr is None} "
          f"dur={d.duration is None} qs={d.quality_score is None}")


def valid_clip(path, frames=10):
    c = av.open(path, "w")
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    c.start_encoding()
    for i in range(frames):
        f = av.VideoFrame(160, 120, "yuv420p")
        for pl in f.planes:
            pl.update(bytes(pl.buffer_size))
        f.pts = i
        for p in st.encode(f):
            c.mux(p)
    for p in st.encode(None):
        c.mux(p)
    c.close()
    return path


def audio_only(path):
    c = av.open(path, "w")
    a = c.add_stream("pcm_s16le", rate=48000)
    a.layout = av.AudioLayout("stereo")
    c.start_encoding()
    for i in range(4):
        af = av.AudioFrame(format="s16", layout="stereo", samples=1024)
        af.sample_rate = 48000
        af.pts = i * 1024
        for p in a.encode(af):
            c.mux(p)
    for p in a.encode(None):
        c.mux(p)
    c.close()
    return path


p_ok = valid_clip(os.path.join(tmp, "ok.mp4"))

p_garbage = os.path.join(tmp, "garbage.mp4")
with open(p_garbage, "wb") as fh:
    fh.write(b"A" * 128)

p_trunc = valid_clip(os.path.join(tmp, "trunc.mp4"), frames=8)
with open(p_trunc, "r+b") as fh:
    fh.truncate(24)

p_audio = audio_only(os.path.join(tmp, "audio.mkv"))

show("SUCCESS (valid)", p_ok)
show("UNREADABLE (garbage)", p_garbage)
show("UNREADABLE (truncated)", p_trunc)
show("NO_VIDEO_STREAM", p_audio)
show("REJECTED_BY_POLICY", p_ok, Ingestor(max_duration=0.001))
