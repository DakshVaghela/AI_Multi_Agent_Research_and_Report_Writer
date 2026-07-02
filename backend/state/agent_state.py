from typing import List

from pydantic import BaseModel, Field

from backend.models.citation import Citation
from backend.models.report import Report
from backend.models.research_note import ResearchNote


class ResearchState(BaseModel):
    topic: str

    research_plan: List[str] = Field(default_factory=list)

    research_notes: List[ResearchNote] = Field(default_factory=list)

    citations: List[Citation] = Field(default_factory=list)

    draft_report: Report | None = None

    critique: str = ""

    revision_count: int = 0

    final_report: Report | None = None