from typing import List, TypedDict


class ResearchState(TypedDict):
    topic: str

    research_plan: List[str]

    research_notes: List[str]

    citations: List[dict]

    draft_report: str

    critique: str

    revision_count: int

    final_report: str