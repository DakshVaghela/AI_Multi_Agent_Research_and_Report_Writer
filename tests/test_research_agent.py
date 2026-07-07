from backend.agents.planner import PlannerAgent
from backend.agents.researcher import ResearchAgent
from backend.state.agent_state import ResearchState


def test_research_agent():

    state = ResearchState(
        topic="Impact of AI in Healthcare Diagnostics"
    )

    planner = PlannerAgent()
    researcher = ResearchAgent()

    state = planner.run(state)
    state = researcher.run(state)

    assert len(state.research_notes) == 1

    note = state.research_notes[0]

    print("\n")
    print("=" * 80)
    print("SUB QUESTION")
    print("=" * 80)
    print(note.sub_question)

    print("\n")
    print("=" * 80)
    print("SOURCE")
    print("=" * 80)
    print(note.source_title)

    print("\n")
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(note.summary)

    print("\n")
    print("=" * 80)
    print("KEY POINTS")
    print("=" * 80)

    for point in note.key_points:
        print("-", point)