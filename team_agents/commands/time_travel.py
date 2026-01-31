import typer

from team_agents.config import create_config
from team_agents.run import run


async def time_travel(thread_id: str, checkpoint_id: str):
    typer.secho(
        f"resume command called with thread id: {thread_id} and checkpoint id: {checkpoint_id}.",
        fg=typer.colors.GREEN,
    )

    config = create_config(thread_id, checkpoint_id)
    await run(None, config)
