from heapq import heappush, heappop
from itertools import count

import networkx as nx


def create_MDD(graph_representation, agent_constraints, agent_state, max_time_step):
    valid_goal_nodes = find_valid_ways(graph_representation, agent_constraints, agent_state, max_time_step)

    # MDD = build_MDD_from_nodes(valid_goal_nodes)
    MDD_dict = build_dict_MDD_from_nodes(valid_goal_nodes, max_time_step)

    return MDD_dict


def find_valid_ways(graph_representation, agent_constraints, agent_state, max_time_step):
    """" Create the MDD based on the current graph representation and maximum allowed depth, the maximum depth corresponds to the time of reaching the final destination, cannot be shorter as it corresponds to the shortest path equivalent"""
    valid_goal_nodes = []
    agent_start_vertex = agent_state.graph_current_vertex
    agent_goal_coordinates = agent_state.graph_target_vertex[0]  # COORDINATES ONLY!

    # node format (time_step, (vertex, orientation),
    start_node = MDD_node(0, agent_start_vertex, None)
    c = count()
    queue = [(c, start_node)]

    while queue:
        _, current_node = heappop(queue)
        if (current_node.location[0], current_node.timestep) in agent_constraints:
            continue

        if current_node.timestep > max_time_step:
            return valid_goal_nodes

        if current_node.timestep == max_time_step and current_node.location[0] != agent_goal_coordinates:
            continue

        if current_node.timestep < max_time_step and current_node.location[0] == agent_goal_coordinates:
            raise ValueError

        if current_node.location[0] == agent_goal_coordinates:
            valid_goal_nodes.append(current_node)

        for neighbor in graph_representation.neighbors(current_node.location):
            if current_node.location[0] is None:
                if neighbor == current_node.location:  # waiting on the same spot, costs 1
                    new_node = MDD_node(current_node.timestep + 1, neighbor, current_node)
                else:  # first PUT on board happens immediately
                    new_node = MDD_node(current_node.timestep, neighbor, current_node)
            else:
                if neighbor == current_node.location:  # waiting on the same spot, costs 1
                    new_node = MDD_node(current_node.timestep + 1, neighbor, current_node)
                else:  # first PUT on board happens immediately
                    new_node = MDD_node(current_node.timestep + 1, neighbor, current_node)

            heappush(queue, (next(c), new_node))

    return valid_goal_nodes


def build_MDD_from_nodes(goal_nodes):
    MDD = nx.DiGraph()

    for node in goal_nodes:
        current_node = node

        while current_node.previous_node is not None:
            current_time = current_node.timestep
            current_vertex = current_node.location[0]
            previous_time = current_node.previous_node.timestep
            previous_vertex = current_node.previous_node.location[0]

            MDD.add_edge((previous_vertex, previous_time), (current_vertex, current_time))

            current_node = current_node.previous_node

    return MDD


def build_dict_MDD_from_nodes(goal_nodes, max_time):
    MDD = {}
    for ts in range(max_time + 1):
        MDD[ts] = []

    for node in goal_nodes:
        current_node = node

        while current_node is not None:
            if current_node.location[0] not in MDD[current_node.timestep]:
                MDD[current_node.timestep].append(current_node.location[0])

            current_node = current_node.previous_node

    return MDD


class MDD_node():
    def __init__(self, current_timestep, current_location, previous_node):
        self.timestep = current_timestep
        self.location = current_location
        self.previous_node = previous_node
