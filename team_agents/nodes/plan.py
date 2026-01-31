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

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"title": "계획 제목", "steps": ["단계 1", "단계 2", "단계 3"]}}

예시 1 - 웹 계산기 개발:
{{"title": "웹 계산기 개발", "steps": ["HTML 구조 작성", "CSS 스타일 적용", "JavaScript 계산 로직 구현", "브라우저 테스트"]}}

예시 2 - 파이썬 스크립트 작성:
{{"title": "CSV 데이터 분석 스크립트 작성", "steps": ["요구사항 분석", "pandas를 이용한 데이터 로드 함수 작성", "데이터 분석 로직 구현", "결과 출력 기능 추가"]}}

예시 3 - API 엔드포인트 구현:
{{"title": "사용자 인증 API 구현", "steps": ["JWT 토큰 기반 인증 방식 설계", "로그인 엔드포인트 구현 (/api/auth/login)", "토큰 검증 미들웨어 작성", "테스트 코드 작성"]}}

이제 계획을 JSON으로만 출력하세요.
"""
