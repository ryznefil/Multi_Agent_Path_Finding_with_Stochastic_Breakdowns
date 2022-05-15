from Thesis_code.algorithms.path_planning.utilities import PriorityNonDuplicateHeap as ph


def identify_and_constraint_conflict(agent_states, grid_height, grid_width, binary_rail_representation, step_max, agents_to_plan, agent_paths, robustness=0):
    conflict_logger = conflict_finder(grid_height, grid_width, binary_rail_representation, step_max)  # create the conflict logger

    for agent_id in agents_to_plan:  # log conflicts for all planned agents TODO: Fix the performance later (not needed to have the priority queue)
        agent_steps_per_move = agent_states[agent_id].steps_per_move
        conflict_logger.log_reservations_advanced(agent_id, agent_paths[agent_id], agent_steps_per_move, agent_states[agent_id].graph_target_vertex, robust=robustness)

    first_conflict, conflict_count, conflict_queue = conflict_logger.get_count_and_first_conflict()  # first conflict (time, coordinates, [two agents])

    if conflict_count == 0:  # no conflict found
        return 0, None, None

    # conflict_type = conflict_logger.identify_conflict_type(first_conflict)
    # conflict_resolution = conflict_logger.resolve_conflict_by_split(first_conflict, conflict_type)
    # conflict_resolution =

    return conflict_count, first_conflict, conflict_resolution, conflict_type, conflict_queue


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
        return self.first_conflict, len(self.queue.queue), self.queue.queue

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
                    self.occupation_info[v1[0]][v1_time + i].append((agent_id, 'E'))
                    if len(self.occupation_info[v1[0]][v1_time + i]) >= 2:
                        self.advanced_log_conflict(v1_time + i, v1[0], v2[0], self.occupation_info[v1[0]][v1_time + i], agent_id)
            elif v1 != v2:  # agent is moving
                for i in range(agent_steps_per_move + robust):
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

            if self.first_conflict is None:
                self.first_conflict = (conflict_time, conflict_node, next_node, [conflict_log[0][0], current_agent])  # log agents in conflict also for later

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
        conflict_time, conflict_node, low_prio_next_node, conflict_agents = conflict

        return constraints

    # def identify_conflict_type(self, conflict):
    #     conflict_time, conflict_node, low_prio_next_node, conflict_agents = conflict
    #     higher_prio_agent = conflict_agents[0]
    #     lower_prio_agent = conflict_agents[1]
    #     log_node = self.occupation_info[conflict_node][conflict_time]
    #
    #     if (higher_prio_agent, 'E') in log_node and (lower_prio_agent, 'E') in log_node:
    #         # TODO: Resolve conflict
    #         # both agents cannot occupy at that time
    #         return Conflict_Types.VERTEX_ENTRY_CONFLICT
    #     elif (higher_prio_agent, 'E') in log_node and (lower_prio_agent, 'S') in log_node:
    #         if (higher_prio_agent, 'S') in self.occupation_info[low_prio_next_node][conflict_time]:   # if the higher priority agent leaves at that time the node of the next node of the low prio agent we have a conflict
    #             # TODO: Resolve conflict
    #             # higher priority agent cannot enter the conflict node at conflict time
    #             # lower priority agent cannot enter the next node at conflict time
    #             return Conflict_Types.EDGE_CONFLICT
    #         else: # delayed vertex conflict
    #             # TODO: Resolve conflict
    #             # higher priority agent cannot occupy the vertex at the conflict time
    #             # lower priority agent cannot occupy the vertex before (t-1)
    #             return Conflict_Types.VERTEX_OTHER_CONFLICT
    #     elif (higher_prio_agent, 'S') in log_node and (lower_prio_agent, 'E') in log_node:
    #         return Conflict_Types.VERTEX_TRIPLE_CONFLICT
    #     else:
    #         print("Non-existing error encountered")
    #         raise ValueError

    # def resolve_conflict_by_split(self, conflict, conflict_type):
    # conflict_time, conflict_node, low_prio_next_node, conflict_agents = conflict
    # higher_prio_agent = conflict_agents[0]
    # lower_prio_agent = conflict_agents[1]
    #
    # # TODO make automatic
    # if conflict_type == Conflict_Types.VERTEX_ENTRY_CONFLICT:
    #     constraint_lower_prio = (conflict_node, conflict_time, conflict_time + 1,lower_prio_agent)
    #     constraint_higher_prio = (conflict_node, conflict_time, conflict_time + 1, higher_prio_agent)
    # elif conflict_type == Conflict_Types.VERTEX_OTHER_CONFLICT:
    #     constraint_lower_prio = (conflict_node, conflict_time - 1, conflict_time, lower_prio_agent)
    #     constraint_higher_prio = (conflict_node, conflict_time, conflict_time + 1, higher_prio_agent)
    # elif conflict_type == Conflict_Types.EDGE_CONFLICT:
    #     constraint_lower_prio = (low_prio_next_node, conflict_time, conflict_time, lower_prio_agent)
    #     constraint_higher_prio = (conflict_node, conflict_time, conflict_time, higher_prio_agent)
    # elif conflict_type == Conflict_Types.VERTEX_TRIPLE_CONFLICT:
    #     constraint_lower_prio = (conflict_node, conflict_time, conflict_time + 1,      lower_prio_agent)
    #     constraint_higher_prio = (conflict_node, conflict_time - 1, conflict_time, higher_prio_agent)
    # else:
    #     print("Non-existing error encountered")
    #     raise ValueError
    #
    # return [[constraint_lower_prio_a, constraint_lower_prio_b], [constraint_higher_prio_a, constraint_higher_prio_b]]

    # BASIC LOGGING CODES ------------------------------------------------------------------------------------------------------------------------------------------------
    def log_conflict(self, conflict_time, conflict_node, conflicting_agent, current_agent):
        self.queue.push((conflict_time, conflict_node))  # log only the time and location into the conflict count
        if self.first_conflict is None:
            self.first_conflict = (conflict_time, conflict_node, [conflicting_agent, current_agent])  # log agents in conflict also for later

    def check_reservations(self, agent_id, agent_path, agent_steps_per_move, agent_target, robust=0):
        """"Log reservations based on the agent vertex path"""
        log_id = agent_id + 1
        for t in range(len(agent_path) - 1):  # minus 2 as we are always computing t+1
            v1 = agent_path[t][0]  # vertex
            v2 = agent_path[t + 1][0]
            v1_time = agent_path[t][1]  # time visited

            if v1[0] is None:  # do not reserve until placed on board
                continue
            elif v1[0] == agent_target[0]:  # agent reached the target, will be immediately removed
                for i in range(robust + 1):  # reserve over the planned entry and robustness period
                    if self.occupation_info[v1[0]][v1_time + i - 1] == log_id or self.occupation_info[v1[0]][v1_time + i - 1] == 0:
                        self.occupation_info[v1[0]][v1_time - 1 + i] = log_id
                    else:
                        self.log_conflict(v1_time + i - 1, v1[0], self.occupation_info[v1[0]][v1_time + i - 1] - 1, agent_id)
            elif v1 == v2:  # agent is waiting
                for i in range(agent_steps_per_move + robust + 1):
                    if self.occupation_info[v1[0]][v1_time + i - 1] == log_id or self.occupation_info[v1[0]][v1_time + i - 1] == 0:
                        self.occupation_info[v1[0]][v1_time + i - 1] = log_id
                    else:
                        self.log_conflict(v1_time + i - 1, v1[0], self.occupation_info[v1[0]][v1_time + i - 1] - 1, agent_id)
            elif v1 != v2:  # agent is moving
                for i in range(agent_steps_per_move + robust + 1):
                    if self.occupation_info[v1[0]][v1_time + i - 1] == 0 or self.occupation_info[v1[0]][v1_time + i - 1] == log_id:
                        self.occupation_info[v1[0]][v1_time + i - 1] = log_id
                    else:
                        self.log_conflict(v1_time + i - 1, v1[0], self.occupation_info[v1[0]][v1_time + i - 1] - 1, agent_id)
            else:
                print("ERROR: we should not be here!")
                raise ValueError

    def force_write_path(self, agent_id, agent_path, agent_steps_per_move, agent_target, robust=0):
        log_id = agent_id + 1
        for t in range(len(agent_path) - 1):  # minus 2 as we are always computing t+1
            v1 = agent_path[t][0]  # vertex
            v2 = agent_path[t + 1][0]
            v1_time = agent_path[t][1]  # time visited

            if v1[0] is None:  # do not reserve until placed on board
                continue
            elif v1[0] == agent_target[0]:  # agent reached the target, will be immediately removed
                for i in range(robust + 1):  # reserve over the planned entry and robustness period
                    self.occupation_info[v1[0]][v1_time - 1 + i] = log_id
            elif v1 == v2:  # agent is waiting
                for i in range(agent_steps_per_move + robust + 1):
                    self.occupation_info[v1[0]][v1_time + i - 1] = log_id
            elif v1 != v2:  # agent is moving
                for i in range(agent_steps_per_move + robust + 1):
                    self.occupation_info[v1[0]][v1_time + i - 1] = log_id
            else:
                print("ERROR: we should not be here!")
                raise ValueError
