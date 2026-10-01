"""
DecodedVideo — Contract #2, Layer 2 (Decode).

Per Stage 1 §8, Contract #2.
Produces correctly ordered decoded media from SourceDescription.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..utils.confidence import Confidence, ProvenanceEntry


class DecodedVideo(BaseModel):
    """
    Contract #2 — decoded media representation.
    Frames stored as a directory of image files (PNG) or numpy-backed reference.
    PTS array provides presentation timestamps in seconds.
    """

    frames_ref: str          # path to directory containing decoded frames
    pts: list[float]         # presentation timestamps in seconds, one per frame
    duration: float          # total duration in seconds
    width: int
    height: int
    fps: float               # actual frames per second
    cfr_vfr: str             # "cfr" | "vfr" | "mixed"

    # Optional metadata propagated from SourceDescription
    frame_count: int
    codec: Optional[str] = None
    color_space: Optional[str] = None

    # ── Stage 1 §6 — confidence + provenance envelope (was computed then discarded) ──
    confidence: Confidence
    provenance: list[ProvenanceEntry] = Field(default_factory=list)

    # ── Stage 1 §3 Layer 2 — partial decode marks segments UNCERTAIN, continue ──
    state: str = "extracted"                                   # Stage 2 §2.1.4 B: extracted | uncertain
    uncertain_frames: list[int] = Field(default_factory=list)  # frame indices that failed conversion

    model_config = {"arbitrary_types_allowed": True}
