class CBS_node():
    def __init__(self, agent_paths, agent_constraint_dictionary, total_cost, MDDs):
        self.agent_paths = agent_paths
        self.agent_constraints = agent_constraint_dictionary
        self.total_cost = total_cost
        self.MDDs = MDDs
