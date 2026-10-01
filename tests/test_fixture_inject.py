"""
The T-R3b fixture builder, under test.

This is the only way in this project to obtain an artifact that DECLARES a producer.
R3 measured that no fixture built by writing tags can carry one: the muxer destroys
the declaration at write time under every instruction tried. So the builder is load-
bearing for T1 and T3, and its own failure modes must be caught by tests rather than
assumed away.

Two failure modes are covered here that metadata assertions alone would miss:

  1. a payload built with the wrong field order yields a file that OPENS, reports the
     brand keys, and silently loses the encoder tag;
  2. a file whose chunk-offset table was not repaired OPENS, reports correct metadata,
     and decodes to garbage.

The second is why `_frames_match` exists: correctness of this fixture is a statement
about decoded picture data, not about a dict of tags.
"""
from __future__ import annotations

import os
import sys

import av

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _s23_fixture_inject as fix  # noqa: E402

DECLARED = "HandBrake 1.6.0 2023041600"


def test_base_file_alone_declares_only_the_muxer(tmp_path):
    """The control: before injection, the base file declares nothing but FFmpeg.

    Without this, a test asserting the injected value could pass even if injection
    were a no-op.
    """
    base = fix.build_base(str(tmp_path / "base.mp4"))
    result = fix.verify(base, "Lavf62.12.102")

    assert "HandBrake" not in str(result["container"]), (
        "the base fixture must not contain the declaration under test"
    )
    assert result["container"].get("encoder", "").startswith("Lavf")


def test_injection_produces_a_real_declaration(tmp_path):
    base = fix.build_base(str(tmp_path / "base.mp4"))
    out = str(tmp_path / "declared.mp4")
    fix.inject_declaration(base, out, DECLARED)
    result = fix.verify(out, DECLARED)

    assert result["bytes_contain_declared"], "the bytes must carry the declaration"
    assert result["matches_expected"], (
        f"the mechanism must read it back verbatim; got {result['container']}"
    )


def test_injected_file_is_not_corrupt(tmp_path):
    """The integrity property: identical decoded frames to the base file.

    This is the check that a wrong stco repair cannot pass. The file would still
    open and still report the right tag; only the picture would be wrong.
    """
    base = fix.build_base(str(tmp_path / "base.mp4"))
    out = str(tmp_path / "declared.mp4")
    fix.inject_declaration(base, out, DECLARED)
    integrity = fix._frames_match(base, out)

    assert integrity["base_frames"] > 0, "the base must decode to something"
    assert integrity["injected_frames"] == integrity["base_frames"]
    assert integrity["identical"], (
        "decoded frames differ from the base file: the chunk-offset table was "
        "repaired incorrectly and the fixture would decode to garbage"
    )


def test_injected_file_still_decodes_to_the_right_geometry(tmp_path):
    """A second, independent integrity read: the stream itself must be intact."""
    base = fix.build_base(str(tmp_path / "base.mp4"))
    out = str(tmp_path / "declared.mp4")
    fix.inject_declaration(base, out, DECLARED)

    c = av.open(out, "r")
    try:
        s = c.streams.video[0]
        assert (s.width, s.height) == (160, 120)
        assert s.codec_context.name == "h264"
    finally:
        c.close()


def test_declared_value_survives_a_longer_payload(tmp_path):
    """A declaration longer than the muxer default must work, not just equal-length."""
    base = fix.build_base(str(tmp_path / "base.mp4"))
    long_decl = "SomeVeryLongAuthoringTool 2026-01-01 build 99999 revision abcdef"
    out = str(tmp_path / "long.mp4")
    fix.inject_declaration(base, out, long_decl)
    result = fix.verify(out, long_decl)

    assert result["matches_expected"], (
        f"a longer declaration must be handled; got {result['container']}"
    )
    assert fix._frames_match(base, out)["identical"]


def test_no_declaration_survives_by_being_written_as_a_tag(tmp_path):
    """The measurement that motivated the injector, asserted so it cannot regress.

    If a future PyAV/FFmpeg ever preserved a written container-scope declaration,
    this would fail — which is the signal to REPLACE the injector, not to delete it.
    """
    import numpy as np
    path = str(tmp_path / "tagged.mp4")
    c = av.open(path, "w")
    c.metadata["encoder"] = DECLARED
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    c.start_encoding()
    for i in range(4):
        f = av.VideoFrame.from_ndarray(np.zeros((120, 160, 3), dtype=np.uint8),
                                       format="rgb24")
        f.pts = i
        for p in st.encode(f):
            c.mux(p)
    for p in st.encode(None):
        c.mux(p)
    c.close()

    raw = open(path, "rb").read()
    assert DECLARED.encode("utf-8") not in raw, (
        "R3's finding no longer holds: a written container-scope declaration now "
        "survives, so the atom injector is obsolete and should be retired"
    )
