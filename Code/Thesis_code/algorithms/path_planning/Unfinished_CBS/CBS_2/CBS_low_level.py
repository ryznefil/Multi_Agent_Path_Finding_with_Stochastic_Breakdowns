from heapq import heappush, heappop
from itertools import count


def replan_agents(graph_representation, agent_states, constrained_agents, constraint_dictionary, max_step, heuristic):
    """Replan individual paths for selected agents that are newly constrained"""
    new_paths = {}
    new_MDDs = {}

    for agent_id in constrained_agents:
        new_path = low_level_search_single_agent(graph_representation, agent_states[agent_id], constraint_dictionary[agent_id], heuristic, max_step, False)
        new_paths[agent_id] = new_path

    return True, new_paths


def low_level_search_single_agent(graph, agent_state, agent_forbidden_nodes, heuristic, step_max, debug_print=False):
    """"A* algorithm used to calculate the shortest non-blocking path for all agents, takes into account agent's speed"""
    agent_id = agent_state.id
    if debug_print:
        print("Planning agent: ", agent_id)
    planned_agent = agent_state
    agent_target = planned_agent.graph_target_vertex
    agent_steps_per_move = agent_state.steps_per_move

    push = heappush
    pop = heappop
    c = count()

    queue = [(0, next(c), tuple((planned_agent.graph_current_vertex, 0)), 0, None)]
    enqueued = {}
    explored = {}

    while queue:
        _, _, current_node, dist, parent = pop(queue)

        if current_node in explored:  # explored the node in the given time-step
            continue

        explored[current_node] = parent  # add node to explored list and mark its parent for later path reverse

        current_vertex = current_node[0]  # tile coordinates of the current node, including orientation
        current_node_timestep = current_node[1]  # time value of the current node

        if current_node_timestep >= step_max:  # Strugling to find a solution within the step limit => skip this train and plan other
            print("agent: ", agent_id, "OVERSTEPPED THE STEP LIMIT")
            return []  # TODO: At this point I assume no execution for this agent, hence empty list

        if current_node[0] == agent_target:  # Found the target
            path = [current_node]
            node = parent

            while node is not None:  # reconstruct the rest of the path and reserve spots where we move
                path.append(node)
                node = explored[node]
            path.reverse()
            return path

        for adj_node, w in graph[current_node[0]].items():  # expand a new node
            if current_vertex[0] is None:
                if adj_node == current_vertex:  # waiting on the same spot, costs 1
                    neighbor = tuple((adj_node, current_node_timestep + 1))
                    edge_cost = w['weight']
                else:  # first PUT on board happens immediately
                    neighbor = tuple((adj_node, current_node_timestep))  # move to the next node and increment the time correspondingly
                    edge_cost = w['weight']
                    # increment the cost of the edge by the number of steps made
            else:
                if adj_node == current_vertex:  # waiting on the same spot, costs 1
                    neighbor = tuple((adj_node, current_node_timestep + 1))
                    edge_cost = w['weight']
                else:  # move to a different tile, including dead end tile as the orientation changes
                    neighbor = tuple((adj_node, current_node_timestep + agent_steps_per_move))  # move to the next node and increment the time correspondingly
                    edge_cost = w['weight'] * agent_steps_per_move  # increment the cost of the edge by the number of steps made

            if neighbor in explored:
                continue

            prevented = False
            if neighbor[0][0] is not None:  # FIXME check if we are not moving into conflicting position
                for t in range(0, agent_steps_per_move + 1):
                    if (neighbor[0][0], neighbor[1] + t) in agent_forbidden_nodes:
                        prevented = True
                        break

            if prevented:
                continue

            ncost = dist + edge_cost  # increase the cost for the price of the taken edge
            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
                if qcost <= ncost:
                    continue  # already better in queue, do not push
            else:
                if neighbor[0][0] != None:  # we are not waiting to place the train on the rails
                    h = heuristic(neighbor[0], agent_target, agent_steps_per_move)
                else:  # train still in NONE location - calculate the distance from his grid start + 1 for the placement
                    h = heuristic(planned_agent.graph_starting_vertex, agent_target, agent_steps_per_move) - 1

            enqueued[neighbor] = ncost, h
            push(queue, (ncost + h, next(c), neighbor, ncost, current_node))  # push into the OPEN list

    print("GOAL NOT REACHABLE!")
    raise ValueError
