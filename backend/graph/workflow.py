from langgraph.graph import END, START, StateGraph

from backend.graph.nodes import (
    critic_node,
    planner_node,
    researcher_node,
    writer_node,
)
from backend.graph.router import critic_router
from backend.state.agent_state import ResearchState


class ResearchWorkflow:

    def __init__(self):

        graph = StateGraph(ResearchState)

        graph.add_node("planner", planner_node)
        graph.add_node("researcher", researcher_node)
        graph.add_node("writer", writer_node)
        graph.add_node("critic", critic_node)

        graph.add_edge(START, "planner")

        graph.add_edge("planner", "researcher")

        graph.add_edge("researcher", "writer")

        graph.add_edge("writer", "critic")

        graph.add_conditional_edges(
            "critic",
            critic_router,
            {
                "writer": "writer",
                "end": END,
            },
        )

        self.workflow = graph.compile()

    def run(
        self,
        state: ResearchState,
    ) -> ResearchState:

        result = self.workflow.invoke(state)

        if isinstance(result, dict):
            return ResearchState(**result)

        return result


research_workflow = ResearchWorkflow()