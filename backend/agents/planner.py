from backend.services.llm_service import llm_service
from backend.state.agent_state import ResearchState
from backend.prompts.planner import PLANNER_SYSTEM_PROMPT


class PlannerAgent:

    def run(self, state: ResearchState) -> ResearchState:

        response = llm_service.generate(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=state.topic,
        )

        plan = []

        for line in response.split("\n"):
            line = line.strip()

            if line:
                plan.append(line)

        state.research_plan = plan
        return state
