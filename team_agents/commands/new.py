from pathlib import Path

import nanoid
import typer
from langchain_core.messages import HumanMessage

from team_agents.config import create_config
from team_agents.run import run
from team_agents.state import State, Status


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

    state = State(status=Status.TO_PLAN, messages=[HumanMessage(content=request)])
    config = create_config(thread_id)

    await run(state, config)
