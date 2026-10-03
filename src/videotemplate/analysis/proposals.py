"""Versioned, user-reviewable video component analysis proposals."""
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


class ProposedShotSpan(BaseModel):
    """Contiguous visual shot span; a shot is not automatically a story section."""

    id: str
    order: int = Field(ge=0)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    origin: Literal["detector"] = "detector"
    review_state: Literal["unreviewed"] = "unreviewed"


class NormalizedRegion(BaseModel):
    """Optional source-frame box using 0..1 coordinates from top-left."""

    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def validate_bounds(self) -> "NormalizedRegion":
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("normalized region must fit within the source frame")
        return self


ComponentTrack = Literal["visual", "text", "audio", "creative", "integrity"]
ComponentKind = Literal[
    "shot",
    "person",
    "object",
    "action",
    "setting",
    "background",
    "camera-motion",
    "split-screen-or-overlay",
    "on-screen-text",
    "watermark-or-brand-mark",
    "speech",
    "music",
    "sound-effect",
    "silence",
    "beat",
    "creative-role",
    "abrupt-start",
    "abrupt-end",
    "black-or-freeze",
    "unknown",
]

SIGNAL_COVERAGE = frozenset(
    {
        "technical-facts",
        "shot-boundaries",
        "people-and-subjects",
        "objects-and-actions",
        "setting-and-background",
        "camera-and-layout",
        "on-screen-text",
        "speech",
        "music-and-sound",
        "creative-beats",
        "source-integrity",
    }
)


class ComponentFinding(BaseModel):
    """One time-grounded observation; multiple tracks may overlap in time."""

    id: str
    track: ComponentTrack
    kind: ComponentKind
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    label: str = Field(min_length=1, max_length=120)
    summary: str | None = Field(default=None, max_length=500)
    # Clip-local, anonymous continuity only; never a cross-video identity.
    entity_ref: str | None = Field(default=None, max_length=80)
    region: NormalizedRegion | None = None
    mask_artifact_ref: str | None = Field(default=None, max_length=160)
    evidence_at_ms: int | None = Field(default=None, ge=0)
    role: Literal[
        "hook",
        "context",
        "setup",
        "tutorial-step",
        "demonstration",
        "action",
        "reaction",
        "reveal",
        "payoff",
        "call-to-action",
        "lyric-beat",
        "transition",
        "unknown",
    ] | None = None
    origin: Literal[
        "detector",
        "classifier",
        "ocr",
        "transcriber",
        "audio-analyzer",
        "multimodal-model",
        "user",
        "derived",
    ]
    provider_name: str
    provider_version: str
    processing: Literal["local", "server", "unknown"]
    confidence: float | None = Field(default=None, ge=0, le=1)
    confidence_calibrated: bool = False
    uncertainty: Literal["low", "medium", "high", "unknown"] = "unknown"
    review_state: Literal["unreviewed", "accepted", "edited", "ignored"] = "unreviewed"

    @model_validator(mode="after")
    def validate_finding(self) -> "ComponentFinding":
        if self.end_ms <= self.start_ms:
            raise ValueError("component findings must have a positive time range")
        if self.evidence_at_ms is not None and not self.start_ms <= self.evidence_at_ms < self.end_ms:
            raise ValueError("evidence timestamp must fall inside the finding time range")
        if self.confidence is not None and not self.confidence_calibrated:
            raise ValueError("confidence scores may be included only when calibrated")
        if (self.track == "creative") != (self.kind == "creative-role"):
            raise ValueError("creative-role findings must use the creative track")
        expected_tracks = {
            "shot": "visual",
            "person": "visual",
            "object": "visual",
            "action": "visual",
            "setting": "visual",
            "background": "visual",
            "camera-motion": "visual",
            "split-screen-or-overlay": "visual",
            "on-screen-text": "text",
            "watermark-or-brand-mark": "text",
            "speech": "audio",
            "music": "audio",
            "sound-effect": "audio",
            "silence": "audio",
            "beat": "audio",
            "abrupt-start": "integrity",
            "abrupt-end": "integrity",
            "black-or-freeze": "integrity",
        }
        if self.kind in expected_tracks and expected_tracks[self.kind] != self.track:
            raise ValueError(f"{self.kind} findings must use the {expected_tracks[self.kind]} track")
        if self.role is not None and self.kind != "creative-role":
            raise ValueError("role labels belong only to creative-role findings")
        return self


