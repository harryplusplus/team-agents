import os

import typer
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from psycopg_pool import AsyncConnectionPool

from team_agents.graph import create_graph
from team_agents.state import State
from team_agents.utils import create_conversation_history, log, sanitize_utf8


async def run(state: State | None, config: RunnableConfig):
    pool = AsyncConnectionPool(os.environ["DATABASE_URL"])
    try:
        checkpointer = AsyncPostgresSaver(pool)  # pyright: ignore[reportArgumentType]
        await checkpointer.setup()

        graph = create_graph(checkpointer)

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
            current_input = Command(resume=sanitize_utf8(user_message))

        log(create_conversation_history(result["messages"]))

    finally:
        await pool.close()
