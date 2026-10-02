"""Experimental adaptive visual-cut proposals using PySceneDetect.

This finds candidate shot boundaries only. It does not infer story meaning,
recommend exclusions, or modify/split the source file.
"""
from __future__ import annotations

import uuid
from pathlib import Path

import scenedetect
from scenedetect import AdaptiveDetector, SceneManager, open_video

from ..models.source_description import SourceDescription
from .proposals import (
    AnalysisProposal,
    AnalysisWarning,
    MediaFacts,
    ProposedSection,
    ProposalBoundary,
)


class ShotBoundaryAnalysisError(Exception):
    """Raised when the source cannot produce a usable shot-boundary proposal."""


class AdaptiveShotBoundaryAnalyzer:
    """Local experimental adapter; thresholds are uncalibrated for this product."""

    producer_name = "pyscenedetect.adaptive"

    def analyze(self, source: SourceDescription) -> AnalysisProposal:
        if not Path(source.source_path).is_file():
            raise ShotBoundaryAnalysisError("The selected source file is unavailable.")
        if source.duration is None or not 0 < source.duration.value <= 30:
            raise ShotBoundaryAnalysisError("Analysis requires a readable video no longer than 30 seconds.")
        if source.video_stream is None:
            raise ShotBoundaryAnalysisError("The selected file has no readable video stream.")

        try:
            video = open_video(source.source_path, backend="pyav")
            manager = SceneManager()
            manager.add_detector(AdaptiveDetector())
            manager.detect_scenes(video=video, show_progress=False)
            scenes = manager.get_scene_list()
        except Exception as exc:
            raise ShotBoundaryAnalysisError("The video could not be analyzed. Keep using manual section editing.") from exc

        duration_ms = int(round(source.duration.value * 1000))
        cuts = [
            int(round(start.get_seconds() * 1000))
            for start, _end in scenes[1:]
            if 0 < start.get_seconds() * 1000 < duration_ms
        ]
        cuts = sorted(set(cuts))

        edges = [0, *cuts, duration_ms]
        sections = [
            ProposedSection(
                id=f"shot_{index + 1}",
                order=index,
                start_ms=start,
                end_ms=end,
            )
            for index, (start, end) in enumerate(zip(edges, edges[1:]))
            if end > start
        ]
        boundaries = [
            ProposalBoundary(id=f"cut_{index + 1}", at_ms=cut)
            for index, cut in enumerate(cuts)
        ]

        fps = source.fps_actual.value if source.fps_actual else None
        return AnalysisProposal(
            id=f"analysis_{uuid.uuid4().hex[:16]}",
            source_id=source.id,
            status="ready",
            producer_name=self.producer_name,
            producer_version=scenedetect.__version__,
            processing="local",
            media_facts=MediaFacts(
                duration_ms=duration_ms,
                width=source.video_stream.width,
                height=source.video_stream.height,
                frame_rate=fps if fps and fps > 0 else None,
                has_audio=bool(source.audio_streams),
            ),
            boundaries=boundaries,
            sections=sections,
            warnings=[
                AnalysisWarning(
                    code="shot_boundaries_are_not_story_sections",
                    message="These are unreviewed visual-cut candidates. They may split camera motion or miss edits; confirm, merge, or split them before saving.",
                ),
                AnalysisWarning(
                    code="detector_thresholds_not_calibrated",
                    message="The detector has not been evaluated on the product's annotated short-video set. No confidence score is claimed.",
                ),
            ],
        )

