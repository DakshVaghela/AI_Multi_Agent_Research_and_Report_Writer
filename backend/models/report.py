from typing import List

from pydantic import BaseModel

from backend.models.citation import Citation


class Report(BaseModel):
    title: str
    executive_summary: str = ""
    introduction: str = ""
    body: str = ""
    conclusion: str = ""
    references: List[Citation] = []