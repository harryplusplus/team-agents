from enum import Enum
from typing import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage


class Status(str, Enum):
    TO_QUESTION = "to_question"
    TO_PLAN = "to_plan"
    TO_NEXT_STEP = "to_next_step"
    TO_REPORT = "to_report"
    TO_END = "to_end"

    IN_PROGRESS = "in_progress"


class State(TypedDict):
    messages: list[BaseMessage]
    status: Status
    original_request: HumanMessage | None
    plan: dict | None
    current_step: int | None
    step_results: list[str] | None
