import os

import typer
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from team_agents.graph import create_graph
from team_agents.llm import create_llm
from team_agents.state import State


async def run(state: State | None, config: RunnableConfig):
    pool = AsyncConnectionPool(os.environ["DATABASE_URL"])
    try:
        checkpointer = AsyncPostgresSaver(pool)  # pyright: ignore[reportArgumentType]
        await checkpointer.setup()

        llm = create_llm()
        graph = create_graph(checkpointer, llm)

        result = await graph.ainvoke(
            state,
            config=config,
        )

        typer.secho(result, fg=typer.colors.GREEN)

    finally:
        await pool.close()
