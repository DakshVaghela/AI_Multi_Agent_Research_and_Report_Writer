from typing import List

from pydantic import BaseModel, Field
from pydantic import HttpUrl
from backend.models.citation import Citation


class ResearchNote(BaseModel):
    sub_question: str

    source_title: str

    summary: str

    key_points: List[str] = Field(default_factory=list)

    citations: List[Citation] = Field(default_factory=list)

    source_url: HttpUrl

    full_content: str