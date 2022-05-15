# Preditctors can be used to do short time prediction which can help in avoiding conflicts in the network
import time as t
import numpy as np
from flatland.envs.malfunction_generators import malfunction_from_params
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.schedule_generators import sparse_schedule_generator
from flatland.utils.rendertools import RenderTool, AgentRenderVariant

from Thesis_code.algorithms.path_execution import temporal_graph_processor
from Thesis_code.algorithms.path_planning.heuristics import distance_map_heuristic
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance
from Thesis_code.algorithms.path_planning.priority_based.k_robust import k_robust_priority_routing_with_speed
from Thesis_code.algorithms.path_to_action_convertors import temporal_graph
from Thesis_code.observations import custom_observations
from Thesis_code.testing.test_run.ordering_types import ordering_types
from Thesis_code.algorithms.path_planning import  agent_ordering as agent_ord_alg

def easy_instance():
    dict = {}
    dict['width'] = 20 # width of the instance
    dict["height"] = 35 # height of the instance
    dict["nr_trains"] = 50 # number of trains in the instance
    dict["cities_in_map"] = 2 # number cities in the instance
    dict["seed"] = 0 # seed for map creation
    dict["grid_distribution_of_cities"] = True # symmetric city allocation over the grid
    dict["max_rails_between_cities"] = 1 # maximum number of rails between cities
    dict["max_rail_in_cities"] = 1 # maximum number of rail around cities, 1 is neccessary, other serve as bypasses
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25} # configuration of agents speeds, equal distribution with 0.25 each

    return dict

def moderate_instance():
    dict = {}
    dict['width'] = 60  # width of the instance
    dict["height"] = 60  # height of the instance
    dict["nr_trains"] = 80  # number of trains in the instance
    dict["cities_in_map"] = 13  # number cities in the instance
    dict["seed"] = 0  # seed for map creation
    dict["grid_distribution_of_cities"] = True  # symmetric city allocation over the grid
    dict["max_rails_between_cities"] = 1  # maximum number of rails between cities
    dict["max_rail_in_cities"] = 1  # maximum number of rail around cities, 1 is neccessary, other serve as bypasses
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}  # configuration of agents speeds, equal distribution with 0.25 each

    return dict

def hard_instance():
    dict = {}
    dict['width'] = 100  # width of the instance
    dict["height"] = 100  # height of the instance
    dict["nr_trains"] = 150  # number of trains in the instance
    dict["cities_in_map"] = 35  # number cities in the instance
    dict["seed"] = 0  # seed for map creation
    dict["grid_distribution_of_cities"] = True  # symmetric city allocation over the grid
    dict["max_rails_between_cities"] = 2  # maximum number of rails between cities
    dict["max_rail_in_cities"] = 3  # maximum number of rail around cities, 1 is neccessary, other serve as bypasses
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}  # configuration of agents speeds, equal distribution with 0.25 each

    return dict

def extreme_instance():
    dict = {}
    dict['width'] = 150  # width of the instance
    dict["height"] = 150  # height of the instance
    dict["nr_trains"] = 200  # number of trains in the instance
    dict["cities_in_map"] = 35  # number cities in the instance
    dict["seed"] = 0  # seed for map creation
    dict["grid_distribution_of_cities"] = True  # symmetric city allocation over the grid
    dict["max_rails_between_cities"] = 3  # maximum number of rails between cities
    dict["max_rail_in_cities"] = 3  # maximum number of rail around cities, 1 is neccessary, other serve as bypasses
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}  # configuration of agents speeds, equal distribution with 0.25 each

    return dict

def frequent_breakdown():
    return {'malfunction_rate': 230, 'min_duration': 10,'max_duration': 15}

def moderate_breakdown():
    return {'malfunction_rate': 1000, 'min_duration': 10,'max_duration': 20}

def rare_breakdown():
    return {'malfunction_rate': 2500, 'min_duration': 25,'max_duration': 50}

