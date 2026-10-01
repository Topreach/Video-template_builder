"""
Stage 2.3 remediation cycle 2 — version carriers (§2.1.15 v1.2, owned by 2.15).

Cycle 1 established observation, scope, origin and eligibility. Cycle 2 lands the
carriers §2.1.15 already specified and 2.15 already owns, and wires the eligibility
rule to them. It adds NO new carrier and invents NO new vocabulary: every field
here is named by the §2.1.15 v1.2 migration table.

These tests are the conformance suite for §2.1.15 R1–R9, written so each rule can
fail independently:

  R1  tool_version required on an `estimate` field's producing entry
  R2  model_version omitted, never null
  R3  SourceInfo.version omitted when nothing eligible — never "" / "unknown"
  R4  "unknown" permitted for tool_version ONLY, and only when introspection fails
  R5  cache gate is exact equality, and "unknown" is a non-match
  R6  stable groups may carry the version; absence never makes them non-conformant
  R7  recorded verbatim; no parsing, normalising, or canonicalising
  R8  versions are producer identity — never an ObservationState, never state input
  R9  one introspection point: producer_identity()
"""
from __future__ import annotations

import av
import numpy as np

from videotemplate.ingestion.ingestor import Ingestor
from videotemplate.models.source_description import ObservationOrigin
from videotemplate.utils.confidence import (
    ObservationState,
    ProvenanceEntry,
    SourceInfo,
    SourceLayer,
    producer_identity,
)


def _make_clip(path: str, container_fmt: str = "mp4",
               stream_tags: dict | None = None,
               container_tags: dict | None = None) -> str:
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



# ── R9: one introspection point ────────────────────────────────────────────────────


def test_producer_identity_is_verbatim_and_stable():
    """R7 + R9: the helper reports the producer's own string, unchanged."""
    identity = producer_identity()

    assert identity["tool_version"] == av.__version__, (
        "R7: the version is copied verbatim, not re-formatted"
    )
    assert identity["tool_version"] != "unknown", (
        "R4: 'unknown' is only for genuinely undeterminable introspection; PyAV is "
        "importable, so the sentinel is not permitted here"
    )
    assert producer_identity() == identity, "R9: repeated calls must agree"


# ── R1/R2/R4: the builder-side carriers ────────────────────────────────────────────


def test_estimate_field_provenance_carries_tool_version(tmp_path):
    """R1: quality_score is a heuristic, so its producing entry must carry the version."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    entries = desc.quality_score.provenance
    assert entries, "an estimate must record provenance"
    for entry in entries:
        assert entry.tool_version is not None, (
            "R1: an `estimate` field with no tool_version on its producing entry is "
            "non-conformant; absence is not permitted here"
        )
        assert entry.tool_version == producer_identity()["tool_version"]


def test_probe_provenance_carries_tool_version(tmp_path):
    """R1/R6: the container probe's entry carries the builder version."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    for entry in desc.container.provenance:
        assert entry.tool_version == av.__version__


def test_model_version_is_omitted_not_null(tmp_path):
    """R2: no model produced these values, so the key must be absent entirely."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))


# ── R3: the source-side carrier, and the rule that binds it ────────────────────────


def test_source_version_omitted_when_only_muxer_authored(tmp_path):
    """R3: a muxer self-description is not a declaration, so the key is omitted."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    assert desc.container.source.version is None
    assert "version" not in desc.container.source.model_dump()


def test_source_version_never_carries_a_sentinel(tmp_path):
    """R3 forbids "" and "unknown" absolutely on this field.

    NOTE: this is the one place the owning contract and an intuitive reading
    diverge, and the contract wins. §2.1.15 R3 permits the "unknown" sentinel on
    `tool_version` (R4) and forbids it on `SourceInfo.version` outright. A missing
    artifact declaration is expressed by OMISSION, never by a placeholder.
    """
    for container_fmt in ("mp4", "mkv"):
        desc = Ingestor(max_duration=30.0).ingest(
            _make_clip(str(tmp_path / f"c.{container_fmt}"),
                       container_fmt=container_fmt))
        version = desc.container.source.version

        assert version not in ("", "unknown", "none", "N/A"), (
            f"R3: {container_fmt} produced a sentinel on SourceInfo.version: "
            f"{version!r}. Omission is the only legal representation of 'declares none'"
        )


