from langchain_openai import ChatOpenAI

from team_agents.nodes.plan import PlanNode
from team_agents.nodes.question import QuestionNode
from team_agents.shared import State, Status


class RequestAnalysisNode:
    name = "request_analysis"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        return state

    @staticmethod
    def to_question_or_plan(state: State) -> str:
        status = state["status"]
        if status == Status.TO_QUESTION:
            return QuestionNode.name
        elif status == Status.TO_PLAN:
            return PlanNode.name

        raise ValueError(f"invalid status: {status}")
