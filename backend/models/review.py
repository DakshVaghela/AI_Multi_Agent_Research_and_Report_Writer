from pydantic import BaseModel


class Review(BaseModel):
    approved: bool
    feedback: str