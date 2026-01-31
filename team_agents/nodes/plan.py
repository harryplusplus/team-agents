from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, parse_llm_output


class Plan(BaseModel):
    title: str
    steps: list[str]


class PlanNode:
    name = "plan"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        prompt = self._build_prompt(create_conversation_history(state["messages"]))
        response = await self.llm.ainvoke(prompt)
        result = parse_llm_output(response.content, Plan)

        state["messages"].append(
            AIMessage(
                content=f"계획이 수립되었습니다.\n\n제목: {result.title}\n\n단계:\n"
                + "\n".join(f"{i + 1}. {step}" for i, step in enumerate(result.steps))
            )
        )

        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 작업 계획 수립 전문가입니다.
사용자의 요청을 분석하고 구체적인 실행 계획을 수립하세요.

대화 기록:
{conversation_history}

JSON 포맷으로 계획을 작성하세요:
{{"title": "계획 제목", "steps": ["단계 1", "단계 2", "단계 3"]}}

응답 예시:
{{"title": "웹 계산기 개발", "steps": ["1. HTML 구조 작성", "2. CSS 스타일 적용", "3. JavaScript 계산 로직 구현"]}}
"""
