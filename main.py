import asyncio
import logging
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

from team_agents.commands.new import new as new_command
from team_agents.commands.resume import resume as resume_command
from team_agents.commands.time_travel import time_travel as time_travel_command

load_dotenv()


if os.environ.get("DEBUG"):
    typer.secho("Debug mode enabled.", fg=typer.colors.GREEN)
    logging.basicConfig(level=logging.DEBUG)


app = typer.Typer()


@app.command()
def new(request_file: Path = typer.Option(..., help="Request file path")):
    asyncio.run(new_command(request_file))


@app.command()
def resume(
    thread_id: str = typer.Option(..., help="Thread ID"),
):
    asyncio.run(resume_command(thread_id))


@app.command()
def time_travel(
    thread_id: str = typer.Option(..., help="Thread ID"),
    checkpoint_id: str = typer.Option(..., help="Checkpoint ID"),
):
    asyncio.run(time_travel_command(thread_id, checkpoint_id))


if __name__ == "__main__":
    app()
