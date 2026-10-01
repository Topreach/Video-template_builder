"""
SourceDescription — Contract #1, Layer 1 (Ingestion).

Per Stage 1 §8, Contract #1.
Contract discipline is fixed by Stage 2 §2.1 (docs/specs/stage2_1_contract_boundary.md);
field-level detail lives in docs/specs/stage2_source_description.md, subordinate to §2.1.

Observation states follow Stage 2 §2.1.4 Dimension B:
    extracted | absent | uncertain | unavailable
"""
from __future__ import annotations

import enum
import uuid
from typing import Optional

from pydantic import BaseModel, Field

from ..utils.confidence import (
    Confidence,
    Fidelity,
    FidelityType,
    ObservationState,
    ProvenanceEntry,
    SourceInfo,
    ValidationInfo,
    ValidationStatus,
)


# ── Stage 2.3 §G.2.4 — producer-declaration observation ────────────────────────────
#
# R3 measured that a container's "encoder" tag is written into the artifact by the
# MUXER at write time (mp4 '©too', Matroska 'MuxingApp'/'WritingApp'), and that a
# value supplied by the authoring tool is destroyed before the file exists. The
# value is physically present, so presence in bytes proves nothing about authorship.
# This model records the authorship separately from the value, which is the only
# thing that makes "the probe failed to expose a declaration" distinguishable from
# "the artifact contains no declaration".
#
# SCOPE OF THIS CHANGE (Stage 2.3 remediation cycle 1):
#   - adds observation of producer-relevant metadata with an explicit origin;
#   - retains the verbatim key and value R7 requires;
#   - does NOT touch SourceInfo.version or ProvenanceEntry: those carriers are
#     specified by §2.1.15 and owned by 2.15, and inventing them here would be the
#     drift this audit exists to prevent.
#
# PENDING §2.1 v1.3: `origin` is an envelope-level attribute and the stage-local
# declaration below should be promoted to §2.1 once that amendment is accepted.


class ObservationOrigin(str, enum.Enum):
    """Who authored an observed value (Stage 2.3 §G.2.4).

    The four values are exhaustive over what was measured. `probe_generated` is
    deliberately absent: R3 found no instance of the probe fabricating a value, and
    an origin class with no measured instance is a category that cannot be tested.
    The prohibition the draft intended is expressed instead as the eligibility rule
    on `SourceInfo.version` below, which is where it is actually enforceable.
    """

    ARTIFACT_DECLARED = "artifact_declared"
    MUXER_AUTHORED = "muxer_authored"
    PROBE_OBSERVED = "probe_observed"
    UNAVAILABLE = "unavailable"


class ProducerDeclaration(BaseModel):
    """One producer-related metadata value, with its authorship and its origin.

    `origin` and `state` answer different questions and are never substitutes:
      - `origin`  — who wrote the value (authorship)
      - `state`   — whether the value exists (observation, §2.1.4 Dimension B)

    A value can be extracted AND muxer-authored; that combination is the whole
    point, and collapsing it to either axis alone loses the audit fact.

    §2.1.16: this model is a §2.1 v1.3 CONSUMER of `ObservationState.CONFLICTING`. The
    vocabulary member is §2.1's; 2.3 only applies it, per its own §V.5.1 rule.
    """

    scope: str
    canonical_key: str
    original_key: str
    original_value: str
    origin: ObservationOrigin
    state: ObservationState = ObservationState.EXTRACTED
    # rule_id names the registered normalisation rule applied to reach
    # `canonical_key`. `None` means the canonical key has no registered rule, i.e.
    # the key is unrecognised. That is recorded here rather than as a new
    # ObservationState value, because ObservationState is frozen at four members.
    rule_id: Optional[str] = None


class ProbeFailureState(str, enum.Enum):
    """Stage 2.3 §V.1 — a probe outcome that did NOT complete.

    These are the four §V.1 FAILURE states. They are NOT a new rejection vocabulary:
    §V.1 R-3 requires each to map onto exactly one code from the §2.1.5 closed
    `REJ_*` set, and 2.3 may not mint a new one. This enum records WHICH condition
    occurred; the mapping to a `REJ_*` code is `ingestion_status`'s job (§2.1.5) and
    is a separate 2.15 migration row — deliberately NOT implemented here.

    The critical member for G18 is UNREADABLE. It is a FAILURE state; `ObservationState.
    UNAVAILABLE` on the same group is the STATE-axis fact. Keeping the two separate is
    what stops a probe failure collapsing into METADATA_ABSENT: the latter is a SUCCESS
    state meaning "the scope was read and held no declaration".
    """

    UNREADABLE = "unreadable"
    NO_VIDEO_STREAM = "no_video_stream"
    RESOURCE_LIMIT = "resource_limit"
    REJECTED_BY_POLICY = "rejected_by_policy"


