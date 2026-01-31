from langchain_core.runnables import RunnableConfig


def create_config(thread_id: str, checkpoint_id: str | None = None):
    configurable = {"thread_id": thread_id}
    if checkpoint_id is not None:
        configurable["checkpoint_id"] = checkpoint_id

    return RunnableConfig(configurable=configurable)
