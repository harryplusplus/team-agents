from pathlib import Path

import nanoid
from langchain_core.messages import HumanMessage

from team_agents.config import create_config
from team_agents.run import run
from team_agents.state import State, Status
from team_agents.utils import log


async def new(task_file: Path):
    log("new command called.")

    with task_file.open() as f:
        task = f.read()

    log(f"begin task content from file: {task_file}")
    log(task)
    log("end task content.")

    thread_id = nanoid.generate()
    log(f"thread id: {thread_id}")

    state = State(
        status=Status.IN_PROGRESS,
        messages=[HumanMessage(content=task)],
        plan=None,
        current_step=None,
        step_results=None,
    )
    config = create_config(thread_id)

    await run(state, config)
