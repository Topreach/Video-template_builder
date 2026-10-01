"""
Confidence, Provenance, and Fidelity envelope models.

Per Stage 1 §6: Every important field has VALUE + SOURCE LAYER + PROVENANCE[] + CONFIDENCE + FIDELITY + VALIDATION.
"""
from __future__ import annotations

import enum
from typing import Optional

from pydantic import BaseModel, Field


class ConfidenceType(str, enum.Enum):
    """Confidence semantic category per Stage 1 §6.

    NOTE: this is NOT the observation state. `ConfidenceType.MEASURED` describes *how* a value
    was obtained (as opposed to detected/tracked/inferred). The observation state — whether the
    value exists at all — is `ObservationState` below (Stage 2 §2.1.4 Dimension B). The two axes
    are orthogonal: a field can be `state=extracted` with `confidence.type=detection`.
    """

    MEASURED = "measured"
    DETECTION = "detection"
    TRACKING = "tracking"
    IDENTITY_PERSISTENCE = "identity_persistence"
    SEMANTIC_INTERPRETATION = "semantic_interpretation"
    INFERRED = "inferred"
    FUSION = "fusion"


class ObservationState(str, enum.Enum):
    """
    Observation state — Stage 2 §2.1.4 Dimension B. Inherited by all twelve contracts.

    EXTRACTED   the Builder obtained the value
    ABSENT      the Builder checked; the property does not exist in this source
    UNCERTAIN   evidence exists; the Builder cannot establish the value confidently
    UNAVAILABLE the Builder could not determine the value (probe failed / no evidence)
    CONFLICTING §2.1.16 (v1.3) — two or more MUTUALLY INCONSISTENT values were obtained
                from DISTINCT evidence sources, and ALL of them are retained

    `absent` is a positive assertion; `unavailable` is a capability statement. They are never
    interchangeable, and neither is ever used as a substitute for a `null`/not-applicable group.

    CONFLICTING is additive and does not restate the other four. The discriminator is normative
    (§2.1.16 §3): UNCERTAIN is difficulty INTERPRETING one value; CONFLICTING is difficulty
    CHOOSING between two or more values that each parsed cleanly and each came from a different
    addressable source. A single ambiguous value is `uncertain` and is never `conflicting`.
    """
    EXTRACTED = "extracted"
    ABSENT = "absent"
    UNCERTAIN = "uncertain"
    UNAVAILABLE = "unavailable"
    CONFLICTING = "conflicting"


class FidelityType(str, enum.Enum):
    """
    Fidelity contract indicates how faithfully a field must be preserved
    from the source, per Stage 1 §4.4 and §12 of the Entity contract.
    """

    PRESERVED = "preserved"
    STRUCTURAL = "structural"
    REGENERABLE = "regenerable"


class SourceLayer(str, enum.Enum):
    """Representation boundaries per Stage 1 §4."""

    SOURCE_NATIVE = "source_native"
    ANALYSIS_NORMALIZED = "analysis_normalized"
    EVIDENCE = "evidence"
    SEMANTIC = "semantic"
    TEMPLATE_DNA = "template_dna"


class Fidelity(BaseModel):
    type: FidelityType
    tolerance: Optional[str] = None


def producer_identity() -> dict[str, str]:
    """§2.1.15 R9 — the single introspection point for builder-side identity.

    R9: provenance entries are written by ONE helper. Per-producer ad-hoc
    introspection is forbidden — it is how two different versions end up in the
    same cache. Every producer obtains its tool version here.

    R7: the value is recorded verbatim as the producer reports it — never parsed,
    normalised, or canonicalised.
    R4: "unknown" is the ONLY permitted sentinel, and only when introspection is
    genuinely impossible. It is never a stand-in for a version that does exist.

    Builder side only. This must never be written to `SourceInfo.version`, which
    §2.1.15 fixes as the SOURCE-side declaration (R3).
    """
    try:
        import av
        return {"tool": "PyAV", "tool_version": str(av.__version__)}
    except Exception:  # noqa: BLE001 - introspection impossible; R4 sentinel
        return {"tool": "PyAV", "tool_version": "unknown"}


class SourceInfo(BaseModel):
    layer: SourceLayer
    model: Optional[str] = None
    tool: Optional[str] = None
    # §2.1.15 v1.2: the SOURCE-side producer string the analysed object declares.
    #
    # R3 is unusually strict here: optional / unavailable-allowed, and NEVER "" /
    # "unknown" / a Builder version. Omission means "the object declares none". A
    # sentinel would be indistinguishable from a declaration, which is the
    # fabrication this field exists to prevent. `exclude_if` enforces the omission
    # at serialisation; without it the key is emitted as `null`, which R2 forbids.
    version: Optional[str] = Field(default=None, exclude_if=lambda v: v is None)


class ProvenanceEntry(BaseModel):
    """
    Each evidence transformation logs:
    source_layer, evidence_refs[], transform_type, confidence_delta
    """

    layer: SourceLayer
    evidence_refs: list[str] = Field(default_factory=list)
    transform_type: str = "none"
    confidence_delta: float = 0.0
    # §2.1.15 v1.2, builder side. R1: required on the producing entry of any
    # `estimate`-stability field; its absence makes that field non-conformant.
    # R4: "unknown" is the only permitted sentinel, and only when introspection is
    # genuinely undeterminable.
    tool_version: Optional[str] = Field(default=None, exclude_if=lambda v: v is None)
    # R2: optional. Omitted when no model/heuristic produced the value; never null.
    model_version: Optional[str] = Field(default=None, exclude_if=lambda v: v is None)


class Confidence(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    type: ConfidenceType = ConfidenceType.MEASURED
    calibration: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ValidationStatus(str, enum.Enum):
    VALIDATED = "validated"
    CONFLICT = "conflict"
    UNCERTAIN = "uncertain"


class ValidationInfo(BaseModel):
    status: ValidationStatus = ValidationStatus.VALIDATED
    rules_passed: list[str] = Field(default_factory=list)
    rules_failed: list[str] = Field(default_factory=list)


class FieldEnvelope:
    """
    Mixin for fields that carry confidence + provenance + fidelity + validation.
    Usage: embed as a sub-model on data classes where needed.
    """
