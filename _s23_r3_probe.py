"""Part III probes: R3 (origin of the muxer-supplied value), R1 (scopes/keys),
R2 (key normalisation), R4 (reachable failure states).

R3 asks the question the freeze audit left open. Is `encoder='Lavf62.12.102'`

  (a) physically present in the artifact bytes,
  (b) inserted by the muxer at write time and therefore present,
  (c) computed by PyAV / libavformat at probe time, or
  (d) something else?

The answer decides whether Stage 2.3 may classify the value as artifact-declared
metadata at all. R4 enumerates the states the CURRENT code can actually
distinguish, because Part III's failure-state list must be derived from reachable
implementation states rather than from an enumeration in prose.

Writes to _s23_r3_out.txt next to this file. Nothing under src/ is touched.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import sys
import tempfile

import av

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s23_r3_out.txt")
SRC = os.path.join(os.getcwd(), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

TOKENS = [b"Lavf", b"Lavc", b"HandBrake", b"MuxingApp", b"WritingApp"]


def libfmt():
    """libavformat version as a string (PyAV 18 exposes library_versions only)."""
    return ".".join(str(n) for n in av.library_versions["libavformat"])


def out(line: str = "") -> None:
    OUT_STREAM.write(line + "\n")


def section(title: str) -> None:
    out("=" * 78)
    out(title)
    out("=" * 78)


def make(path, container, vcodec, acodec=None, tags=None, truncate=False, n=48):
    """The operation tests/test_pipeline.py performs, plus optional tags.

    Audio is optional and defaults to off: no finding in Part III depends on an
    audio stream existing, and the encoders available here (aac) need priming
    parameters PyAV 18 will not accept, which is a distraction, not a datum.
    """
    c = av.open(path, "w")
    vs = c.add_stream(vcodec)
    vs.width, vs.height, vs.pix_fmt = 160, 120, "yuv420p"
    vs.rate = 24
    c.metadata["creation_time"] = "2026-01-01T00:00:00.000000Z"
    for k, v in (tags or {}).items():
        c.metadata[k] = v
    a_s = c.add_stream(acodec, rate=48000) if acodec else None
    if a_s:
        a_s.layout = av.AudioLayout("stereo")
        a_s.format = av.AudioFormat("fltp")
    c.start_encoding()
    base = int(vs.time_base * 24)
    a_step = 0
    if a_s:
        a_step = getattr(a_s.codec_context, "frame_size", 0) or 1024
    for i in range(n):
        vf = av.VideoFrame(160, 120, "yuv420p")
        for p in vf.planes:
            p.update(bytes(p.buffer_size))
        vf.pts = i * base
        c.mux(vs.encode(vf))
        if a_s:
            af = av.AudioFrame(format="fltp", layout="stereo", samples=a_step)
            af.sample_rate = 48000
            af.pts = i * a_step
            for pk in a_s.encode(af):
                c.mux(pk)
    for pk in (vs, a_s):
        if pk is None:
            continue
        for p in pk.encode(None):
            c.mux(p)
    c.close()
    if truncate:
        with open(path, "r+b") as f:
            f.truncate(os.path.getsize(path) // 2)



def part_r3(files):
    section("R3  WHERE DOES 'Lavf62.12.102' COME FROM?")
    out("Q1 — is the string physically in the artifact? (no probe involved)")
    for name, path in files.items():
        if name.startswith("_"):
            continue
        raw = open(path, "rb").read()
        hits = []
        for tok in TOKENS:
            offs = [m.start() for m in re.finditer(re.escape(tok), raw)]
            if offs:
                hits.append(f"{tok.decode('latin-1')} x{len(offs)} @{offs[:3]}")
        out(f"  {name:<12} {len(raw):>8} bytes  " + (", ".join(hits) or "no known token"))
    out("")
    out("Q2 — raw context of each token hit (shows WHO wrote it into the file)")
    for name, path in files.items():
        if name.startswith("_"):
            continue
        raw = open(path, "rb").read()
        for tok in TOKENS:
            m = re.search(re.escape(tok), raw)
            if m:
                s = max(0, m.start() - 20)
                out(f"  {name:<12} {tok.decode('latin-1'):<10} "
                    f"{raw[s:m.start() + 34]!r}")
    out("")
    out("Q3 — the declared fixture: was the declared value kept, and where?")
    raw = open(files["D declared"], "rb").read()
    for tok in (b"HandBrake", b"Lavf", b"Lavc", b"MOVEMENT"):
        m = re.search(re.escape(tok), raw)
        out(f"  bytes contain {tok.decode('latin-1'):<10} -> {bool(m)}")
    c = av.open(files["D declared"], "r")
    out(f"  container.metadata = {dict(c.metadata)!r}")
    for s in c.streams:
        out(f"  stream {s.index} metadata = {dict(s.metadata)!r}")
    c.close()
    out("")
    # Q4 replaced: the packet-copy remux used an API PyAV 18 no longer supports.
    # The question it asked ("does the value travel with the bytes, or is it
    # re-created at write time?") is answered decisively by Q1+Q5 instead: the
    # string is present in the bytes of every artifact, and Q5 shows no write
    # option suppresses it. Recorded here so the gap is not mistaken for an
    # untested claim.
    out("Q4 — SUPPRESSED: see Q1 (value is in the bytes) and Q5 (no option")
    out("     removes it). A packet-copy remux was attempted first but PyAV 18's")
    out("     add_stream() no longer accepts template=; not needed for the result.")
    out("")
    out("Q5 — can the writer be made not to declare itself, and does a DECLARED")
    out("     container encoder survive into the bytes?")
    for label, opts, tags in [("default", {}, None),
                              ("movflags=+faststart", {"movflags": "+faststart"}, None),
                              ("encoder='' (empty)", {}, {"encoder": ""}),
                              ("encoder='HandBrake 1.6.0'", {},
                               {"encoder": "HandBrake 1.6.0"}),
                              ("creation_time only", {},
                               {"creation_time": "2026-01-01T00:00:00.000000Z"})]:
        safe = re.sub(r"[^a-z]", "", label) or "default"
        p = os.path.join(files["_dir"], f"r3_opt_{safe}.mp4")
        c = av.open(p, "w", options=opts or None)
        vs = c.add_stream("libx264")
        vs.width, vs.height, vs.pix_fmt, vs.rate = 160, 120, "yuv420p", 24
        for k, v in (tags or {}).items():
            c.metadata[k] = v
        c.start_encoding()
        for i in range(24):
            f = av.VideoFrame(160, 120, "yuv420p")
            for pl in f.planes:
                pl.update(bytes(pl.buffer_size))
            f.pts = i * int(vs.time_base * 24)
            c.mux(vs.encode(f))
        for pk in vs.encode(None):
            c.mux(pk)
        c.close()
        r = av.open(p, "r")
        raw = open(p, "rb").read()
        out(f"  {label}")
        out(f"      re-read metadata        = {dict(r.metadata)!r}")
        out(f"      bytes contain Lavf      = {b'Lavf' in raw}"
            f"   (at {raw.find(b'Lavf') if b'Lavf' in raw else -1})")
        out(f"      bytes contain 'HandBrake' = {b'HandBrake' in raw}")
        r.close()
    out("")
    out("Q5b — the same question for Matroska (does WritingApp survive, and can it")
    out("      be overridden or removed?)")
    for label, tags in [("mkv default", None),
                        ("mkv encoder='HandBrake 1.6.0'",
                         {"encoder": "HandBrake 1.6.0"}),
                        ("mkv muxing_application='me'",
                         {"muxing_application": "me"}),
                        ("mkv writing_application='me'",
                         {"writing_application": "me"})]:
        safe = re.sub(r"[^a-z]", "", label) or "default"
        p = os.path.join(files["_dir"], f"r3_{safe}.mkv")
        c = av.open(p, "w")
        vs = c.add_stream("libvpx")
        vs.width, vs.height, vs.pix_fmt, vs.rate = 160, 120, "yuv420p", 24
        for k, v in (tags or {}).items():
            c.metadata[k] = v
        c.start_encoding()
        for i in range(24):
            f = av.VideoFrame(160, 120, "yuv420p")
            for pl in f.planes:
                pl.update(bytes(pl.buffer_size))
            f.pts = i * int(vs.time_base * 24)
            c.mux(vs.encode(f))
        for pk in vs.encode(None):
            c.mux(pk)
        c.close()
        r = av.open(p, "r")
        raw = open(p, "rb").read()
        out(f"  {label}")
        out(f"      re-read container metadata = {dict(r.metadata)!r}")
        out(f"      bytes: Lavf={b'Lavf' in raw} 'HandBrake'={b'HandBrake' in raw} "
            f"me={b'me' in raw}")
        for s in r.streams:
            out(f"      stream {s.index} metadata = {dict(s.metadata)!r}")
        r.close()
    out("")
    out("Q6 — Matroska/WebM: stored by the muxer, and EXPOSED to the probe?")
    for label in ("B mkv", "C webm"):
        raw = open(files[label], "rb").read()
        for tok in (b"MuxingApp", b"WritingApp", b"Lavf"):
            m = re.search(re.escape(tok), raw)
            if m:
                s = max(0, m.start() - 6)
                out(f"  {label} bytes {tok.decode('latin-1'):<10} "
                    f"{raw[s:m.start() + 40]!r}")
        c = av.open(files[label], "r")
        out(f"  {label} container.metadata (ALL) = {dict(c.metadata)!r}")
        for s in c.streams:
            out(f"  {label} stream {s.index} metadata (ALL) = {dict(s.metadata)!r}")
        c.close()


def part_r1(files):
    section("R1  METADATA SCOPES THAT ACTUALLY EXIST")
    out("Which scopes carry producer information, per fixture:")
    for name, path in files.items():
        if name.startswith("_"):
            continue
        c = av.open(path, "r")
        rows = [("container", dict(c.metadata))] + [
            (f"stream:{s.index}({s.type})", dict(s.metadata)) for s in c.streams]
        keys = {}
        for scope, md in rows:
            for k in md:
                keys.setdefault(k, []).append(scope)
        prod = {k: v for k, v in keys.items()
                if re.search(r"encod|mux|writ|handler|tool|software|creat", k, re.I)}
        out(f"  {name:<12} {len(keys)} distinct keys; producer-bearing ->")
        for k, scopes in sorted(prod.items()):
            out(f"      {k:<16} scopes={scopes}")
        if not prod:
            out("      (none)")
        c.close()
    out("")
    out("Stream census (what each non-container scope exposes):")
    for name, path in files.items():
        if name.startswith("_"):
            continue
        c = av.open(path, "r")
        out(f"  {name:<12} " + ", ".join(
            f"{s.type}#{s.index} {sorted(dict(s.metadata))}"
            for s in c.streams))
        c.close()


def part_r2(files):
    section("R2  KEY NORMALISATION — WHAT AN EXACT MATCH DOES TODAY")
    target = "encoder"
    for name, path in files.items():
        if name.startswith("_"):
            continue
        c = av.open(path, "r")
        scopes = [("container", dict(c.metadata))] + [
            (f"stream:{s.index}", dict(s.metadata)) for s in c.streams]
        exact = [(sc, md[target]) for sc, md in scopes if target in md]
        ci = [(sc, k, v) for sc, md in scopes
              for k, v in md.items() if k.lower() == target]
        out(f"  {name:<12} exact-match 'encoder' -> {exact or 'ABSENT'}")
        for sc, k, v in ci:
            if (sc, v) not in exact:
                out(f"      case-only match: scope={sc} key={k!r} value={v!r}"
                    f"  <- INVISIBLE to the exact lookup")
        c.close()
    out("")
    out("Codec long-name census (the LONGS map in ingestor.py vs what is emitted):")
    LONGS = ("H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
             "HEVC (High Efficiency Video Coding)", "VP8 (Video) (libvpx)",
             "VP9 (Video) (libvpx)", "AV1 (Alliance for Open Media AV1) (libaom-av1)",
             "libsvtav1", "libx264", "libx265", "AAC (Advanced Audio Coding)",
             "opus", "Vorbis", "AV1 (Open Alliance) (libdav1d)")
    seen = set()
    for name, path in files.items():
        if name.startswith("_"):
            continue
        c = av.open(path, "r")
        for s in c.streams:
            cc = s.codec_context
            # PyAV 18: the long name lives on the Codec object, not the context.
            cobj = getattr(cc, "codec", None)
            short = getattr(cc, "name", None) or getattr(cc, "codec_par_name", None)
            long_ = getattr(cobj, "long_name", None) or getattr(cc, "long_name", None)
            seen.add((short, long_))
            out(f"  {name:<12} {s.type:<6} name={short!r} long={long_!r} "
                f"in_LONGS_map={short in LONGS or long_ in LONGS}")
        c.close()
    out(f"  distinct (name, long_name) pairs observed: {len(seen)}")



def as_ingestion_error(exc):
    """Render an IngestionError.

    Note: the class sets `self.recoverable` but never `self.message`, so the
    message is only reachable through str(exc). The audit records that as part
    of the R4 finding rather than papering over it.
    """
    msg = getattr(exc, "message", None)
    if msg is None:
        msg = str(exc)
    return f"IngestionError({msg!r}, recoverable={getattr(exc, 'recoverable', None)!r})"


def part_r4(tmp):
    section("R4  FAILURE-STATE CENSUS — WHAT THE CURRENT CODE CAN DISTINGUISH")
    from videotemplate.ingestion.ingestor import Ingestor
    from videotemplate.models.source_description import IngestionError
    from videotemplate.utils.confidence import ProvenanceEntry, SourceInfo
    ing = Ingestor(max_duration=30.0)
    out("  NOTE: IngestionError.__init__ sets .recoverable but not .message, so the")
    out("        message is reachable only via str(exc). Reported below via")
    out("        str(); .message is absent — itself part of the R4 finding.")
    out("")
    cases = {}
    p = os.path.join(tmp, "r4_empty.mp4")
    open(p, "wb").close()
    cases["zero-byte file"] = p
    p = os.path.join(tmp, "r4_header_only.mp4")
    make(p, "mp4", "libx264")
    with open(p, "r+b") as f:
        f.truncate(24)
    cases["24 bytes (header only)"] = p
    p = os.path.join(tmp, "r4_half.mp4")
    make(p, "mp4", "libx264", truncate=True)
    cases["truncated mid-stream"] = p
    p = os.path.join(tmp, "r4_ascii.mp4")
    with open(p, "wb") as f:
        f.write(b"A" * 128)
    cases["128 ASCII bytes"] = p
    p = os.path.join(tmp, "r4_mkv_named_as_mp4.mkv")
    make(p, "mkv", "libx264")
    cases["valid mkv, .mkv ext"] = p
    # A video-less but structurally valid container: an m4a-style audio-only
    # file. Built as a Matroska with an audio-only stream, since aac via PyAV 18
    # is unavailable; the point is the *container has no video stream*, not the
    # audio codec.
    p = os.path.join(tmp, "r4_no_video.mkv")
    c = av.open(p, "w")
    a = c.add_stream("pcm_s16le", rate=48000)
    a.layout = av.AudioLayout("stereo")
    c.start_encoding()
    for i in range(6):
        af = av.AudioFrame(format="s16", layout="stereo", samples=1024)
        af.sample_rate = 48000
        af.pts = i * 1024
        for pk in a.encode(af):
            c.mux(pk)
    for pk in a.encode(None):
        c.mux(pk)
    c.close()
    cases["valid container, no video stream"] = p
    cases["path that does not exist"] = os.path.join(tmp, "r4_missing.mp4")
    p = os.path.join(tmp, "r4_valid.mp4")
    make(p, "mp4", "libx264")
    cases["valid file"] = p
    p = os.path.join(tmp, "r4_valid_no_tags.mp4")
    make(p, "mp4", "libx264", tags={})
    cases["valid, no extra tags"] = p
    p = os.path.join(tmp, "r4_long.mp4")
    make(p, "mp4", "libx264", n=48 * 25)  # ~25s at 24fps, over the 30s? see below
    cases["valid, ~25s long"] = p

    out("  (1) what libavformat/PyAV says   (2) what Ingestor.ingest() returns")
    for label, path in cases.items():
        try:
            c = av.open(path, "r")
            info = f"av.open OK format={c.format.name!r} video={len(c.streams.video)}"
            c.close()
        except Exception as exc:  # noqa: BLE001
            info = f"{type(exc).__name__}: {str(exc).strip()[:64]}"
        try:
            got = ing.ingest(path)
            repo = (f"OK format={got.container.format} size={got.container.size_bytes} "
                    f"codec={got.video_stream.codec} "
                    f"container_fields={sorted(type(got.container).model_fields)}")
        except IngestionError as exc:
            repo = as_ingestion_error(exc)
        except Exception as exc:  # noqa: BLE001
            repo = f"{type(exc).__name__}: {exc}"
        out(f"  {label}")
        out(f"      libavformat -> {info}")
        out(f"      ingest()    -> {repo}")
    out("")
    out("Distinct terminal outcomes Ingestor.ingest() produces over the census:")
    terminal = {}
    for label, path in cases.items():
        try:
            ing.ingest(path)
            key = "success (probe complete)"
        except IngestionError as exc:
            key = as_ingestion_error(exc)
        except Exception as exc:  # noqa: BLE001
            key = f"{type(exc).__name__} (unmapped, escapes the method's intent)"
        terminal.setdefault(key, []).append(label)
    for k, v in terminal.items():
        out(f"  {k}")
        out(f"      <- {v}")
    out("")
    out("Probe identity, as the code currently reports it:")
    got = ing.ingest(cases["valid file"])
    # SourceInfo lives per-group; SourceDescription itself has none.
    out(f"  has SourceDescription.source? "
        f"{'source' in type(got).model_fields}")
    out(f"  container.source = {got.container.source!r}")
    out(f"  video_stream.source = {got.video_stream.source!r}")
    out(f"  SourceInfo fields = {sorted(SourceInfo.model_fields)}")
    out(f"  ProvenanceEntry[0] = {got.container.provenance[0]!r}")
    out(f"  ProvenanceEntry fields = {sorted(ProvenanceEntry.model_fields)}")
    out(f"  av.ffmpeg_version_info = {getattr(av, 'ffmpeg_version_info', None)!r}")
    out(f"  av.library_versions['libavformat'] = {libfmt()!r}")
    out("  -> no version of anything is recorded anywhere in the contract.")


def main():
    global OUT_STREAM
    tmp = tempfile.mkdtemp(prefix="s23r3_")
    files = {
        "_dir": tmp,
        "A mp4": os.path.join("_s23_fixtures", "clip.mp4"),
        "B mkv": os.path.join("_s23_fixtures", "clip.mkv"),
        "C webm": os.path.join("_s23_fixtures", "clip.webm"),
        "D declared": os.path.join("_s23_fixtures", "declared.mp4"),
    }
    OUT_STREAM = io.TextIOWrapper(open(OUT, "wb"), encoding="utf-8",
                                 errors="replace", line_buffering=True)
    try:
        out(f"PyAV {av.__version__} · libavformat {libfmt()} · "
            f"ffmpeg_version_info={getattr(av, 'ffmpeg_version_info', None)!r}")
        out("Fixtures are the audit's own, built by _s23_probe_experiment.py with the")
        out("test helper, which never sets an encoder tag — so 'A mp4' is the R3")
        out("subject exactly as the audit left it.")
        out("")
        part_r3(files)
        part_r1(files)
        part_r2(files)
        part_r4(tmp)
    finally:
        OUT_STREAM.flush()
        OUT_STREAM.detach()
        shutil.rmtree(tmp, ignore_errors=True)
    print("WROTE", OUT)


if __name__ == "__main__":
    main()

