from typing import List

from pydantic import BaseModel, Field


class Summary(BaseModel):
    summary: str
    key_points: List[str] = Field(default_factory=list)