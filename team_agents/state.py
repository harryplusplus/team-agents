from enum import Enum
from typing import TypedDict

from langchain_core.messages import BaseMessage


class Status(str, Enum):
    TO_QUESTION = "to_question"
    TO_PLAN = "to_plan"
    TO_REPORT = "to_report"
    TO_END = "to_end"

    IN_PROGRESS = "in_progress"


class State(TypedDict):
    messages: list[BaseMessage]
    status: Status
