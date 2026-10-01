"""Tests for Block 1: Ingestion, Decode, Quality, and the async pipeline."""
from __future__ import annotations

import asyncio
import json
import os
from fractions import Fraction

import av
import numpy as np
import pytest

from videotemplate.ingestion.ingestor import Ingestor, IngestionError
from videotemplate.models.source_description import ProbeFailureState
from videotemplate.utils.confidence import ObservationState
from videotemplate.decode.decoder import Decoder, DecodeError
from videotemplate.quality.analyzer import QualityAnalyzer
from videotemplate.pipeline import (
    JOB_STATE_SCHEMA_VERSION,
    JobStatus,
    PipelineExecutor,
)


def create_simple_video(
    path: str,
    duration: float = 1.0,
    fps: float = 10.0,
    sar: Fraction | None = None,
) -> str:
    """
    Create a minimal test video with a moving square.

    Pass `sar` to request a non-square pixel aspect ratio; PyAV then reports both
    sample_aspect_ratio and display_aspect_ratio as `fractions.Fraction`.
    """
    fps_int = int(fps)
    container = av.open(path, mode="w")
    stream = container.add_stream("libx264", rate=Fraction(fps_int), time_base=Fraction(1, fps_int * 100))
    stream.width = 160
    stream.height = 120
    stream.pix_fmt = "yuv420p"
    if sar is not None:
        stream.sample_aspect_ratio = sar

    n_frames = int(duration * fps)

    for i in range(n_frames):
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        x = int((i / max(n_frames - 1, 1)) * 100)
        img[30:50, x:x + 20] = 255

        frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        frame.pts = i
        frame.time_base = stream.time_base
        for packet in stream.encode(frame):
            container.mux(packet)

    # Flush encoder
    for packet in stream.encode(None):
        container.mux(packet)

    container.close()
    return path


