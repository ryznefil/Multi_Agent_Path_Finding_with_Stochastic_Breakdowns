import math as m


class AgentState:
    """Our wrapper around the flatlant agent object. It supports core functionality and core representation, but we aim to keep additions to the minimum"""

    def __init__(self, handle, agent):
        self.id = handle
        self.flatland_agent = agent  # Maintain all original inputs
        self.state = agent.status
        self.steps_per_move = m.ceil(1 / self.flatland_agent.speed_data['speed'])

        self.graph_before_placement_vertex = (None, self.id)  # vertex before putting on the game plan
        self.graph_current_vertex = (agent.position, self.id)  # Initial position is None for all agents, distinguish by ID
        self.time_expanded_current_graph_vertex = (self.graph_current_vertex, 0)  # Added timestep to the node

        self.graph_starting_vertex = (agent.initial_position, agent.initial_direction)  # agent is placed here after spawn
        self.time_expanded_starting_graph_vertex = (self.graph_starting_vertex, 0)
        self.graph_target_vertex = (agent.target, 5)  # 5 to distinguish this node from other which have one of 4 orientations

    def update_agent(self, agent):
        """Update the agent wrapper after each round of the game"""
        self.flatland_agent = agent
        self.state = agent.status
        self.steps_per_move = m.ceil(1 / self.flatland_agent.speed_data['speed'])

        if self.flatland_agent.position is None:
            self.graph_current_vertex = (self.flatland_agent.position, self.id)
        else:
            self.graph_current_vertex = (self.flatland_agent.position, agent.direction)


def AgentsInitializer(railEnv):
    """"Extracts initial agent data from the environment to our object graph_representation
        returns a list of agents"""
    agents_array = []
    for i in range(railEnv.get_num_agents()):
        agents_array.append(AgentState(handle=i, agent=railEnv.agents[i]))

    return agents_array
