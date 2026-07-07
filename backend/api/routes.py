from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from backend.api import jobs
from backend.api.schemas import JobStatusResponse, ReportRequest

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _to_response(job: jobs.Job) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        topic=job.topic,
        error=job.error,
        report=job.report,
    )


@router.post("", response_model=JobStatusResponse, status_code=202)
def create_report(request: ReportRequest, background_tasks: BackgroundTasks):
    job = jobs.create_job(topic=request.topic)
    background_tasks.add_task(jobs.run_job, job.job_id)
    return _to_response(job)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_report(job_id: str):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_response(job)


@router.get("/{job_id}/pdf")
def download_report_pdf(job_id: str):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != jobs.JobStatus.COMPLETED or job.pdf_path is None:
        raise HTTPException(status_code=409, detail="Report is not ready yet")

    return FileResponse(
        path=job.pdf_path,
        media_type="application/pdf",
        filename=f"{job.topic[:50] or 'report'}.pdf",
    )
