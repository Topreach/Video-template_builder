"""Stage 2.3 probe-capability experiment (reproducible evidence for the 2.3 freeze audit).

Builds fixtures exactly the way tests/test_pipeline.py does, then asks the ONLY approved probe
mechanism in this repo (PyAV, av.open) what it can actually see. Prints a plain-text report.
Run:  python _s23_probe_experiment.py > _s23_out.txt 2>&1
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

import av
import numpy as np

TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s23_fixtures")


def dec(v) -> str:
    if isinstance(v, tuple):
        return "%d.%d.%d" % v
    return "%d.%d.%d" % ((v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)


def write_clip(path, duration=1.0, fps=10.0, codec=None, container_metadata=None, stream_metadata=None):
    """Same construction as tests/test_pipeline.create_simple_video, plus optional tags."""
    fps_int = int(fps)
    codec = codec or ("libvpx" if path.lower().endswith((".webm",)) else "libx264")
    container = av.open(path, mode="w")
    if container_metadata:
        for k, v in container_metadata.items():
            container.metadata[k] = v
    stream = container.add_stream(codec, rate=Fraction(fps_int), time_base=Fraction(1, fps_int * 100))
    stream.width = 160
    stream.height = 120
    stream.pix_fmt = "yuv420p"
    if stream_metadata:
        for k, v in stream_metadata.items():
            stream.metadata[k] = v
    n_frames = int(duration * fps)
    for i in range(n_frames):
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        x = int((i / max(n_frames - 1, 1)) * 100)
        img[30:50, x : x + 20] = 255
        frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        frame.pts = i
        frame.time_base = stream.time_base
        for packet in stream.encode(frame):
            container.mux(packet)
    for packet in stream.encode(None):
        container.mux(packet)
    container.close()
    return path


def probe(path, label):
    print(f"\n=== {label} :: {os.path.basename(path)}")
    try:
        c = av.open(path, metadata_errors="warn")
    except Exception as exc:  # noqa: BLE001 - the failure IS the datum
        print(f"  PROBE FAILURE: {type(exc).__name__}: {exc}")
        sys.stdout.flush()
        return
    with c:
        print(f"  format.name      = {c.format.name!r}")
        print(f"  format.long_name = {c.format.long_name!r}")
        print(f"  format.flags     = {getattr(c.format, 'flags', 'n/a')!r}")
        print(f"  container.meta   = {dict(c.metadata)!r}")
        print(f"  duration(container) = {c.duration!r}  bit_rate = {c.bit_rate!r}")
        for i, s in enumerate(c.streams):
            cc = s.codec_context
            cname = getattr(cc, "codec_par_name", None) or getattr(cc, "name", None)
            cobj = getattr(cc, "codec", None)
            clong = getattr(cobj, "long_name", None) or getattr(cc, "long_name", None)
            print(f"  stream[{i}] type={s.type!r} codec={cname!r} long={clong!r}")
            print(f"    stream.meta   = {dict(s.metadata)!r}")
            print(f"    tb={getattr(s, 'time_base', None)!r} dur={getattr(s, 'duration', None)!r} "
                  f"br={getattr(s, 'bit_rate', None)!r} profile={getattr(cc, 'profile', None)!r}")
            if s.type == "video":
                print(f"    {s.width}x{s.height} pix={getattr(s, 'pix_fmt', None)!r} "
                      f"sar={getattr(s, 'sample_aspect_ratio', None)!r} "
                      f"rate={getattr(s, 'average_rate', None)!r}/{getattr(s, 'guessed_rate', None)!r}")
        sys.stdout.flush()


def main() -> int:
    os.makedirs(TMP, exist_ok=True)
    print("## PROBE IDENTITY (builder-side)")
    print(f"  av.__version__      = {av.__version__!r}")
    lv = av.library_versions
    print(f"  av.library_versions = {lv!r}")
    for k in sorted(lv):
        print(f"    {k} = {dec(lv[k])}")
    print(f"  av.ffmpeg_version_info = {av.ffmpeg_version_info!r}")

    print("\n## FIXTURES (built as the test suite builds them)")
    a = write_clip(os.path.join(TMP, "clip.mp4"))
    b = write_clip(os.path.join(TMP, "clip.mkv"))
    try:
        c = write_clip(os.path.join(TMP, "clip.webm"))
    except Exception as exc:  # noqa: BLE001
        c = None
        print(f"  (webm writer unavailable: {type(exc).__name__}: {exc})")
    d = write_clip(
        os.path.join(TMP, "declared.mp4"),
        container_metadata={"encoder": "HandBrake 1.6.0 2023041600", "major_brand": "isom"},
        stream_metadata={"encoder": "Lavc61.3.100", "handler_name": "VideoHandler"},
    )
    e = os.path.join(TMP, "truncated.mp4")
    with open(a, "rb") as src, open(e, "wb") as dst:
        dst.write(src.read(200))  # header only: malformed container
    f = os.path.join(TMP, "fake.mp4")
    with open(f, "wb") as dst:
        dst.write(b"NOT A VIDEO AT ALL" * 8)

    probe(a, "A  mp4, no tags written")
    probe(b, "B  mkv, no tags written")
    if c:
        probe(c, "C  webm, libvpx")
    probe(d, "D  mp4, container+stream encoder tags declared")
    probe(e, "E  truncated mp4 (malformed)")
    probe(f, "F  non-video bytes named .mp4")

    print("\n## WHAT THE CONTRACT LAYER RECORDS (real ContainerInfo fields)")
    from videotemplate.ingestion.ingestor import Ingestor, IngestionError

    ing = Ingestor(max_duration=30.0)
    for path, lbl in ((a, "A"), (d, "D declared-tags"), (e, "E truncated"), (f, "F non-video")):
        try:
            sd = ing.ingest(path)
        except IngestionError as exc:
            print(f"  {lbl}: IngestionError(recoverable={exc.recoverable}) {exc}")
            continue
        ci = sd.container
        print(f"  {lbl}: container.format={ci.format!r} format_long={ci.format_long!r} "
              f"size={ci.size_bytes} source={ci.source} "
              f"prov={[p.model_dump() for p in ci.provenance]}")
        print(f"       ContainerInfo fields = {sorted(ci.model_dump().keys())}")
        print(f"       has container_id? {'container_id' in sd.model_dump()}  "
              f"has encoder anywhere? {'encoder' in json.dumps(sd.model_dump() , default=str)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
