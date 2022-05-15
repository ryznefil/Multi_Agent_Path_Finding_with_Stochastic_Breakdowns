# Preditctors can be used to do short time prediction which can help in avoiding conflicts in the network

from flatland.envs.malfunction_generators import no_malfunction_generator
from flatland.envs.rail_env import RailEnv
# Preditctors can be used to do short time prediction which can help in avoiding conflicts in the network
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.schedule_generators import sparse_schedule_generator

# IMPORT ALL NECCESSARY METHODS FROM MY IMPLEMENTATION
from Thesis_code.observations import custom_observations
from Thesis_code.testing.test_instances_creation import blueprints_manual_setups


def generate_single_blueprint(width, height, nr_trains, cities_in_map, seed, grid_distribution_of_cities, max_rails_between_cities, max_rail_in_cities, speed_ration_map):
    """"Create individual env blueprint"""
    dict = {}
    dict['width'] = width
    dict["height"] = height
    dict["nr_trains"] = nr_trains
    dict["cities_in_map"] = cities_in_map
    dict["seed"] = seed
    dict["grid_distribution_of_cities"] = grid_distribution_of_cities
    dict["max_rails_between_cities"] = max_rails_between_cities
    dict["max_rail_in_cities"] = max_rail_in_cities
    dict["speed_ration_map"] = speed_ration_map

    return dict


def generate_instance_from_blueprint(blueprint):
    """"Create one env based on the blueprint"""
    dict = blueprint
    rail_generator = sparse_rail_generator(max_num_cities=dict["cities_in_map"],
                                           seed=dict["seed"],
                                           grid_mode=dict["grid_distribution_of_cities"],
                                           max_rails_between_cities=dict["max_rails_between_cities"],
                                           max_rails_in_city=dict["max_rail_in_cities"])

    schedule_generator = sparse_schedule_generator(dict["speed_ration_map"])
    private_observation_builder = custom_observations.CustomGlobalObservation()

    env = RailEnv(width=dict['width'],
                  height=dict["height"],
                  rail_generator=rail_generator,
                  schedule_generator=schedule_generator,
                  number_of_agents=dict["nr_trains"],
                  obs_builder_object=private_observation_builder,
                  malfunction_generator_and_process_data=no_malfunction_generator(),
                  remove_agents_at_target=True)
    env.reset()
    return env


def save_test_env(test_env, save_location):
    """"save test instance into the folder"""
    test_env.save(save_location, save_distance_maps=False)  # TODO: Bugged distance map saving


def create_and_save_envs(multiple_blueprints, folder):
    """"Generate test instances based on the blueprints and place them into the specified folder"""
    for test_id in range(len(multiple_blueprints)):
        test_name = folder + "/Level_" + str(test_id) + ".pkl"
        print("Creating test: ", test_id)
        test_env = generate_instance_from_blueprint(multiple_blueprints[test_id])
        save_test_env(test_env, test_name)


if __name__ == "__main__":
    test_folder = "C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/Generated_tests_harder"
    instances_blueprint = blueprints_manual_setups.generate_manual_setups(15)  # get the blueprint for the required setups
    create_and_save_envs(instances_blueprint, test_folder)