class TestIngestion:
    """Tests for Block 1, Layer 1 (Ingestion)."""

    @pytest.fixture
    def test_video(self, tmp_path):
        path = str(tmp_path / "test.mp4")
        return create_simple_video(path, duration=1.0, fps=10.0)

    def test_ingest_valid_video(self, test_video):
        """Ingesting a valid short video should produce a complete SourceDescription."""
        ingestor = Ingestor(max_duration=30.0)
        result = ingestor.ingest(test_video)

        assert result.id.startswith("src_")
        assert result.source_path == test_video
        assert result.container.format == "mp4"
        assert result.container.size_bytes > 0
        assert result.video_stream.codec in ("h264", "libx264", "mpeg4")
        assert result.video_stream.width == 160
        assert result.video_stream.height == 120
        assert result.duration.value > 0
        assert result.fps_actual.value > 0
        assert result.cfr_vfr.is_cfr is True
        assert result.audio_streams == []
        # Contract-level `extraction_status` was removed from Contract #1 (Stage 2 D-3);
        # per-group `state` now carries this information (Stage 2 §2.1.4 B).
        assert result.cfr_vfr.state == "extracted"

    def test_ingest_rejects_too_long(self, test_video):
        """A duration overrun is a RECORDED failure state, not an exception.

        MIGRATED in the G18/R-2 pass. This test used to assert
        `pytest.raises(IngestionError)`, which §2.1.9 line 412 already flagged for
        migration. Under §V.1 R-2 the outcome is recorded ON the group.

        NOTE: this asserts the R-2 representation, NOT `ingestion_status.status ==
        "rejected"` with a REJ_* reason. That is §2.1.5's contract-level gate and is a
        separate migration row (§2.1.9 line 409); it is deliberately not implemented here,
        because §V.1 specifies the group-level failure state and nothing more. The
        assertion below will be replaced, not deleted, when that row lands.
        """
        ingestor = Ingestor(max_duration=0.001)
        result = ingestor.ingest(test_video)

        assert result.container.probe_state == ProbeFailureState.REJECTED_BY_POLICY
        assert result.container.producer_state == ObservationState.UNAVAILABLE
        # Non-contract text: present for operators, never a state a consumer may branch on.
        assert "exceeds" in result.container.probe_detail.lower()
        # Groups the probe never reached stay ABSENT (§2.2 F.3.1 rule 2).
        assert result.video_stream is None

    def test_ingest_rejects_nonexistent(self):
        """Non-existent files should be rejected."""
        ingestor = Ingestor()
        with pytest.raises(IngestionError) as exc_info:
            ingestor.ingest("/nonexistent/path/video.mp4")
        assert "not found" in str(exc_info.value).lower()

    def test_ingest_optional_fields(self, test_video):
        """Optional fields may be populated when available."""
        ingestor = Ingestor(max_duration=30.0)
        result = ingestor.ingest(test_video)

        assert result.bit_depth is not None
        assert result.bit_depth.luma == 8
        assert result.color_space is not None
        assert result.chroma is not None
        assert result.chroma.subsampling == "4:2:0"
        assert result.quality_score.value is not None

    def test_cfr_detection(self, test_video):
        """
        CFR video must be classified appropriately AND report a real timing analysis.

        Regression: `cfr_vfr` was computed from a SECOND demux pass over the same container,
        which returns no packets — so every source was reported as state="uncertain" with
        confidence 0.5 and variance 0.0. Timing evidence is now collected once and shared.
        """
        ingestor = Ingestor(max_duration=30.0)
        result = ingestor.ingest(test_video)
        assert result.fps_actual.type in ("cfr", "vfr", "mixed")
        assert result.cfr_vfr.state == "extracted"
        assert result.cfr_vfr.confidence.value > 0.5
        assert result.cfr_vfr.variance >= 0.0

    def test_generational_estimate(self, test_video):
        """Generational estimate heuristic should produce a value."""
        ingestor = Ingestor(max_duration=30.0)
        result = ingestor.ingest(test_video)
        assert result.generational_estimate is not None
        assert result.generational_estimate.value in (
            "prosumer_phone", "dslr", "broadcast", "cinema", "unknown"
        )

    def test_ingest_preserves_provenance(self, test_video):
        """Every field should carry provenance per Stage 1 §6."""
        ingestor = Ingestor(max_duration=30.0)
        result = ingestor.ingest(test_video)

        assert result.container.provenance
        assert result.video_stream.provenance
        assert result.fps_actual.provenance
        assert result.cfr_vfr.provenance
        assert result.duration.provenance

    def test_duration_validation_30s_limit(self, tmp_path):
        """SourceDescription must enforce the 30-second limit from Stage 1 §1."""
        path = str(tmp_path / "short.mp4")
        create_simple_video(path, duration=0.5, fps=5.0)
        ingestor = Ingestor(max_duration=30.0)
        result = ingestor.ingest(path)
        assert result.duration.value <= 30.0

    def test_ingest_anamorphic_aspect_ratio(self, tmp_path):
        """
        Regression (audit B2): PyAV reports aspect ratios as `fractions.Fraction`, which
        is NOT subscriptable. Indexing it raised `TypeError: 'Fraction' object is not
        subscriptable` for any clip carrying SAR/DAR metadata — i.e. most real footage.
        """
        path = str(tmp_path / "anamorphic.mp4")
        create_simple_video(path, duration=1.0, fps=10.0, sar=Fraction(4, 3))

        result = Ingestor(max_duration=30.0).ingest(path)

        sar_num, sar_den = (int(part) for part in result.video_stream.sample_aspect_ratio.split(":"))
        assert abs(sar_num / sar_den - 4 / 3) < 0.01

        dar_num, dar_den = (int(part) for part in result.video_stream.display_aspect_ratio.split(":"))
        assert abs(dar_num / dar_den - 16 / 9) < 0.01

    def test_format_display_ratio_accepts_all_pyav_shapes(self):
        """`_format_display_ratio` must handle Fraction, tuple/list, None and junk."""
        assert Ingestor._format_display_ratio(Fraction(16, 9), fallback="0:1") == "16:9"
        assert Ingestor._format_display_ratio((4, 3), fallback="0:1") == "4:3"
        assert Ingestor._format_display_ratio([1, 1], fallback="0:1") == "1:1"
        assert Ingestor._format_display_ratio(None, fallback="0:1") == "0:1"
        assert Ingestor._format_display_ratio(Fraction(0, 1), fallback="0:1") == "0:1"
        assert Ingestor._format_display_ratio("garbage", fallback="0:1") == "0:1"

    def test_optional_groups_expose_state(self, test_video):
        """
        Stage 1 §9.1 (ABSENT-ALLOWED / UNCERTAIN-ALLOWED): every group that can be
        present-or-absent must expose `state`, so downstream can distinguish
        "looked for and not found" (absent) from "looked for, ambiguous" (uncertain).
        """
        result = Ingestor(max_duration=30.0).ingest(test_video)
        valid = {"extracted", "uncertain", "absent", "unavailable"}

        assert result.bit_depth.state in valid
        assert result.color_space.state in valid
        assert result.chroma.state in valid
        assert result.generational_estimate.state in valid
        assert result.quality_score.state in valid
        assert result.fps_actual.state in valid
        assert result.cfr_vfr.state in valid
        if result.transfer is not None:
            assert result.transfer.state in valid

        # The synthetic clip uses a well-known codec/pixel format → extracted
        assert result.color_space.state == "extracted"
        assert result.chroma.state == "extracted"
        assert result.generational_estimate.state == "extracted"
        # D-2: an estimate can never assert absence of generation
        assert result.generational_estimate.state != "absent"


