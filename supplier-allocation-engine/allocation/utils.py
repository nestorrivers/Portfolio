from typing import Tuple
from haversine import haversine, Unit


def distance_miles(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Compute the distance between two latitude/longitude points in miles.
    """
    return haversine(a, b, unit=Unit.MILES)
