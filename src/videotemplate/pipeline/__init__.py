"""
Pipeline — Block 1 (Technical Foundation) + BLOCK 2/3 glue.

Per Stage 1 §2 and §10:
- Asynchronous job pipeline: ingest→decode→quality→analysis_parallel→fusion→semantic→dna→validate
- Each job persists intermediate state for recovery.
- Stage 1 implementation covers: ingest→decode→quality
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import time
import uuid
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..ingestion.ingestor import Ingestor
from ..decode.decoder import Decoder, DecodeError
from ..quality.analyzer import QualityAnalyzer
from ..models.source_description import SourceDescription, IngestionError
from ..models.decoded_video import DecodedVideo
from ..models.quality_report import QualityReport


class JobStatus(str, Enum):
    PENDING = "pending"
    INGESTING = "ingesting"
    DECODING = "decoding"
    ANALYZING_QUALITY = "analyzing_quality"
    COMPLETED = "completed"
    FAILED = "failed"


# §9 Decision 5 — persisted state is versioned so migrations stay explicit.
JOB_STATE_SCHEMA_VERSION = 1


@dataclass
class Job:
    """A pipeline job tracking the processing of a single video."""
    id: str
    input_path: str
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None

    # Intermediate results
    source_description: Optional[SourceDescription] = None
    decoded_video: Optional[DecodedVideo] = None
    quality_report: Optional[QualityReport] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "input_path": self.input_path,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }


class PipelineExecutor:
    """
    Executes the job pipeline asynchronously.
    Stage 1 covers: Ingestion → Decode → Quality
    """

    def __init__(self, work_dir: str = "workspace"):
        self.work_dir = work_dir
        self.jobs: dict[str, Job] = {}
        # asyncio holds only a WEAK reference to tasks, so an unreferenced task can be
        # garbage-collected mid-flight. Keep strong refs until each task finishes.
        self._tasks: set[asyncio.Task] = set()
        os.makedirs(work_dir, exist_ok=True)

    async def submit(self, video_path: str) -> str:
        """Submit a video for processing. Returns job_id immediately."""
        job_id = f"job_{uuid.uuid4().hex[:16]}"
        job = Job(id=job_id, input_path=video_path)
        self.jobs[job_id] = job
        self._persist_job_state(job)

        task = asyncio.create_task(self._run_job(job))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return job_id

    async def wait(self, job_id: str, timeout: float = 300.0, poll: float = 0.05) -> Optional[Job]:
        """
        Await a job's terminal status, yielding to the event loop while it runs.

        The job task must live inside the SAME event loop as the caller. Submitting with
        `asyncio.run(executor.submit(path))` and then polling from outside the loop leaves
        the task orphaned — asyncio.run() cancels pending tasks when it closes the loop —
        so the job would stay PENDING forever. See cli._drive_pipeline.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.jobs.get(job_id)
            if job is None or job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return job
            await asyncio.sleep(poll)
        return self.jobs.get(job_id)

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job status and results."""
        return self.jobs.get(job_id)

    async def _run_job(self, job: Job):
        """Execute the pipeline stages for a job."""
        job.status = JobStatus.INGESTING
        job.started_at = time.time()
        self._persist_job_state(job)

        decoder: Optional[Decoder] = None

        try:
            # Stage 2: Ingestion
            ingestor = Ingestor(max_duration=30.0)
            source = ingestor.ingest(job.input_path)
            job.source_description = source
            self._persist_job_state(job)

            job.status = JobStatus.DECODING
            self._persist_job_state(job)

            # Stage 3: Decode
            decoder = Decoder(output_dir=self._job_frames_dir(job.id))
            decoded = decoder.decode(source)
            job.decoded_video = decoded
            self._persist_job_state(job)
            # NOTE: decoder.cleanup() deliberately runs in the outer `finally` below.
            # Calling it here would delete the frames *before* the Quality stage reads
            # them whenever the Decoder owns its temp directory.

            job.status = JobStatus.ANALYZING_QUALITY
            self._persist_job_state(job)

            # Stage 4: Quality
            analyzer = QualityAnalyzer()
            quality = analyzer.analyze(decoded, source)
            job.quality_report = quality
            self._persist_job_state(job)

            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()

        except IngestionError as exc:
            job.status = JobStatus.FAILED
            job.error = f"Ingestion error: {exc}"
            job.completed_at = time.time()
        except DecodeError as exc:
            job.status = JobStatus.FAILED
            job.error = f"Decode error: {exc}"
            job.completed_at = time.time()
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = f"Unexpected error: {exc}"
            job.completed_at = time.time()
        finally:
            # Runs after EVERY stage, success or failure, so frames stay available for the
            # whole pipeline (Quality reads them) and are only released at the end.
            if decoder is not None:
                decoder.cleanup()
            # §9 Decision 4 — decoded frames are heavy, regenerable assets: never
            # persisted, and reclaimed here. Quality analysis has already consumed them
            # on the success path, and they are re-creatable from the source file. This
            # runs on the failure path too, so a crashed job cannot leak disk.
            self._cleanup_job_frames(job.id)

        self._persist_job_state(job)

    def _job_frames_dir(self, job_id: str) -> str:
        return os.path.join(self.work_dir, "frames", job_id)

    def _cleanup_job_frames(self, job_id: str) -> None:
        """Delete the per-job frame directory (regenerable, never persisted)."""
        frames_dir = self._job_frames_dir(job_id)
        if os.path.isdir(frames_dir):
            shutil.rmtree(frames_dir, ignore_errors=True)

    def _persist_job_state(self, job: Job):
        """Persist job state for recovery (Stage 1 §9.4 - selective persistence)."""
        state_file = os.path.join(self.work_dir, "jobs", f"{job.id}.json")
        os.makedirs(os.path.dirname(state_file), exist_ok=True)

        state = job.to_dict()
        state["schema_version"] = JOB_STATE_SCHEMA_VERSION
        # Persist intermediate results if present
        if job.source_description:
            state["source_description"] = job.source_description.model_dump(mode="json")
        if job.quality_report:
            state["quality_report"] = job.quality_report.model_dump(mode="json")
        # Don't persist DecodedVideo (frames ref is temp)

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def recover_job(self, job_id: str) -> Optional[Job]:
        """Recover a job from persisted state."""
        state_file = os.path.join(self.work_dir, "jobs", f"{job_id}.json")
        if not os.path.exists(state_file):
            return None

        with open(state_file) as f:
            state = json.load(f)

        # §9 Decision 5 — never silently reinterpret state written by a newer schema.
        version = state.get("schema_version", JOB_STATE_SCHEMA_VERSION)
        if version > JOB_STATE_SCHEMA_VERSION:
            warnings.warn(
                f"Job state {job_id} was written with schema v{version}, "
                f"but this build understands v{JOB_STATE_SCHEMA_VERSION}; "
                f"unknown fields will be ignored.",
                RuntimeWarning,
                stacklevel=2,
            )

        job = Job(
            id=state["id"],
            input_path=state["input_path"],
            status=JobStatus(state["status"]),
            created_at=state["created_at"],
            started_at=state.get("started_at"),
            completed_at=state.get("completed_at"),
            error=state.get("error"),
        )

        if "source_description" in state:
            job.source_description = SourceDescription(**state["source_description"])
        if "quality_report" in state:
            job.quality_report = QualityReport(**state["quality_report"])

        self.jobs[job_id] = job
        return job
