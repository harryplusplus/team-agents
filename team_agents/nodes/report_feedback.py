from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from team_agents.state import State, Status


class ReportFeedbackNode:
    name = "report_feedback"

    def __init__(self):
        pass

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        last = state["messages"][-1]
        response = interrupt(last.content)
        state["messages"].append(HumanMessage(content=response))

        return state
