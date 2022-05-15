from heapq import heappush, heappop
from itertools import count

import Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_3.CBS_low_level as CBS_low_level
import Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_3.CBS_utilities as CBS_utils
# from BP.algorithms.path_planning.CBS_3.alternative_conflict_solving import identify_and_constraint_conflict
import Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_3.testing_case_conflict_solving as conflict_solver
from Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_3.CBS_node import CBS_node
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance


class CBS_high_level():
    def __init__(self, env, graph_representation, agent_states, binary_rail_representation, grid_width, grid_height, max_step, debug_print=False, robustness=0):
        # initialize the essentials
        self.env = env
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
        _, start_agents_individual_paths, start_MDDs = CBS_low_level.replan_agents(self.graph_representation, self.agent_states, agents_to_plan, start_agents_constraints_dictionary, self.step_max,
                                                                                   manhattan_distance, self.env.distance_map.get())
        start_path_cost = CBS_utils.sum_of_cost(start_agents_individual_paths, agents_to_plan)
        start_node = CBS_node(start_agents_individual_paths, start_agents_constraints_dictionary, start_path_cost, MDDs=start_MDDs)

        fifo_order = count()
        queue = []
        heappush(queue, (start_path_cost, fifo_order, start_node))
        counter_expansions = 0
        explored_dictionaries = []

        while queue:
            counter_expansions += 1
            _, fifo_counter, current_node = heappop(queue)

            explored_dictionaries.append(current_node.agent_constraints)

            # log the reservations
            conflict_avoidance_table = conflict_solver.log_reservations(self.agent_states, self.grid_height, self.grid_width, self.array_representation, self.step_max, agents_to_plan,
                                                                        current_node.agent_paths, robustness=0)

            if len(conflict_avoidance_table.queue.content_set) == 0:
                print(CBS_utils.final_cost(current_node.agent_paths, agents_to_plan))
                return current_node.agent_paths

            # look for a cardinal or semi cardinal conflict
            cardinal, semi_cardinal, non_cardinal = conflict_solver.get_suitable_conflict(conflict_avoidance_table, current_node.MDDs)

            conflict = None
            conflict_resolution = None
            if cardinal is not None:
                conflict = cardinal
                conflict_resolution = conflict_avoidance_table.create_constraint_tuple(conflict, conflict[2])
                # resolve this
            elif semi_cardinal is not None:
                conflict = semi_cardinal
                conflict_resolution = None
                # resolve this
            else:
                conflict = non_cardinal
                conflict_resolution = None
                # if non-cardinal try to bypass

            print("Current conflict: ", conflict, "current cost: ", current_node.total_cost, "Current expansion: ", counter_expansions)

            for constraints in conflict_resolution:
                constrained_agents = []
                for limitation in constraints:
                    constrained_agents.append(limitation[3])
                new_constraint_dictionary = CBS_utils.extend_constraint_dictionary(agents_to_plan, current_node.agent_constraints, constrained_agents, constraints)
                if new_constraint_dictionary in explored_dictionaries:
                    print("ALREADY SEEN BRO")
                    continue
                _, replanned_path, replanned_MDDs = CBS_low_level.replan_agents(self.graph_representation, self.agent_states, constrained_agents, new_constraint_dictionary, self.step_max,
                                                                                manhattan_distance, self.env.distance_map.get())
                new_agent_paths = CBS_utils.replance_old_paths(replanned_path, current_node.agent_paths, agents_to_plan, constrained_agents)
                new_MDDs = CBS_utils.replance_old_MDD(replanned_MDDs, current_node.MDDs, agents_to_plan, constrained_agents)
                new_cost = CBS_utils.sum_of_cost(new_agent_paths, agents_to_plan)
                new_node = CBS_node(new_agent_paths, new_constraint_dictionary, new_cost, new_MDDs)
                heappush(queue, (new_cost, next(fifo_order), new_node))

        print("Way not found")
        raise ValueError
