def manhattan_distance(p1, p2, steps_per_tile):
    """"Manhattan distance calculating function, taking into account different speeds (multiply the distance that will be covered)"""
    (x1, y1) = p1[0]
    (x2, y2) = p2[0]
    d = abs(x1 - x2) + abs(y1 - y2)
    d_speed = d * steps_per_tile
    return d_speed


def distance_map_heuristic(distance_map, player_id, evaluated_vertex, steps_per_tile):
    """Heuristic based on the distance matrix - based on the shortest distance to the goal from every node for every player"""
    position = evaluated_vertex[0]
    orientation = evaluated_vertex[1]
    if orientation == 5:  # in case of the goal node ....
        return 0

    return int(distance_map[player_id][position[0]][position[1]][orientation]) * steps_per_tile
