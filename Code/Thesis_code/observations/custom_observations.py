from flatland.core.env_observation_builder import ObservationBuilder

from Thesis_code.graph_representation import agent_state
from Thesis_code.graph_representation import representation_converter as rc


class CustomGlobalObservation(ObservationBuilder):
    """"Custom observation builder used in Flatland env creation, contains the graph representation of the grid env"""

    def __init__(self):
        super().__init__()
        self.observation_space = [2]  # TODO: required by the engine, must specify the dimensions of observations
        self.agents_states = []
        self.graph_builder = rc.NXGraphBuilder()

    def reset(self):
        """"Reset the observation build. Called when creating the env and every time the env is reset"""
        self.agents_states = agent_state.AgentsInitializer(self.env)
        self.graph_builder = rc.NXGraphBuilder()
        self.graph_builder.initialize_graph(self.env.rail.grid, self.agents_states, self.env.height, self.env.width)

    def get_many(self, ids=[]):
        """"Standard get many for observations"""
        for agent in self.agents_states:
            self.get(agent.id)

        return tuple((self.graph_builder.get_graph(), self.agents_states))

    def get(self, id):
        self.agents_states[id].update_agent(self.env.agents[id])
