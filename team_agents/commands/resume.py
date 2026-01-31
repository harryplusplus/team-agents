import typer

from team_agents.graph import get_graph
from team_agents.shared import build_config


async def resume(thread_id: str):
    typer.secho(
        f"resume command called with thread id: {thread_id}.", fg=typer.colors.GREEN
    )

    async with get_graph() as graph:
        result = await graph.ainvoke(
            None,
            config=build_config(thread_id),
        )

        typer.echo(result)
