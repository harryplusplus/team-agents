from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, parse_llm_output


class Report(BaseModel):
    summary: str
    details: str


class ReportNode:
    name = "report"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        conversation_history = create_conversation_history(state["messages"])
        prompt = self._build_prompt(conversation_history)
        response = await self.llm.ainvoke(prompt)
        result = parse_llm_output(response.content, Report)

        state["messages"].append(
            AIMessage(
                content=f"""# 최종 리포트

## 요약
{result.summary}

## 상세 내용
{result.details}
"""
            )
        )

        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 작업 결과를 사용자에게 보고하는 전문가입니다.
전체 대화 내용을 분석하고, 사용자의 요청이 어떻게 처리되었는지 명확한 리포트를 작성하세요.

대화 기록:
{conversation_history}

JSON 포맷으로 응답하세요:
{{"summary": "작업 결과 요약 (1-2문장)", "details": "상세 내용 (계획, 실행 과정, 결과 등)"}}

응답 예시:
{{"summary": "웹 계산기 개발이 완료되었습니다.", "details": "1. HTML/CSS/JavaScript를 사용하여 반응형 웹 계산기 구현\\n2. 기본 사칙연산 및 괄호 처리 기능 추가\\n3. 브라우저 테스트 완료"}}
"""
