from enum import Enum
from typing import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig


class Status(str, Enum):
    TO_QUESTION = "to_question"
    TO_PLAN = "to_plan"
    TO_REPORT = "to_report"
    TO_END = "to_end"

    IN_PROGRESS = "in_progress"


class State(TypedDict):
    messages: list[BaseMessage]
    status: Status


def build_config(thread_id: str, checkpoint_id: str | None = None):
    configurable = {"thread_id": thread_id}
    if checkpoint_id is not None:
        configurable["checkpoint_id"] = checkpoint_id

    return RunnableConfig(configurable=configurable)


def format_messages(messages: list[BaseMessage]) -> str:
    return "\n".join(f"{m.type}: {m.content}" for m in messages)
