from datetime import datetime

from pydantic import BaseModel, HttpUrl


class Citation(BaseModel):
    title: str
    url: HttpUrl
    source: str
    snippet: str = ""
    retrieved_at: datetime = datetime.now()