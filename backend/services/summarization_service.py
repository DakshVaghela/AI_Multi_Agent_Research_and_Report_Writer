import json

from backend.models.summary import Summary
from backend.prompts.summarizer import SUMMARIZER_SYSTEM_PROMPT
from backend.services.llm_service import llm_service
from backend.utils.json_parser import parse_llm_json

class SummarizationService:
    """
    Summarizes extracted article content into structured notes.
    """

    def summarize(self, article: str) -> Summary:

        prompt = f"""
Article:

{article[:12000]}

Return ONLY valid JSON in this format:

{{
    "summary": "...",
    "key_points": [
        "...",
        "...",
        "..."
    ]
}}
"""

        response = llm_service.generate(
            system_prompt=SUMMARIZER_SYSTEM_PROMPT,
            user_prompt=prompt,
            num_ctx=16384,
            json_mode=True,
        )

        try:
            data = parse_llm_json(response)
            return Summary(**data)

        except Exception:
            return Summary(
                summary=response,
                key_points=[],
            )


summarization_service = SummarizationService()