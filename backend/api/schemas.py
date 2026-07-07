from typing import Optional

from pydantic import BaseModel

from backend.models.report import Report


class ReportRequest(BaseModel):
    topic: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    topic: str
    error: Optional[str] = None
    report: Optional[Report] = None