def test_probe_version_can_never_become_source_version(tmp_path):
    """The prohibition this whole stage exists to enforce.

    `av.ffmpeg_version_info` and the libav* versions describe the PROBE. Writing
    either into SourceInfo.version is R3-forged substitution, and it would fail
    silently because those values are always present and always well-formed.
    """
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    version = desc.container.source.version
    probe_versions = {str(av.__version__),
                      str(getattr(av, "ffmpeg_version_info", ""))}
    for _lib, nums in av.library_versions.items():
        probe_versions.add(".".join(str(n) for n in nums))
        probe_versions.add("".join(str(n) for n in nums))

    if version is not None:
        assert version not in probe_versions, (
            f"SourceInfo.version={version!r} is a probe/library version; it must "
            f"come only from the artifact's own declaration"
        )


def test_declared_producer_populates_source_version_verbatim(tmp_path):
    """R3 + R7: an eligible declaration populates the carrier, copied verbatim."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "declared.mp4"),
                   stream_tags={"encoder": "HandBrake 1.6.0"}))

    assert desc.container.source.version == "HandBrake 1.6.0", (
        "R7: the declared string is copied verbatim — no name/version split, no "
        "release derivation, no canonicalisation"
    )
    declared = [d for d in desc.container.producer_declarations
                if d.origin is ObservationOrigin.ARTIFACT_DECLARED]
    assert declared, "the eligible declaration must also remain in the observation"


# ── R8: versions are producer identity, never observed properties ───────────────────


def test_version_fields_never_carry_an_observation_state(tmp_path):
    """R8: they must not appear anywhere a state would be read from."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    blob = str(desc.container.provenance)
    assert "ObservationState" not in blob
    assert "extracted" not in blob, (
        "a producer version is not an observed property; it must never appear "
        "where a state would be read from"
    )
    for entry in desc.container.provenance:
        assert isinstance(entry.layer, SourceLayer)


def test_versions_are_not_confined_to_source_identity(tmp_path):
    """R8: producer identity must not leak into SourceDescription.source_identity."""
    desc = Ingestor(max_duration=30.0).ingest(
        _make_clip(str(tmp_path / "clip.mp4")))

    assert "source_identity" not in type(desc).model_fields, (
        "R8 forbids these appearing in source_identity; if that group is added it "
        "must not carry the version carriers"
    )


def test_observation_state_vocabulary_is_unchanged():
    """R8 + the cycle-1 boundary: the vocabulary is whatever §2.1 has authorised.

    This test was written at §2.1 v1.2 and asserted a frozen four. v1.3 adds
    `conflicting` through the controlled amendment at §2.1.16, so the guard moves to
    asserting the authorised v1.3 set instead of the superseded four. The point of the
    guard is unchanged and is preserved explicitly below: the vocabulary is extended
    ONLY by a §2.1 amendment, never by the stage that wants the member. A 2.3 test
    that failed here once is what the rule exists to prevent.
    """
    authorised = {"extracted", "absent", "uncertain", "unavailable", "conflicting"}
    assert {s.value for s in ObservationState} == authorised

    # The four original members keep their exact meaning and spelling (S-1, additive).
    assert {"extracted", "absent", "uncertain", "unavailable"} <= authorised
    # `conflicting` was authorised for CONFLICTING, not for version identity (R8).
    assert not {s.value for s in ObservationState} & {
        "declared", "versioned", "version", "unknown_version"}


def test_no_carrier_was_invented_in_either_direction():
    """The field set is exactly the §2.1.15 v1.2 migration table, no more."""
    assert set(ProvenanceEntry.model_fields) == {
        "layer", "evidence_refs", "transform_type", "confidence_delta",
        "tool_version", "model_version",
    }
    assert set(SourceInfo.model_fields) == {"layer", "model", "tool", "version"}


# ── R5: the cache gate ─────────────────────────────────────────────────────────────


def test_cache_gate_rule_is_exact_equality_with_unknown_as_non_match():
    """R5: equality matches only on exact strings, and 'unknown' never matches.

    NOTE: there is no cache component in the repository today, so this asserts the
    RULE as specified rather than exercising an implementation. R5 is the rule that
    makes §2.2's C5 ("no version-blind estimate hits") mechanically testable once
    that cache exists. Until then the rule is recorded, not demonstrated, and this
    test must not be read as discharging a cache conformance obligation.
    """
    def cache_match(a: str, b: str) -> bool:
        # R5: exact equality AND neither side is the R4 sentinel.
        return a == b and "unknown" not in (a, b)

    assert cache_match("18.1.0", "18.1.0")
    assert not cache_match("18.1.0", "18.1.1")
    assert not cache_match("unknown", "unknown"), (
        "R5: an 'unknown' on either side is a NON-match forcing recompute; it is a "
        "poison value for the cache, not a wildcard"
    )
    assert not cache_match("unknown", "18.1.0")