class SignalReport(BaseModel):
    """Coverage record, including analyses that have not run or are unsupported."""

    signal: Literal[
        "technical-facts",
        "shot-boundaries",
        "people-and-subjects",
        "objects-and-actions",
        "setting-and-background",
        "camera-and-layout",
        "on-screen-text",
        "speech",
        "music-and-sound",
        "creative-beats",
        "source-integrity",
    ]
    state: Literal["completed", "partial", "not-run", "unsupported", "failed"]
    calibration: Literal["not-evaluated", "calibrated", "not-applicable"]
    provider_name: str | None = None
    provider_version: str | None = None
    processing: Literal["local", "server", "unknown"] | None = None
    evidence_count: int = Field(default=0, ge=0)
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_report(self) -> "SignalReport":
        if self.state == "completed" and not all(
            (self.provider_name, self.provider_version, self.processing)
        ):
            raise ValueError("completed signal reports require provider version and processing location")
        if self.state in {"partial", "not-run", "unsupported", "failed"} and not self.note:
            raise ValueError("incomplete signal reports require a user-readable explanation")
        if self.state in {"not-run", "unsupported", "failed"} and self.evidence_count:
            raise ValueError("signals that did not complete cannot report evidence")
        return self


class AnalysisWarning(BaseModel):
    code: str
    message: str


class AnalysisProposal(BaseModel):
    schema_version: Literal[2] = 2
    id: str
    source_id: str
    status: Literal["ready", "partial", "failed"]
    scope: Literal["shot-boundaries-only", "component-inventory"]
    producer_name: str
    producer_version: str
    processing: Literal["local", "server"]
    media_facts: MediaFacts
    boundaries: list[ProposalBoundary] = Field(default_factory=list)
    shot_spans: list[ProposedShotSpan] = Field(default_factory=list)
    components: list[ComponentFinding] = Field(default_factory=list)
    signal_reports: list[SignalReport] = Field(default_factory=list)
    warnings: list[AnalysisWarning] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_proposal(self) -> "AnalysisProposal":
        """Reject timelines or coverage claims that could mislead section review."""
        duration = self.media_facts.duration_ms
        boundary_times = [boundary.at_ms for boundary in self.boundaries]
        if boundary_times != sorted(set(boundary_times)):
            raise ValueError("proposal boundaries must be unique and ordered")
        if any(at >= duration for at in boundary_times):
            raise ValueError("proposal boundaries must fall inside the source duration")

        shot_ids: set[str] = set()
        previous_end = 0
        for index, shot in enumerate(self.shot_spans):
            if shot.id in shot_ids:
                raise ValueError("shot span ids must be unique")
            shot_ids.add(shot.id)
            if shot.order != index:
                raise ValueError("shot span order must be contiguous from zero")
            if shot.start_ms != previous_end:
                raise ValueError("shot spans must cover the timeline without gaps or overlaps")
            if shot.end_ms > duration:
                raise ValueError("shot spans must end within the source duration")
            previous_end = shot.end_ms

        if not self.shot_spans or previous_end != duration:
            raise ValueError("shot spans must cover the full source duration")
        span_starts = {shot.start_ms for shot in self.shot_spans[1:]}
        if set(boundary_times) != span_starts:
            raise ValueError("proposal boundaries must match interior shot span starts")

        component_ids: set[str] = set()
        for component in self.components:
            if component.id in component_ids:
                raise ValueError("component ids must be unique")
            component_ids.add(component.id)
            if component.end_ms > duration:
                raise ValueError("component findings must end within the source duration")

        signal_names = [report.signal for report in self.signal_reports]
        if len(signal_names) != len(set(signal_names)):
            raise ValueError("each analysis signal must have one coverage report")
        for report in self.signal_reports:
            if report.state == "not-run" and report.evidence_count:
                raise ValueError("a signal that has not run cannot report evidence")

        missing_signals = SIGNAL_COVERAGE.difference(signal_names)
        incomplete_coverage = missing_signals or any(
            report.state in {"not-run", "partial", "failed"}
            for report in self.signal_reports
        )
        if self.scope == "shot-boundaries-only" and self.status == "ready":
            raise ValueError("shot-boundary-only analysis is always partial component coverage")
        if self.scope == "component-inventory" and self.status == "ready" and incomplete_coverage:
            raise ValueError("a ready component inventory must report complete coverage for every signal")

        if self.status == "ready" and incomplete_coverage:
            raise ValueError("a proposal with incomplete signal coverage cannot be ready")
        return self
