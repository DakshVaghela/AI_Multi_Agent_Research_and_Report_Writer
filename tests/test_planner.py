import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
    
from backend.agents.planner import PlannerAgent

state = {
    "topic": "Impact of AI in Healthcare Diagnostics",
    "research_plan": [],
    "research_notes": [],
    "citations": [],
    "draft_report": "",
    "critique": "",
    "revision_count": 0,
    "final_report": "",
}

planner = PlannerAgent()

updated_state = planner.run(state)

print("\nResearch Plan:\n")

for item in updated_state["research_plan"]:
    print(item)