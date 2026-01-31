from langchain_openai import ChatOpenAI

from team_agents.state import State, Status


class PlanNode:
    name = "plan"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        return state
