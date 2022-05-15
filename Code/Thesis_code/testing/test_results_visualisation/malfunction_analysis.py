import pickle

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from Thesis_code.testing.test_run.ordering_types import ordering_types


def assign_name(ordering_type):
    if ordering_type == ordering_types.FLATLAND:
        return "Flatland base"
    elif ordering_type == ordering_types.FAST_FIRST:
        return "Fast-First"
    elif ordering_type == ordering_types.SLOW_FIRST:
        return "Slow-First"
    elif ordering_type == ordering_types.CLOSE_FIRST:
        return "Close-First"
    elif ordering_type == ordering_types.REMOTE_FIRST:
        return "Remote-First"


if __name__ == '__main__':
    sns.set()
    sns.set_style("ticks")

    data_type_1 = {}
    data_type_2 = {}
    data_type_3 = {}
    container = [data_type_1, data_type_2, data_type_3]


    data = data_type_3
    for type in ordering_types:
        file = None
        # file = "C:/Users/Personal-Win10/Documents/BP/flatland-round-2/Flatland_round_2/BP/testing/test_results/malfunction_and_ordering_results/final_results/DM/27_05FAST_HARD_TPG_OPT" + str(type)
        with (open(file, "rb")) as openfile:
            data[str(type)] = pickle.load(openfile)

    trial = ""
    x = [i for i in range(1, 13)]
    printed_types = [ordering_types.REMOTE_FIRST, ordering_types.CLOSE_FIRST, ordering_types.SLOW_FIRST, ordering_types.FLATLAND, ordering_types.FAST_FIRST]
    for malfunction in range(0,1):
        save_loc = None

        title = "Completion rate, malfunction: " + str(malfunction)
        test_type = 'total_RT'
        data = data_type_3
        for order in printed_types:
            plt.plot(x, np.array(data[str(order)]['tpg_RT'][malfunction]) + np.array(data[str(order)]['plan_RT'][malfunction]), label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Time in seconds')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        #plt.title(title)
        plt.savefig(save_loc + test_type  + str(malfunction) + trial + '.png')
        plt.show()

        title = "Completion rate, malfunction: " + str(malfunction)
        test_type = 'malf_comp'
        data = data_type_3
        for order in printed_types:
            plt.plot(x, data[str(order)]['comp'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Completion rate')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        #plt.title(title)
        plt.savefig(save_loc + test_type + "_run_" + str(malfunction) + trial + '.png')
        plt.show()

        title = "Sum of Individual Costs values, malfunction: " + str(malfunction)
        data = data_type_3
        test_type = 'malf_SIC'
        for order in printed_types:
            plt.plot(x, np.array(data[str(order)]['SIC'][malfunction]) * -1, label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Sum of Individual Costs')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type + "_run_"+ str(malfunction) + trial + '.png')
        plt.show()

        title = "Makespan, malfunction: " + str(malfunction)
        data = data_type_3
        test_type = 'malf_MS'
        for order in printed_types:
            plt.plot(x, data[str(order)]['MS'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Make-span')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type + "_run_"+ str(malfunction) + trial + '.png')
        plt.show()

        title = "Total malfunction occurrences, malfunction: " + str(malfunction)
        data = data_type_3
        test_type = 'malf_ct'
        for order in printed_types:
            plt.plot(x, data[str(order)]['malf_ct'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Malfunction occurrences')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type + "_run_"+ str(malfunction) + trial + '.png')
        plt.show()

        title = "Total malfunction duration: " + str(malfunction)
        data = data_type_3
        test_type = 'malf_dur'
        for order in printed_types:
            plt.plot(x, data[str(order)]['malf_dur'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Duration')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type + "_run_"+ str(malfunction) + trial + '.png')
        plt.show()

        title = "Total planning RT, malfunction: " + str(malfunction)
        data = data_type_3
        test_type = 'plan_RT'
        for order in printed_types:
            plt.plot(x, data[str(order)]['plan_RT'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Time in seconds')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type+ "_run_" + str(malfunction) + trial + '.png')
        plt.show()
        #
        title = "Total TPG RT, malfunction: " + str(malfunction)
        data = data_type_3
        test_type = 'tpg_RT'
        for order in printed_types:
            plt.plot(x, data[str(order)]['tpg_RT'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Time in seconds')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type + "_run_"+ str(malfunction)+ trial + '.png')
        plt.show()
        #
        title = "Expansion count, malfunction: " + str(malfunction)
        data = data_type_3
        test_type = 'exp'
        for order in printed_types:
            plt.plot(x, data[str(order)]['exp'][malfunction], label=assign_name(order), linestyle='--', marker='o')
        plt.xticks(np.arange(len(x) + 1))
        plt.ylabel('Expansions')
        plt.xlabel('Test instance number')
        plt.legend()
        sns.despine()
        # plt.title(title)
        plt.savefig(save_loc + test_type + "_run_"+ str(malfunction) + trial + '.png')
        plt.show()
