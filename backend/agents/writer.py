from backend.models.report import Report
from backend.prompts.writer import WRITER_SYSTEM_PROMPT
from backend.services.llm_service import llm_service
from backend.state.agent_state import ResearchState
from backend.utils.json_parser import parse_llm_json


class WriterAgent:
    """
    Generates a research report from research notes.
    Can also improve an existing report using critic feedback.
    """

    def run(
        self,
        state: ResearchState,
        feedback: str = "",
    ) -> ResearchState:

        notes = ""

        for index, note in enumerate(state.research_notes, start=1):

            key_points = "\n".join(
                f"- {point}" for point in note.key_points
            )

            notes += f"""
Research Note {index}

Question:
{note.sub_question}

Summary:
{note.summary}

Key Points:
{key_points}

"""

        prompt = f"""
Research Notes

{notes}

Reviewer Feedback

{feedback}

Instructions:

- If reviewer feedback is empty, generate the first draft.
- Otherwise improve the report according to the reviewer feedback.
"""

        response = llm_service.generate(
            system_prompt=WRITER_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.2,
            num_predict=8192,
            num_ctx=16384,
            json_mode=True,
        )
        
        data = parse_llm_json(response)

        report = Report(
            **data,
            references=state.citations,
        )

        state.draft_report = report

        return state