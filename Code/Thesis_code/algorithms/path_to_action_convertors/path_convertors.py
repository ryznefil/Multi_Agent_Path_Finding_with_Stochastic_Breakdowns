from Thesis_code.algorithms.path_to_action_convertors.conversion_types import ConversionType


def convert_timed_vertex_path_to_actions(shortest_vertex_paths, graph_representation):
    """"shortest paths - dictionary of paths, graph - networkX graph_representation, to be used only for execution without malfunctions"""
    agent_steps = {}
    edge_paths = {}

    for agent_id in range(len(shortest_vertex_paths)):
        agent_path = shortest_vertex_paths[agent_id]
        agent_action = []
        edges_list = []

        for step_number in range(len(agent_path) - 1):
            step_time = agent_path[step_number][1]

            edge = graph_representation[agent_path[step_number][0]][agent_path[step_number + 1][0]]  # edge representing the step from the current node to the next node
            edges_list.append(edge)
            agent_action.append(tuple((edge['action'], step_time)))

        agent_steps[agent_id] = agent_action
        edge_paths[agent_id] = edges_list

    return ConversionType.STANDARD, agent_steps, edge_paths
