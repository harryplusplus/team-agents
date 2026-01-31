from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from team_agents.shared import State, Status


class QuestionNode:
    name = "question"

    def __init__(self):
        pass

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        # 마지막 AI 메시지(질문)를 가져오기
        last_message = state["messages"][-1]

        # 사용자에게 질문을 보여주고 응답을 기다림
        user_response = interrupt({"question": last_message.content})

        # 사용자 응답을 메시지에 추가
        state["messages"].append(HumanMessage(content=user_response))

        return state
