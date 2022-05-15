from heapq import heappush, heappop
from itertools import count

import networkx as nx


def create_MDD(graph_representation, agent_constraints, agent_state, max_time_step, distance_map):
    valid_goal_nodes = find_valid_ways(graph_representation, agent_constraints, agent_state, max_time_step, distance_map)

    MDD = build_MDD_from_nodes(valid_goal_nodes)
    MDD_dict = build_dict_MDD_from_nodes(valid_goal_nodes, max_time_step)

    return MDD_dict


def find_valid_ways(graph_representation, agent_constraints, agent_state, max_time_step, distance_map):
    """" Create the MDD based on the current graph representation and maximum allowed depth, the maximum depth corresponds to the time of reaching the final destination, cannot be shorter as it corresponds to the shortest path equivalent"""
    valid_goal_nodes = []
    agent_start_vertex = agent_state.graph_current_vertex
    agent_goal_coordinates = agent_state.graph_target_vertex[0]  # COORDINATES ONLY!

    # node format (time_step, (vertex, orientation),
    start_node = MDD_node(0, agent_start_vertex, None)
    c = count()
    queue = [(0, c, start_node)]

    while queue:
        timestep, _, current_node = heappop(queue)

        if current_node.location[0] is not None:
            if current_node.location[1] == 5:
                continue
            shortest_distance = distance_map[
                agent_state.id, current_node.location[0][0], current_node.location[0][1], current_node.location[1]]  # get the distance to goal node from the current location
        else:
            start_graph = agent_state.graph_starting_vertex
            shortest_distance = distance_map[agent_state.id, start_graph[0][0], start_graph[0][1], start_graph[1]]  # get the distance to goal node from the current location

        if timestep > max_time_step:  # we have crossed the time limit, terminate
            return valid_goal_nodes

        if (current_node.location[0], timestep) in agent_constraints:  # the node is constrained and cannot be explored
            continue

        if current_node.location[0] == agent_goal_coordinates:  # arrived at the goal
            valid_goal_nodes.append(current_node)

        if shortest_distance > (max_time_step - timestep):
            continue

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
                    new_node = MDD_node(current_node.timestep + agent_state.steps_per_move, neighbor, current_node)

            heappush(queue, (new_node.timestep, next(c), new_node))

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

            if current_node.previous_node is not None and current_node.previous_node.location[0] is None and current_node.previous_node.timestep == current_node.timestep:
                current_node = current_node.previous_node.previous_node
            else:
                current_node = current_node.previous_node

    return MDD


class MDD_node():
    def __init__(self, current_timestep, current_location, previous_node):
        self.timestep = current_timestep
        self.location = current_location
        self.previous_node = previous_node
