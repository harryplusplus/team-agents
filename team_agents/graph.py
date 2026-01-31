import os
from contextlib import asynccontextmanager

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import START, StateGraph
from langgraph.types import Checkpointer

from team_agents.nodes.execution import ExecutionNode
from team_agents.nodes.plan import PlanNode
from team_agents.nodes.question import QuestionNode
from team_agents.nodes.report import ReportNode
from team_agents.nodes.report_result_analysis import ReportResultAnalysisNode
from team_agents.nodes.request_analysis import (
    RequestAnalysisNode,
)
from team_agents.nodes.review import ReviewNode
from team_agents.shared import State


def build_graph(checkpointer: Checkpointer, llm: ChatOpenAI):
    builder = StateGraph(State)
    builder.add_node(RequestAnalysisNode.name, RequestAnalysisNode(llm))
    builder.add_node(QuestionNode.name, QuestionNode())
    builder.add_node(PlanNode.name, PlanNode(llm))
    builder.add_node(ExecutionNode.name, ExecutionNode(llm))
    builder.add_node(ReviewNode.name, ReviewNode(llm))
    builder.add_node(ReportNode.name, ReportNode(llm))
    builder.add_node(ReportResultAnalysisNode.name, ReportResultAnalysisNode(llm))

    builder.add_edge(START, RequestAnalysisNode.name)
    builder.add_conditional_edges(
        RequestAnalysisNode.name, RequestAnalysisNode.to_question_or_plan
    )
    builder.add_edge(QuestionNode.name, RequestAnalysisNode.name)
    builder.add_edge(PlanNode.name, ExecutionNode.name)
    builder.add_edge(ExecutionNode.name, ReviewNode.name)
    builder.add_conditional_edges(ReviewNode.name, ReviewNode.to_plan_or_report)
    builder.add_edge(ReportNode.name, ReportResultAnalysisNode.name)
    builder.add_conditional_edges(
        ReportResultAnalysisNode.name, ReportResultAnalysisNode.to_plan_or_end
    )

    return builder.compile(checkpointer=checkpointer)


@asynccontextmanager
async def get_graph():
    async with AsyncPostgresSaver.from_conn_string(
        os.environ["DATABASE_URL"]
    ) as checkpointer:
        await checkpointer.setup()

        llm = ChatOpenAI(
            base_url=os.environ["API_URL"],
            api_key=lambda: os.environ["API_KEY"],
            model=os.environ["MODEL"],
            verbose=True if os.environ.get("DEBUG") else False,
        )

        yield build_graph(checkpointer, llm)
