from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, log_state, parse_llm_output


class PlanInput(BaseModel):
    title: str
    steps: list[str]


class PlanNode:
    name = "plan"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        prompt = self._build_prompt(create_conversation_history(state))
        response = await self.llm.ainvoke(prompt)
        result = parse_llm_output(response.content, PlanInput)

        # 계획을 State에 저장
        state["plan"] = {"title": result.title, "steps": result.steps}
        state["current_step"] = 0
        state["step_results"] = []

        state["messages"].append(
            AIMessage(
                content=f"계획이 수립되었습니다.\n\n제목: {result.title}\n\n단계:\n"
                + "\n".join(f"{i + 1}. {step}" for i, step in enumerate(result.steps))
            )
        )

        log_state(self.name, state)
        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 작업 계획 수립 전문가입니다.
사용자의 요청을 분석하고 구체적인 실행 계획을 수립하세요.

중요: 대화 기록에 이전 실행의 실패나 반려 피드백이 있다면, 그 원인을 분석하고 다른 방법으로 계획을 수정해야 합니다.
같은 방법을 반복하면 다시 반려될 것입니다.

대화 기록:
{conversation_history}

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"title": "계획 제목", "steps": ["단계 1", "단계 2", "단계 3"]}}

예시 1 - 초기 계획 (웹 계산기 개발):
{{"title": "웹 계산기 개발", "steps": ["HTML 구조 작성", "CSS 스타일 적용", "JavaScript 계산 로직 구현", "브라우저 테스트"]}}

예시 2 - 깃헙 API 제한으로 인한 계획 수정:
{{"title": "깃헙 스타 증가량 기반 언어 분석 (웹 검색 방식)", "steps": ["TIOBE/PYPL 지수 참조하여 언어 목록 선정", "웹 검색으로 각 언어별 인기 저장소 수집", "웹 검색으로 최근 3개월 스타 증가량 정보 수집", "언어별 증가량 계산 및 순위 매기기", "데이터 시각화 및 리포트 작성"]}}

예시 3 - API 제한으로 인한 계획 수정:
{{"title": "소셜 미디어 트렌드 분석 (공식 API 대안)", "steps": ["분석 대상 플랫폼 선정", "웹 크롤링으로 데이터 수집 계획 수립", "크롤링 도구 선택 및 설정", "데이터 수집 및 전처리", "트렌드 분석 및 시각화"]}}

이제 계획을 JSON으로만 출력하세요.
"""