class ContainerInfo(BaseModel):
    # format/format_long are Optional ONLY because a probe failure must still emit the
    # group (§V.1 R-2). On UNREADABLE the format could not be determined, so it is
    # absent -- NOT "unknown". Writing "unknown" here would reintroduce exactly the
    # sentinel A9 was just discharged for removing.
    format: Optional[str]
    format_long: Optional[str]
    size_bytes: int

    source: Optional[SourceInfo] = None
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    # Additive/optional: a minor bump under §2.1.5's version policy. Absent means
    # "this producer was not observed", never "no producer was declared".
    producer_declarations: list[ProducerDeclaration] = Field(default_factory=list)
    # §2.1.16 v1.3: the group-level observation state for the declarations above.
    # `extracted` for one value, `conflicting` when two scopes disagree and BOTH are
    # retained, `absent` when nothing was observed. The declarations are the record;
    # this is the rollup, and it is never emitted unless its conditions actually hold.
    producer_state: Optional[ObservationState] = Field(
        default=None, exclude_if=lambda v: v is None
    )
    # Stage 2.3 §V.1 R-2 (G18): a probe FAILURE is recorded ON the group, not raised
    # away. `probe_state` is ABSENT on success and set to a ProbeFailureState on
    # failure. This is the STATE-AXIS half of the acceptance criterion: on failure
    # `producer_state` is UNAVAILABLE (the probe could not determine it), which is a
    # different ObservationState from ABSENT (the probe read the scope and found
    # nothing). `probe_detail` is non-contract human text; no consumer may branch on it.
    probe_state: Optional[ProbeFailureState] = Field(
        default=None, exclude_if=lambda v: v is None
    )
    probe_detail: Optional[str] = Field(
        default=None, exclude_if=lambda v: v is None
    )


class VideoStreamInfo(BaseModel):
    codec: str
    codec_long: str
    profile: Optional[str] = None
    level: Optional[str] = None
    width: int
    height: int
    coded_width: int
    coded_height: int
    # Amendment Record v1.2 (G10 / Stage 2.3 A9): the sibling of sample_aspect_ratio.
    # It carried the same defect via fallback="0:1" -- and A9's sentinel tuple could
    # not see "0:1", so the row went green with a live sentinel still in the contract.
    display_aspect_ratio: Optional[str]
    # stage2_source_description.md Amendment Record v1.1 (G10 / Stage 2.3 A9): OPTIONAL.
    # The probe measured `sample_aspect_ratio = None` on ordinary square-pixel clips,
    # and the non-optional type forced a fabricated `"1:1"` -- indistinguishable from a
    # genuinely declared 1:1. `null` now means "the source declares none"; it never
    # carries a sentinel. Note the key stays REQUIRED: null == "checked, declares none",
    # which is not the same as "not applicable" (S-2).
    sample_aspect_ratio: Optional[str]
    frame_rate: str
    avg_frame_rate: str
    time_base: str
    nb_frames: int

    source: Optional[SourceInfo] = None
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class AudioStreamInfo(BaseModel):
    stream_index: int
    codec: str
    codec_long: str
    sample_rate: int
    channels: int
    channel_layout: str
    bits_per_sample: Optional[int] = None
    duration: float
    bit_rate: Optional[int] = None
    language: Optional[str] = None
    title: Optional[str] = None

    source: Optional[SourceInfo] = None
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class FpsActual(BaseModel):
    value: float
    type: str  # "cfr" | "vfr" | "mixed"
    state: str = "extracted"  # Stage 2 §2.1.4 B observation state
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class CfrVfr(BaseModel):
    is_cfr: bool
    is_vfr: bool
    variance: float
    max_delta: float
    state: str = "extracted"  # Stage 2 §2.1.4 B observation state
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class DurationInfo(BaseModel):
    value: float
    start_time: float
    end_time: float
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class BitDepth(BaseModel):
    luma: int
    chroma: int
    state: str = "extracted"  # Stage 2 §2.1.4 B observation state
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    fidelity: Fidelity = Field(default_factory=lambda: Fidelity(type=FidelityType.PRESERVED))
    validation: ValidationInfo = Field(default_factory=ValidationInfo)


