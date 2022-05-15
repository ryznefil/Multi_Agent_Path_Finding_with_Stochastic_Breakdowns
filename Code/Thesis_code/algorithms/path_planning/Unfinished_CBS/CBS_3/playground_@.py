import time as t

import Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_3.testing_cases as tc
from Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_3.CBS_high_level import CBS_high_level

if __name__ == "__main__":
    agent_count = 2
    h = 1
    w = 4
    max_steps = 100
    graph, agent_states, vertex_array = tc.straight_no_detour(w, agent_count)

    # Planning and execution --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    a = t.time()
    priority_planner = CBS_high_level(graph, agent_states, vertex_array, w, h, max_steps, debug_print=False, robustness=0)
    selected_agents = [i for i in range(agent_count)]
    agent_full_vertex_paths = priority_planner.high_level_search(selected_agents)
    b = t.time()
    c = b - a
    print(c)

    # conversion_type, agent_action_paths, edge_paths = path_convertors.convert_timed_vertex_path_to_actions(agent_full_vertex_paths, graph_representation)
    #
    # # path_processor = pp.PathProcessor(env)
    # # perc_rate, steps, cumulative_reward, normalized_reward = path_processor.run_basic_simulation(agent_given_actions=agent_action_paths, agent_vertex_debug=agent_full_vertex_paths, step_info=step_info, render=True, animation_sleep=0,
    # #                                                                                              selected_agents=selected_agents)
    # # priority_profiling_info = priority_planner.get_expansions_and_time()
    #
    # tpg = temporal_graph.create_temporal_plan_graph(agent_full_vertex_paths, graph_representation, selected_agents = selected_agents)
    # tmp_proc = temporal_graph_processor.PathProcessor(env)
    # perc_rate, steps, cumulative_reward, normalized_reward = tmp_proc.run_basic_simulation(tpg, step_info, render=True, selected_agents= selected_agents)
    # # priority_profiling_info = priority_planner.get_expansions_and_time()
    # # print_info(priority_profiling_info)
    # print(perc_rate, steps)
