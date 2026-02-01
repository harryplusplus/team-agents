import asyncio
import logging
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

from team_agents.commands.draw_ascii import draw_ascii
from team_agents.commands.draw_mermaid import draw_mermaid
from team_agents.commands.new import new
from team_agents.commands.resume import resume
from team_agents.commands.time_travel import time_travel
from team_agents.utils import log

load_dotenv()


if os.environ.get("DEBUG"):
    log("Debug mode enabled.")
    logging.basicConfig(level=logging.DEBUG)


app = typer.Typer()


@app.command(name="new")
def new_command(task_file: Path = typer.Option(..., help="Task file path")):
    asyncio.run(new(task_file))


@app.command(name="resume")
def resume_command(
    thread_id: str = typer.Option(..., help="Thread ID"),
):
    asyncio.run(resume(thread_id))


@app.command(name="time-travel")
def time_travel_command(
    thread_id: str = typer.Option(..., help="Thread ID"),
    checkpoint_id: str = typer.Option(..., help="Checkpoint ID"),
):
    asyncio.run(time_travel(thread_id, checkpoint_id))


@app.command(name="draw-ascii")
def draw_ascii_command():
    draw_ascii()


@app.command(name="draw-mermaid")
def draw_mermaid_command():
    draw_mermaid()


if __name__ == "__main__":
    app()
