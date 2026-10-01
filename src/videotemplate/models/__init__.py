"""
Interface contracts — Stage 1 §8. The ONLY models allowed to cross layer boundaries.

Implemented (Block 1): #1 SourceDescription, #2 DecodedVideo, #3 QualityReport.

Remaining contracts #4-#12 (TemporalEvidence, SpatialEvidence, EntityModel,
MotionEvidence, AudioEvidence, TextEvidence, SemanticStructure, TemplateDNA,
ValidationReport) arrive with Stages 5-15 and must conform to §6 (confidence +
provenance envelope) and §9.1 (REQUIRED / OPTIONAL / ABSENT-ALLOWED / UNCERTAIN-ALLOWED).
"""
from .source_description import SourceDescription, IngestionError
from .decoded_video import DecodedVideo
from .quality_report import QualityReport
from .template_recipe import (
    AudioLayer,
    AssetOrigin,
    MediaSlot,
    ReplacementIdea,
    SectionDecision,
    TemplateFormat,
    TemplateOutputProfile,
    TemplateProvenance,
    TemplateRecipe,
    TemplateSection,
    TemplateStatus,
    TextLayer,
    VisualEdit,
)

__all__ = [
    "SourceDescription",
    "IngestionError",
    "DecodedVideo",
    "QualityReport",
    "AudioLayer",
    "AssetOrigin",
    "MediaSlot",
    "ReplacementIdea",
    "SectionDecision",
    "TemplateFormat",
    "TemplateOutputProfile",
    "TemplateProvenance",
    "TemplateRecipe",
    "TemplateSection",
    "TemplateStatus",
    "TextLayer",
    "VisualEdit",
]
