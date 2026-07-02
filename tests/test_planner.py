import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


import backend.agents.planner as planner_module
from backend.agents.planner import PlannerAgent
from backend.state.agent_state import ResearchState


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        return "\n".join(
            [
                "1. What are the main AI diagnostic tools used in healthcare?",
                "2. How accurate are AI diagnostic systems compared with clinicians?",
                "3. What are the risks of bias in AI healthcare diagnostics?",
                "4. How does AI affect diagnostic speed and patient outcomes?",
                "5. What regulations govern AI diagnostic tools?",
            ]
        )


planner_module.llm_service = FakeLLMService()


def test_planner_creates_research_plan():
    state = ResearchState(
        topic="Impact of AI in Healthcare Diagnostics"
    )

    planner = PlannerAgent()
    updated_state = planner.run(state)

    assert len(updated_state.research_plan) == 5
    assert updated_state.research_plan[0].startswith("1.")


if __name__ == "__main__":
    state = ResearchState(
        topic="Impact of AI in Healthcare Diagnostics"
    )

    planner = PlannerAgent()
    updated_state = planner.run(state)

    print("\nResearch Plan:\n")

    for item in updated_state.research_plan:
        print(item)
