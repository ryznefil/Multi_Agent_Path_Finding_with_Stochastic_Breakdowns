# Preditctors can be used to do short time prediction which can help in avoiding conflicts in the network
import math as m
import time as t

from flatland.envs.malfunction_generators import _malfunction_prob
from flatland.envs.malfunction_generators import malfunction_from_params
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.schedule_generators import sparse_schedule_generator
from flatland.utils.rendertools import RenderTool, AgentRenderVariant

from Thesis_code.algorithms.path_execution.k_robust_path_processor import K_Robust_Path_Processor
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance
from Thesis_code.algorithms.path_planning.priority_based.k_robust import k_robust_priority_routing_with_speed
from Thesis_code.algorithms.path_to_action_convertors import path_convertors
from Thesis_code.observations import custom_observations


def makespan(agent_vertex_paths, planned_agents):
    """"Calculate the makespan of the planned paths"""
    cost = 0
    for agent_id in planned_agents:
        path_cost = agent_vertex_paths[agent_id][-2][1]  # get the timestamp of the last node on the map, bypass the sink node
        cost = max(path_cost, cost)
    return cost


def monte_carlo_test(random, path_len, repeats, malf_prob, min_dur, max_dur):
    cumulative_malf = 0
    cum_occurances = 0
    for iteration in range(30, repeats):
        for step in range(path_len):
            if random.rand() < malf_prob:
                cum_occurances += 1
                exp_dur = random.randint(min_dur, max_dur + 1)
                cumulative_malf += exp_dur
    avg_malf = cumulative_malf / repeats
    avg_occurences = cum_occurances / repeats

    return avg_malf, avg_occurences


width = 20  # With of map
height = 20  # Height of map
nr_trains = 15  # Number of trains that have an assigned task in the env
cities_in_map = 5  # Number of cities where agents can start or end
seed = 14  # Random seed
grid_distribution_of_cities = True  # Type of city distribution, if False cities are randomly placed
max_rails_between_cities = 1  # Max number of tracks allowed between cities. This is number of entry point to a city
max_rail_in_cities = 1  # Max number of parallel tracks within a city, representing a realistic trainstation

# CASE 2
# width = 15  # With of map
# height = 15  # Height of map
# nr_trains = 11 # Number of trains that have an assigned task in the env
# cities_in_map = 5  # Number of cities where agents can start or end
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
speeds = [1.0, 0.75, 0.5, 0.33]
speed_ration_map = {1: 0.25, 0.75: 0.25, 0.33: 0.25, 0.5: 0.25}  # Slow freight train
schedule_generator = sparse_schedule_generator(speed_ration_map)

stochastic_data = {'prop_malfunction': 0.0,
                   'malfunction_rate': 50,  # Rate of malfunction occurence of single agent
                   'min_duration': 2,  # Minimal duration of malfunction
                   'max_duration': 2  # Max duration of malfunction
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

print("Priority planning")
# env_renderer.render_env(show=True, show_observations=False)

# Get initial observations from out observations
init_obs = env.obs_builder.get_many()
max_steps = env._max_episode_steps
graph_representation = init_obs[0]
agents_states = init_obs[1]

distance_map = env.distance_map.get()
max_duration = 0

for agent in agents_states:
    distance = distance_map[agent.id, agent.graph_starting_vertex[0][0], agent.graph_starting_vertex[0][1], agent.graph_starting_vertex[1]] * agent.steps_per_move
    max_duration = max(max_duration, distance)

selected_agents = [i for i in range(len(env.agents))]
init_obs = env.obs_builder.get_many()
max_steps = env._max_episode_steps
graph_representation = init_obs[0]
agents_states = init_obs[1]

malf_rate = env.malfunction_process_data.malfunction_rate
malf_min = env.malfunction_process_data.min_duration
malf_max = env.malfunction_process_data.max_duration
avg_duration = (malf_min + malf_max) / 2
malf_turn_prob = _malfunction_prob(malf_rate)

priority_planner = k_robust_priority_routing_with_speed.priority_planner_speed(graph_representation, agents_states, env.rail.grid, env.width, env.height, env._max_episode_steps, debug_print=True,
                                                                               robustness=0)
agent_full_vertex_paths = priority_planner.calculate_non_conflicting_paths(agents_to_plan=selected_agents, env_reference=env, heuristic_function=manhattan_distance)

longest_path = makespan(agent_full_vertex_paths, selected_agents)
first_estimate = m.ceil(longest_path * avg_duration * malf_turn_prob)
mc = monte_carlo_test(env.np_random, longest_path, 1000000, malf_turn_prob, malf_min, malf_max)

if first_estimate < mc[0]:
    print()

# agent_full_vertex_paths= priority_planner.calculate_non_conflicting_paths(agents_to_plan=selected_agents, env_reference=env, heuristic_function=distance_map_heuristic)
priority_planner = k_robust_priority_routing_with_speed.priority_planner_speed(graph_representation, agents_states, env.rail.grid, env.width, env.height, env._max_episode_steps, debug_print=True,
                                                                               robustness=12)
agent_full_vertex_paths = priority_planner.calculate_non_conflicting_paths(agents_to_plan=selected_agents, env_reference=env, heuristic_function=manhattan_distance)
conversion_type, agent_action_paths, edge_paths = path_convertors.convert_timed_vertex_path_to_actions(agent_full_vertex_paths, graph_representation)
init_obs = env.obs_builder.get_many()
max_steps = env._max_episode_steps
graph_representation = init_obs[0]
agents_states = init_obs[1]
a = t.time()
path_processor = K_Robust_Path_Processor(env)
perc_rate, steps, cumulative_reward, normalized_reward = path_processor.run_basic_simulation(agent_given_actions=agent_action_paths, agent_vertex_debug=agent_full_vertex_paths, step_info=step_info,
                                                                                             render=True, animation_sleep=0,
                                                                                             selected_agents=selected_agents)
# priority_profiling_info = priority_planner.get_expansions_and_time()
# print_info(priority_profiling_info)
print(perc_rate, steps)
print("Total astar expansions: ", priority_planner.total_expansions)
b = t.time()
c = b - a
print("Time: ", c)
observation, step_info = env.reset(regenerate_rail=False, regenerate_schedule=False, activate_agents=False, random_seed=14)
