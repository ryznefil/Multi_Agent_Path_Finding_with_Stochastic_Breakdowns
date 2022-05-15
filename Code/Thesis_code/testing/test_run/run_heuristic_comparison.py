# Preditctors can be used to do short time prediction which can help in avoiding conflicts in the network
import os
import pickle
import time as t

from flatland.envs.malfunction_generators import malfunction_from_file
from flatland.envs.malfunction_generators import no_malfunction_generator
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_file
from flatland.envs.schedule_generators import schedule_from_file
from flatland.utils.rendertools import RenderTool, AgentRenderVariant

from Thesis_code.algorithms.path_execution.k_robust_path_processor import K_Robust_Path_Processor
from Thesis_code.algorithms.path_planning.heuristics import distance_map_heuristic
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance
from Thesis_code.algorithms.path_planning.priority_based.k_robust import k_robust_priority_routing_with_speed
from Thesis_code.algorithms.path_to_action_convertors import path_convertors
# IMPORT ALL NECCESSARY METHODS FROM MY IMPLEMENTATION
from Thesis_code.observations import custom_observations


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
                          malfunction_generator_and_process_data=malfunction_generator,
                          obs_builder_object=observations_object,
                          random_seed=seed)

    observation, step_info = env.reset()
    env_renderer = RenderTool(env, gl="PILSVG",
                              agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS_AND_BOX,
                              show_debug=False,
                              screen_height=1000,  # Adjust these parameters to fit your resolution
                              screen_width=1000)  # Adjust these parameters to fit your resolution

    return env, env_renderer, observation, step_info


