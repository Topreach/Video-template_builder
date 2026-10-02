"""Versioned, user-reviewable video analysis proposals."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="after")
    def validate_timeline(self) -> "AnalysisProposal":
        """Reject proposals that could make the review UI lose or duplicate source time."""
        duration = self.media_facts.duration_ms
        boundary_times = [boundary.at_ms for boundary in self.boundaries]
        if boundary_times != sorted(set(boundary_times)):
            raise ValueError("proposal boundaries must be unique and ordered")
        if any(at >= duration for at in boundary_times):
            raise ValueError("proposal boundaries must fall inside the source duration")

        section_ids: set[str] = set()
        previous_end = 0
        for index, section in enumerate(self.sections):
            if section.id in section_ids:
                raise ValueError("proposal section ids must be unique")
            section_ids.add(section.id)
            if section.order != index:
                raise ValueError("proposal section order must be contiguous from zero")
            if section.start_ms != previous_end:
                raise ValueError("proposal sections must cover the timeline without gaps or overlaps")
            if section.end_ms > duration:
                raise ValueError("proposal sections must end within the source duration")
            previous_end = section.end_ms

        if not self.sections or previous_end != duration:
            raise ValueError("proposal sections must cover the full source duration")
        section_starts = {section.start_ms for section in self.sections[1:]}
        if set(boundary_times) != section_starts:
            raise ValueError("proposal boundaries must match interior section starts")
        return self
