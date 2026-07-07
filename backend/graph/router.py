from backend.config.settings import settings
from backend.state.agent_state import ResearchState


def critic_router(state: ResearchState) -> str:
    """
    Decide whether to finish or revise the report.
    """

    if state.final_report is not None:
        return "end"

    return "writer"