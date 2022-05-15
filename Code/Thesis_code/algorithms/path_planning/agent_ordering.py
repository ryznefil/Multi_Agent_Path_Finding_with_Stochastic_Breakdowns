def fast_first(env, agent_states):
    return agent_speed_and_position_sort(env, agent_states, reversed=False)

def slow_first(env, agent_states):
    return agent_speed_and_position_sort(env, agent_states, reversed=True)

def close_first(env, agent_states):
    return agent_speed_and_position_sort_no_speed(env, agent_states, reversed=False)

def remote_first(env, agent_states):
    return agent_speed_and_position_sort_no_speed(env, agent_states, reversed=True)

def agent_speed_and_position_sort(env, agent_states, reversed=False):
    distance_map = env.distance_map.get()
    tmp_array = []
    agent_ordering = []

    for agent in agent_states:
        agent_position = agent.graph_starting_vertex
        step_per_tile = agent.steps_per_move
        agent_id = agent.id
        agent_goal_distance = distance_map[agent_id, agent_position[0][0], agent_position[0][1], agent_position[1]]

        if reversed:
            tmp_array.append((-step_per_tile, -agent_goal_distance, agent_id))
        else:
            tmp_array.append((step_per_tile, agent_goal_distance, agent_id))

    tmp_array.sort()  # all sorted in increasing fashion

    for element in tmp_array:
        agent_ordering.append(element[2])

    return agent_ordering


def agent_speed_and_position_sort_no_speed(env, agent_states, reversed=False):
    distance_map = env.distance_map.get()
    tmp_array = []
    agent_ordering = []

    for agent in agent_states:
        spm = agent.steps_per_move
        agent_position = agent.graph_starting_vertex
        agent_id = agent.id
        agent_goal_distance = distance_map[agent_id, agent_position[0][0], agent_position[0][1], agent_position[1]]

        if reversed:
            tmp_array.append((-agent_goal_distance * spm, agent_id))
        else:
            tmp_array.append((agent_goal_distance * spm, agent_id))

    tmp_array.sort()  # all sorted in increasing fashion

    for element in tmp_array:
        agent_ordering.append(element[1])

    return agent_ordering
