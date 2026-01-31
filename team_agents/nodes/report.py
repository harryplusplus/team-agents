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
전체 대화 내용을 분석하고, **사용자의 원래 질문에 대한 답변**을 명확하게 전달하세요.

중요: 각 에이전트가 어떤 작업을 했는지 프로세스를 나열하는 것이 목적이 아닙니다.
**사용자가 궁금해했던 것에 대한 정확한 답변**을 제공하는 것이 핵심입니다.

대화 기록:
{conversation_history}

JSON 포맷으로 응답하세요:
{{"summary": "사용자 질문에 대한 직접적인 답변 요약 (1-2문장)", "details": "사용자 질문에 대한 상세한 답변"}}

응답 예시:
사용자 질문: "파이썬 3.13의 새로운 기능은 뭐야?"
{{"summary": "Python 3.13은 실험적 JIT 컴파일러, 개선된 에러 메시지, 타입 시스템 개선 등을 도입했습니다.", "details": "주요 새로운 기능:\\n1. 실험적 JIT 컴파일러 (copy-and-patch) - 성능 향상\\n2. 더 명확한 에러 메시지 - 디버깅 편의성 개선\\n3. 타입 힌트 시스템 개선 - type 에러 더 정확히 표시\\n4. 인터랙티브 쉘 개선"}}
"""
