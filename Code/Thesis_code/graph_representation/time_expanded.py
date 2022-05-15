import networkx as nx


def expand_graph(graph, step_limit):
    """Create full time expanded graph from a standard graph"""
    expanded_g = nx.DiGraph()

    # Add edges for each layer
    for time_step in range(step_limit - 1):
        for edge in graph.edges(data=True):
            attr_dict = {}
            attr_dict['weight'] = edge[2]['weight']
            attr_dict['grid_pos'] = edge[2]['grid_pos']
            attr_dict['orientation'] = edge[2]['orientation']
            attr_dict['str_orientation'] = edge[2]['str_orientation']
            attr_dict['str_action'] = edge[2]['str_action']
            attr_dict['action'] = edge[2]['action']
            expanded_g.add_edge((edge[0], time_step), (edge[1], time_step + 1), attr_dict=attr_dict)

    return expanded_g
