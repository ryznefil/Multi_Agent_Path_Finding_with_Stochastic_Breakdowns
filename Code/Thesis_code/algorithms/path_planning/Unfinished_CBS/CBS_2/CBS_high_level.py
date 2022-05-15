from heapq import heappush, heappop
from itertools import count

import Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_2.CBS_low_level as CBS_low_level
import Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_2.CBS_utilities as CBS_utils
from Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_2.CBS_node import CBS_node
# from BP.algorithms.path_planning.CBS_2.alternative_conflict_solving import identify_and_constraint_conflict
from Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_2.testing_case_conflict_solving import identify_and_constraint_conflict
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance


class CBS_high_level():
    def __init__(self, graph_representation, agent_states, binary_rail_representation, grid_width, grid_height, max_step, debug_print=False, robustness=0):
        # initialize the essentials
        self.graph_representation = graph_representation
        self.agent_states = agent_states
        self.binary_rail_representation = binary_rail_representation
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.debug_print = debug_print
        self.step_max = max_step
        self.array_representation = self.array_from_graph()

        self.agent_vertex_paths = {}  # final paths dictionary

    def array_from_graph(self):
        array_repre = []
        nodes = self.graph_representation.nodes
        for node in nodes:
            if node[0] not in array_repre:
                array_repre.append(node[0])

        return array_repre

    def high_level_search(self, selected_agents=None):
        if selected_agents is None:
            agents_to_plan = [i for i in range(len(self.agent_states))]
        else:
            agents_to_plan = selected_agents

        start_agents_constraints_dictionary = CBS_utils.init_constraint_dict(agents_to_plan)
        _, start_agents_individual_paths = CBS_low_level.replan_agents(self.graph_representation, self.agent_states, agents_to_plan, start_agents_constraints_dictionary, self.step_max,
                                                                       manhattan_distance)
        start_path_cost = CBS_utils.sum_of_cost(start_agents_individual_paths, agents_to_plan)
        # conflict_count, conflicts, conflict_resolution, conflict_type, conflict_queue = identify_and_constraint_conflict(self.agent_states, self.grid_height, self.grid_width, self.binary_rail_representation, self.step_max, agents_to_plan, start_agents_individual_paths, robustness=0)
        start_node = CBS_node(start_agents_individual_paths, start_agents_constraints_dictionary, None, None, start_path_cost, None, None, None)

        fifo_order = count()
        queue = []
        # heappush(queue, (start_path_cost, conflict_count, fifo_order, start_node))
        heappush(queue, (start_path_cost, fifo_order, start_node))
        counter_expansions = 0
        explored_dictionaries = []

        while queue:
            counter_expansions += 1
            _, fifo_counter, current_node = heappop(queue)

            explored_dictionaries.append(current_node.agent_constraints)

            conflict_count, conflicts, conflict_resolution, conflict_type, _ = identify_and_constraint_conflict(self.agent_states, self.grid_height, self.grid_width, self.array_representation,
                                                                                                                self.step_max, agents_to_plan,
                                                                                                                current_node.agent_paths, robustness=0)

            if conflict_count == 0:
                print(CBS_utils.final_cost(current_node.agent_paths, agents_to_plan))
                return current_node.agent_paths

            print("Current conflict: ", conflicts, "current cost: ",
                  current_node.total_cost, "Current expansion: ", counter_expansions, "current constraints: ", conflict_resolution, "conflict count: ", conflict_count)

            for constraints in conflict_resolution:
                constrained_agents = []
                for limitation in constraints:
                    constrained_agents.append(limitation[3])
                new_constraint_dictionary = CBS_utils.extend_constraint_dictionary(agents_to_plan, current_node.agent_constraints, constrained_agents, constraints)
                if new_constraint_dictionary in explored_dictionaries:
                    print("ALREADY SEEN BRO")
                    continue
                _, replanned_path = CBS_low_level.replan_agents(self.graph_representation, self.agent_states, constrained_agents, new_constraint_dictionary, self.step_max, manhattan_distance)
                new_agent_paths = CBS_utils.replance_old_paths(replanned_path, current_node.agent_paths, agents_to_plan, constrained_agents)
                # new_conflict_count, new_conflicts, new_conflict_resolution, new_conflict_type, new_conflict_queue = identify_and_constraint_conflict(self.agent_states, self.grid_height, self.grid_width, self.binary_rail_representation, self.step_max, agents_to_plan, new_agent_paths, robustness=0)
                # new_conflict_count, new_conflicts, new_conflict_resolution, new_conflict_type, new_conflict_queue = identify_and_constraint_conflict(self.agent_states, self.grid_height, self.grid_width, self.array_representation, self.step_max,
                #                                                                                                                                      agents_to_plan, new_agent_paths, robustness=0)
                new_cost = CBS_utils.sum_of_cost(new_agent_paths, agents_to_plan)
                # if new_conflict_count == 0:
                #     print(new_cost)
                #     return new_agent_paths
                # new_node = CBS_node(new_agent_paths, new_constraint_dictionary, new_conflicts, new_conflict_resolution, new_cost, new_conflict_type, new_conflict_count, new_conflict_queue)
                new_node = CBS_node(new_agent_paths, new_constraint_dictionary, None, None, new_cost, None, None, None)
                # heappush(queue, (new_cost, new_conflict_count, next(fifo_order), new_node))
                heappush(queue, (new_cost, next(fifo_order), new_node))

        print("Way not found")
        raise ValueError
