"""Versioned, user-reviewable video analysis proposals."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MediaFacts(BaseModel):
    duration_ms: int = Field(gt=0, le=30_000)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    frame_rate: float | None = Field(default=None, gt=0)
    has_audio: bool | None = None


class ProposalBoundary(BaseModel):
    id: str
    at_ms: int = Field(gt=0)
    origin: Literal["detector"] = "detector"
    cue: Literal["visual-cut"] = "visual-cut"
    uncertainty: Literal["unknown"] = "unknown"
    review_state: Literal["unreviewed"] = "unreviewed"


class ProposedSection(BaseModel):
    """Contiguous shot span; this is not a semantic/story section."""

    id: str
    order: int = Field(ge=0)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    origin: Literal["detector"] = "detector"
    review_state: Literal["unreviewed"] = "unreviewed"


class AnalysisWarning(BaseModel):
    code: str
    message: str


class AnalysisProposal(BaseModel):
    schema_version: Literal[1] = 1
    id: str
    source_id: str
    status: Literal["ready", "partial", "failed"]
    producer_name: str
    producer_version: str
    processing: Literal["local"]
    media_facts: MediaFacts
    boundaries: list[ProposalBoundary] = Field(default_factory=list)
    sections: list[ProposedSection] = Field(default_factory=list)
    warnings: list[AnalysisWarning] = Field(default_factory=list)

