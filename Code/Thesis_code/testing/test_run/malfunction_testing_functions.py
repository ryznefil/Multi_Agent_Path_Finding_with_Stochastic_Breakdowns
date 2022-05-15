import os
import pickle
import time as t
import numpy as np

from flatland.envs.malfunction_generators import malfunction_from_file
from flatland.envs.malfunction_generators import malfunction_from_params
from flatland.envs.malfunction_generators import no_malfunction_generator
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_file
from flatland.envs.schedule_generators import schedule_from_file
from flatland.utils.rendertools import RenderTool, AgentRenderVariant

from Thesis_code.algorithms.path_execution import temporal_graph_processor
from Thesis_code.algorithms.path_planning import agent_ordering as ordering
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance
from Thesis_code.algorithms.path_planning.priority_based.k_robust import k_robust_priority_routing_with_speed
from Thesis_code.algorithms.path_to_action_convertors import temporal_graph
# IMPORT ALL NECCESSARY METHODS FROM MY IMPLEMENTATION
from Thesis_code.observations import custom_observations
from Thesis_code.testing.test_run.ordering_types import ordering_types


def replace_agent_speed(env, speed_data, agent_states):
    speeds, speed_prob = speed_data
    agents = env.agents
    rng = np.random.RandomState(0)
    new_speeds = rng.choice(speeds, len(agents), speed_prob)

    for agent in agents:
        agent.speed_data['speed'] = new_speeds[agent.handle]
        agent_states[agent.handle].update_agent(agent)


def append_to_dict(final_dict, content_dict):
    for key in final_dict.keys():
        final_dict[key].append(content_dict[key])


def average_out_dict(results_dict):
    for key in results_dict.keys():
        results_dict[key] = list_avg(results_dict[key])
    return results_dict


def create_multi_dict(malfunctions_scenarios):
    new_dict = {}
    for i in range(malfunctions_scenarios):
        new_dict[i] = []
    return new_dict


def list_avg(inserted_list):
    return sum(inserted_list) / len(inserted_list)


def SIC(agent_vertex_paths):
    SIC = 0
    for agent_id in range(len(agent_vertex_paths)):
        if len(agent_vertex_paths[agent_id]) == 0:
            continue
        SIC += (agent_vertex_paths[agent_id][-2][1] - 1)
    return SIC


def makespan(agent_vertex_paths):
    MS = 0
    for agent_id in range(len(agent_vertex_paths)):
        if len(agent_vertex_paths[agent_id]) == 0:
            continue
        MS = max(agent_vertex_paths[agent_id][-2][1] - 1, MS)
    return MS


def print_info(output_info):
    print("Total planning time: ", output_info[0])
    print("Total expanded nodes: ", output_info[1])
    print("Deepest expaded node: ", output_info[2])
    agent_dict = output_info[3]
    for i in range(len(agent_dict)):
        note = agent_dict[i]
        print("Agent ", i, "took: ", note[0], " expanded: ", note[1], " deepest exapansion: ", note[2])


def load_env(observations_object, test_name, seed, malfunctions=False, malfunction_generator=None):
    if not malfunctions:
        env = RailEnv(width=1, height=1, rail_generator=rail_from_file(test_name),
                      schedule_generator=schedule_from_file(test_name),
                      remove_agents_at_target=True,
                      malfunction_generator_and_process_data=no_malfunction_generator(),
                      obs_builder_object=observations_object,
                      random_seed=seed)
    else:
        if malfunction_generator is None:
            env = RailEnv(width=1, height=1, rail_generator=rail_from_file(test_name),
                          schedule_generator=schedule_from_file(test_name),
                          remove_agents_at_target=True,
                          malfunction_generator_and_process_data=malfunction_from_file(test_name),
                          obs_builder_object=observations_object,
                          random_seed=seed)
        else:
            env = RailEnv(width=1, height=1, rail_generator=rail_from_file(test_name),
                          schedule_generator=schedule_from_file(test_name),
                          remove_agents_at_target=True,
                          malfunction_generator_and_process_data=malfunction_from_params(malfunction_generator),
                          obs_builder_object=observations_object,
                          random_seed=seed)

    observation, step_info = env.reset()
    env_renderer = RenderTool(env, gl="PILSVG",
                              agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS_AND_BOX,
                              show_debug=False,
                              screen_height=1000,  # Adjust these parameters to fit your resolution
                              screen_width=1000)  # Adjust these parameters to fit your resolution

    return env, env_renderer, observation, step_info