if __name__ == "__main__":
    """"Prepare outputs for the heuristics comparison visualisation"""

    # prepare structures
    unordered_manhattan_exp = []
    unordered_distance_exp = []
    unordered_manhattan_SIC = []
    unordered_distance_SIC = []
    unordered_manhattan_MS = []
    unordered_distance_MS = []
    unordered_manhattan_RT = []
    unordered_distance_RT = []
    unordered_distance_comp = []
    unordered_manhattan_comp = []

    run = 0
    test_env_files_folder = "C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/test_Instances/Generated_tests_final_selection"

    for test_id in range(12):  # Set to the expected number of cases per forlder
        test_name = test_env_files_folder + "/Level_" + str(test_id) + ".pkl"

        # check if the test case exists, else continue
        try:
            os.stat(test_name)
        except:
            continue

        print(test_name)

        avg_unordered_manhattan_exp = []
        avg_unordered_manhattan_SIC = []
        avg_unordered_manhattan_MS = []
        avg_unordered_manhattan_RT = []
        avg_unordered_distance_comp = []

        avg_unordered_distance_exp = []
        avg_unordered_distance_SIC = []
        avg_unordered_distance_MS = []
        avg_unordered_distance_RT = []
        avg_unordered_manhattan_comp = []

        for seed in range(1):
            private_observation_builder = custom_observations.CustomGlobalObservation()

            env, env_renderer, observation, step_info = load_env(private_observation_builder, test_name, seed=seed,
                                                                 malfunctions=False, malfunction_generator=None)
            print(test_id, env._max_episode_steps)
            continue
            # Get initial observations from out observations
            init_obs = env.obs_builder.get_many()
            max_steps = env._max_episode_steps
            graph_representation = init_obs[0]
            agents_states = init_obs[1]

            # UNORDERED ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            try:
                selected_agents = [i for i in range(len(env.agents))]
                print("MANHATTAN DISTANCE =----=----=----=----=----=----=----=----=----=----=----")
                priority_planner = k_robust_priority_routing_with_speed.priority_planner_speed(graph_representation,
                                                                                               agents_states,
                                                                                               env.distance_map.rail.grid,
                                                                                               env.width,
                                                                                               env.height,
                                                                                               max_steps,
                                                                                               debug_print=False,
                                                                                               robustness=0,
                                                                                               optimize=False)
                t1 = t.time()
                agent_full_vertex_paths = priority_planner.calculate_non_conflicting_paths(
                    agents_to_plan=selected_agents, env_reference=env, heuristic_function=manhattan_distance)
                t2 = t.time()
                t_total = t2 - t1

                conversion_type, agent_action_paths, edge_paths = path_convertors.convert_timed_vertex_path_to_actions(
                    agent_full_vertex_paths, graph_representation)
                path_processor = K_Robust_Path_Processor(env)
                perc_rate, steps, cumulative_reward, normalized_reward = path_processor.run_basic_simulation(
                    agent_given_actions=agent_action_paths, agent_vertex_debug=agent_full_vertex_paths,
                    step_info=step_info, render=False, animation_sleep=0,
                    selected_agents=selected_agents)

                avg_unordered_manhattan_exp.append(priority_planner.total_expansions)
                avg_unordered_manhattan_SIC.append(cumulative_reward)
                avg_unordered_manhattan_MS.append(makespan(agent_full_vertex_paths))
                avg_unordered_manhattan_RT.append(t_total)
                avg_unordered_manhattan_comp.append(perc_rate)

                print("MAP DISTANCE =----=----=----=----=----=----=----=----=----=----=----=----=----")
                observation, step_info = env.reset(random_seed=seed)
                init_obs = env.obs_builder.get_many()
                agents_states = init_obs[1]

                priority_planner = k_robust_priority_routing_with_speed.priority_planner_speed(graph_representation,
                                                                                               agents_states,
                                                                                               env.distance_map.rail.grid,
                                                                                               env.width,
                                                                                               env.height,
                                                                                               max_steps,
                                                                                               debug_print=False,
                                                                                               robustness=0,
                                                                                               optimize=False)
                t1 = t.time()
                agent_full_vertex_paths = priority_planner.calculate_non_conflicting_paths(
                    agents_to_plan=selected_agents, env_reference=env, heuristic_function=distance_map_heuristic)
                t2 = t.time()
                t_total = t2 - t1
                conversion_type, agent_action_paths, edge_paths = path_convertors.convert_timed_vertex_path_to_actions(
                    agent_full_vertex_paths, graph_representation)
                path_processor = K_Robust_Path_Processor(env)
                perc_rate, steps, cumulative_reward, normalized_reward = path_processor.run_basic_simulation(
                    agent_given_actions=agent_action_paths, agent_vertex_debug=agent_full_vertex_paths,
                    step_info=step_info, render=False, animation_sleep=0,
                    selected_agents=selected_agents)

                avg_unordered_distance_exp.append(priority_planner.total_expansions)
                avg_unordered_distance_SIC.append(cumulative_reward)
                avg_unordered_distance_MS.append(makespan(agent_full_vertex_paths))
                avg_unordered_distance_RT.append(t_total)
                avg_unordered_distance_comp.append(perc_rate)
            except:
                print("ERROR: FAILED TO COMPLETE THE TEST ", test_name)

            unordered_manhattan_exp.append(list_avg(avg_unordered_manhattan_exp))
            unordered_distance_exp.append(list_avg(avg_unordered_distance_exp))
            unordered_manhattan_SIC.append(list_avg(avg_unordered_manhattan_SIC))
            unordered_distance_SIC.append(list_avg(avg_unordered_distance_SIC))
            unordered_manhattan_MS.append(list_avg(avg_unordered_manhattan_MS))
            unordered_distance_MS.append(list_avg(avg_unordered_distance_MS))
            unordered_manhattan_RT.append(list_avg(avg_unordered_manhattan_RT))
            unordered_distance_RT.append(list_avg(avg_unordered_distance_RT))
            unordered_distance_comp.append(list_avg(avg_unordered_distance_comp))
            unordered_manhattan_comp.append(list_avg(avg_unordered_manhattan_comp))

            run += 1

    dict = {}
    dict['unordered_manhattan_exp'] = unordered_manhattan_exp
    dict['unordered_distance_exp'] = unordered_distance_exp
    dict['unordered_manhattan_SIC'] = unordered_manhattan_SIC
    dict['unordered_distance_SIC'] = unordered_distance_SIC
    dict['unordered_manhattan_MS'] = unordered_manhattan_MS
    dict['unordered_distance_MS'] = unordered_distance_MS
    dict['unordered_manhattan_RT'] = unordered_manhattan_RT
    dict['unordered_distance_RT'] = unordered_distance_RT
    dict['unordered_manhattan_comp'] = unordered_manhattan_comp
    dict['unordered_distance_comp'] = unordered_distance_comp

    # with open('C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/heur_new', 'wb') as handle:
    #     pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    x_axis = [i for i in range(run)]
