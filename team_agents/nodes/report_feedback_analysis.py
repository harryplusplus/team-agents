from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END
from pydantic import BaseModel

from team_agents.nodes.plan import PlanNode
from team_agents.state import State, Status
from team_agents.utils import create_conversation_history, parse_llm_output


class FeedbackAnalysis(BaseModel):
    is_approved: bool
    reason: str


class ReportFeedbackAnalysisNode:
    name = "report_feedback_analysis"

    @staticmethod
    def to_plan_or_end(state: State) -> str:
        status = state["status"]
        if status == Status.TO_PLAN:
            return PlanNode.name
        elif status == Status.TO_END:
            return END

        raise ValueError(f"invalid status: {status}")

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def __call__(self, state: State) -> State:
        state["status"] = Status.IN_PROGRESS

        conversation_history = create_conversation_history(state["messages"])
        prompt = self._build_prompt(conversation_history)
        response = await self.llm.ainvoke(prompt)
        result = parse_llm_output(response.content, FeedbackAnalysis)

        if result.is_approved:
            state["status"] = Status.TO_END
            state["messages"].append(
                AIMessage(content="피드백 분석: 승인되었습니다. 작업을 완료합니다.")
            )
        else:
            state["status"] = Status.TO_PLAN
            state["messages"].append(
                AIMessage(
                    content=f"피드백 분석: 반려되었습니다.\n\n사유:\n{result.reason}"
                )
            )

        return state

    def _build_prompt(self, conversation_history: str) -> str:
        return f"""당신은 사용자의 피드백을 분석하는 전문가입니다.
사용자가 리포트를 보고 남긴 피드백이 승인(통과)인지 반려(다시 작업)인지 판단하세요.

대화 기록:
{conversation_history}

중요: JSON만 출력하세요. 다른 텍스트를 절대 추가하지 마세요. ```json 코드 블록도 사용하지 마세요.

출력 형식:
{{"is_approved": true/false, "reason": "판단 사유"}}

예시 1 - 승인 (긍정 응답):
{{"is_approved": true, "reason": ""}}

예시 2 - 승인 (명시적 만족 표현):
{{"is_approved": true, "reason": ""}}

예시 3 - 반려 (추가 요청):
{{"is_approved": false, "reason": "사용자가 성능 최적화를 추가로 요청했습니다."}}

예시 4 - 반려 (불만족):
{{"is_approved": false, "reason": "사용자가 답변이 불충분하다고 하여 더 자세한 설명이 필요합니다."}}

예시 5 - 승인:
{{"is_approved": true, "reason": ""}}

판단 기준:
- "좋다", "충분하다", "만족한다", "통과", "승인", "OK", "고맙다" → 승인
- "부족하다", "추가하다", "다시하다", "더 자세히", "수정" → 반려

이제 피드백 분석 결과를 JSON으로만 출력하세요.
"""
