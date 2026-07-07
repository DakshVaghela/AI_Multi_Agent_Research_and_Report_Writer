from typing import List

from pydantic import BaseModel, Field

from backend.models.citation import Citation


class Report(BaseModel):
    title: str
    executive_summary: str
    introduction: str
    main_content: str
    conclusion: str

    references: List[Citation] = Field(default_factory=list)