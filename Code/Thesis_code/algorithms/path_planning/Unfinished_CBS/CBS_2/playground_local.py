# Preditctors can be used to do short time prediction which can help in avoiding conflicts in the network
import time as t

from flatland.envs.malfunction_generators import malfunction_from_params
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.schedule_generators import sparse_schedule_generator
from flatland.utils.rendertools import RenderTool, AgentRenderVariant

from Thesis_code.algorithms.path_execution import temporal_graph_processor
from Thesis_code.algorithms.path_planning.Unfinished_CBS.CBS_2.CBS_high_level import CBS_high_level
from Thesis_code.algorithms.path_to_action_convertors import path_convertors
from Thesis_code.algorithms.path_to_action_convertors import temporal_graph
from Thesis_code.observations import custom_observations


def print_info(output_info):
    print("Total planning time: ", output_info[0])
    print("Total expanded nodes: ", output_info[1])
    print("Deepest expaded node: ", output_info[2])
    agent_dict = output_info[3]
    for i in range(len(agent_dict)):
        note = agent_dict[i]
        print("Agent ", i, "took: ", note[0], " expanded: ", note[1], " deepest exapansion: ", note[2])


if __name__ == "__main__":
    # CASE 1
    # width = 14  # With of map
    # height = 14  # Height of map
    # nr_trains = 12# Number of trains that have an assigned task in the env
    # cities_in_map = 2  # Number of cities where agents can start or end
    # seed = 14 # Random seed
    # print(seed)
    # grid_distribution_of_cities = True  # Type of city distribution, if False cities are randomly placed
    # max_rails_between_cities = 1  # Max number of tracks allowed between cities. This is number of entry point to a city
    # max_rail_in_cities = 1  # Max number of parallel tracks within a city, representing a realistic trainstation

    width = 20  # With of map
    height = 20  # Height of map
    nr_trains = 6  # Number of trains that have an assigned task in the env
    cities_in_map = 5  # Number of cities where agents can start or end
    seed = 14  # Random seed
    grid_distribution_of_cities = True  # Type of city distribution, if False cities are randomly placed
    max_rails_between_cities = 1  # Max number of tracks allowed between cities. This is number of entry point to a city
    max_rail_in_cities = 1  # Max number of parallel tracks within a city, representing a realistic trainstation

    # # CASE 2
    # width = 15  # With of map
    # height = 15  # Height of map
    # nr_trains = 2 # Number of trains that have an assigned task in the env
    # cities_in_map = 5  # Number of cities where agents can start or end
    # seed = 14  # Random seed
    # grid_distribution_of_cities = True  # Type of city distribution, if False cities are randomly placed
    # max_rails_between_cities = 1  # Max number of tracks allowed between cities. This is number of entry point to a city
    # max_rail_in_cities = 1  # Max number of parallel tracks within a city, representing a realistic trainstation

    # width = 50  # With of map
    # height = 50  # Height of map
    # nr_trains = 70 # Number of trains that have an assigned task in the env
    # cities_in_map = 8  # Number of cities where agents can start or end
    # seed = 14  # Random seed
    # grid_distribution_of_cities = True  # Type of city distribution, if False cities are randomly placed
    # max_rails_between_cities = 1  # Max number of tracks allowed between cities. This is number of entry point to a city
    # max_rail_in_cities = 1  # Max number of parallel tracks within a city, representing a realistic trainstation

    rail_generator = sparse_rail_generator(max_num_cities=cities_in_map,
                                           seed=seed,
                                           grid_mode=grid_distribution_of_cities,
                                           max_rails_between_cities=max_rails_between_cities,
                                           max_rails_in_city=max_rail_in_cities,
                                           )
    # speed_ration_map = {0.75:0.5, 0.5:0.5}
    speed_ration_map = {1.0: 1.0}
    speeds = sorted(speed_ration_map.keys(), reverse=False)
    # speed_ration_map = {0.75: 0.25, 0.33: 0.25, 0.5:0.10, 1: 0.40}  # Slow freight train
    schedule_generator = sparse_schedule_generator(speed_ration_map)

    stochastic_data = {'prop_malfunction': 0.0,
                       'malfunction_rate': 0,  # Rate of malfunction occurence of single agent
                       'min_duration': 2,  # Minimal duration of malfunction
                       'max_duration': 3  # Max duration of malfunction
                       }

    private_observation_builder = custom_observations.CustomGlobalObservation()
    # #
    env = RailEnv(width=width,
                  height=height,
                  rail_generator=rail_generator,
                  schedule_generator=schedule_generator,
                  number_of_agents=nr_trains,
                  obs_builder_object=private_observation_builder,
                  malfunction_generator_and_process_data=malfunction_from_params(stochastic_data),
                  remove_agents_at_target=True)
    observation, step_info = env.reset()

    env_renderer = RenderTool(env, gl="PILSVG",
                              agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS_AND_BOX,
                              show_debug=False,
                              screen_height=2000,  # Adjust these parameters to fit your resolution
                              screen_width=2000)  # Adjust these parameters to fit your resolution

    # Getting info about the map ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    print("\n The speed information of the agents are:")
    print("=========================================")

    for agent_idx, agent in enumerate(env.agents):
        print(
            "Agent {} speed is: {:.2f} with the current fractional position being {}".format(
                agent_idx, agent.speed_data['speed'], agent.speed_data['position_fraction']))

    # Get what I need to kickstart the planner without uneccessarily bloating observations
    height = env.height
    width = env.width
    binary_rail = env.distance_map.rail.grid

    print("Priority planning")
    # env_renderer.render_env(show=True, show_observations=False)

    # Get initial observations from out observations
    init_obs = env.obs_builder.get_many()
    max_steps = env._max_episode_steps
    graph_representation = init_obs[0]
    agents_states = init_obs[1]

    # selected_agents = []
    # for speed in speeds:
    #     for i in range(len(env.agents)):
    #         if step_info['speed'][i] == speed:
    #             selected_agents.append(i)

    # Planning and execution --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    a = t.time()
    priority_planner = CBS_high_level(graph_representation, agents_states, binary_rail, width, height, max_steps, debug_print=True, robustness=0)
    selected_agents = [i for i in range(len(env.agents))]
    agent_full_vertex_paths = priority_planner.high_level_search(selected_agents)
    b = t.time()
    c = b - a
    print(c)

    conversion_type, agent_action_paths, edge_paths = path_convertors.convert_timed_vertex_path_to_actions(agent_full_vertex_paths, graph_representation)

    # path_processor = pp.PathProcessor(env)
    # perc_rate, steps, cumulative_reward, normalized_reward = path_processor.run_basic_simulation(agent_given_actions=agent_action_paths, agent_vertex_debug=agent_full_vertex_paths, step_info=step_info, render=True, animation_sleep=0,
    #                                                                                              selected_agents=selected_agents)
    # priority_profiling_info = priority_planner.get_expansions_and_time()

    tpg = temporal_graph.create_temporal_plan_graph(agent_full_vertex_paths, graph_representation, selected_agents=selected_agents)
    tmp_proc = temporal_graph_processor.Temporal_Graph_Path_Processor(env)
    perc_rate, steps, cumulative_reward, normalized_reward = tmp_proc.run_basic_simulation(tpg, step_info, render=True, selected_agents=selected_agents)
    # priority_profiling_info = priority_planner.get_expansions_and_time()
    # print_info(priority_profiling_info)
    print(perc_rate, steps)
