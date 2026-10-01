"""
QualityAnalyzer — Block 1, Layer 3 (Quality).

Determines signal reliability from DecodedVideo + SourceDescription.
Always produces a QualityReport, even if low quality. Never blocks pipeline.

Per Stage 1 §3: QualityReport always produced, even if low quality.
"""
from __future__ import annotations

import os
import numpy as np

from ..models.source_description import SourceDescription
from ..models.decoded_video import DecodedVideo
from ..models.quality_report import Artifact, QualityReport, SpatialQualityMap
from ..utils.confidence import Confidence, ConfidenceType, ProvenanceEntry, SourceInfo, SourceLayer


class QualityAnalyzer:
    """Analyzes decoded video for quality artifacts and signal reliability."""

    # Thresholds for blur detection (Laplacian variance)
    BLUR_THRESHOLD = 100.0

    # Threshold for blocking artifacts
    BLOCKING_THRESHOLD = 0.15

    # Frame sampling for quality analysis
    MAX_ANALYSIS_FRAMES = 50

    def analyze(self, decoded: DecodedVideo, source: SourceDescription) -> QualityReport:
        """
        Analyze decoded frames for quality issues.
        Produces a QualityReport with artifacts, spatial quality map, and overall score.
        """
        # Layer tag is EVIDENCE: quality metrics are derived evidence, not media. `tool` is
        # "numpy" — the previous "numpy-opencv" was misleading (no OpenCV is used here).
        source_info = SourceInfo(layer=SourceLayer.EVIDENCE, tool="numpy")

        frames = self._load_sample_frames(decoded, source)
        frame_qualities = self._compute_frame_qualities(frames, decoded)

        artifacts = self._detect_artifacts(frames, decoded, source)

        # Overall quality score.
        # D-2 (Stage 2 §2.1.13): `SourceDescription.quality_score` is a SEALED ingestion-time
        # source-native hint and must NOT be mathematically chained into this authoritative
        # score. The authoritative score is computed from decoded frames only; the hint is
        # recorded as evidence below. (Previously: 0.6*frames + 0.4*source_hint.)
        if frame_qualities:
            overall_score = float(np.mean(frame_qualities))
        else:
            overall_score = 0.0

        source_quality_hint = source.quality_score.value if source.quality_score else None

        # Spatial quality map reference
        spatial_map = SpatialQualityMap(
            ref=decoded.frames_ref,
            frames=[round(q, 4) for q in frame_qualities],
            confidence=Confidence(
                value=0.85,
                type=ConfidenceType.MEASURED,
                calibration=0.85,
            ),
        )

        provenance = [
            ProvenanceEntry(
                layer=SourceLayer.EVIDENCE,
                evidence_refs=["decoded_frames", "quality_heuristics"],
                transform_type="quality_analysis",
                # Stage 1 §6.1 Rule 5 — ANALYSIS-NORMALIZED → EVIDENCE costs -0.05.
                confidence_delta=-0.05,
            )
        ]

        # D-2 (Stage 2 §2.1.13) — the sealed ingestion hint is RECORDED as prior evidence but is
        # deliberately not blended into the authoritative score. Re-admitting it as an explicit
        # input is a Stage 4 decision, not an implicit one.
        if source_quality_hint is not None:
            provenance.append(
                ProvenanceEntry(
                    layer=SourceLayer.SOURCE_NATIVE,
                    evidence_refs=["source.quality_score"],
                    transform_type="hint_recorded_not_chained",
                    confidence_delta=0.0,
                )
            )

        # Generational estimate reference
        gen_ref = None
        if source.generational_estimate:
            gen_ref = source.generational_estimate.value

        return QualityReport(
            score=round(overall_score, 4),
            state="extracted" if frames else "uncertain",
            duration=decoded.duration,
            confidence=Confidence(
                value=0.80 if frames else 0.5,
                type=ConfidenceType.MEASURED,
                calibration=0.85,
            ),
            artifacts=artifacts,
            spatial_quality_map=spatial_map,
            generational_estimate_ref=gen_ref,
            # extraction_status must agree with `state`: no sampled frames means the
            # analysis ran but produced nothing trustworthy (§9.1).
            extraction_status="extracted" if frames else "uncertain",
            # §6 envelope — previously built and then discarded
            source=source_info,
            provenance=provenance,
        )

    def _load_sample_frames(self, decoded: DecodedVideo, source: SourceDescription) -> list[np.ndarray]:
        """Load a sample of frames for quality analysis."""
        frames = []
        frames_dir = decoded.frames_ref

        if not os.path.isdir(frames_dir):
            return frames

        all_frames = sorted(
            f for f in os.listdir(frames_dir) if f.endswith(".png")
        )

        if not all_frames:
            return frames

        # Sample frames evenly
        step = max(1, len(all_frames) // self.MAX_ANALYSIS_FRAMES)
        sampled = all_frames[::step][:self.MAX_ANALYSIS_FRAMES]

        import imageio.v3 as iio
        for fname in sampled:
            try:
                img = iio.imread(os.path.join(frames_dir, fname))
                frames.append(img)
            except Exception:
                continue

        return frames

    def _compute_frame_qualities(self, frames: list[np.ndarray], decoded: DecodedVideo) -> list[float]:
        """Compute quality score per frame based on sharpness, noise, and artifacts."""
        qualities = []

        for frame in frames:
            score = self._frame_quality(frame)
            qualities.append(score)

        return qualities

    def _frame_quality(self, frame: np.ndarray) -> float:
        """
        Compute a quality score (0–1) for a single frame.
        Combines: sharpness (Laplacian variance), noise level, and saturation.
        """
        # Convert to grayscale if needed
        if len(frame.shape) == 3 and frame.shape[2] >= 3:
            gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])
        else:
            gray = frame

        # Sharpness: Laplacian variance — higher = sharper
        laplacian_var = self._laplacian_variance(gray)
        sharpness_score = min(1.0, laplacian_var / self.BLUR_THRESHOLD)

        # Noise: standard deviation of high-frequency residuals
        noise_score = self._noise_estimate(gray)

        # Saturation: std of color channels (if color)
        sat_score = 0.5
        if len(frame.shape) == 3 and frame.shape[2] >= 3:
            r, g, b = frame[..., 0].astype(np.float32), frame[..., 1].astype(np.float32), frame[..., 2].astype(np.float32)
            mean_rgb = (r + g + b) / 3.0
            # Avoid division by zero
            mask = mean_rgb > 1
            if mask.sum() > 0:
                saturation = np.sqrt(
                    ((r - mean_rgb)**2 + (g - mean_rgb)**2 + (b - mean_rgb)**2) / 3.0
                )
                sat_score = min(1.0, float(np.mean(saturation[mask]) / 50.0) if mask.sum() > 0 else 0.5)
            else:
                sat_score = 0.5

        # Combined quality score
        score = (sharpness_score * 0.5 + (1.0 - noise_score) * 0.3 + sat_score * 0.2)
        return round(max(0.0, min(1.0, score)), 4)

    @staticmethod
    def _laplacian_variance(gray: np.ndarray) -> float:
        """Compute Laplacian variance as a sharpness measure."""
        # Simple kernel-based Laplacian
        if gray.shape[0] < 3 or gray.shape[1] < 3:
            return 0.0

        # Use numpy-based Laplacian approximation
        padded = np.pad(gray.astype(np.float32), 1, mode="edge")
        laplacian = (
            padded[2:, 1:-1] + padded[:-2, 1:-1] + padded[1:-1, 2:] + padded[1:-1, :-2]
            - 4 * padded[1:-1, 1:-1]
        )
        return float(np.var(laplacian))

    @staticmethod
    def _noise_estimate(gray: np.ndarray) -> float:
        """
        Estimate noise level via local standard deviation of high-frequency residuals.
        Returns 0.0 (no noise) to 1.0 (high noise).
        """
        if gray.shape[0] < 5 or gray.shape[1] < 5:
            return 0.0

        # Compute local noise estimate via median absolute deviation
        # on high-pass filtered image
        padded = np.pad(gray.astype(np.float32), 2, mode="edge")
        # Simple high-pass: pixel - local mean
        kernel = np.ones((3, 3)) / 9.0
        local_mean = np.zeros_like(gray, dtype=np.float32)
        for i in range(3):
            for j in range(3):
                local_mean += padded[i:i + gray.shape[0], j:j + gray.shape[1]]

        high_pass = gray.astype(np.float32) - local_mean

        # Noise = std of high-pass residuals
        noise = float(np.std(high_pass))
        # Normalize: typical video noise std is 5-20 for 8-bit
        normalized = min(1.0, noise / 30.0)
        return normalized

    def _detect_artifacts(self, frames: list[np.ndarray], decoded: DecodedVideo, source: SourceDescription) -> list[Artifact]:
        """Detect common video artifacts."""
        artifacts = []

        if not frames:
            return artifacts

        # Blur detection
        blur_frames = []
        for i, frame in enumerate(frames):
            if len(frame.shape) == 3 and frame.shape[2] >= 3:
                gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])
            else:
                gray = frame
            lap_var = self._laplacian_variance(gray)
            if lap_var < self.BLUR_THRESHOLD:
                blur_frames.append(i)

        if blur_frames:
            blur_ratio = len(blur_frames) / len(frames)
            artifacts.append(Artifact(
                type="blur",
                severity=round(blur_ratio, 4),
                confidence=Confidence(
                    value=0.85,
                    type=ConfidenceType.DETECTION,
                    calibration=0.85,
                ),
            ))

        # Blocking detection (DCT-based codecs)
        if source.video_stream.codec in ("h264", "h265", "hevc", "mpeg2", "mpeg4"):
            blocking_score = self._detect_blocking(frames)
            if blocking_score > self.BLOCKING_THRESHOLD:
                artifacts.append(Artifact(
                    type="blocking",
                    severity=round(blocking_score, 4),
                    confidence=Confidence(
                        value=0.90,
                        type=ConfidenceType.DETECTION,
                        calibration=0.80,
                    ),
                ))

        # Banding detection
        banding_score = self._detect_banding(frames)
        if banding_score > 0.15:
            artifacts.append(Artifact(
                type="banding",
                severity=round(banding_score, 4),
                confidence=Confidence(
                    value=0.80,
                    type=ConfidenceType.DETECTION,
                    calibration=0.75,
                ),
            ))

        return artifacts

    @staticmethod
    def _detect_blocking(frames: list[np.ndarray]) -> float:
        """
        Detect blocking artifacts by checking for grid patterns in pixel differences.
        Returns 0.0–1.0 where higher = more blocking.
        """
        scores = []
        for frame in frames:
            if len(frame.shape) == 3 and frame.shape[2] >= 3:
                gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)
            else:
                gray = frame.astype(np.float32)

            # Check for discontinuities at block boundaries (16x16)
            block_size = 16
            h, w = gray.shape
            total_discontinuity = 0.0
            total_checked = 0

            # Horizontal block boundaries
            y = block_size
            while y < h - 1:
                diff = np.abs(gray[y, :] - gray[y - 1, :])
                total_discontinuity += float(np.mean(diff))
                total_checked += 1
                y += block_size

            # Vertical block boundaries
            x = block_size
            while x < w - 1:
                diff = np.abs(gray[:, x] - gray[:, x - 1])
                total_discontinuity += float(np.mean(diff))
                total_checked += 1
                x += block_size

            if total_checked > 0:
                avg_disc = total_discontinuity / total_checked
                # Normalize against frame's average gradient
                avg_gradient = float(np.mean(np.abs(np.diff(gray, axis=0)))) + 1e-8
                scores.append(min(1.0, avg_disc / (avg_gradient * 3.0)))

        return float(np.mean(scores)) if scores else 0.0

    @staticmethod
    def _detect_banding(frames: list[np.ndarray]) -> float:
        """
        Detect banding artifacts by checking for low local color variance in gradients.
        Returns 0.0–1.0 where higher = more banding.
        """
        scores = []
        for frame in frames:
            if len(frame.shape) == 3 and frame.shape[2] >= 3:
                gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)
            else:
                gray = frame.astype(np.float32)

            h, w = gray.shape

            # Sample horizontal strips and check for banding
            bands_found = 0
            total_strips = 0
            strip_height = max(1, h // 20)

            for y in range(0, h - strip_height, strip_height):
                strip = gray[y:y + strip_height, :]
                # Compute std along vertical direction within the strip
                if strip.shape[0] > 1:
                    std_along_y = np.std(strip, axis=0)
                    mean_std = float(np.mean(std_along_y))
                    if mean_std < 2.0:  # Low variance = potential banding
                        bands_found += 1
                    total_strips += 1

            if total_strips > 0:
                scores.append(bands_found / total_strips)

        return float(np.mean(scores)) if scores else 0.0