class ColorSpace(BaseModel):
    value: str
    full_name: str
    state: str = "extracted"  # Stage 2 §2.1.4 B observation state
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    fidelity: Fidelity = Field(default_factory=lambda: Fidelity(type=FidelityType.PRESERVED))
    validation: ValidationInfo = Field(default_factory=ValidationInfo)


class TransferCharacteristic(BaseModel):
    value: str
    state: str = "extracted"  # Stage 2 §2.1.4 B observation state
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    fidelity: Fidelity = Field(default_factory=lambda: Fidelity(type=FidelityType.PRESERVED))
    validation: ValidationInfo = Field(default_factory=ValidationInfo)


class ChromaSubsampling(BaseModel):
    subsampling: str
    state: str = "extracted"  # Stage 2 §2.1.4 B observation state
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    fidelity: Fidelity = Field(default_factory=lambda: Fidelity(type=FidelityType.PRESERVED))
    validation: ValidationInfo = Field(default_factory=ValidationInfo)


class GenerationalEstimate(BaseModel):
    value: str  # "prosumer_phone" | "dslr" | "broadcast" | "cinema" | "unknown"
    # D-2 (Stage 2 §2.1.13) — an ESTIMATE, never a measured fact. Allowed states are
    # extracted | uncertain | unavailable: the Builder cannot assert "there is no generation" (absent).
    state: str = "extracted"
    confidence: Confidence
    source: SourceInfo
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    fidelity: Fidelity = Field(default_factory=lambda: Fidelity(type=FidelityType.REGENERABLE))
    validation: ValidationInfo = Field(default_factory=ValidationInfo)


class QualityScore(BaseModel):
    """
    Ingestion-time PRELIMINARY technical source signal (Stage 2 D-2).

    This is a sealed source-native hint, NOT the authoritative quality assessment — that is
    `QualityReport.score` (Contract #3). It must never be presented as "the video is N% good",
    and per Stage 2 §2.1.13 it must not be mathematically chained into `QualityReport.score`.
    """

    value: Optional[float] = None  # null if cannot measure
    state: str  # "extracted" | "absent" | "uncertain" | "unavailable" — Stage 2 §2.1.4 B
    confidence: Confidence
    source: Optional[SourceInfo] = None
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class SourceDescription(BaseModel):
    """
    Contract #1 — the first interface contract produced by the Ingestion layer.
    Captures structural identity of the input video using only source-native metadata.
    """

    id: str = Field(default_factory=lambda: f"src_{uuid.uuid4().hex[:16]}")
    source_path: str

    container: ContainerInfo
    # Groups for steps the probe NEVER REACHED are absent from the contract, never
    # null-filled (§2.2 F.3.1 rule 2). They became Optional in the R-2 migration
    # (G18) because a probe failure must still emit a contract carrying the affected
    # group. On a successful probe they are ALWAYS populated -- see
    # tests/test_probe_failure_recording.py, which asserts both halves.
    video_stream: Optional[VideoStreamInfo] = None

    fps_actual: Optional[FpsActual] = None
    cfr_vfr: Optional[CfrVfr] = None
    duration: Optional[DurationInfo] = None
    audio_streams: list[AudioStreamInfo] = Field(default_factory=list)

    # OPTIONAL
    bit_depth: Optional[BitDepth] = None
    color_space: Optional[ColorSpace] = None
    transfer: Optional[TransferCharacteristic] = None
    chroma: Optional[ChromaSubsampling] = None
    generational_estimate: Optional[GenerationalEstimate] = None

    # UNCERTAIN-ALLOWED
    quality_score: Optional[QualityScore] = None

    # NOTE (Stage 2 D-3): the contract-level `extraction_status` field was REMOVED from
    # Contract #1. Per Stage 1 §9.1 it is a DNA-level (Contract #11) rollup. Within Contract #1
    # the equivalent information is carried per group by `state` (Stage 2 §2.1.4 B) and at the
    # contract level by `ingestion_status` (Stage 2 §2.1.5, to be added in 2.15).

    model_config = {"arbitrary_types_allowed": True}


class IngestionError(Exception):
    """Raised when ingestion fails for a recoverable reason."""

    def __init__(self, message: str, recoverable: bool = True):
        super().__init__(message)
        self.recoverable = recoverable
