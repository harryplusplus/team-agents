import os
from typing import TypedDict

import nanoid
from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


class State(TypedDict):
    message: str


async def hello_node(state: State) -> State:
    return {"message": f"Hello, {state['message']}!"}


async def main():
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        await checkpointer.setup()

        graph = StateGraph(State)

        graph.add_node("hello", hello_node)
        graph.set_entry_point("hello")
        graph.set_finish_point("hello")

        app = graph.compile(checkpointer=checkpointer)

        thread_id = nanoid.generate()
        print("Running with thread id:", thread_id)

        result = await app.ainvoke(
            {"message": "world"}, config={"configurable": {"thread_id": thread_id}}
        )

        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
