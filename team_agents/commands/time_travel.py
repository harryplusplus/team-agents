from team_agents.config import create_config
from team_agents.run import run
from team_agents.utils import log


async def time_travel(thread_id: str, checkpoint_id: str):
    log(
        f"resume command called with thread id: {thread_id} and checkpoint id: {checkpoint_id}.",
    )

    config = create_config(thread_id, checkpoint_id)
    await run(None, config)
