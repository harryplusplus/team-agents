import json
import re
from typing import TypeVar

import typer
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _extract_text(content: str | list[str | dict]) -> str:
    """
    BaseMessage.content를 문자열로 변환합니다.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if text := item.get("text"):
                    parts.append(text)
        return "\n".join(parts)

    return str(content)


def _extract_json(content: str) -> str:
    """
    문자열에서 JSON을 추출합니다.

    순서:
    1. ```json``` 코드 블록
    2. ``` 코드 블록
    3. 중괄호로 감싸진 JSON
    """
    # ```json``` 코드 블록
    match = re.search(r"```json\s*\n?(.*?)\n?```", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # ``` 코드 블록
    match = re.search(r"```\s*\n?(.*?)\n?```", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 중괄호로 감싸진 JSON
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        return match.group(0)

    raise ValueError(f"No JSON found in content: {content[:200]}...")


def parse_llm_output(
    content: str | list[str | dict],
    schema: type[T],
) -> T:
    """
    AI 응답에서 JSON을 추출하고 Pydantic 모델로 파싱합니다.

    Args:
        content: BaseMessage.content (str | list[str | dict])
        schema: Pydantic BaseModel 클래스

    Returns:
        파싱된 Pydantic 모델 인스턴스

    Raises:
        ValueError: JSON을 찾을 수 없을 때
        json.JSONDecodeError: JSON 파싱 실패
        ValidationError: Pydantic 검증 실패
    """
    text = _extract_text(content)
    json_str = _extract_json(text)
    data = json.loads(json_str)
    return schema.model_validate(data)


def format_messages(messages: list[BaseMessage]) -> str:
    return "\n".join(f"{m.type}: {m.content}" for m in messages)


def log(log):
    typer.secho(log, fg=typer.colors.GREEN)
