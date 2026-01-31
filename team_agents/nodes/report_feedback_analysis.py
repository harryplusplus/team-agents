from langchain_openai import ChatOpenAI
from langgraph.graph import END

from team_agents.nodes.plan import PlanNode
from team_agents.state import State, Status


class ReportFeedbackAnalysisNode:
    name = "report_feedback_analysis"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        return state

    @staticmethod
    def to_plan_or_end(state: State) -> str:
        status = state["status"]
        if status == Status.TO_PLAN:
            return PlanNode.name
        elif status == Status.TO_END:
            return END

        raise ValueError(f"invalid status: {status}")
