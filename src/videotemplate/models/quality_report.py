"""
QualityReport — Contract #3, Layer 3 (Quality).

Per Stage 1 §8, Contract #3.
Determines signal reliability. Always produces report, even if low quality.
Never blocks pipeline.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..utils.confidence import Confidence, ProvenanceEntry, SourceInfo


class Artifact(BaseModel):
    type: str           # "blocking" | "banding" | "blur" | "noise" | "compression"
    severity: float     # 0.0–1.0
    confidence: Confidence


class SpatialQualityMap(BaseModel):
    """
    Per-frame or per-region quality indicators.
    Can be a reference to a stored map or inline values.
    """

    ref: Optional[str] = None       # path to stored quality map file
    frames: list[float] = Field(default_factory=list)  # per-frame quality score 0–1
    confidence: Confidence


class QualityReport(BaseModel):
    score: float                        # overall 0.0–1.0
    state: str = "extracted"            # Stage 2 §2.1.4 B: extracted | uncertain | absent | unavailable
    duration: float                     # seconds (must match source)
    confidence: Confidence

    artifacts: list[Artifact] = Field(default_factory=list)
    spatial_quality_map: Optional[SpatialQualityMap] = None

    # OPTIONAL
    generational_estimate_ref: Optional[str] = None

    extraction_status: str = "extracted"  # "extracted" | "absent" | "uncertain"

    # ── Stage 1 §6 — confidence + provenance envelope (was computed then discarded) ──
    source: Optional[SourceInfo] = None
    provenance: list[ProvenanceEntry] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
