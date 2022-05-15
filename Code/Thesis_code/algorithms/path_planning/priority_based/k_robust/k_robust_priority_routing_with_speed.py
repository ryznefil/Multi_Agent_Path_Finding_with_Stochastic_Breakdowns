import math as m
from heapq import heappush, heappop
from itertools import count

import networkx as nx
from flatland.envs.agent_utils import RailAgentStatus as status

from Thesis_code.algorithms.path_planning.heuristics import distance_map_heuristic
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance
from Thesis_code.algorithms.path_planning.priority_based.k_robust.k_robust_basic_conflict_logger import robust_conflict_logger


class priority_planner_speed():
    def __init__(self, graph_representation, agent_states, binary_rail_representation, grid_width, grid_height, max_step=None, debug_print=False, robustness=0, optimize=True):
        # initialize the essentials
        self.max_multiplier = 8  # used for maximum step setting
        self.graph_representation = graph_representation
        self.agent_states = agent_states
        self.binary_rail_representation = binary_rail_representation
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.debug_print = debug_print
        self.robustness = robustness
        self.distance_map = None
        self.optimize = optimize

        if max_step is None:
            self.step_max = int(self.max_multiplier * 2 * (self.grid_width + self.grid_height + 20))
        else:
            self.step_max = max_step

        self.conflict_logger = robust_conflict_logger(self.grid_height, self.grid_width, self.binary_rail_representation, self.step_max)

        self.agent_steps_per_move = self._ceil_steps_per_move()
        self.agent_vertex_paths = {}  # final paths dictionary
        self.agent_action_dictionary = {}  # final action dictionaries
        self.agent_edge_paths = {}

        # TODO export profiling
        self.total_expansions = 0

    def _ceil_steps_per_move(self):
        """"For each agent determine the number of steps required for it to move from one tile to another"""
        speed_list = []
        for agent_state in self.agent_states:
            speed = agent_state.flatland_agent.speed_data['speed']
            speed_list.append(m.ceil(1 / speed))

        return speed_list

    def calculate_non_conflicting_paths(self, env_reference, agents_to_plan=None, heuristic_function=manhattan_distance, TPG = False):
        if heuristic_function == distance_map_heuristic:  # if the other heuristic function
            self.distance_map = env_reference.distance_map.get()  # make the env calculate the distance map

        """"Call to calculate A* shortest paths for all agents"""
        for agent in self.agent_states:  # assign empty path to all agents, those who are not planned will remain with empty path and do nothing
            self.agent_vertex_paths[agent.id] = []

        if agents_to_plan is None:  # Determine the set of planned agents, all if selected is None
            planned_agents = self.agent_states
        else:
            planned_agents = list(self.agent_states[i] for i in agents_to_plan)

        # calculate path for every agent
        for local_agent in planned_agents:
            if local_agent.flatland_agent.status == status.DONE_REMOVED:  # skip already planned agents, preparation for re-planning
                continue

            self.agent_vertex_paths[local_agent.id] = self._basic_priority_path_finding(G=self.graph_representation, agent_id=local_agent.id, heuristic=heuristic_function)  # calculate and assign path

        if TPG:
            return self.agent_vertex_paths, self.conflict_logger.occupation_info
        else:
            return self.agent_vertex_paths

    def calculate_ordered_paths(self, env_reference, agents_dictionary, agents_to_plan, heuristic_function=manhattan_distance, short=True, TPG = False):
        if heuristic_function == distance_map_heuristic:  # if the other heuristic function
            self.distance_map = env_reference.distance_map.get()  # make the env calculate the distance map

        """"Call to calculate A* shortest paths for all agents"""
        for agent in self.agent_states:  # assign empty path to all agents, those who are not planned will remain with empty path and do nothing
            self.agent_vertex_paths[agent.id] = []

        for dict_round in agents_dictionary.keys():
            dict_section = agents_dictionary[dict_round]

            while len(dict_section) != 0:
                if short:
                    shortest_path = m.inf
                    best_agent = m.inf
                else:
                    shortest_path = -m.inf
                    best_agent = -m.inf
                best_path = None
                for agent_id in dict_section:
                    path = self._modified_priority_path_finding(G=self.graph_representation, agent_id=agent_id, heuristic=heuristic_function)  # calculate and assign path
                    if len(path) == 0:
                        continue
                    len_path = self.path_len_meter(path)
                    if short:
                        if len_path < shortest_path:
                            shortest_path = len_path
                            best_agent = agent_id
                            best_path = path
                    else:
                        if len_path > shortest_path:
                            shortest_path = len_path
                            best_agent = agent_id
                            best_path = path
                        elif len_path == shortest_path and agent_id < best_agent:
                            shortest_path = len_path
                            best_agent = agent_id
                            best_path = path
                if best_path != None:
                    planned_agent = self.agent_states[best_agent]
                    agent_steps_per_move = self.agent_steps_per_move[best_agent]
                    agent_target = planned_agent.graph_target_vertex
                    self.agent_vertex_paths[best_agent] = best_path
                    self.conflict_logger.log_reservations(best_agent, best_path, agent_steps_per_move, agent_target, robust=self.robustness)
                    dict_section.remove(best_agent)
                else:  # none agent found path
                    dict_section = []

        if TPG:
            return self.agent_vertex_paths, self.conflict_logger.occupation_info
        else:
            return self.agent_vertex_paths

    def path_len_meter(self, agent_path):
        last_ts = agent_path[-2][1]
        entry_ts = 0
        while agent_path[entry_ts][0][0] is None:
            entry_ts += 1

        return last_ts - entry_ts

    def _basic_priority_path_finding(self, G, agent_id, heuristic):
        """"A* algorithm used to calculate the shortest non-blocking path for all agents, takes into account agent's speed"""
        if self.debug_print:
            print("Planning agent: ", agent_id)

        planned_agent = self.agent_states[agent_id]
        agent_steps_per_move = self.agent_steps_per_move[agent_id]
        agent_target = planned_agent.graph_target_vertex

        # TODO: for dynamic replanning later
        agent_speed = planned_agent.flatland_agent.speed_data['speed']
        initial_speed_fraction = planned_agent.flatland_agent.speed_data['position_fraction']

        push = heappush
        pop = heappop
        c = count()

        start = tuple((planned_agent.graph_current_vertex, 0))  # start node at time-step 0
        # queue = [(0, next(c), start, 0, None)]
        if self.optimize:
            queue = [(0, -m.inf, next(c), start, 0, None)]
        else:
            queue = [(0, next(c), start, 0, None)]
        enqueued = {}
        explored = {}

        while queue:
            if self.optimize:
                _, current_placement, _, current_node, dist, parent = pop(queue)
            else:
                _, _, current_node, dist, parent = pop(queue)

            if current_node in explored:  # explored the node in the given timestep
                # Skip bad paths that were enqueued before finding a better one
                qcost, h = enqueued[current_node]
                if qcost < dist:
                    continue

            explored[current_node] = parent  # add node to explored list and mark its parent for later path reverse

            current_vertex = current_node[0]  # tile coordinates of the current node
            current_node_timestep = current_node[1]  # time value of the current node

            if current_node_timestep >= self.step_max:  # Strugling to find a solution within the step limit => skip this train and plan other
                print("agent: ", agent_id, "OVERSTEPPED THE STEP LIMIT")
                return []  # TODO: At this point I assume no execution for this agent, hence empty list

            if current_node[0] == agent_target:  # Found the target
                path = [(current_node[0], current_node[1])]
                node = parent

                while node is not None:  # reconstruct the rest of the path and reserve spots where we move
                    path.append((node[0], node[1]))
                    node = explored[node]
                path.reverse()
                self.conflict_logger.log_reservations(agent_id, path, agent_steps_per_move, agent_target, robust=self.robustness)

                # print("agent_id: ", agent_id, "search expansions: ", len(explored))
                self.total_expansions += len(explored)
                return path

            for adj_node, w in G[current_node[0]].items():  # expand a new node
                if current_vertex[0] is None:
                    neighbor = tuple((adj_node, current_node_timestep + 1))  # put on the board and increment the time by one
                    edge_cost = w['weight']
                    if adj_node[0] is not None:
                        current_placement = - (current_node_timestep + 1)
                    else:
                        current_placement = - (m.inf)
                else:
                    if adj_node == current_vertex:  # waiting on the same spot, costs 1
                        neighbor = tuple((adj_node, current_node_timestep + 1))
                        edge_cost = w['weight']
                        # current_placement = - (current_node_timestep + 1)
                    else:  # move to a different tile, including dead end tile as the orientation changes
                        neighbor = tuple((adj_node, current_node_timestep + agent_steps_per_move))  # move to the next node and increment the time correspondingly
                        edge_cost = w['weight'] * agent_steps_per_move  # increment the cost of the edge by the number of steps made
                        # current_placement = - (current_node_timestep + agent_steps_per_move)

                if neighbor in explored:
                    continue

                if neighbor[0][0] is not None:  # FIXME check if we are not moving into conflicting position
                    # TODO: improve solution for wait, but should not be necessary ....
                    if self.conflict_logger.check_conflict(neighbor[0][0], neighbor[1] - 1, steps_per_move=agent_steps_per_move + 1,
                                                           robust=self.robustness):  # TODO: Check, again whether the reservations for speed 1 and partial are really different due to the engine limitations
                        continue

                ncost = dist + edge_cost  # increase the cost for the price of the taken edge
                if neighbor in enqueued:
                    qcost, h = enqueued[neighbor]
                    if qcost <= ncost:
                        continue  # already better in queue, do not push
                else:  # TODO: create a unified interface for heuristics
                    if heuristic == manhattan_distance:
                        if neighbor[0][0] != None:  # we are not waiting to place the train on the rails
                            h = heuristic(neighbor[0], agent_target, agent_steps_per_move)
                        else:  # train still in NONE location - calculate the distance from his grid start + 1 for the placement
                            h = heuristic(planned_agent.graph_starting_vertex, agent_target, agent_steps_per_move)
                    elif heuristic == distance_map_heuristic:
                        if neighbor[0][0] != None:  # we are not waiting to place the train on the rails
                            try:
                                h = heuristic(self.distance_map, agent_id, neighbor[0], agent_steps_per_move)
                            except:
                                continue  # the node may not be leading to the final destination! Skip
                        else:  # train still in NONE location - calculate the distance from his grid start + 1 for the placement
                            h = heuristic(self.distance_map, agent_id, planned_agent.graph_starting_vertex, agent_steps_per_move)
                    else:
                        raise ValueError

                enqueued[neighbor] = ncost, h
                if self.optimize:
                    push(queue, (ncost + h, current_placement, next(c), neighbor, ncost, current_node))  # push into the OPEN list
                else:
                    push(queue, (ncost + h, next(c), neighbor, ncost, current_node))  # push into the OPEN list
        raise nx.NetworkXNoPath("Node %s not reachable from %s" % (
        agent_target, start))  # TODO: deal with this as impossible routing happens in the non-complete algorithm, but remove only when we know that the algorithm works

    def _modified_priority_path_finding(self, G, agent_id, heuristic):
        """"A* algorithm used to calculate the shortest non-blocking path for all agents, takes into account agent's speed"""
        if self.debug_print:
            print("Planning agent: ", agent_id)

        planned_agent = self.agent_states[agent_id]
        agent_steps_per_move = self.agent_steps_per_move[agent_id]
        agent_target = planned_agent.graph_target_vertex

        # TODO: for dynamic replanning later
        agent_speed = planned_agent.flatland_agent.speed_data['speed']
        initial_speed_fraction = planned_agent.flatland_agent.speed_data['position_fraction']

        push = heappush
        pop = heappop
        c = count()

        start = tuple((planned_agent.graph_current_vertex, 0))  # start node at time-step 0
        if self.optimize:
            queue = [(0, -m.inf, next(c), start, 0, None)]
        else:
            queue = [(0, next(c), start, 0, None)]
        enqueued = {}
        explored = {}

        while queue:

            if self.optimize:
                _, current_placement, _, current_node, dist, parent = pop(queue)
            else:
                _, _, current_node, dist, parent = pop(queue)

            if current_node in explored:  # explored the node in the given timestep
                # Skip bad paths that were enqueued before finding a better one
                qcost, h = enqueued[current_node]
                if qcost < dist:
                    continue

            explored[current_node] = parent  # add node to explored list and mark its parent for later path reverse

            current_vertex = current_node[0]  # tile coordinates of the current node
            current_node_timestep = current_node[1]  # time value of the current node

            if current_node_timestep >= self.step_max:  # Strugling to find a solution within the step limit => skip this train and plan other
                print("agent: ", agent_id, "OVERSTEPPED THE STEP LIMIT")
                return []  # TODO: At this point I assume no execution for this agent, hence empty list

            if current_node[0] == agent_target:  # Found the target
                path = [(current_node[0], current_node[1])]
                node = parent

                while node is not None:  # reconstruct the rest of the path and reserve spots where we move
                    path.append((node[0], node[1]))
                    node = explored[node]
                path.reverse()
                # print("agent_id: ", agent_id, "search expansions: ", len(explored))
                self.total_expansions += len(explored)
                return path

            for adj_node, w in G[current_node[0]].items():  # expand a new node
                if current_vertex[0] is None:
                    neighbor = tuple((adj_node, current_node_timestep + 1))  # put on the board and increment the time by one
                    edge_cost = w['weight']
                    if self.optimize:
                        if adj_node[0] is not None:
                            current_placement = - (current_node_timestep + 1)
                        else:
                            current_placement = - (m.inf)
                else:
                    if adj_node == current_vertex:  # waiting on the same spot, costs 1
                        neighbor = tuple((adj_node, current_node_timestep + 1))
                        edge_cost = w['weight']
                    else:  # move to a different tile, including dead end tile as the orientation changes
                        neighbor = tuple((adj_node, current_node_timestep + agent_steps_per_move))  # move to the next node and increment the time correspondingly
                        edge_cost = w['weight'] * agent_steps_per_move  # increment the cost of the edge by the number of steps made

                if neighbor in explored:
                    continue

                if neighbor[0][0] is not None:  # FIXME check if we are not moving into conflicting position
                    # TODO: improve solution for wait, but should not be necessary ....
                    if self.conflict_logger.check_conflict(neighbor[0][0], neighbor[1] - 1, steps_per_move=agent_steps_per_move + 1,
                                                           robust=self.robustness):  # TODO: Check, again whether the reservations for speed 1 and partial are really different due to the engine limitations
                        continue

                ncost = dist + edge_cost  # increase the cost for the price of the taken edge
                if neighbor in enqueued:
                    qcost, h = enqueued[neighbor]
                    if qcost <= ncost:
                        continue  # already better in queue, do not push
                else:  # TODO: create a unified interface for heuristics
                    if heuristic == manhattan_distance:
                        if neighbor[0][0] != None:  # we are not waiting to place the train on the rails
                            h = heuristic(neighbor[0], agent_target, agent_steps_per_move)
                        else:  # train still in NONE location - calculate the distance from his grid start + 1 for the placement
                            h = heuristic(planned_agent.graph_starting_vertex, agent_target, agent_steps_per_move)
                    elif heuristic == distance_map_heuristic:
                        if neighbor[0][0] != None:  # we are not waiting to place the train on the rails
                            try:
                                h = heuristic(self.distance_map, agent_id, neighbor[0], agent_steps_per_move)
                            except:
                                continue  # the node may not be leading to the final destination! Skip
                        else:  # train still in NONE location - calculate the distance from his grid start + 1 for the placement
                            h = heuristic(self.distance_map, agent_id, planned_agent.graph_starting_vertex, agent_steps_per_move)
                    else:
                        raise ValueError

                enqueued[neighbor] = ncost, h
                if self.optimize:
                    push(queue, (ncost + h, current_placement, next(c), neighbor, ncost, current_node))  # push into the OPEN list
                else:
                    push(queue, (ncost + h, next(c), neighbor, ncost, current_node))  # push into the OPEN list

        raise nx.NetworkXNoPath("Node %s not reachable from %s" % (
        agent_target, start))  # TODO: deal with this as impossible routing happens in the non-complete algorithm, but remove only when we know that the algorithm works

