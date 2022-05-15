# PATH AND CONSTRAINT LOGGING --------------------------------------------------
def init_constraint_dict(agents):
    """Create the constraint dictionary at the beginning of the CBS planning"""
    constraint_dic = {}
    for agent_id in agents:
        constraint_dic[agent_id] = []

    return constraint_dic


def replance_old_paths(new_individual_paths, old_paths, agents_to_plan, replanned_agents):
    new_paths = {}  # copy.deepcopy(old_paths)
    # new_paths = copy.deepcopy(old_paths)

    for agent_id in agents_to_plan:
        if agent_id in replanned_agents:
            continue

        new_paths[agent_id] = old_paths[agent_id]
        # for step in old_paths[agent_id]:
        #     new_paths[agent_id].append(step)

    for agent_id in replanned_agents:
        new_paths[agent_id] = new_individual_paths[agent_id]

    return new_paths


def replance_old_MDD(new_individual_MDDs, old_MDDs, agents_to_plan, replanned_agents):
    new_MDDs = {}

    for agent_id in agents_to_plan:
        if agent_id in replanned_agents:
            continue

        new_MDDs[agent_id] = old_MDDs[agent_id]
        # for step in old_paths[agent_id]:
        #     new_paths[agent_id].append(step)

    for agent_id in replanned_agents:
        new_MDDs[agent_id] = new_individual_MDDs[agent_id]

    return new_MDDs


def extend_constraint_dictionary(agents_to_plan, constraints_previous, constrained_agents, new_constraints):
    new_constraint_dictionary = {}
    # new_constraints = copy.deepcopy(constraints_previous)

    for agent_id in agents_to_plan:  # copy simply unchanged agents
        if agent_id in constrained_agents:
            continue
        new_constraint_dictionary[agent_id] = constraints_previous[agent_id]

    for limitation in new_constraints:
        agent_id = limitation[3]
        new_constraint_dictionary[agent_id] = []
        for old_constraint in constraints_previous[agent_id]:
            new_constraint_dictionary[agent_id].append(old_constraint)

        for time_step in range(limitation[1], limitation[2] + 1):
            new_constraint_dictionary[agent_id].append((limitation[0], time_step))

        new_constraint_dictionary[agent_id].sort()

    return new_constraint_dictionary


# MOVEMENT UTILS AND COST FUNCTIONS --------------------------------------------------
def makespan(agent_vertex_paths, planned_agents):
    """"Calculate the makespan of the planned paths"""
    cost = 0
    for agent_id in planned_agents:
        path_cost = agent_vertex_paths[agent_id][-2][1]  # get the timestamp of the last node on the map, bypass the sink node
        cost = max(path_cost, cost)
    return cost


def final_cost(agent_vertex_paths, planned_agents):
    """"Calculate the makespan of the planned paths"""
    cost = 0
    for agent_id in planned_agents:
        path_cost = agent_vertex_paths[agent_id][-2][1]  # get the timestamp of the last node on the map, bypass the sink node
        cost = max(path_cost, cost)
    return cost


def sum_of_cost(agent_vertex_paths, planned_agents):
    """"Calculate the sum of cost of the planned paths"""
    cost = 0
    for agent_id in planned_agents:
        path_cost = agent_vertex_paths[agent_id][-2][1]  # get the timestamp of the last node on the map, bypass the sink node
        cost += path_cost
    return cost


def single_path_cost(agent_path, agent_id):
    if len(agent_path) == 0:
        return 0

    return agent_path[agent_id][-2][1]
