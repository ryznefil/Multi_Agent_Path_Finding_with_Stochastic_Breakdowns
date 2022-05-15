from multiprocessing import Process

from Thesis_code.testing.test_run.malfunction_testing_functions import run_testing
from Thesis_code.testing.test_run.ordering_types import ordering_types
from Thesis_code.algorithms.path_planning.heuristics import manhattan_distance
from Thesis_code.algorithms.path_planning.heuristics import distance_map_heuristic

if __name__ == '__main__':
    # prepare malfunction scenarios
    stoch_dict = {}
    stoch_dict[0] = {'prop_malfunction': 0.0, 'malfunction_rate': 230, 'min_duration': 2,
                        'max_duration': 5}
    stoch_dict[1] = {'prop_malfunction': 0.0, 'malfunction_rate': 1000, 'min_duration': 10,
                        'max_duration': 20}
    stoch_dict[2] = {'prop_malfunction': 0.0, 'malfunction_rate': 2500, 'min_duration': 25,
                        'max_duration': 50}

    # prepare speed scenarios
    speed_scenario_dict = {}
    speed_scenario_dict[0] = ([1.0, 0.5, 1/3, 0.25], [0.25, 0.25, 0.25, 0.25])
    speed_scenario_dict[1] = ([1.0, 0.5, 1 / 3, 0.25], [0.5, 0.5/3, 0.5/3, 0.5/3])
    speed_scenario_dict[2] = ([1.0, 0.5, 1 / 3, 0.25], [0.5/3, 0.5/3, 0.5/3, 0.5])
    speed_scenario_dict[3] = ([1.0, 0.5, 1 / 3, 0.25], [0.15, 0.35, 0.35, 0.15])


    """Run malfuction and ordering testing, use multiple threads to execute faster"""
    processes = []
    for order in ordering_types:
        date ="31_05"
        name = date + "FINAL_TPG_OPT" + str(order)
        source = "C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/test_Instances/Generated_tests_final_selection"
        process = Process(target=run_testing, args=[order, name, source, stoch_dict, distance_map_heuristic, 20, None])
        process.start()
        processes.append(process)


    for process in processes:
        process.join()




