from enum import Enum


class Conflict_Types(Enum):
    VERTEX_ENTRY_CONFLICT = 0
    VERTEX_OTHER_CONFLICT = 1
    VERTEX_TRIPLE_CONFLICT = 2
    EDGE_CONFLICT = 3
