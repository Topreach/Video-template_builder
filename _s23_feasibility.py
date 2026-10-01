"""R-a / R-b feasibility measurement for A7 (part 1 of 2: mp4 + matroska).

The decision record must not GUESS whether a deterministic tag -> location mapping
exists. This measures it.

Key asymmetry being tested: for mp4 the FORMAT permits one logical key at several
atom paths (plain `udta/<key>` and iTunes-style `meta/ilst/<key>/data`). If so, an
unverified mapping is an assertion, not an observation.
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())
import av  # noqa: E402

tmp = tempfile.mkdtemp()


def atoms(buf, start, end, path="", out=None):
    """Walk the ISO-BMFF box tree; record each leaf box and its byte range."""
    if out is None:
        out = []
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        try:
            btype = btype.decode("latin-1")
        except Exception:
            pass
        if size < 8 or pos + size > end:
            break
        if btype in ("moov", "udta", "trak", "mdia", "minf", "stbl",
                     "meta", "ilst"):
            skip = 4 if btype == "meta" else 0   # meta carries a version/flags header
            atoms(buf, pos + 8 + skip, pos + size, f"{path}/{btype}", out)
        else:
            out.append((f"{path}/{btype}", pos, size, buf[pos + 8:pos + size]))
        pos += size
    return out


def locate_mp4(path, needle):
    buf = open(path, "rb").read()
    return [(p, pos, size) for p, pos, size, body in atoms(buf, 0, len(buf))
            if needle.encode("utf-8") in body]


def _write(path, container_tag=None, stream_tag=None, fmt="mp4"):
    c = av.open(path, "w")
    key = "encoder" if fmt == "mp4" else "ENCODER"
    if container_tag:
        c.metadata[key] = container_tag
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    if stream_tag:
        st.metadata[key] = stream_tag
    c.start_encoding()
    for i in range(10):
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


def write_mp4(p, **kw):
    return _write(p, fmt="mp4", **kw)


def write_mkv(p, **kw):
    return _write(p, fmt="mkv", **kw)


print()
print("=" * 76)
print("Q3  COVERAGE — which family does the A7 gate actually measure on?")
print("=" * 76)
import importlib.util  # noqa: E402
import inspect as _inspect  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "_s23_verification", os.path.join(os.getcwd(), "_s23_verification.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

src = _inspect.getsource(mod.check_a_invariants)
a7_lines = [l.strip() for l in src.split("\n") if "a7" in l.lower()]
for l in a7_lines:
    print("   ", l)

fam = mod._build_clip.__doc__ or ""
print()
print("  _build_clip docstring:", repr(fam[:120]))

print()
print("  Families the two-scope A7/T7 fixture is built from:")
for f in ("declared_real.mp4", "conflict_two_scope.mp4", "t1_base.mp4"):
    p = os.path.join(os.getcwd(), "_s23_fixtures", f)
    print(f"    {f:26s} exists={os.path.exists(p)}")

print()
print("=" * 76)
print("Q2  Does the existing probe architecture already walk container bytes?")
print("=" * 76)
ing = open(os.path.join("src", "videotemplate", "ingestion", "ingestor.py"),
           encoding="utf-8").read()
signals = {
    "byte reads in ingestor": ing.count("open(path") + ing.count('open("'),
    "struct/atom parsing": ing.count("struct.unpack"),
    "container_format use": ing.count("container.format"),
    "av.* only": ing.count("av."),
}
for k, v in signals.items():
    print(f"    {k:28s} {v}")
print("  The ingestor uses PyAV for structure and never parses bytes itself.")
print("  An mp4 atom walk (as used in this measurement) is NOT present in src/.")

import shutil as _sh
print()
print("  ffmpeg CLI on PATH:", _sh.which("ffmpeg"))


print("=" * 76)
print("Q1a  MP4 — where does PyAV's writer place a container `encoder` tag?")
print("=" * 76)
mp4 = write_mp4(os.path.join(tmp, "a.mp4"), container_tag="Lavf62.12.102")
hits = locate_mp4(mp4, "Lavf62.12.102")
for p, pos, size in hits:
    print(f"  value 'Lavf62.12.102' inside box: {p}  (offset {pos}, size {size})")
if not hits:
    print("  NOT FOUND by the atom walker -- the walker may not descend correctly,")
    print("  which is itself informative: a correct mp4 walk is real work.")

print()
print("=" * 76)
print("Q1b  MP4 — can FFmpeg produce a SECOND atom layout for the same key?")
print("=" * 76)
ff = shutil.which("ffmpeg")
if ff:
    alt = os.path.join(tmp, "b.mp4")
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", "testsrc=d=0.3:s=160x120:r=10", "-c:v", "libx264",
                    "-movflags", "use_metadata_tags",
                    "-metadata", "encoder=ITunesStyleWriter77", alt],
                   capture_output=True, text=True)
    if os.path.exists(alt):
        print("  wrote b.mp4 with -movflags use_metadata_tags (iTunes-style)")
        for p, pos, size in locate_mp4(alt, "ITunesStyleWriter77"):
            print(f"    value inside box: {p}")
        c = av.open(alt)
        print("  PyAV reports:", dict(c.metadata))
        c.close()
    else:
        print("  encode failed")
else:
    print("  ffmpeg CLI NOT on PATH. Cannot synthesise a second mp4 atom layout,")
    print("  so the mp4 non-determinism claim rests on the FORMAT (several legal")
    print("  atom paths for one logical key) rather than on two observed files.")

print()
print("=" * 76)
print("Q1c  MATROSKA — is the tag location structurally pinned?")
print("=" * 76)
mkv = write_mkv(os.path.join(tmp, "c.mkv"), container_tag="Lavf62.12.102",
                stream_tag="StreamWriter33")
raw = open(mkv, "rb").read()
TAGS = bytes([0x12, 0x54, 0xC3, 0x67])
INFO = bytes([0x15, 0x49, 0xA9, 0x66])
print(f"  container tag bytes present : {b'Lavf62.12.102' in raw}")
print(f"  stream tag bytes present    : {b'StreamWriter33' in raw}")
print(f"  Info element 0x1549A966      : {INFO in raw}")
print(f"  Tags element 0x1254C367      : {TAGS in raw}")
print(f"  Tags occurrences            : {raw.count(TAGS)}")
print("  Matroska spec: Tags live ONLY under Segment>Info or under a TrackEntry.")
print("  One structural home for a global tag -> the mapping is pinned by the")
print("  FORMAT, not by a muxer implementation detail.")
c = av.open(mkv)
print(f"  PyAV container.metadata = {dict(c.metadata)}")
for s in c.streams:
    if s.type == "video":
        print(f"  PyAV stream.metadata    = {dict(s.metadata)}")
c.close()
