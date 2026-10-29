"""
In-memory job manager for tracking long-running design generation tasks.

Stores jobs in a thread-safe dictionary. Each job tracks its current stage,
progress percentage, generated files, and any errors.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime
from typing import Optional

from app.schemas.design import JobInfo, JobStatus, JobStage


class JobManager:
    """Thread-safe in-memory job store."""

    def __init__(self):
        self._jobs: dict[str, JobInfo] = {}
        self._lock = threading.Lock()

    def create_job(self, design_id: str) -> JobInfo:
        """Create a new job and return it."""
        job_id = str(uuid.uuid4())
        job = JobInfo(
            job_id=job_id,
            design_id=design_id,
            status=JobStatus.PENDING,
            stage=JobStage.VALIDATING,
            progress=0.0,
            message="Job created",
            created_at=datetime.now().isoformat(),
        )
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[JobInfo]:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        stage: Optional[JobStage] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        files: Optional[dict[str, str]] = None,
    ) -> Optional[JobInfo]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            if status is not None:
                job.status = status
            if stage is not None:
                job.stage = stage
            if progress is not None:
                job.progress = progress
            if message is not None:
                job.message = message
            if error is not None:
                job.error = error
            if files is not None:
                job.files.update(files)
            return job

    def list_jobs(self) -> list[JobInfo]:
        with self._lock:
            return list(self._jobs.values())


# Global singleton
job_manager = JobManager()
