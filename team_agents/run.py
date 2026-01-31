import os

import typer
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from psycopg_pool import AsyncConnectionPool

from team_agents.graph import create_graph
from team_agents.llm import create_llm
from team_agents.state import State
from team_agents.utils import log


async def run(state: State | None, config: RunnableConfig):
    pool = AsyncConnectionPool(os.environ["DATABASE_URL"])
    try:
        checkpointer = AsyncPostgresSaver(pool)  # pyright: ignore[reportArgumentType]
        await checkpointer.setup()

        llm = create_llm()
        graph = create_graph(checkpointer, llm)

        current_input = state
        result = None
        while True:
            result = await graph.ainvoke(
                current_input,
                config=config,
            )

            if "__interrupt__" not in result:
                break

            ai_message = result["__interrupt__"][0].value
            user_message = typer.prompt(ai_message)
            current_input = Command(resume=user_message)

        log(result)

    finally:
        await pool.close()