class TestDecode:
    """Tests for Block 1, Layer 2 (Decode)."""

    @pytest.fixture
    def decoded(self, tmp_path):
        path = str(tmp_path / "test.mp4")
        create_simple_video(path, duration=1.0, fps=10.0)
        ingestor = Ingestor(max_duration=30.0)
        source = ingestor.ingest(path)
        decoder = Decoder(output_dir=str(tmp_path / "frames"))
        try:
            decoded = decoder.decode(source)
            return decoded, str(tmp_path)
        finally:
            decoder.cleanup()

    def test_decode_produces_frames(self, decoded):
        """Decode should produce a DecodedVideo with frames."""
        decoded_video, _ = decoded
        assert decoded_video.frame_count > 0
        assert decoded_video.width == 160
        assert decoded_video.height == 120
        assert len(decoded_video.pts) == decoded_video.frame_count
        assert decoded_video.duration > 0
        assert decoded_video.cfr_vfr in ("cfr", "vfr", "mixed")

    def test_decode_frames_exist(self, decoded):
        """Decoded frames should exist as PNG files."""
        decoded_video, tmp_path = decoded
        assert os.path.isdir(decoded_video.frames_ref)
        pngs = [f for f in os.listdir(decoded_video.frames_ref) if f.endswith(".png")]
        assert len(pngs) == decoded_video.frame_count

    def test_decode_confidence_envelope(self, decoded):
        """
        Stage 1 §6 — Contract #2 must carry confidence + provenance. The decoder used to
        compute both and then discard them, silently losing the boundary-crossing record.
        """
        decoded_video, _ = decoded

        assert 0.0 <= decoded_video.confidence.value <= 1.0
        assert decoded_video.state == "measured"
        assert decoded_video.uncertain_frames == []

        layers = [entry.layer.value for entry in decoded_video.provenance]
        assert "source_native" in layers
        assert "analysis_normalized" in layers

        # §6.1 Rule 5 — SOURCE-NATIVE → ANALYSIS-NORMALIZED crossing is lossless
        normalized = [e for e in decoded_video.provenance if e.layer.value == "analysis_normalized"]
        assert all(e.confidence_delta == 0.0 for e in normalized)

    def test_decode_keeps_source_cfr_vfr_verdict(self, decoded):
        """
        Stage 1 §4 — lower representations must never leak upward. A partial decode must
        NOT rewrite the source-native CFR/VFR verdict; it is reported via `state` instead.
        """
        decoded_video, _ = decoded
        assert decoded_video.cfr_vfr in ("cfr", "vfr", "mixed")
        assert decoded_video.cfr_vfr == "cfr"  # synthetic clip is constant frame rate

    def test_decode_pts_monotonic(self, decoded):
        """PTS values should be monotonically non-decreasing."""
        decoded_video, _ = decoded
        pts = decoded_video.pts
        for i in range(len(pts) - 1):
            assert pts[i] <= pts[i + 1]


