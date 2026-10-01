"""
CLI entry point for the Template DNA Builder.

Usage:
    python -m videotemplate.cli ingest <video_path>
    python -m videotemplate.cli run <video_path>    # full pipeline
    python -m videotemplate.cli status <job_id>
    python -m videotemplate.cli recover <job_id>
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time

from .ingestion.ingestor import Ingestor
from .pipeline import Job, JobStatus, PipelineExecutor


def cmd_ingest(path: str):
    """Run ingestion only and print SourceDescription."""
    ingestor = Ingestor(max_duration=30.0)
    try:
        source = ingestor.ingest(path)
        print(json.dumps(source.model_dump(mode="json"), indent=2, default=str))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


async def _drive_pipeline(path: str, timeout: float = 300.0) -> tuple[PipelineExecutor, str, Job | None]:
    """
    Submit a job and drive it to completion inside a SINGLE event loop.

    `asyncio.run(executor.submit(path))` looks equivalent but is not: asyncio.run()
    closes the loop (cancelling pending tasks) as soon as submit() returns, orphaning the
    job task so the job stays PENDING forever. Keeping submit() and the polling inside one
    loop is what makes the async job model (Stage 1 §9, Decision 2) actually work.
    """
    executor = PipelineExecutor()
    job_id = await executor.submit(path)
    print(f"Job submitted: {job_id}")
    print(f"Poll with: python -m videotemplate.cli status {job_id}")

    deadline = time.monotonic() + timeout
    last_status = None
    while time.monotonic() < deadline:
        job = executor.get_job(job_id)
        if job is None:
            return executor, job_id, None
        # Honest progress: report the stage name on every transition, never a fake %.
        if job.status != last_status:
            last_status = job.status
            print(f"[{job.status.value}] {job.error or 'processing...'}")
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
            break
        await asyncio.sleep(0.25)

    return executor, job_id, executor.get_job(job_id)


def cmd_run(path: str):
    """Run the full Block 1 pipeline (ingest → decode → quality)."""
    executor, job_id, job = asyncio.run(_drive_pipeline(path))
    if job is None:
        print("ERROR: Job not found", file=sys.stderr)
        sys.exit(1)

    if job.source_description:
        print("\n=== SourceDescription ===")
        print(json.dumps(job.source_description.model_dump(mode="json"), indent=2, default=str))
    if job.quality_report:
        print("\n=== QualityReport ===")
        print(json.dumps(job.quality_report.model_dump(mode="json"), indent=2, default=str))

    if job.status != JobStatus.COMPLETED:
        print(f"\nERROR: Job {job_id} ended as {job.status.value}", file=sys.stderr)
        sys.exit(1)


def cmd_status(job_id: str):
    """Check job status."""
    executor = PipelineExecutor()
    job = executor.recover_job(job_id)
    if job is None:
        # Also check in-memory jobs
        job = executor.get_job(job_id)
    if job is None:
        print(f"Job {job_id} not found")
        sys.exit(1)
    print(json.dumps(job.to_dict(), indent=2, default=str))


def cmd_recover(job_id: str):
    """Recover a job from persisted state."""
    executor = PipelineExecutor()
    job = executor.recover_job(job_id)
    if job is None:
        print(f"Job {job_id} not found in persisted state")
        sys.exit(1)
    print(f"Recovered job: {job.id}")
    print(f"Status: {job.status.value}")
    if job.source_description:
        print("SourceDescription available")
    if job.quality_report:
        print("QualityReport available")
    if job.error:
        print(f"Error: {job.error}")


def main():
    parser = argparse.ArgumentParser(
        description="Template DNA Builder — video to structured template representation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_ingest = subparsers.add_parser("ingest", help="Run ingestion only")
    p_ingest.add_argument("path", help="Path to video file")

    p_run = subparsers.add_parser("run", help="Run full Block 1 pipeline")
    p_run.add_argument("path", help="Path to video file")

    p_status = subparsers.add_parser("status", help="Check job status")
    p_status.add_argument("job_id", help="Job ID")

    p_recover = subparsers.add_parser("recover", help="Recover a job")
    p_recover.add_argument("job_id", help="Job ID")

    args = parser.parse_args()
    commands = {
        "ingest": lambda: cmd_ingest(args.path),
        "run": lambda: cmd_run(args.path),
        "status": lambda: cmd_status(args.job_id),
        "recover": lambda: cmd_recover(args.job_id),
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
