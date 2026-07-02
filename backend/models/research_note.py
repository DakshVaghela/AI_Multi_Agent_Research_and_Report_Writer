from typing import List

from pydantic import BaseModel

from backend.models.citation import Citation


class ResearchNote(BaseModel):
    sub_question: str
    summary: str
    key_points: List[str] = []
    citations: List[Citation] = []