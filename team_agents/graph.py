from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.types import Checkpointer

from team_agents.nodes.execution import ExecutionNode
from team_agents.nodes.plan import PlanNode
from team_agents.nodes.report import ReportNode
from team_agents.nodes.report_feedback import ReportFeedbackNode
from team_agents.nodes.report_feedback_analysis import ReportFeedbackAnalysisNode
from team_agents.nodes.review import ReviewNode
from team_agents.nodes.task_analysis import (
    TaskAnalysisNode,
)
from team_agents.nodes.task_question import TaskQuestionNode
from team_agents.state import State


def create_graph(checkpointer: Checkpointer, llm: ChatOpenAI):
    builder = StateGraph(State)
    builder.add_node(TaskAnalysisNode.name, TaskAnalysisNode(llm))
    builder.add_node(TaskQuestionNode.name, TaskQuestionNode())
    builder.add_node(PlanNode.name, PlanNode(llm))
    builder.add_node(ExecutionNode.name, ExecutionNode(llm))
    builder.add_node(ReviewNode.name, ReviewNode(llm))
    builder.add_node(ReportNode.name, ReportNode(llm))
    builder.add_node(ReportFeedbackNode.name, ReportFeedbackNode())
    builder.add_node(ReportFeedbackAnalysisNode.name, ReportFeedbackAnalysisNode(llm))

    builder.add_edge(START, TaskAnalysisNode.name)
    builder.add_conditional_edges(
        TaskAnalysisNode.name, TaskAnalysisNode.to_question_or_plan
    )
    builder.add_edge(TaskQuestionNode.name, TaskAnalysisNode.name)
    builder.add_edge(PlanNode.name, ExecutionNode.name)
    builder.add_edge(ExecutionNode.name, ReviewNode.name)
    builder.add_conditional_edges(ReviewNode.name, ReviewNode.to_plan_or_report)
    builder.add_edge(ReportNode.name, ReportFeedbackNode.name)
    builder.add_edge(ReportFeedbackNode.name, ReportFeedbackAnalysisNode.name)
    builder.add_conditional_edges(
        ReportFeedbackAnalysisNode.name, ReportFeedbackAnalysisNode.to_plan_or_end
    )

    return builder.compile(checkpointer=checkpointer)
