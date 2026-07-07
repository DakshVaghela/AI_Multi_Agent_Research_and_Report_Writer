from backend.agents.critic import CriticAgent
from backend.agents.planner import PlannerAgent
from backend.agents.researcher import ResearchAgent
from backend.agents.writer import WriterAgent
from backend.state.agent_state import ResearchState


planner_agent = PlannerAgent()
researcher_agent = ResearchAgent()
writer_agent = WriterAgent()
critic_agent = CriticAgent()


def planner_node(state: ResearchState) -> ResearchState:
    return planner_agent.run(state)


def researcher_node(state: ResearchState) -> ResearchState:
    return researcher_agent.run(state)


def writer_node(state: ResearchState) -> ResearchState:
    return writer_agent.run(state)


def critic_node(state: ResearchState) -> ResearchState:
    return critic_agent.run(state)