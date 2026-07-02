from backend.services.llm_service import llm_service
from backend.state.agent_state import ResearchState


class PlannerAgent:

    SYSTEM_PROMPT = """
You are an expert research planner.

Given a research topic, create 5 clear sub-questions.

Return only a numbered list.
"""

    def run(self, state: ResearchState) -> ResearchState:

        response = llm_service.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=state.topic,
        )

        plan = []

        for line in response.split("\n"):
            line = line.strip()

            if line:
                plan.append(line)

        state.research_plan = plan
        return state
