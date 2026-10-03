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
    ComponentFinding,
    MediaFacts,
    ProposedShotSpan,
    ProposalBoundary,
    SignalReport,
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
        shot_spans = [
            ProposedShotSpan(
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
        producer_version = scenedetect.__version__
        has_audio = bool(source.audio_streams)
        components = [
            ComponentFinding(
                id=f"component_shot_{shot.order + 1}",
                track="visual",
                kind="shot",
                start_ms=shot.start_ms,
                end_ms=shot.end_ms,
                label=f"Visual shot {shot.order + 1}",
                summary="A visual span between candidate cut points. Story role and replaceable content were not analyzed.",
                origin="detector",
                provider_name=self.producer_name,
                provider_version=producer_version,
                processing="local",
            )
            for shot in shot_spans
        ]
        audio_state = "not-run" if has_audio else "unsupported"
        audio_note = None if has_audio else "The source has no audio stream."
        signal_reports = [
            SignalReport(
                signal="technical-facts",
                state="completed",
                calibration="not-applicable",
                provider_name="videotemplate.ingestion",
                provider_version="0.1.0",
                processing="local",
                evidence_count=1,
            ),
            SignalReport(
                signal="shot-boundaries",
                state="completed",
                calibration="not-evaluated",
                provider_name=self.producer_name,
                provider_version=producer_version,
                processing="local",
                evidence_count=len(boundaries),
                note="Detector output has not been calibrated on the product corpus.",
            ),
            SignalReport(signal="people-and-subjects", state="not-run", calibration="not-evaluated", note="People/subject tracks are not identified by this cut-only prototype; no person identity is inferred."),
            SignalReport(signal="objects-and-actions", state="not-run", calibration="not-evaluated", note="Objects and actions are not identified by this cut-only prototype."),
            SignalReport(signal="setting-and-background", state="not-run", calibration="not-evaluated", note="Scene setting and background elements are not identified by this cut-only prototype."),
            SignalReport(signal="camera-and-layout", state="not-run", calibration="not-evaluated", note="Camera motion, framing, split-screen, and overlay layout are not identified by this cut-only prototype."),
            SignalReport(signal="on-screen-text", state="not-run", calibration="not-evaluated", note="OCR has not run."),
            SignalReport(signal="speech", state=audio_state, calibration="not-evaluated", note=audio_note or "Speech recognition has not run."),
            SignalReport(signal="music-and-sound", state=audio_state, calibration="not-evaluated", note=audio_note or "Music, sound effects, silence, and beat analysis have not run."),
            SignalReport(signal="creative-beats", state="not-run", calibration="not-evaluated", note="Hook, setup, action, reaction, reveal, payoff, CTA, and tutorial roles are not inferred."),
            SignalReport(signal="source-integrity", state="not-run", calibration="not-evaluated", note="Partial starts/ends, black frames, freezes, and abrupt endings are not evaluated."),
        ]
        return AnalysisProposal(
            id=f"analysis_{uuid.uuid4().hex[:16]}",
            source_id=source.id,
            status="partial",
            scope="shot-boundaries-only",
            producer_name=self.producer_name,
            producer_version=producer_version,
            processing="local",
            media_facts=MediaFacts(
                duration_ms=duration_ms,
                width=source.video_stream.width,
                height=source.video_stream.height,
                frame_rate=fps if fps and fps > 0 else None,
                has_audio=has_audio,
            ),
            boundaries=boundaries,
            shot_spans=shot_spans,
            components=components,
            signal_reports=signal_reports,
            warnings=[
                AnalysisWarning(
                    code="shot_boundaries_are_not_story_sections",
                    message="These are unreviewed visual-cut candidates. They may split camera motion or miss edits; confirm, merge, or split them before saving.",
                ),
                AnalysisWarning(
                    code="detector_thresholds_not_calibrated",
                    message="The detector has not been evaluated on the product's annotated short-video set. No confidence score is claimed.",
                ),
                AnalysisWarning(
                    code="component_inventory_incomplete",
                    message="This is only a visual-cut pass, not the full component analysis needed to build a reusable template. The signal report lists analyses that were not run.",
                ),
            ],
        )
