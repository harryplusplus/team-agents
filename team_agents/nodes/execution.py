from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, log, parse_llm_output


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

        conversation_history = create_conversation_history(state["messages"])
        prompt = self._build_prompt(conversation_history)
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

        state["messages"].append(
            AIMessage(
                content=f"실행 결과:\n\n{result.result}\n\n설명:\n{result.explanation}"
            )
        )

        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 작업을 실행하는 개발자입니다.
수립된 계획을 바탕으로 작업을 수행하세요.
필요한 경우 웹 검색 도구를 사용하여 최신 정보를 확인하세요.

대화 기록:
{conversation_history}

JSON 포맷으로 응답하세요:
{{"result": "실행 결과", "explanation": "설명"}}

응답 예시:
{{"result": "검색 결과: Python 3.13은 2024년 10월 출시되었습니다.", "explanation": "웹 검색을 통해 최신 정보를 확인했습니다."}}
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

JSON 포맷으로 응답하세요:
{{"result": "최종 답변", "explanation": "설명"}}
"""
