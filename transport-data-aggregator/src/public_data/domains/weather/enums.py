from enum import Enum


class TemperatureDescription(str, Enum):
    FREEZING = "freezing"
    COLD = "cold"
    COOL = "cool"
    MILD = "mild"
    COMFORTABLE = "comfortable"
    WARM = "warm"
    HOT = "hot"
    SCORCHING = "scorching"


class WindDirection(str, Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"
    UNKNOWN = "Unknown"
