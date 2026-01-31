from enum import Enum
from typing import TypedDict

from langchain_core.messages import BaseMessage


class Status(str, Enum):
    TO_QUESTION = "to_question"
    TO_PLAN = "to_plan"
    TO_NEXT_STEP = "to_next_step"
    TO_REPORT = "to_report"
    TO_END = "to_end"

    IN_PROGRESS = "in_progress"


class Plan(TypedDict):
    title: str
    steps: list[str]


class State(TypedDict):
    messages: list[BaseMessage]
    status: Status
    plan: Plan | None
    current_step: int | None
    step_results: list[str] | None
