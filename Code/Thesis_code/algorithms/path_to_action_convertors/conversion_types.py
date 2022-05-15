from enum import Enum


class ConversionType(Enum):
    STANDARD = 0  # not in grid yet (position is None) -> prediction as if it were at initial position
    TEMPORAL_PLAN_GRAPH = 1  # in grid (position is not None), not done -> prediction is remaining path
