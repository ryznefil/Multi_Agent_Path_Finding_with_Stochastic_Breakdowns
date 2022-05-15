class CBS_node():
    def __init__(self, agent_paths, agent_constraint_dictionary, agent_conflicts, new_constraints, total_cost, conflict_type, conflict_count, conflict_queue, MDD=None):
        self.agent_paths = agent_paths
        self.agent_constraints = agent_constraint_dictionary
        self.agent_conflicts = agent_conflicts
        self.new_constraints = new_constraints
        self.total_cost = total_cost
        self.conflict_type = conflict_type
        self.conflict_count = conflict_count
        self.conflicts_queue = conflict_queue

        self.MDD = MDD
