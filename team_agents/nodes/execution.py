from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.state import State, Status
from team_agents.utils import (
    create_conversation_history,
    log,
    log_state,
    parse_llm_output,
)


@tool
def web_search(query: str) -> str:
    """웹에서 정보를 검색합니다. 한국어 검색도 지원합니다."""

    search = DuckDuckGoSearchResults(num_results=5)
    results = search.invoke(query)
    return results


class Execution(BaseModel):
    result: str
    explanation: str


class ExecutionNode:
    name = "execution"

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.bind_tools([web_search])

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        # 현재 스텝 정보 가져오기
        plan = state["plan"]
        current_step_idx = state["current_step"] if state["current_step"] is not None else 0
        steps = plan["steps"] if plan else []
        current_step = steps[current_step_idx] if steps else "작업 진행"

        conversation_history = create_conversation_history(state["messages"])
        prompt = self._build_prompt(conversation_history, current_step)
        response = await self.llm.ainvoke(prompt)

        result: Execution | None = None
        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "web_search":
                    query = tool_call["args"]["query"]
                    search_result = web_search.invoke(query)
                    # 검색 결과를 바탕으로 최종 응답 생성
                    followup_prompt = self._build_followup_prompt(
                        search_result,
                        conversation_history,
                        str(response.content),
                        query,
                    )
                    final_response = await self.llm.ainvoke(followup_prompt)
                    result = parse_llm_output(final_response.content, Execution)
                else:
                    log("Unknown tool called: " + tool_call["name"])
                    result = Execution(result="실행 완료", explanation="도구 호출 완료")
        else:
            result = parse_llm_output(response.content, Execution)

        if result is None:
            raise ValueError("Failed to parse LLM output")

        # 실행 결과를 step_results에 추가
        if state["step_results"] is None:
            state["step_results"] = []
        state["step_results"].append(f"{result.result}\n\n설명: {result.explanation}")

        state["messages"].append(
            AIMessage(
                content=f"[{current_step_idx + 1}/{len(steps)}] {current_step}\n\n실행 결과:\n\n{result.result}\n\n설명:\n{result.explanation}"
            )
        )

        log_state(self.name, state)
        return state

    def _build_prompt(self, conversation_history: str, current_step: str) -> str:
        return f"""당신은 작업을 실행하는 개발자입니다.
수립된 계획을 바탕으로 작업을 수행하세요.

현재 실행할 작업: {current_step}
필요한 경우 웹 검색 도구를 사용하여 최신 정보를 확인하세요.

대화 기록:
{conversation_history}

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"result": "실행 결과 내용", "explanation": "설명"}}

예시 1 - 웹 검색으로 답변:
{{"result": "Python 3.13은 2024년 10월 7일에 출시되었습니다. 주요 특징은 실험적인 JIT 컴파일러와 개선된 에러 메시지입니다.", "explanation": "웹 검색을 통해 Python 3.13의 출시일과 주요 특징을 확인했습니다."}}

예시 2 - 코드 작성:
{{"result": "def add(a, b):\\n    return a + b\\n\\ndef subtract(a, b):\\n    return a - b", "explanation": "요청한 덧셈과 뺄셈 함수를 작성했습니다."}}

예시 3 - 분석 결과:
{{"result": "해당 이슈는 메모리 누수로 인해 발생합니다. 객체가 제때 해제되지 않고 있습니다.", "explanation": "코드를 분석한 결과, 이벤트 리스너가 제거되지 않아 메모리 누수가 발생하고 있음을 확인했습니다."}}

이제 실행 결과를 JSON으로만 출력하세요.
"""

    def _build_followup_prompt(
        self, search_result: str, conversation_history: str, reasoning: str, query: str
    ) -> str:
        return f"""당신은 작업을 실행하는 개발자입니다.
웹 검색 결과를 바탕으로 사용자에게 답변을 제공하세요.

대화 기록:
{conversation_history}

검색 전 reasoning:
{reasoning}

검색 쿼리:
{query}

검색 결과:
{search_result}

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"result": "최종 답변", "explanation": "설명"}}

예시 1:
{{"result": "파이썬 3.13의 새로운 기능: 1) 실험적 JIT 컴파일러 2) 개선된 에러 메시지 3) 타입 시스템 개선", "explanation": "검색 결과를 바탕으로 Python 3.13의 주요 신규 기능을 정리했습니다."}}

예시 2:
{{"result": "LangGraph는 LangChain 팀이 개발한 상태 기반 에이전트 워크플로우 프레임워크입니다.", "explanation": "공식 문서 검색 결과를 통해 LangGraph의 정의를 확인했습니다."}}

이제 검색 결과를 분석한 답변을 JSON으로만 출력하세요.
"""
