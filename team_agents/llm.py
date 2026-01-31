import os

from langchain_openai import ChatOpenAI


def create_llm(temperature: float) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=os.environ["API_URL"],
        api_key=lambda: os.environ["API_KEY"],
        model=os.environ["MODEL"],
        verbose=True if os.environ.get("DEBUG") else False,
        temperature=temperature,
    )