def run_testing(ordering_type, file_name, source_location, stoch_dict, heuristic, seeed_rounds, speed_data = None):
    run = 0
    comp = create_multi_dict(len(stoch_dict))
    exp = create_multi_dict(len(stoch_dict))
    SIC = create_multi_dict(len(stoch_dict))
    MS = create_multi_dict(len(stoch_dict))
    plan_RT = create_multi_dict(len(stoch_dict))
    tpg_RT = create_multi_dict(len(stoch_dict))
    malf_ct = create_multi_dict(len(stoch_dict))
    malf_dur = create_multi_dict(len(stoch_dict))

    test_env_files_folder = source_location
    # test_env_files_folder = "C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/Flatland_official_test_envs"
    for test_id in range(12):  # Set to the expected number of cases per forlder
        test_name = test_env_files_folder + "/Level_" + str(test_id) + ".pkl"

        # check if the test case exists, else continue
        try:
            os.stat(test_name)
        except:
            continue

        print(str(ordering_type), ": ", test_name)

        second_round_runs = seeed_rounds

        avg_comp = create_multi_dict(len(stoch_dict))
        avg_exp = create_multi_dict(len(stoch_dict))
        avg_SIC = create_multi_dict(len(stoch_dict))
        avg_MS = create_multi_dict(len(stoch_dict))
        avg_plan_RT = create_multi_dict(len(stoch_dict))
        avg_tpg_RT = create_multi_dict(len(stoch_dict))
        avg_malf_ct = create_multi_dict(len(stoch_dict))
        avg_malf_dur = create_multi_dict(len(stoch_dict))

        private_observation_builder = custom_observations.CustomGlobalObservation()
        env, env_renderer, observation, step_info = load_env(private_observation_builder, test_name, seed=0, malfunctions=False, malfunction_generator=None)

        # CALCULATE PATHS AND THE TPG ------ THIS IS THE SAME FOR ALL!
        # try:
        init_obs = env.obs_builder.get_many()
        agents_states = init_obs[1]
        max_steps = env._max_episode_steps
        graph_representation = init_obs[0]

        if speed_data is not None:
            replace_agent_speed(env, speed_data, agents_states) # REPLACE THE AGENTS SPEEDS BY NEWLY GENERATED ONES

        # order agents - prepared for different speeds
        if ordering_type == ordering_types.FLATLAND:
            selected_agents = [i for i in range(len(agents_states))]
        elif ordering_type == ordering_types.FAST_FIRST:
            selected_agents = ordering.agent_speed_and_position_sort(env, agents_states, reversed=False)
        elif ordering_type == ordering_types.SLOW_FIRST:
            selected_agents = ordering.agent_speed_and_position_sort(env, agents_states, reversed=True)
        elif ordering_type == ordering_types.CLOSE_FIRST:
            selected_agents = ordering.agent_speed_and_position_sort_no_speed(env, agents_states, False)
        elif ordering_type == ordering_types.REMOTE_FIRST:
            selected_agents = ordering.agent_speed_and_position_sort_no_speed(env, agents_states, True)

        priority_planner = k_robust_priority_routing_with_speed.priority_planner_speed(graph_representation, agents_states, env.distance_map.rail.grid, env.width, env.height, max_steps,
                                                                                       debug_print=False, robustness=0, optimize=True)
        t1 = t.time()
        agent_full_vertex_paths, reservation_table = priority_planner.calculate_non_conflicting_paths(agents_to_plan=selected_agents, env_reference=env, heuristic_function=heuristic, TPG = True)
        t2 = t.time()
        t_plan = t2 - t1
        x = priority_planner.total_expansions

        t1 = t.time()
        tpg = temporal_graph.create_temporal_plan_graph(agent_full_vertex_paths, graph_representation, reservation_table)
        t2 = t.time()
        t_tpg = t2 - t1

        # SIMULATE THE RUNTIME - different for different malfunctions
        for seed in range(second_round_runs):
            print(str(ordering_type), "run: ", run, "seed: ", seed)
            for mf_schdl in range(len(stoch_dict)):  # range(1, len(stoch_dict)): # set to the expected number of folders
                tpg = temporal_graph.reset_TPG(tpg)
                malfunction_schedule = stoch_dict[mf_schdl]
                env, env_renderer, observation, step_info = load_env(private_observation_builder, test_name, seed=seed, malfunctions=True, malfunction_generator=malfunction_schedule)
                if speed_data is not None:
                    replace_agent_speed(env, speed_data, agents_states)
                tmp_proc = temporal_graph_processor.Temporal_Graph_Path_Processor(env)
                perc_rate, steps, cumulative_reward, normalized_reward, malf_count, malf_d = tmp_proc.run_basic_simulation(agent_full_vertex_paths, tpg, step_info, render=False,
                                                                                                                           selected_agents=selected_agents, malf_counter=True)
                avg_comp[mf_schdl].append(perc_rate)
                avg_exp[mf_schdl].append(priority_planner.total_expansions)
                avg_SIC[mf_schdl].append(cumulative_reward)
                avg_MS[mf_schdl].append(steps)
                avg_plan_RT[mf_schdl].append(t_plan)
                avg_tpg_RT[mf_schdl].append(t_tpg)
                avg_malf_ct[mf_schdl].append(malf_count)
                avg_malf_dur[mf_schdl].append(malf_d)
        # except:
        # print("ERROR: FAILED TO COMPLETE THE TEST ", test_name)

        append_to_dict(comp, average_out_dict(avg_comp))
        append_to_dict(exp, average_out_dict(avg_exp))
        append_to_dict(SIC, average_out_dict(avg_SIC))
        append_to_dict(MS, average_out_dict(avg_MS))
        append_to_dict(plan_RT, average_out_dict(avg_plan_RT))
        append_to_dict(tpg_RT, average_out_dict(avg_tpg_RT))
        append_to_dict(malf_ct, average_out_dict(avg_malf_ct))
        append_to_dict(malf_dur, average_out_dict(avg_malf_dur))

        run += 1

    dict = {}
    dict['comp'] = comp
    dict['exp'] = exp
    dict['MS'] = MS
    dict['SIC'] = SIC
    dict['plan_RT'] = plan_RT
    dict['tpg_RT'] = tpg_RT
    dict['malf_ct'] = malf_ct
    dict['malf_dur'] = malf_dur
    dict['total_time'] = sum(plan_RT) + sum(tpg_RT)

    with open("C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results/malfunction_and_ordering_results/DM/" + file_name, 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
