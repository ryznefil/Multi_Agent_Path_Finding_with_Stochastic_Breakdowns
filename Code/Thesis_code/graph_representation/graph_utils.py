import numpy as np


def get_edges_associated_with_grid_pos(all_edges, step, grid_pos, outgoing):
    """"Fetches all edges associated with one tile in the grid world"""
    edges = []
    for edge in all_edges:
        if outgoing:
            if edge[1][0][0] == grid_pos and edge[1][1] == step:
                edges.append(edge)
        else:
            if edge[0][0][0] == grid_pos and edge[0][1] == step:
                edges.append(edge)
    return edges


def position_converter(grid_position, train_orientation):
    """"Convert the original train position to the graph node coordinate system
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    return: tuple((graph position), train orientation)
    """

    if (train_orientation == 0):
        graph_x_coord = 2 + 2 * grid_position[0]
        graph_y_coord = 1 + 2 * grid_position[1]
    elif (train_orientation == 1):
        graph_x_coord = 1 + 2 * grid_position[0]
        graph_y_coord = 2 * grid_position[1]
    elif (train_orientation == 2):
        graph_x_coord = 2 * grid_position[0]
        graph_y_coord = 1 + 2 * grid_position[1]
    else:
        graph_x_coord = 1 + 2 * grid_position[0]
        graph_y_coord = 2 + 2 * grid_position[1]

    return ((graph_x_coord, graph_y_coord), train_orientation)


def action_recognition(current_orientation, new_orientation, dead_end_bool):
    """"Recognize the action required to replicate the edge (movement in the grid system) given current and new train orientation"""
    if (current_orientation == new_orientation or dead_end_bool):  # forward, in case of deadend can only wait or go forward, hence solve right here!
        return 2
    elif ((current_orientation - 1) % 4 == new_orientation):  # turn left
        return 1
    else:  # turn right
        return 3


def action_to_char(int: int):
    """"string equivalent for action number"""
    return {0: 'N',
            1: 'L',
            2: 'F',
            3: 'R',
            4: 'S'}[int]


def orientation_to_char(int: int):
    """string equivalent for orientation number"""
    return {0: 'N',
            1: 'E',
            2: 'S',
            3: 'W'}[int]


def tile_is_deadend(cell_transition):
    """Checks if one entry can only by exited by a turn-around."""
    maskDeadEnds = 0b0010000110000100

    if cell_transition & maskDeadEnds > 0:
        return True
    else:
        return False


def modify_position(position, destination_orientation):
    """"Use to shift the position tuple in a given direction when generating the graph graph_representation"""
    modifiers = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 0:North, 1:East, 2:South, 3: West
    return (
        (position[0] + modifiers[destination_orientation][0]), (position[1] + modifiers[destination_orientation][1]))


def sum_take4(bit_array, start):
    """"Checks whether there is an edge in the given direction"""
    return bit_array[start] + bit_array[start + 1] + bit_array[start + 2] + bit_array[start + 3]


def decimal_to_binary(tile_decimal_value):
    """Converts the 16bit decimal value graph_representation of one tile to a 16 parts 0/1 array"""
    return np.unpackbits(np.array([tile_decimal_value >> 8, tile_decimal_value & 0xff], dtype=np.uint8))
