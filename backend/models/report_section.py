from pydantic import BaseModel


class ReportSection(BaseModel):
    section_title: str
    content: str