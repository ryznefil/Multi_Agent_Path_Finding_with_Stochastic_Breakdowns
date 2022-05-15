from Thesis_code.algorithms.path_planning.utilities import PriorityNonDuplicateHeap as ph


def log_reservations(agent_states, grid_height, grid_width, binary_rail_representation, step_max, agents_to_plan, agent_paths, robustness=0):
    conflict_logger = conflict_finder(grid_height, grid_width, binary_rail_representation, step_max)  # create the conflict logger

    for agent_id in agents_to_plan:  # log conflicts for all planned agents TODO: Fix the performance later (not needed to have the priority queue)
        agent_steps_per_move = agent_states[agent_id].steps_per_move
        conflict_logger.log_reservations_advanced(agent_id, agent_paths[agent_id], agent_steps_per_move, agent_states[agent_id].graph_target_vertex, robust=robustness)

    return conflict_logger


def get_suitable_conflict(conflict_logger, MDDs):
    first_conflict = None
    semi_cardinal = None
    cardinal = None
    conflict_queue = conflict_logger.queue

    while conflict_queue.queue:
        (conflict_time, conflict_tile) = conflict_queue.pop()
        log = conflict_logger.occupation_info[conflict_tile][conflict_time]
        agents_mds_conflict_time = []
        agents = []
        for agent_log in log:
            agents.append(agent_log)
            agent_mds = MDDs[agent_log[0]]
            if len(agent_mds[conflict_time]) == 1:
                agents_mds_conflict_time.append(agent_log)  # save the ID of agent in cardinal conflict
            elif len(agent_mds[conflict_time]) == 0:
                raise ValueError

        if first_conflict is None:
            first_conflict = (conflict_time, conflict_tile, agents)

        # check if the conflict was cardinal
        if len(agents_mds_conflict_time) >= 2:
            return (conflict_time, conflict_tile, agents_mds_conflict_time, agents), semi_cardinal, first_conflict
        elif len(agents_mds_conflict_time) == 1 and semi_cardinal is None:
            semi_cardinal = (conflict_time, conflict_tile, agents_mds_conflict_time, agents)

        return cardinal, semi_cardinal, first_conflict


class conflict_finder():
    def __init__(self, h, w, array_nodes, step_max):
        self.h = h
        self.w = w
        self.array_nodes = array_nodes
        self.step_max = step_max

        self.queue = ph()
        self.occupation_info = self.initialize_advanced_time_occupancy_dictionary_basic(array_nodes, step_max)

    def initialize_advanced_time_occupancy_dictionary_basic(self, array_nodes, step_max):
        """"the basic 0, or agent id reservation dictionary"""
        occupation_info = {}
        for node in array_nodes:
            occupation_info[node] = [list() for j in range(step_max + 2)]
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
                self.occupation_info[v1[0]][last_node_time].append((agent_id, 'S', v2[0]))  # mark that we start leaving the node
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
            elif reservation_set[0][0] < reservation_set[1][0] and (reservation_set[0][1] == 'S' and reservation_set[1][1] == 'E'):
                return False
            elif reservation_set[0][0] > reservation_set[1][0] and (reservation_set[0][1] == 'E' and reservation_set[1][1] == 'S'):
                return False

        return True

    def create_constraint_tuple(self, conflict, agents_to_limit):
        conflict_time, conflict_node, _, _ = conflict

        constraints = []

        for non_constrained in agents_to_limit:
            tmp = []

            for constrained in agents_to_limit:
                if constrained[0] == non_constrained[0]:
                    continue
                elif constrained[1] == 'S':
                    tmp.append((conflict_node, conflict_time - 1, conflict_time, constrained[0]))
                elif constrained[1] == 'E':
                    tmp.append((conflict_node, conflict_time, conflict_time + 1, constrained[0]))
                else:
                    raise ValueError

            constraints.append(tmp)

        return constraints

    def create_constraint_many(self, conflict):
        conflict_time, conflict_node = conflict
        log = self.occupation_info[conflict_node][conflict_time]
        agents_in_conflict = []
        # for reservation in log:
        #     agents_in_conflict.append(reservation[0])

        constraints = []

        for non_constrained in log:
            tmp = []
            non_constrained_situation = non_constrained[1]
            for constrained in log:
                constrained_id = constrained[0]
                if constrained_id == non_constrained[0]:
                    continue
                if non_constrained_situation == 'S':
                    non_constrained_next_node = non_constrained[2]
                    if constrained[1] == 'S':
                        tmp.append((conflict_node, conflict_time - 1, conflict_time, constrained_id))
                    elif constrained[1] == 'E':
                        if (constrained_id, 'S') in self.occupation_info[non_constrained_next_node][conflict_time]:  # edge conflict!
                            tmp.append((conflict_node, conflict_time, conflict_time + 1, constrained_id))
                        else:  # vertex follow up conflict
                            tmp.append((conflict_node, conflict_time, conflict_time + 1, constrained_id))
                    else:
                        raise ValueError
                elif non_constrained_situation == 'E':
                    if constrained[1] == 'E':
                        tmp.append((conflict_node, conflict_time, conflict_time + 1, constrained_id))
                    elif constrained[1] == 'S':
                        constrained_next_node = constrained[2]
                        if (non_constrained[0], 'S') in self.occupation_info[constrained_next_node][conflict_time]:  # edge conflict
                            tmp.append((constrained_next_node, conflict_time, conflict_time + 1, constrained_id))
                        else:  # vertex follow up conflict
                            tmp.append((conflict_node, conflict_time - 1, conflict_time, constrained_id))
                    else:
                        raise ValueError
                else:
                    raise ValueError

                # if constrained[0] == non_constrained[0]:
                #     continue
                # elif constrained[1] == 'S':
                #     tmp.append((conflict_node, conflict_time - 1, conflict_time, constrained[0]))
                # elif constrained[1] == 'E':
                #     tmp.append((conflict_node, conflict_time, conflict_time + 1, constrained[0]))
                # else:
                #     raise ValueError

                # if constrained[0] == non_constrained[0]:
                #     continue
                # tmp.append((conflict_node, conflict_time, conflict_time + 1, constrained[0]))

            constraints.append(tmp)

        return constraints
