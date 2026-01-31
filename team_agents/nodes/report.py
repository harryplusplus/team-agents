from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, log_state, parse_llm_output


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

        log_state(self.name, state)
        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 작업 결과를 사용자에게 보고하는 전문가입니다.
전체 대화 내용을 분석하고, **사용자의 원래 질문에 대한 답변**을 명확하게 전달하세요.

중요: 각 에이전트가 어떤 작업을 했는지 프로세스를 나열하는 것이 목적이 아닙니다.
**사용자가 궁금해했던 것에 대한 정확한 답변**을 제공하는 것이 핵심입니다.

대화 기록:
{conversation_history}

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"summary": "사용자 질문에 대한 직접적인 답변 요약 (1-2문장)", "details": "사용자 질문에 대한 상세한 답변"}}

예시 1:
사용자 질문: "파이썬 3.13의 새로운 기능은 뭐야?"
{{"summary": "Python 3.13은 실험적 JIT 컴파일러, 개선된 에러 메시지, 타입 시스템 개선 등을 도입했습니다.", "details": "주요 새로운 기능:\\n1. 실험적 JIT 컴파일러 (copy-and-patch) - 성능 향상\\n2. 더 명확한 에러 메시지 - 디버깅 편의성 개선\\n3. 타입 힌트 시스템 개선 - type 에러 더 정확히 표시\\n4. 인터랙티브 쉘 개선"}}

예시 2:
사용자 질문: "FastAPI와 Flask의 차이는?"
{{"summary": "FastAPI는 비동기 처리에 최적화되어 있고 자동 문서 생성을 제공하며, Flask는 경량화되어 있고 오랜 기간 사용된成熟한 프레임워크입니다.", "details": "FastAPI: 비동기 지원(Starlette 기반), 자동 OpenAPI 문서, 데이터 검증(Pydantic)\\n\\nFlask: 동기 처리, 간단한 구조, 풍부한 확장 생태계, 오랜 역사"}}

예시 3:
사용자 질문: "리눅스에서 파일 찾는 명령어는?"
{{"summary": "리눅스에서 파일을 찾는 주요 명령어는 find, locate, grep이 있습니다.", "details": "1. find: 실시간 파일 검색, 다양한 옵션 지원 (예: find /home -name '*.txt')\\n2. locate: 데이터베이스를 사용한 빠른 검색 (예: locate filename)\\n3. grep: 파일 내용 검색 (예: grep 'pattern' file.txt)"}}

이제 리포트를 JSON으로만 출력하세요.
"""
