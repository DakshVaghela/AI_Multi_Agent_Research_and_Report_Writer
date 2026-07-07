from backend.models.review import Review
from backend.prompts.critic import CRITIC_SYSTEM_PROMPT
from backend.services.llm_service import llm_service
from backend.state.agent_state import ResearchState
from backend.utils.json_parser import parse_llm_json


class CriticAgent:
    """
    Reviews the generated report and stores feedback.
    The workflow engine (LangGraph) will decide whether to send the report
    back to the Writer Agent for another revision.
    """

    def review(self, report) -> Review:

        prompt = f"""
Title:
{report.title}

Executive Summary:
{report.executive_summary}

Introduction:
{report.introduction}

Main Discussion:
{report.main_content}

Conclusion:
{report.conclusion}
"""

        response = llm_service.generate(
            system_prompt=CRITIC_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.2,
            num_predict=4096,
            num_ctx=16384,
            json_mode=True,
        )

        data = parse_llm_json(response)

        return Review(**data)

    def run(
        self,
        state: ResearchState,
    ) -> ResearchState:
        from backend.config.settings import settings

        review = self.review(state.draft_report)

        state.critique = review.feedback

        if review.approved:
            state.final_report = state.draft_report
        else:
            state.revision_count += 1
            if state.revision_count >= settings.MAX_REVISIONS:
                state.final_report = state.draft_report

        return state