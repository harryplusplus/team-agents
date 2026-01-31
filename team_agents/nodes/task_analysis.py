from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.nodes.plan import PlanNode
from team_agents.nodes.task_question import TaskQuestionNode
from team_agents.state import State, Status
from team_agents.utils import format_messages, parse_llm_output


class Result(BaseModel):
    has_question: bool
    question: str = ""


class TaskAnalysisNode:
    name = "task_analysis"

    @staticmethod
    def to_question_or_plan(state: State) -> str:
        status = state["status"]
        if status == Status.TO_QUESTION:
            return TaskQuestionNode.name
        elif status == Status.TO_PLAN:
            return PlanNode.name

        raise ValueError(f"invalid status: {status}")

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        prompt = self._build_prompt(format_messages(state["messages"]))
        response = await self.llm.ainvoke(prompt)
        result = parse_llm_output(response.content, Result)

        if result.has_question:
            state["status"] = Status.TO_QUESTION
            state["messages"].append(AIMessage(content=result.question))
        else:
            state["status"] = Status.TO_PLAN
            state["messages"].append(
                AIMessage(content="요청이 명확합니다. 계획을 세우겠습니다.")
            )

        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 사용자의 요청을 분석하고 명확하게 만드는 전문가입니다.
당신의 분석을 바탕으로 다른 작업자들이 계획하고 실행하고 검토하고 사용자에게 보고합니다.
사용자의 요청에 모호한 정보가 있다면 반드시 질문하세요.

대화 기록:
{conversation_history}

JSON 포맷으로 응답하세요.
{{"has_question": true/false, "question": "질문 내용" }}

응답 예시:
{{"has_question": true, "question": "1. 어떤 플랫폼용 계산기인가요? (웹, 모바일, 데스크톱)\n2. 어떤 기능이 필요한가요?"}}
{{"has_question": false, "question": ""}} 
"""