if __name__ == "__main__":
    # EXAMPLE CONFIGURATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Configuration of the test instance - SELECT ONLY ONE ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    dict = easy_instance()
    #dict = moderate_instance()
    #dict = hard_instance()
    #dict = extreme_instance()

    # Configuration of breakdown scenario - SELECT ONLY ONE ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    breakdown_scenario = frequent_breakdown()
    #breakdown_scenario = moderate_breakdown()
    #breakdown_scenario = rare_breakdown()

    # Configuration of state space search heuristic - SELECT ONLY ONE ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    heuristic = distance_map_heuristic
    # heuristic = manhattan_distance

    # Configuration of agent ordering heuristics - SELECT ONLY ONE ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    agent_ordering = ordering_types.FLATLAND
    #agent_ordering = ordering_types.FAST_FIRST
    #agent_ordering = ordering_types.SLOW_FIRST
    #agent_ordering = ordering_types.CLOSE_FIRST
    # agent_ordering = ordering_types.REMOTE_FIRST

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Generate the railway map
    rail_generator = sparse_rail_generator(max_num_cities=dict["cities_in_map"], # set the maximum number of cities in the map
                                           seed=dict["seed"],
                                           grid_mode=dict["grid_distribution_of_cities"],
                                           max_rails_between_cities=dict["max_rails_between_cities"],
                                           max_rails_in_city=dict["max_rail_in_cities"])
    schedule_generator = sparse_schedule_generator(dict["speed_ration_map"])

    # Breakdown generator configuration
    stochastic_data = {'malfunction_rate': breakdown_scenario['malfunction_rate'], 'min_duration': breakdown_scenario['min_duration'], 'max_duration': breakdown_scenario['max_duration'] }

    # Our representation builder
    private_observation_builder = custom_observations.CustomGlobalObservation()

    # building the rail env wit agents
    print("Generating an environment")
    env = RailEnv(width=dict['width'],
                  height=dict["height"],
                  rail_generator=rail_generator,
                  schedule_generator=schedule_generator,
                  number_of_agents=dict["nr_trains"],
                  obs_builder_object=private_observation_builder,
                  malfunction_generator_and_process_data=malfunction_from_params(stochastic_data),
                  remove_agents_at_target=True)
    observation, step_info = env.reset() # activation of the instance

    # instance rendering tool
    env_renderer = RenderTool(env, gl="PILSVG",
                              agent_render_variant=AgentRenderVariant.ONE_STEP_BEHIND,
                              show_debug=False,
                              screen_height=800,  # Adjust these parameters to fit your resolution
                              screen_width=800)  # Adjust these parameters to fit your resolution


    # Getting info about the map ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    print("/n The speed information of the agents are:")
    print("=========================================")
    for agent_idx, agent in enumerate(env.agents):
        print(
            "Agent {} speed is: {:.2f} with the current fractional position being {}".format(
                agent_idx, agent.speed_data['speed'], agent.speed_data['position_fraction']))

    # Get what I need to kickstart the planner without uneccessarily bloating observations
    height = env.height
    width = env.width
    binary_rail = env.distance_map.rail.grid

    # Get initial observations from out observations
    init_obs = env.obs_builder.get_many()
    max_steps = env._max_episode_steps
    graph_representation = init_obs[0]
    agents_states = init_obs[1]

    # CONFIGURE AGENT ORDERING:

    if agent_ordering == ordering_types.FLATLAND:
        selected_agents = [i for i in range(len(agents_states))]
    elif agent_ordering == ordering_types.FAST_FIRST:
        selected_agents = agent_ord_alg.fast_first(env, agents_states)
    elif agent_ordering == ordering_types.REMOTE_FIRST:
        selected_agents = agent_ord_alg.remote_first(env, agents_states)
    elif agent_ordering == ordering_types.CLOSE_FIRST:
        selected_agents = agent_ord_alg.close_first(env, agents_states)
    elif agent_ordering == ordering_types.SLOW_FIRST:
        selected_agents = agent_ord_alg.slow_first(env, agents_states)
    else:
        print("ERROR: UNKNOWN AGENT ORDERING")
        raise ValueError

    # Prioritised planning --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    print("Phase 1 - planning paths")
    tp_s = t.time()
    priority_planner = k_robust_priority_routing_with_speed.priority_planner_speed(graph_representation, agents_states, binary_rail, width, height, max_steps, debug_print=True, robustness=0, optimize=True)
    agent_full_vertex_paths, reservation_table = priority_planner.calculate_non_conflicting_paths(agents_to_plan=selected_agents, env_reference=env, heuristic_function=distance_map_heuristic, TPG = True)
    tp_e = t.time()
    tp_total = tp_e - tp_s

    # Temporal graph construction --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    print("Phase 2 - constructing the temporal plan graph")
    tg_s = t.time()
    tpg = temporal_graph.create_temporal_plan_graph(agent_full_vertex_paths, graph_representation, reservation_table)
    tg_e = t.time()
    tg_total = tg_e - tg_s

    # Path execution --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    print("Phase 3 - plan execution")
    tmp_proc = temporal_graph_processor.Temporal_Graph_Path_Processor(env, env_renderer)
    perc_rate, steps, cumulative_reward, normalized_reward, malf_count, malf_d = tmp_proc.run_basic_simulation(agent_full_vertex_paths, tpg, step_info, render=True, selected_agents=selected_agents, malf_counter=True, copy_dct=False)
    print("INSTANCE COMPLETED ----------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Completion rate: ", perc_rate)
    print("Sum of individual cost: ", -1*cumulative_reward, ", Makespan: ", steps)
    print("Breakdown occurrences: ", malf_count, ", Total breakdown duration: ", malf_d)
    print("Prioritised planning run-time (sec): ", tp_total, ", TPG constrution run-time: ", tg_total)



