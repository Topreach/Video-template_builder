"""Versioned, renderer-independent recipe for an editable short-video template."""
from __future__ import annotations

import enum
import uuid
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TemplateFormat(str, enum.Enum):
    MUSIC_BEAT = "music_beat"
    CINEMATIC = "cinematic"
    ACTION = "action"
    COMEDY = "comedy"
    STORY = "story"
    TUTORIAL = "tutorial"
    PRODUCT_SHOWCASE = "product_showcase"
    OTHER = "other"


class SectionDecision(str, enum.Enum):
    """User's decision for a section detected in the reference video."""

    EDIT = "edit"
    KEEP = "keep"
    EXCLUDE = "exclude"


class TemplateStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"


class AssetOrigin(str, enum.Enum):
    USER = "user"
    LICENSED = "licensed"
    GENERATED = "generated"
    REFERENCE = "reference"
    PLACEHOLDER = "placeholder"


class MediaSlot(BaseModel):
    """A replaceable image/video slot with guidance for the template user."""

    id: str
    prompt: str
    accepted_types: list[str] = Field(default_factory=lambda: ["video", "image"])
    required: bool = True
    target_duration_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    min_duration_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    max_duration_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    framing: Optional[str] = None

    @model_validator(mode="after")
    def validate_duration_range(self) -> "MediaSlot":
        if (
            self.min_duration_seconds is not None
            and self.max_duration_seconds is not None
            and self.min_duration_seconds > self.max_duration_seconds
        ):
            raise ValueError("minimum slot duration cannot exceed maximum")
        if self.target_duration_seconds is not None:
            if self.min_duration_seconds is not None and self.target_duration_seconds < self.min_duration_seconds:
                raise ValueError("target slot duration is below its minimum")
            if self.max_duration_seconds is not None and self.target_duration_seconds > self.max_duration_seconds:
                raise ValueError("target slot duration exceeds its maximum")
        return self


class ReplacementIdea(BaseModel):
    """Optional user-reviewed replacement suggestion; never applied implicitly."""

    id: str
    description: str
    rationale: Optional[str] = None
    origin: AssetOrigin = AssetOrigin.PLACEHOLDER
    asset_ref: Optional[str] = None
    rights_scope: Optional[str] = None
    accepted: bool = False


class TextLayer(BaseModel):
    id: str
    text: str
    start_offset_seconds: float = Field(default=0, ge=0, le=30)
    end_offset_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    editable: bool = True
    style: dict[str, str | int | float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_timing(self) -> "TextLayer":
        if self.end_offset_seconds is not None and self.end_offset_seconds <= self.start_offset_seconds:
            raise ValueError("text layer end must be after its start")
        return self


class AudioLayer(BaseModel):
    id: str
    role: str  # music, source_audio, voiceover, sound_effect
    origin: AssetOrigin = AssetOrigin.PLACEHOLDER
    asset_ref: Optional[str] = None
    start_offset_seconds: float = Field(default=0, ge=0, le=30)
    end_offset_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    volume: float = Field(default=1.0, ge=0, le=2)
    muted: bool = False
    editable: bool = True
    rights_scope: Optional[str] = None

    @model_validator(mode="after")
    def validate_timing(self) -> "AudioLayer":
        if self.end_offset_seconds is not None and self.end_offset_seconds <= self.start_offset_seconds:
            raise ValueError("audio layer end must be after its start")
        return self


class VisualEdit(BaseModel):
    id: str
    operation: str  # replace_subject, change_background, replace_object, remove_object
    target_description: str
    replacement_prompt: Optional[str] = None
    replacement_asset_ref: Optional[str] = None
    start_offset_seconds: float = Field(default=0, ge=0, le=30)
    end_offset_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    user_approved: bool = False


class TemplateSection(BaseModel):
    """A source interval and its user-approved role in the reusable edit."""

    id: str
    order: int = Field(ge=0)
    role: str
    label: str
    purpose: Optional[str] = None
    source_start_seconds: float = Field(ge=0, le=30)
    source_end_seconds: float = Field(gt=0, le=30)
    target_duration_seconds: Optional[float] = Field(default=None, gt=0, le=30)
    decision: SectionDecision = SectionDecision.EDIT
    required: bool = True
    media_slots: list[MediaSlot] = Field(default_factory=list)
    replacement_ideas: list[ReplacementIdea] = Field(default_factory=list)
    text_layers: list[TextLayer] = Field(default_factory=list)
    audio_layers: list[AudioLayer] = Field(default_factory=list)
    visual_edits: list[VisualEdit] = Field(default_factory=list)
    effects: list[dict[str, str | int | float | bool]] = Field(default_factory=list)
    transition_after: Optional[str] = None
    analysis_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    user_confirmed: bool = False

    @model_validator(mode="after")
    def validate_interval(self) -> "TemplateSection":
        if self.source_end_seconds <= self.source_start_seconds:
            raise ValueError("section end must be after its start")
        return self


class TemplateOutputProfile(BaseModel):
    aspect_ratio: str = "9:16"
    max_duration_seconds: float = Field(default=30, gt=0, le=30)
    resolution_width: Optional[int] = Field(default=None, gt=0)
    resolution_height: Optional[int] = Field(default=None, gt=0)
    frame_rate: Optional[float] = Field(default=None, gt=0, le=120)
    container: str = "mp4"


class TemplateProvenance(BaseModel):
    reference_source_id: Optional[str] = None
    analysis_version: Optional[str] = None
    rights_declaration: Optional[str] = None
    created_by: Optional[str] = None
    parent_template_id: Optional[str] = None


class TemplateRecipe(BaseModel):
    """The editable, saved product artifact; independent of a renderer."""

    id: str = Field(default_factory=lambda: f"tpl_{uuid.uuid4().hex[:16]}")
    schema_version: int = Field(default=1, ge=1)
    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    format_tags: list[TemplateFormat] = Field(default_factory=list)
    status: TemplateStatus = TemplateStatus.DRAFT
    output_profile: TemplateOutputProfile = Field(default_factory=TemplateOutputProfile)
    sections: list[TemplateSection] = Field(min_length=1)
    global_text_layers: list[TextLayer] = Field(default_factory=list)
    global_audio_layers: list[AudioLayer] = Field(default_factory=list)
    provenance: TemplateProvenance = Field(default_factory=TemplateProvenance)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @model_validator(mode="after")
    def validate_recipe(self) -> "TemplateRecipe":
        section_ids = [section.id for section in self.sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("section IDs must be unique within a template")
        orders = [section.order for section in self.sections]
        if len(orders) != len(set(orders)):
            raise ValueError("section order values must be unique within a template")
        if self.sections and max(section.source_end_seconds for section in self.sections) > 30:
            raise ValueError("reference sections cannot exceed the 30-second input limit")
        return self