class TestQuality:
    """Tests for Block 1, Layer 3 (Quality)."""

    @pytest.fixture
    def quality_report(self, tmp_path):
        path = str(tmp_path / "test.mp4")
        create_simple_video(path, duration=2.0, fps=10.0)
        ingestor = Ingestor(max_duration=30.0)
        source = ingestor.ingest(path)
        decoder = Decoder(output_dir=str(tmp_path / "frames"))
        try:
            decoded = decoder.decode(source)
            analyzer = QualityAnalyzer()
            report = analyzer.analyze(decoded, source)
            return report, decoded, source
        finally:
            decoder.cleanup()

    def test_quality_report_structure(self, quality_report):
        """QualityReport should have required fields per Stage 1 §8 Contract #3."""
        report, decoded, source = quality_report
        assert 0.0 <= report.score <= 1.0
        assert report.duration > 0
        assert report.state in ("extracted", "uncertain")
        assert report.extraction_status == "extracted"

    def test_quality_spatial_map(self, quality_report):
        """Spatial quality map should have per-frame scores."""
        report, decoded, source = quality_report
        assert report.spatial_quality_map is not None
        assert len(report.spatial_quality_map.frames) > 0
        for score in report.spatial_quality_map.frames:
            assert 0.0 <= score <= 1.0

    def test_quality_artifacts_list(self, quality_report):
        """Artifacts list should be valid (may be empty)."""
        report, decoded, source = quality_report
        assert isinstance(report.artifacts, list)
        for artifact in report.artifacts:
            assert 0.0 <= artifact.severity <= 1.0
            assert 0.0 <= artifact.confidence.value <= 1.0

    def test_quality_never_blocks(self, quality_report):
        """Quality analysis must always produce a report — never raises."""
        report, _, _ = quality_report
        assert report is not None

    def test_quality_evidence_envelope(self, quality_report):
        """
        Stage 1 §6 + §6.1 Rule 5 — Layer 3 must report its EVIDENCE source and the
        ANALYSIS-NORMALIZED → EVIDENCE cost of -0.05. Both were built and then discarded.
        """
        report, _, _ = quality_report

        assert report.source is not None
        assert report.source.layer.value == "evidence"
        assert report.source.tool == "numpy"

        assert report.provenance
        assert report.provenance[0].layer.value == "evidence"
        assert report.provenance[0].transform_type == "quality_analysis"
        assert report.provenance[0].confidence_delta == pytest.approx(-0.05)


def _drive(executor: PipelineExecutor, path: str, timeout: float = 120.0):
    """Submit a job and wait for terminal status inside ONE event loop."""
    async def run():
        job_id = await executor.submit(path)
        return job_id, await executor.wait(job_id, timeout=timeout)

    return asyncio.run(run())


class TestPipeline:
    """
    Stage 1 §9 Decision 2 (async job pipeline) and Decision 4 (selective persistence).

    Regression coverage for two audit defects that had none:
      B1 — `Decoder(work_dir=...)` made every job fail with a TypeError.
      B4 — `asyncio.run(executor.submit(...))` orphaned the job task, so jobs never
           progressed past PENDING.
    """

    def test_pipeline_completes_and_reclaims_frames(self, tmp_path):
        path = str(tmp_path / "test.mp4")
        create_simple_video(path, duration=1.0, fps=10.0)
        work_dir = tmp_path / "workspace"
        executor = PipelineExecutor(work_dir=str(work_dir))

        job_id, job = _drive(executor, path)

        assert job is not None, "job vanished from the executor"
        assert job.status == JobStatus.COMPLETED, job.error
        assert job.source_description is not None
        assert job.decoded_video is not None
        assert job.quality_report is not None

        # Decision 4 — SourceDescription/QualityReport persisted, frames deliberately not
        state_file = work_dir / "jobs" / f"{job_id}.json"
        assert state_file.exists()
        persisted = json.loads(state_file.read_text())
        assert persisted["schema_version"] == JOB_STATE_SCHEMA_VERSION
        assert "source_description" in persisted
        assert "quality_report" in persisted
        assert "decoded_video" not in persisted

        # Decision 4 — frames are heavy regenerable assets, reclaimed at job end
        assert not (work_dir / "frames" / job_id).exists()

    def test_pipeline_reports_failure_without_raising(self, tmp_path):
        work_dir = tmp_path / "workspace"
        executor = PipelineExecutor(work_dir=str(work_dir))

        _, job = _drive(executor, str(tmp_path / "does_not_exist.mp4"))

        assert job.status == JobStatus.FAILED
        assert "Ingestion error" in job.error

        # the failure path must not leak frames either
        frames_root = work_dir / "frames"
        assert not frames_root.exists() or not any(frames_root.iterdir())

    def test_recover_job_from_persisted_state(self, tmp_path):
        path = str(tmp_path / "test.mp4")
        create_simple_video(path, duration=1.0, fps=10.0)
        work_dir = tmp_path / "workspace"

        job_id, job = _drive(PipelineExecutor(work_dir=str(work_dir)), path)
        assert job.status == JobStatus.COMPLETED, job.error

        # A fresh executor is equivalent to a new process: recovers purely from disk
        recovered = PipelineExecutor(work_dir=str(work_dir)).recover_job(job_id)

        assert recovered is not None
        assert recovered.id == job_id
        assert recovered.status == JobStatus.COMPLETED
        assert recovered.source_description is not None
        assert recovered.quality_report is not None

    def test_recover_missing_job_returns_none(self, tmp_path):
        executor = PipelineExecutor(work_dir=str(tmp_path / "workspace"))
        assert executor.recover_job("job_does_not_exist") is None
