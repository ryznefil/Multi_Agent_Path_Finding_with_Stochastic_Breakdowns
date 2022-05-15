def generate_manual_setups(agent_adjustment=0):
    """"Manual preparation of outlines for test files, Agent adjustment variable can be used to increase/decrease the number of agents across tests"""

    difficulty_adjustment = agent_adjustment
    generated_setups = {}
    # SMALL ##########################################################################################################################################################################################################################################################################
    # CASE 0  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 0
    dict = {}
    dict['width'] = 15
    dict["height"] = 15
    dict["nr_trains"] = 20 + difficulty_adjustment
    dict["cities_in_map"] = 2
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    dict["max_rails_between_cities"] = 1
    dict["max_rail_in_cities"] = 1
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 1  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 1
    dict = {}
    dict['width'] = 20
    dict["height"] = 20
    dict["nr_trains"] = 50 + difficulty_adjustment
    dict["cities_in_map"] = 3
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    dict["max_rails_between_cities"] = 1
    dict["max_rail_in_cities"] = 1
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 2  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 2
    dict = {}
    dict['width'] = 20
    dict["height"] = 35
    dict["nr_trains"] = 50 + difficulty_adjustment
    dict["cities_in_map"] = 2
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    dict["max_rails_between_cities"] = 1
    dict["max_rail_in_cities"] = 1
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict
    # MEDIUM ##########################################################################################################################################################################################################################################################################
    # CASE 3  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 3
    dict = {}
    dict['width'] = 55
    dict["height"] = 35
    dict["nr_trains"] = 80 + difficulty_adjustment
    dict["cities_in_map"] = 15
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    dict["max_rails_between_cities"] = 2
    dict["max_rail_in_cities"] = 2
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 4  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 4
    dict = {}
    dict['width'] = 60
    dict["height"] = 60
    dict["nr_trains"] = 80 + difficulty_adjustment
    dict["cities_in_map"] = 13
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    dict["max_rails_between_cities"] = 1
    dict["max_rail_in_cities"] = 1
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 5  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 5
    dict = {}
    dict['width'] = 70
    dict["height"] = 60
    dict["nr_trains"] = 100 + difficulty_adjustment
    dict["cities_in_map"] = 15
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    dict["max_rails_between_cities"] = 2
    dict["max_rail_in_cities"] = 1
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # LARGE ##########################################################################################################################################################################################################################################################################
    # CASE 6  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 6
    dict = {}
    dict['width'] = 75
    dict["height"] = 75
    dict["nr_trains"] = 120 + difficulty_adjustment
    dict["cities_in_map"] = 20
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = False
    dict["max_rails_between_cities"] = 2
    dict["max_rail_in_cities"] = 2
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 7  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 7
    dict = {}
    dict['width'] = 80
    dict["height"] = 100
    dict["nr_trains"] = 120 + difficulty_adjustment
    dict["cities_in_map"] = 30
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = False
    dict["max_rails_between_cities"] = 2
    dict["max_rail_in_cities"] = 2
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 8  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 8
    dict = {}
    dict['width'] = 100
    dict["height"] = 100
    dict["nr_trains"] = 150 + difficulty_adjustment
    dict["cities_in_map"] = 35
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = True
    # dict["max_rails_between_cities"] = 4
    # dict["max_rail_in_cities"] = 6
    dict["max_rails_between_cities"] = 2
    dict["max_rail_in_cities"] = 3
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # ULTRA LARGE ##########################################################################################################################################################################################################################################################################
    # CASE 9  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 9
    dict = {}
    dict['width'] = 150
    dict["height"] = 150
    dict["nr_trains"] = 150 + difficulty_adjustment
    dict["cities_in_map"] = 35
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = False
    dict["max_rails_between_cities"] = 2
    dict["max_rail_in_cities"] = 6
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 10  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 10
    dict = {}
    dict['width'] = 150
    dict["height"] = 150
    dict["nr_trains"] = 200
    dict["cities_in_map"] = 50
    dict["seed"] = 5
    dict["grid_distribution_of_cities"] = False
    dict["max_rails_between_cities"] = 3
    dict["max_rail_in_cities"] = 3
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    # CASE 11  =----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----==----=----=
    case = 11
    dict = {}
    dict['width'] = 150
    dict["height"] = 150
    dict["nr_trains"] = 200
    dict["cities_in_map"] = 35
    dict["seed"] = 0
    dict["grid_distribution_of_cities"] = False
    dict["max_rails_between_cities"] = 3
    dict["max_rail_in_cities"] = 3
    dict["speed_ration_map"] = {1: 0.25, 0.5: 0.25, 1 / 3: 0.25, 0.25: 0.25}
    generated_setups[case] = dict

    return generated_setups
