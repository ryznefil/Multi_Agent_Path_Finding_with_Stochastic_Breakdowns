import pickle

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set()
sns.set_style("ticks")


file = None
with (open(file, "rb")) as openfile:
    base_and_order = pickle.load(openfile)

heuristics_comparison = True
ordering_comparison = False
other_ordering_comparison = False

if heuristics_comparison:
    # SIC
    x = [i for i in range(1, 13)]
    plt.plot(x, -1 * np.array(base_and_order['unordered_manhattan_SIC']), label='Manhattan Distance', linestyle='--', marker='o')
    plt.plot(x, -1 * np.array(base_and_order['unordered_distance_SIC']), label='Distance map', linestyle='--', marker='o')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Sum of Individual Costs')
    plt.xlabel('Test instance number')
    # plt.title("Sum of Individual Costs values (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig('C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results_visualisation/Results_images/heuristic_im/SIC.png')
    plt.show()

    # MS
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_manhattan_MS'], label='Manhattan Distance', linestyle='--', marker='o')
    plt.plot(x, base_and_order['unordered_distance_MS'], label='Distance map', linestyle='--', marker='o')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Make-span')
    plt.xlabel('Test instance number')
    # plt.title("Make-span values (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig('C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results_visualisation/Results_images/heuristic_im/MS.png')
    plt.show()

    # Run Time
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_manhattan_RT'], label='Manhattan Distance', linestyle='--', marker='o')
    plt.plot(x, base_and_order['unordered_distance_RT'], label='Distance map', linestyle='--', marker='o')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Time in seconds')
    plt.xlabel('Test instance number')
    # plt.title("Average A* Expansions (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig('C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results_visualisation/Results_images/heuristic_im/RT.png')
    plt.show()

    # Expansion
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_manhattan_exp'], label='Manhattan Distance', linestyle='--', marker='o')
    plt.plot(x, base_and_order['unordered_distance_exp'], label='Distance map', linestyle='--', marker='o')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Expansions')
    plt.xlabel('Test instance number')
    # plt.title("Average A* Expansions (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig('C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results_visualisation/Results_images/heuristic_im/EX.png')
    plt.show()

    # Expansion
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_manhattan_comp'], label='Manhattan Distance', linestyle='--', marker='o')
    plt.plot(x, base_and_order['unordered_distance_comp'], label='Distance map', linestyle='--', marker='o')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Completion rate')
    plt.xlabel('Test instance number')
    # plt.title("Average A* Expansions (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig('C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results_visualisation/Results_images/heuristic_im/COMP.png')
    plt.show()

if ordering_comparison:
    # SIC
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_distance_SIC'], label='Flatland ordering')
    plt.plot(x, base_and_order['ordered_distance_SIC'], label='S + D standard ordering')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Sum of Individual Costs')
    plt.xlabel('Test case number')
    # plt.title("Sum of Individual Costs values (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig(
        'C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/final_testing/ordering_im/ordering_SIC.png')
    plt.show()

    # MS
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_distance_SIC'], label='Flatland ordering')
    plt.plot(x, base_and_order['ordered_distance_SIC'], label='S + D standard ordering')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Make-span')
    plt.xlabel('Test case number')
    # plt.title("Make-span values (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig(
        'C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/final_testing/ordering_im/ordering_MS.png')
    plt.show()

    # Run Time
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_distance_SIC'], label='Flatland ordering')
    plt.plot(x, base_and_order['ordered_distance_SIC'], label='S + D standard ordering')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Time in seconds')
    plt.xlabel('Test case number')
    # plt.title("Average A* Expansions (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig(
        'C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/final_testing/ordering_im/ordering_RT.png')
    plt.show()

    # Expansion
    x = [i for i in range(1, 13)]
    plt.plot(x, base_and_order['unordered_distance_SIC'], label='Flatland ordering')
    plt.plot(x, base_and_order['ordered_distance_SIC'], label='S + D standard ordering')
    plt.xticks(np.arange(len(x) + 1))
    plt.ylabel('Expansions')
    plt.xlabel('Test case number')
    # plt.title("Average A* Expansions (without priority ordering)")
    plt.legend()
    sns.despine()
    plt.savefig(
        'C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/final_testing/ordering_im/ordering_EX.png')
    plt.show()
