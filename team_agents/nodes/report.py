from langchain_openai import ChatOpenAI

from team_agents.shared import State, Status


class ReportNode:
    name = "report"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        return state
