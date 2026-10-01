"""
Stage 2.3 remediation cycle 1 — producer-declaration observation (R1/R2/R3).

Behavioural tests for the origin-bearing observation added to ContainerInfo. They
make three claims falsifiable:

  R3  a value written into the artifact by the MUXER is classified muxer_authored
      and is never promoted to an artifact-declared producer identity;
  R2  a key is found regardless of container-specific casing ('ENCODER' vs
      'encoder'), and the verbatim key/value survive the fold;
  A1  the implementation DEMONSTRABLY withholds an ineligible producer value, rather
      than passing the invariant by having no field to violate.

That last one is the point of this cycle. Before it, A1 was a VACUOUS-PASS: with no
producer field at all, nothing could be invented. A vacuous pass is not a pass.
"""
from __future__ import annotations

import av
import numpy as np

from videotemplate.ingestion.ingestor import Ingestor
from videotemplate.models.source_description import ObservationOrigin


def _make_clip(path: str, container_fmt: str = "mp4", stream_tags: dict | None = None,
               container_tags: dict | None = None) -> str:
    """Build a clip the way the rest of the suite builds them, plus optional tags."""
    codec = "libvpx" if container_fmt == "webm" else "libx264"
    container = av.open(path, mode="w")
    for key, value in (container_tags or {}).items():
        container.metadata[key] = value
    stream = container.add_stream(codec, rate=10)
    stream.width, stream.height, stream.pix_fmt = 160, 120, "yuv420p"
    for key, value in (stream_tags or {}).items():
        stream.metadata[key] = value
    for i in range(10):
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        frame[40:60, i * 8:(i * 8) + 8] = 255
        vf = av.VideoFrame.from_ndarray(frame, format="rgb24")
        vf.pts = i
        for packet in stream.encode(vf):
            container.mux(packet)
    for packet in stream.encode(None):
        container.mux(packet)
    container.close()
    return path


def _declarations(path: str):
    return Ingestor(max_duration=30.0).ingest(path).container.producer_declarations


def _find(decls, canonical_key: str):
    return [d for d in decls if d.canonical_key == canonical_key]



# ── R3: muxer-authored values are attributed, not promoted ──────────────────────────


def test_mp4_encoder_tag_is_muxer_authored_not_artifact_declared(tmp_path):
    """The tag IS present, and is the muxer describing itself. Both must hold."""
    path = _make_clip(str(tmp_path / "clip.mp4"))
    encoders = _find(_declarations(path), "encoder")

    assert encoders, "mp4 always carries an encoder tag; finding none is a false absence"
    for decl in encoders:
        assert decl.origin is ObservationOrigin.MUXER_AUTHORED, (
            f"{decl.original_value!r} is the muxer stamping itself; classifying it "
            f"as artifact_declared would fabricate a producer identity"
        )
        assert decl.state.value == "extracted"


def test_mkv_uppercase_encoder_is_found_not_silently_absent(tmp_path):
    """R2: Matroska's 'ENCODER' must resolve to the same canonical key as mp4's.

    This is the measured false absence the audit recorded — an exact-match lookup on
    'encoder' returned ABSENT for mkv and webm while returning a value for mp4, from
    the same string written by the same muxer.
    """
    path = _make_clip(str(tmp_path / "clip.mkv"), container_fmt="mkv")
    encoders = _find(_declarations(path), "encoder")

    assert encoders, "mkv's uppercase ENCODER must resolve to the canonical key"
    for decl in encoders:
        assert decl.original_key == "ENCODER", "the verbatim key must survive the fold"
        assert decl.origin is ObservationOrigin.MUXER_AUTHORED


def test_verbatim_key_and_value_are_retained(tmp_path):
    """R2 + §2.1.15 R7: normalisation must never destroy what it normalises.

    Note the asymmetry this test exposed rather than papered over. Matroska's
    ENCODER arrives from the demuxer still upper-case, so the fold is doing real
    work and `original_key` proves the original survived. TITLE, by contrast, is
    already delivered lower-case by the demuxer — the case change happens in
    libavformat before this code runs. "Verbatim" therefore means verbatim *as the
    mechanism reported it*, not as the authoring tool spelled it. A stricter
    guarantee would require reading raw atoms, which no approved mechanism here does.
    """
    path = _make_clip(str(tmp_path / "clip.mkv"), container_fmt="mkv",
                      container_tags={"TITLE": "a clip"})
    titles = _find(_declarations(path), "title")

    assert titles, "TITLE must fold to the canonical key 'title'"
    for decl in titles:
        assert decl.original_value == "a clip", "the value must survive untouched"
        assert decl.rule_id == "r2.casefold.title"
        assert decl.original_key == decl.original_key.strip()

    encoders = _find(_declarations(path), "encoder")
    assert any(d.original_key == "ENCODER" for d in encoders), (
        "the demuxer's original casing must be retained alongside the folded key"
    )


