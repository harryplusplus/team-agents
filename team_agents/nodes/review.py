from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from team_agents.nodes.execution import ExecutionNode
from team_agents.nodes.plan import PlanNode
from team_agents.nodes.report import ReportNode
from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, log_state, parse_llm_output


class Review(BaseModel):
    is_satisfactory: bool
    feedback: str


class ReviewNode:
    name = "review"

    @staticmethod
    def to_plan_or_next_step_or_report(state: State) -> str:
        status = state["status"]
        if status == Status.TO_PLAN:
            return PlanNode.name
        elif status == Status.TO_NEXT_STEP:
            return ExecutionNode.name
        elif status == Status.TO_REPORT:
            return ReportNode.name

        raise ValueError(f"invalid status: {status}")

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        # 현재 스텝 정보
        plan = state["plan"]
        current_step_idx = state["current_step"] if state["current_step"] is not None else 0
        steps = plan["steps"] if plan else []
        current_step = steps[current_step_idx] if steps else "작업"

        conversation_history = create_conversation_history(state)
        prompt = self._build_prompt(conversation_history, current_step)
        response = await self.llm.ainvoke(prompt)
        result = parse_llm_output(response.content, Review)

        if result.is_satisfactory:
            # 다음 스텝이 있는지 확인
            next_step_idx = current_step_idx + 1
            if next_step_idx < len(steps):
                # 다음 스텝으로
                state["current_step"] = next_step_idx
                state["status"] = Status.TO_NEXT_STEP
                next_step = steps[next_step_idx]
                state["messages"].append(
                    AIMessage(
                        content=f"검토 결과: 통과했습니다.\n\n다음 작업: {next_step}"
                    )
                )
            else:
                # 모든 스텝 완료
                state["status"] = Status.TO_REPORT
                state["messages"].append(
                    AIMessage(content="검토 결과: 모든 작업이 완료되었습니다. 리포트를 작성합니다.")
                )
        else:
            # 반려 - 계획부터 다시 (현재는 이 방식)
            state["status"] = Status.TO_PLAN
            state["messages"].append(
                AIMessage(
                    content=f"검토 결과: 반려되었습니다.\n\n피드백:\n{result.feedback}\n\n계획을 다시 세웁니다."
                )
            )

        log_state(self.name, state)
        return state

    def _build_prompt(self, conversation_history: str, current_step: str) -> str:
        return f"""당신은 작업 결과를 검토하는 리뷰어입니다.
현재 스텝의 실행 결과가 요청사항을 충족하는지 검토하세요.

현재 검토할 작업: {current_step}

대화 기록:
{conversation_history}

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"is_satisfactory": true/false, "feedback": "피드백 내용"}}

예시 1 - 만족스러운 경우:
{{"is_satisfactory": true, "feedback": ""}}

예시 2 - 부족한 경우:
{{"is_satisfactory": false, "feedback": "계산기의 소수점 처리가 누락되었습니다. 10 / 3 = 3.33... 처럼 소수점 계산이 필요합니다."}}

예시 3 - 부족한 경우:
{{"is_satisfactory": false, "feedback": "요청한 '음수 입력 처리' 기능이 구현되지 않았습니다. 다시 구현해주세요."}}

예시 4 - 만족스러운 경우:
{{"is_satisfactory": true, "feedback": ""}}

이제 검토 결과를 JSON으로만 출력하세요.
"""
