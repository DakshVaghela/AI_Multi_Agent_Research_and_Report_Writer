import threading
import uuid
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from backend.graph.workflow import research_workflow
from backend.models.report import Report
from backend.services.report_service import report_service
from backend.state.agent_state import ResearchState

OUTPUT_DIR = Path("outputs")


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    def __init__(self, job_id: str, topic: str):
        self.job_id = job_id
        self.topic = topic
        self.status = JobStatus.PENDING
        self.report: Optional[Report] = None
        self.error: Optional[str] = None
        self.pdf_path: Optional[Path] = None


_jobs: Dict[str, Job] = {}
_lock = threading.Lock()


def create_job(topic: str) -> Job:
    job = Job(job_id=str(uuid.uuid4()), topic=topic)
    with _lock:
        _jobs[job.job_id] = job
    return job


def get_job(job_id: str) -> Optional[Job]:
    with _lock:
        return _jobs.get(job_id)


def run_job(job_id: str) -> None:
    job = get_job(job_id)
    if job is None:
        return

    job.status = JobStatus.RUNNING

    try:
        state = ResearchState(topic=job.topic)
        final_state = research_workflow.run(state)

        report = final_state.final_report or final_state.draft_report
        if report is None:
            raise RuntimeError("Workflow completed without producing a report")

        OUTPUT_DIR.mkdir(exist_ok=True)
        pdf_path = OUTPUT_DIR / f"{job_id}.pdf"
        report_service.export_pdf(report=report, output_path=str(pdf_path))

        job.report = report
        job.pdf_path = pdf_path
        job.status = JobStatus.COMPLETED
    except Exception as exc:  # noqa: BLE001 - surface any workflow failure to the client
        job.error = str(exc)
        job.status = JobStatus.FAILED
