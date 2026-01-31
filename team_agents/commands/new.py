from pathlib import Path

import nanoid
import typer
from langchain_core.messages import HumanMessage

from team_agents.graph import get_graph
from team_agents.shared import State, Status, build_config


async def new(request_file: Path):
    typer.secho("new command called.", fg=typer.colors.GREEN)

    with request_file.open() as f:
        request = f.read()

    typer.secho(
        f"begin request content from file: {request_file}", fg=typer.colors.GREEN
    )
    typer.secho(request, fg=typer.colors.GREEN)
    typer.secho("end request content.", fg=typer.colors.GREEN)

    thread_id = nanoid.generate()
    typer.secho(f"thread id: {thread_id}")

    async with get_graph() as graph:
        result = await graph.ainvoke(
            State(status=Status.TO_PLAN, messages=[HumanMessage(content=request)]),
            config=build_config(thread_id),
        )

        typer.secho(result, fg=typer.colors.GREEN)
