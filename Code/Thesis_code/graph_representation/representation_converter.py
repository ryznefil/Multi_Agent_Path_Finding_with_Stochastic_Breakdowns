import networkx as nx

from Thesis_code.graph_representation.graph_utils import action_recognition, action_to_char, orientation_to_char, \
    tile_is_deadend, modify_position, sum_take4, decimal_to_binary


class NXGraphBuilder:
    """"Graph representation of the Flatland grid world"""

    def __init__(self):
        self.binary_grid = None
        self.nx_graph = nx.DiGraph()

    def get_graph(self):
        """"Return the instance of the graph"""
        return self.nx_graph

    def initialize_graph(self, binary_representation, agent_states, rows, cols):
        """"Call to fully create the graph that is encapsulated in the NxGraph creator"""
        self._grid_to_graph(binary_representation, agent_states, rows, cols)

    def _grid_to_graph(self, binary_representation, agent_states, rows, cols):
        """Call to create a graph graph_representation from the original environment"""
        for row in range(rows):
            for col in range(cols):
                if binary_representation[row][col] != 0:  # skip empty tiles
                    self._tile_to_graph(binary_representation[row][col], (row, col))

        # create starting nodes for each agent
        self._add_start_nodes(agent_states)

        # create end nodes for each agent
        self._add_target_nodes(agent_states)

    def _tile_to_graph(self, tile_decimal_value, position):
        """Call to convert one grid tile to graph graph_representation"""

        tile_binary = decimal_to_binary(tile_decimal_value)  # get a 16 bit tile graph_representation in an array
        dead_end = tile_is_deadend(tile_decimal_value)  # dead end flag

        for orientation in range(4):  # iterate over all 4 possible train orientations and add edges
            idx = orientation * 4

            if sum_take4(tile_binary, idx) == 0:  # continue if the next 4 bits are all 0 => invalid direction
                continue

            current_node = (position, orientation)

            # add self-loop that will allow to represent the option to stop and wait
            self.nx_graph.add_edge(current_node, current_node, weight=1, grid_pos=position,
                                   orientation=orientation,
                                   str_orientation=orientation_to_char(orientation), action=4,
                                   str_action='S')  # can stop in every node

            self.nx_graph.nodes[current_node]['grid_position'] = position

            while idx < 4 * (orientation + 1):  # iterate over the next 4 bits representing movement direction from the node
                if tile_binary[idx] == 1:
                    destination_orientation = idx % 4  # determine train orientation in the next node
                    action = action_recognition(orientation, destination_orientation, dead_end)

                    # add edges representing possible movement
                    target_node = (modify_position(position, destination_orientation), destination_orientation)
                    self.nx_graph.add_edge(current_node, target_node, weight=1, grid_pos=position,
                                           orientation=orientation,
                                           str_orientation=orientation_to_char(orientation),
                                           action=action, str_action=action_to_char(action))
                idx += 1

    def _add_start_nodes(self, agent_states):
        """Add starting nodes to the graph for each agent"""
        for agent_state in agent_states:
            self.nx_graph.add_edge(agent_state.graph_before_placement_vertex, agent_state.graph_starting_vertex, weight=1, grid_pos=None,
                                   orientation=agent_state.flatland_agent.initial_direction, str_orientation=orientation_to_char(agent_state.flatland_agent.initial_direction), action=2,
                                   str_action=action_to_char(0))
            self.nx_graph.add_edge(agent_state.graph_before_placement_vertex, agent_state.graph_before_placement_vertex, weight=1, grid_pos=None,
                                   orientation=None,
                                   str_orientation=None, action=0,
                                   str_action='N')
            self.nx_graph.nodes[agent_state.graph_before_placement_vertex]['grid_position'] = None

    def _add_target_nodes(self, agent_states):
        """Fill in end nodes for each train into the graph, end nodes graph_representation of the depots
        linked to all sides in case it is inside the railway"""

        for agent_state in agent_states:
            grid_target = agent_state.flatland_agent.target
            for orientation in range(4):
                node = (grid_target, orientation)  # convert hypothetical position
                if node in self.nx_graph:
                    self.nx_graph.add_edge(node, agent_state.graph_target_vertex, weight=0, grid_pos=grid_target,
                                           orientation=None, str_orientation=None, action=2,
                                           str_action=action_to_char(2))
                    self.nx_graph.nodes[agent_state.graph_target_vertex]['grid_position'] = grid_target
                    self.nx_graph.nodes[agent_state.graph_target_vertex]['occupied'] = 0
