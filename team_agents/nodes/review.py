from langchain_openai import ChatOpenAI

from team_agents.nodes.plan import PlanNode
from team_agents.nodes.report import ReportNode
from team_agents.state import State, Status


class ReviewNode:
    name = "review"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        return state

    @staticmethod
    def to_plan_or_report(state: State) -> str:
        status = state["status"]
        if status == Status.TO_PLAN:
            return PlanNode.name
        elif status == Status.TO_REPORT:
            return ReportNode.name

        raise ValueError(f"invalid status: {status}")
