import time as t

from Thesis_code.algorithms.path_planning.utilities import PriorityNonDuplicateHeap as ph


def identify_and_constraint_conflict(agent_states, grid_height, grid_width, binary_rail_representation, step_max, agents_to_plan, agent_paths, robustness=0):
    a = t.time()
    conflict_logger = conflict_finder(grid_height, grid_width, binary_rail_representation, step_max)  # create the conflict logger
    b = t.time()
    c = b - a
    print("Creating the reservation dictionary took: ", c)

    a = t.time()
    for agent_id in agents_to_plan:  # log conflicts for all planned agents TODO: Fix the performance later (not needed to have the priority queue)
        agent_steps_per_move = agent_states[agent_id].steps_per_move
        conflict_logger.log_reservations_advanced(agent_id, agent_paths[agent_id], agent_steps_per_move, agent_states[agent_id].graph_target_vertex, robust=robustness)
    b = t.time()
    c = b - a
    print("Logging conflicts took: ", c)

    conflict_count, conflict_queue, first_conflict = conflict_logger.get_count_and_first_conflict()  # first conflict (time, coordinates, [two agents])

    a = t.time()
    if conflict_count == 0:  # no conflict found
        return 0, None, None, None, conflict_queue

    conflict_resolution = conflict_logger.create_constraint(first_conflict)
    b = t.time()
    c = b - a
    print("Resolving conflicts took: ", c)

    return conflict_count, first_conflict, conflict_resolution, None, conflict_queue


class conflict_finder():
    def __init__(self, h, w, binary, step_max):
        self.h = h
        self.w = w
        self.binary = binary
        self.step_max = step_max

        self.queue = ph()
        self.occupation_info = self.initialize_advanced_time_occupancy_dictionary_basic(w, h, binary, step_max)
        self.first_conflict = None  # first encountered conflict

    def initialize_basic_time_occupancy_dictionary_basic(self, w, h, binary_g, step_max):
        """"the basic 0, or agent id reservation dictionary"""
        occupation_info = {}
        for i in range(h):
            for j in range(w):
                if binary_g[i][j] != 0:
                    occupation_info[(i, j)] = [0 for j in range(step_max + 2)]
        return occupation_info

    def initialize_advanced_time_occupancy_dictionary_basic(self, w, h, binary_g, step_max):
        """"the basic 0, or agent id reservation dictionary"""
        occupation_info = {}
        for i in range(h):
            for j in range(w):
                if binary_g[i][j] != 0:
                    occupation_info[(i, j)] = [list() for j in range(step_max + 2)]
        return occupation_info

    def get_count_and_first_conflict(self):
        return len(self.queue.queue), self.queue.queue, self.queue.pop()

    def log_reservations_advanced(self, agent_id, agent_path, agent_steps_per_move, agent_target, robust=0):
        """"Log reservations based on the agent vertex path"""
        for t in range(len(agent_path) - 1):  # minus 2 as we are always computing t+1
            v1 = agent_path[t][0]  # current vertex
            v2 = agent_path[t + 1][0]  # the next occupied vertex
            v1_time = agent_path[t][1]  # time visited

            if v1[0] is None:  # do not reserve until placed on board
                continue
            elif v1[0] == agent_target[0]:  # agent reached the target, will be immediately removed
                for i in range(robust + 1):  # reserve over the planned entry and robustness period
                    self.occupation_info[v1[0]][v1_time + i].append((agent_id, 'E'))
                    if len(self.occupation_info[v1[0]][v1_time + i]) >= 2:
                        self.advanced_log_conflict(v1_time + i, v1[0], v2[0], self.occupation_info[v1[0]][v1_time + i], agent_id)
            elif v1 == v2:  # agent is waiting
                for i in range(agent_steps_per_move + robust + 1):
                    if (agent_id, 'E') not in self.occupation_info[v1[0]][v1_time + i]:
                        self.occupation_info[v1[0]][v1_time + i].append((agent_id, 'E'))
                        if len(self.occupation_info[v1[0]][v1_time + i]) >= 2:
                            self.advanced_log_conflict(v1_time + i, v1[0], v2[0], self.occupation_info[v1[0]][v1_time + i], agent_id)
            elif v1 != v2:  # agent is moving
                for i in range(agent_steps_per_move + robust):
                    if (agent_id, 'E') not in self.occupation_info[v1[0]][v1_time + i]:
                        self.occupation_info[v1[0]][v1_time + i].append((agent_id, 'E'))  # mark that we occupy it at the end for several rounds except the last when we leave
                        if len(self.occupation_info[v1[0]][v1_time + i]) >= 2:
                            self.advanced_log_conflict(v1_time + i, v1[0], v2[0], self.occupation_info[v1[0]][v1_time + i], agent_id)

                last_node_time = v1_time + robust + agent_steps_per_move
                self.occupation_info[v1[0]][last_node_time].append((agent_id, 'S'))  # mark that we start leaving the node
                if len(self.occupation_info[v1[0]][last_node_time]) >= 2:
                    self.advanced_log_conflict(last_node_time, v1[0], v2[0], self.occupation_info[v1[0]][last_node_time], agent_id)
            else:
                print("ERROR: we should not be here!")
                raise ValueError

    def advanced_log_conflict(self, conflict_time, conflict_node, next_node, conflict_log, current_agent):
        if self.conflict_validity((conflict_time, conflict_node)):
            self.queue.push((conflict_time, conflict_node))  # log only the time and location into the conflict count

    def conflict_validity(self, conflict):
        """"Based on the reservation dictionary check if the conflict is still present"""
        if conflict == None:
            return False

        (timestamp, position) = conflict

        if len(self.occupation_info[position][timestamp]) <= 1:
            return False

        if len(self.occupation_info[position][timestamp]) == 2:
            reservation_set = self.occupation_info[position][timestamp]
            if reservation_set[0][0] == reservation_set[1][0]:
                return False
            # first two cases are the situation where conflicts do not happen given the train priorities and action
            # elif reservation_set[0][0] < reservation_set[1][0] and (reservation_set[0][1] == 'S' and reservation_set[1][1] == 'E'):
            #     return False
            # elif reservation_set[0][0] > reservation_set[1][0] and (reservation_set[0][1] == 'E' and reservation_set[1][1] == 'S'):
            #     return False

        return True

    def create_constraint(self, conflict):
        conflict_time, conflict_node = conflict
        log = self.occupation_info[conflict_node][conflict_time]
        agents_in_conflict = []
        for reservation in log:
            agents_in_conflict.append(reservation[0])

        constraints = []

        for non_constrained in agents_in_conflict:
            tmp = []
            for constrained in agents_in_conflict:
                if constrained == non_constrained:
                    continue
                tmp.append(constrained)
            constraints.append((conflict_node, conflict_time, conflict_time + 1, tmp))

        return constraints