def test_stream_scope_is_recorded_separately_from_container_scope(tmp_path):
    """R1: scope is part of the observation, not an assumption."""
    path = _make_clip(str(tmp_path / "clip.mp4"),
                      stream_tags={"handler_name": "VideoHandler"})
    scopes = {d.scope for d in _find(_declarations(path), "handler_name")}

    assert scopes == {"video_stream"}, (
        "handler_name is a stream-scope observation and must not be attributed to "
        f"the container; got scopes={scopes}"
    )


# ── A1: demonstrate withholding, do not merely have nothing to withhold ─────────────


def test_muxer_authored_value_is_never_promoted_to_source_info(tmp_path):
    """A1's real discharge: the value exists AND is not promoted.

    Before this cycle there was no producer field at all, so A1 was a vacuous pass.
    Now there is a value, it is reported, and it is still refused for
    SourceInfo.version. The refusal is the demonstration.
    """
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    assert desc.container.producer_declarations, (
        "A1 can only be demonstrated once a producer-value path exists"
    )
    muxer = [d for d in desc.container.producer_declarations
             if d.origin is ObservationOrigin.MUXER_AUTHORED]
    assert muxer, "the muxer-authored value must still be present and reported"

    # The eligibility rule, now that the carrier exists (§2.1.15 v1.2 / 2.15).
    # Cycle 1 asserted the carrier's ABSENCE, with a standing instruction to
    # replace that assertion with the eligibility rule when the field landed.
    # That replacement is what happens here — the absence assertion is deleted,
    # not merely supplemented, because it would now be false.
    assert "version" in type(desc.container.source).model_fields, (
        "the carrier landed in cycle 2; this test must assert the RULE, not the "
        "absence of the field"
    )
    assert desc.container.source.version is None, (
        "the mp4 tag is muxer_authored, so it is ineligible: R3 requires omission, "
        f"and version={desc.container.source.version!r} is a promoted value"
    )
    dumped = desc.container.source.model_dump()
    assert "version" not in dumped, (
        "R3/R2: when the artifact declares none the key must be OMITTED, never "
        f"emitted as null; got {dumped}"
    )


def test_declared_producer_is_distinguished_from_muxer_authored(tmp_path):
    """A genuine declaration and a muxer stamp must not classify alike.

    The writer cannot persist a container-scope declaration for mp4 (R3 measured
    that the value is destroyed at write time), so the declaration is placed at
    STREAM scope, where it does survive. That is the one reachable route to an
    artifact_declared origin in this environment.
    """
    path = _make_clip(str(tmp_path / "declared.mp4"),
                      stream_tags={"encoder": "HandBrake 1.6.0"})
    stream_encoders = [d for d in _find(_declarations(path), "encoder")
                       if d.scope == "video_stream"]

    assert stream_encoders, "a stream-scope encoder tag must be observed"
    for decl in stream_encoders:
        assert decl.origin is ObservationOrigin.ARTIFACT_DECLARED, (
            f"{decl.original_value!r} was supplied by the authoring tool and is "
            f"not a muxer self-description"
        )
        assert decl.original_value == "HandBrake 1.6.0"


def test_no_producer_name_is_derived_from_a_muxer_tag(tmp_path):
    """A9: the muxer string is reported verbatim and never interpreted."""
    for decl in _declarations(_make_clip(str(tmp_path / "clip.mp4"))):
        if decl.origin is not ObservationOrigin.MUXER_AUTHORED:
            continue
        for forbidden in ("ffmpeg", "handbrake", "8.1"):
            assert forbidden not in decl.original_value.casefold(), (
                "a muxer-authored value must not be rewritten into a producer name"
            )


def test_unregistered_producer_key_is_recorded_as_unrecognised(tmp_path):
    """R2: a key with no registered rule is recorded, not dropped and not 'absent'.

    Matroska is used because the mp4 muxer discards unrecognised tags entirely, so
    mp4 could not exercise this path at all. That asymmetry is itself worth knowing:
    the same unknown key is *unobservable* in mp4 and *unrecognised* in mkv.
    """
    path = _make_clip(str(tmp_path / "clip.mkv"), container_fmt="mkv",
                      container_tags={"ENCODER_TOOLCHAIN": "mystery-9"})
    odd = [d for d in _declarations(path) if d.canonical_key == "encoder_toolchain"]

    assert odd, "an unregistered producer-ish key must still be observed"
    for decl in odd:
        assert decl.rule_id is None, "no registered rule means rule_id must be None"
        assert decl.state.value == "extracted", (
            "unrecognised is not absent; the value was read and kept"
        )


def test_empty_value_yields_unavailable_origin(tmp_path):
    """origin=unavailable is for 'no value obtained', distinct from absent.

    A container tag whose value is the empty string is observed but carries no
    information: no author can be attributed, so the origin is `unavailable` and
    NOT `artifact_declared` (which would claim a declaration exists) and NOT
    `muxer_authored` (which would claim a specific writer).
    """
    path = _make_clip(str(tmp_path / "clip.mkv"), container_fmt="mkv",
                      container_tags={"ENCODER": ""})
    empties = [d for d in _find(_declarations(path), "encoder")
               if not d.original_value]

    for decl in empties:
        assert decl.origin is ObservationOrigin.UNAVAILABLE
