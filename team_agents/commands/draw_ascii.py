from langgraph.checkpoint.memory import MemorySaver

from team_agents.graph import create_graph


def draw_ascii():
    graph = create_graph(MemorySaver())
    print(graph.get_graph().draw_ascii())
