import numpy as np


class robust_conflict_logger():
    def __init__(self, h, w, binary, step_max):
        self.h = h
        self.w = w
        self.step_max = step_max
        self.binary_g = binary
        self.occupation_info = self.initialize_time_occupancy_dictionary_basic()

    def initialize_time_occupancy_dictionary_basic(self):
        """"the basic 0,1 reservation disctionary"""
        occupation_info = {}
        for i in range(self.h):
            for j in range(self.w):
                if self.binary_g[i][j] != 0:
                    occupation_info[(i, j)] = np.zeros(self.step_max + 20)
        return occupation_info

    def log_reservations(self, agent_id, agent_path, agent_steps_per_move, agent_target, robust=0):
        """"Log reservations based on the agent vertex path"""
        log_id = agent_id + 1
        for t in range(len(agent_path) - 1):  # minus 2 as we are always computing t+1
            v1 = agent_path[t][0]  # vertex
            v2 = agent_path[t + 1][0]
            v1_time = agent_path[t][1]  # time visited
            v2_time = agent_path[t + 1][1]

            if v1[0] is None:  # do not reserve until placed on board
                continue
            elif v1[0] == agent_target[0]:  # agent reached the target, will be immediately removed
                if self.occupation_info[v1[0]][v1_time - 1] == log_id or self.occupation_info[v1[0]][v1_time - 1] == 0:
                    for i in range(robust + 1):  # reserve over the planned entry and robustness period
                        self.occupation_info[v1[0]][v1_time - 1 + i] = log_id
                else:
                    print("ERROR: Crossing planned path!")
            elif v1 == v2:  # agent is waiting
                for i in range(agent_steps_per_move + robust + 1):
                    if self.occupation_info[v1[0]][v1_time + i - 1] == log_id or self.occupation_info[v1[0]][v1_time + i - 1] == 0:
                        self.occupation_info[v1[0]][v1_time + i - 1] = log_id
                    else:
                        print("ERROR: Crossing planned path!")
            elif v1 != v2:  # agent is moving
                for i in range(agent_steps_per_move + robust + 1):
                    if self.occupation_info[v1[0]][v1_time + i - 1] == 0 or self.occupation_info[v1[0]][v1_time + i - 1] == log_id:
                        self.occupation_info[v1[0]][v1_time + i - 1] = log_id
                    else:
                        print("ERROR: Crossing planned path!")
            else:
                print("ERROR: we should not be here!")
                raise ValueError

    def check_conflict(self, coordinates, timestep, steps_per_move, robust=0):
        """"check conflicts when enqueing node"""
        for i in range(steps_per_move + robust):
            if self.occupation_info[coordinates][timestep + i] != 0:
                return True

        return False