# SAVE
#
# from heapq import heappush, heappop
# from itertools import count
# from flatland.envs.agent_utils import RailAgentStatus as status
# import math as m
# import numpy as np
# import time as t
#
# from BP.algorithms.path_planning.priority_based.k_robust.k_robust_basic_conflict_logger import basic_conflict_logger
# from BP.algorithms.path_planning.heuristics import manhattan_distance
# from BP.algorithms.path_planning.heuristics import distance_map_heuristic
# import flatland.envs.distance_map as distance_map
#
# import networkx as nx
#
# class priority_planner_speed():
#     def __init__(self, graph_representation, agent_states, binary_rail_representation, grid_width, grid_height, max_step = None, debug_print = False, robustness = 0):
#         # initialize the essentials
#         self.max_multiplier = 8  #used for maximum step setting
#         self.graph_representation = graph_representation
#         self.agent_states = agent_states
#         self.binary_rail_representation = binary_rail_representation
#         self.grid_height = grid_height
#         self.grid_width = grid_width
#         self.debug_print = debug_print
#         self.robustness = robustness
#         self.distance_map = None
#
#         if max_step is None:
#             self.step_max = int(self.max_multiplier * 2 * (self.grid_width + self.grid_height + 20))
#         else:
#             self.step_max = max_step
#
#         self.conflict_logger = basic_conflict_logger(self.grid_height, self.grid_width, self.binary_rail_representation, self.step_max)
#
#         self.agent_steps_per_move = self._ceil_steps_per_move()
#         self.agent_vertex_paths = {}  # final paths dictionary
#         self.agent_action_dictionary = {} # final action dictionaries
#         self.agent_edge_paths = {}
#
#
#         #TODO export profiling
#         self.total_expansions = 0
#
#     def _ceil_steps_per_move(self):
#         """"For each agent determine the number of steps required for it to move from one tile to another"""
#         speed_list = []
#         for agent_state in self.agent_states:
#             speed = agent_state.flatland_agent.speed_data['speed']
#             speed_list.append(m.ceil(1/speed))
#
#         return speed_list
#
#     def calculate_non_conflicting_paths(self, env_reference, agents_to_plan=None, heuristic_function=manhattan_distance):
#         if heuristic_function == distance_map_heuristic: # if the other heuristic function
#             self.distance_map = env_reference.distance_map.get()  # make the env calculate the distance map
#
#         """"Call to calculate A* shortest paths for all agents"""
#         for agent in self.agent_states: # assign empty path to all agents, those who are not planned will remain with empty path and do nothing
#             self.agent_vertex_paths[agent.id] = []
#
#         if agents_to_plan is None: #Determine the set of planned agents, all if selected is None
#             planned_agents = self.agent_states
#         else:
#             planned_agents = list(self.agent_states[i] for i in agents_to_plan)
#
#         # calculate path for every agent
#         for local_agent in planned_agents:
#             if local_agent.flatland_agent.status == status.DONE_REMOVED: # skip already planned agents, preparation for re-planning
#                 continue
#
#             self.agent_vertex_paths[local_agent.id] = self._basic_priority_path_finding(G=self.graph_representation, agent_id=local_agent.id, heuristic=heuristic_function) #calculate and assign path
#
#         return self.agent_vertex_paths
#
#     def _basic_priority_path_finding(self, G, agent_id, heuristic):
#         """"A* algorithm used to calculate the shortest non-blocking path for all agents, takes into account agent's speed"""
#         if self.debug_print:
#             print("Planning agent: ", agent_id)
#
#         planned_agent = self.agent_states[agent_id]
#         agent_steps_per_move = self.agent_steps_per_move[agent_id]
#         agent_target = planned_agent.graph_target_vertex
#
#         #TODO: for dynamic replanning later
#         agent_speed = planned_agent.flatland_agent.speed_data['speed']
#         initial_speed_fraction = planned_agent.flatland_agent.speed_data['position_fraction']
#
#         push = heappush
#         pop = heappop
#         c = count()
#
#         start = tuple((planned_agent.graph_current_vertex, 0))  # start node at time-step 0
#         queue = [(0, next(c), start, 0, None)]
#         # queue = [(0, 0, next(c), start, 0, None)]
#         enqueued = {}
#         explored = {}
#
#         while queue:
#             _, _, current_node, dist, parent = pop(queue)
#             # _ , current_placement,_, current_node, dist, parent = pop(queue)
#
#             if current_node in explored:  # explored the node in the given timestep
#                 # Skip bad paths that were enqueued before finding a better one
#                 qcost, h = enqueued[current_node]
#                 if qcost < dist:
#                      continue
#
#             explored[current_node] = parent  # add node to explored list and mark its parent for later path reverse
#
#             current_vertex = current_node[0]  # tile coordinates of the current node
#             current_node_timestep = current_node[1]  # time value of the current node
#
#             if current_node_timestep >= self.step_max:  # Strugling to find a solution within the step limit => skip this train and plan other
#                 print("agent: ", agent_id, "OVERSTEPPED THE STEP LIMIT")
#                 return [] #TODO: At this point I assume no execution for this agent, hence empty list
#
#             if current_node[0] == agent_target:  # Found the target
#                 path = [(current_node[0], current_node[1])]
#                 node = parent
#
#                 while node is not None: # reconstruct the rest of the path and reserve spots where we move
#                     path.append((node[0], node[1]))
#                     node = explored[node]
#                 path.reverse()
#                 self.conflict_logger.log_reservations(agent_id, path, agent_steps_per_move, agent_target, robust=self.robustness)
#
#                 # print("agent_id: ", agent_id, "search expansions: ", len(explored))
#                 self.total_expansions += len(explored)
#                 return path
#
#             for adj_node, w in G[current_node[0]].items():  # expand a new node
#                 if current_vertex[0] is None:
#                     neighbor = tuple((adj_node, current_node_timestep + 1)) # put on the board and increment the time by one
#                     edge_cost = w['weight']
#                     if adj_node[0] is not None:
#                         current_placement = - (current_node_timestep + 1)
#                     else:
#                         current_placement = - (m.inf)
#                 else:
#                     if adj_node == current_vertex: # waiting on the same spot, costs 1
#                         neighbor = tuple((adj_node, current_node_timestep + 1))
#                         edge_cost = w['weight']
#                     else: # move to a different tile, including dead end tile as the orientation changes
#                         neighbor = tuple((adj_node, current_node_timestep + agent_steps_per_move)) # move to the next node and increment the time correspondingly
#                         edge_cost = w['weight'] * agent_steps_per_move # increment the cost of the edge by the number of steps made
#
#                 if neighbor in explored:
#                     continue
#
#                 if neighbor[0][0] is not None: # FIXME check if we are not moving into conflicting position
#                     #TODO: improve solution for wait, but should not be necessary ....
#                     if self.conflict_logger.check_conflict(neighbor[0][0], neighbor[1]-1, steps_per_move=agent_steps_per_move+1, robust=self.robustness):  # TODO: Check, again whether the reservations for speed 1 and partial are really different due to the engine limitations
#                         continue
#
#                 ncost = dist + edge_cost  # increase the cost for the price of the taken edge
#                 if neighbor in enqueued:
#                     qcost, h = enqueued[neighbor]
#                     if qcost <= ncost:
#                         continue # already better in queue, do not push
#                 else: # TODO: create a unified interface for heuristics
#                     if heuristic == manhattan_distance:
#                         if neighbor[0][0] != None: #we are not waiting to place the train on the rails
#                             h = heuristic(neighbor[0], agent_target, agent_steps_per_move)
#                         else: #train still in NONE location - calculate the distance from his grid start + 1 for the placement
#                             h = heuristic(planned_agent.graph_starting_vertex, agent_target, agent_steps_per_move) + 1
#                     elif heuristic == distance_map_heuristic:
#                         if neighbor[0][0] != None:  # we are not waiting to place the train on the rails
#                             try:
#                                 h = heuristic(self.distance_map, agent_id, neighbor[0], agent_steps_per_move)
#                             except:
#                                 continue # the node may not be leading to the final destination! Skip
#                         else:  # train still in NONE location - calculate the distance from his grid start + 1 for the placement
#                             h = heuristic(self.distance_map, agent_id,planned_agent.graph_starting_vertex, agent_steps_per_move) + 1
#                     else:
#                         raise ValueError
#
#                 enqueued[neighbor] = ncost, h
#                 # push(queue, (ncost + h, current_placement, next(c), neighbor, ncost, current_node))  # push into the OPEN list
#                 push(queue, (ncost + h, next(c), neighbor, ncost, current_node)) #push into the OPEN list
#
#         raise nx.NetworkXNoPath("Node %s not reachable from %s" % (agent_target, start)) #TODO: deal with this as impossible routing happens in the non-complete algorithm, but remove only when we know that the algorithm works
#
