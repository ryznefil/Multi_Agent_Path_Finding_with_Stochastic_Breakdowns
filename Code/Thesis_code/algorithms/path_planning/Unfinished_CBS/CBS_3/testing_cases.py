import networkx as nx
from Thesis_code.graph_representation.testing_case_agent_state import AgentState


def straight_no_detour(track_len, agent_count=2):
    graph = nx.DiGraph()

    # one way
    for w in range(1, track_len):
        start = ((0, w - 1), 3)
        end = ((0, w), 3)
        graph.add_edge(start, end, weight=1)

    # and another
    for w in range(track_len - 2, -1, -1):
        start = ((0, w + 1), 1)
        end = ((0, w), 1)
        graph.add_edge(start, end, weight=1)

    # dead ends
    graph.add_edge(((0, track_len - 1), 3), ((0, track_len - 2), 1), weight=1)
    graph.add_edge(((0, 0), 1), ((0, 1), 3), weight=1)

    # end connections
    graph.add_edge(((0, 0), 1), ((0, 0), 5), weight=1)
    graph.add_edge(((0, track_len - 1), 3), ((0, track_len - 1), 5), weight=1)

    # create agents
    agent_key_start_a = ((0, 0), 3)
    agent_key_end_a = ((0, track_len - 1), 3)
    agent_key_start_b = ((0, track_len - 1), 1)
    agent_key_end_b = ((0, 0), 1)

    agent_states = []

    for agent_id in range(agent_count):
        if agent_id % 2 == 0:
            start = agent_key_start_a
            end = agent_key_end_a
        else:
            start = agent_key_start_b
            end = agent_key_end_b

        graph.add_edge((None, agent_id), start, weight=1)

        agent = AgentState(agent_id, 1, start, end)
        agent_states.append(agent)

    # add waits - has to be done after all agents starts in None are added
    vertices = graph.nodes
    for vertex in vertices:
        graph.add_edge(vertex, vertex, weight=1)

    # create the vertex array
    vertex_array = []
    for w in range(track_len):
        vertex_array.append((0, w))

    return (graph, agent_states, vertex_array)


x = straight_no_detour(4, 2)
print()
