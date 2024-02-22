""" This module contains utility functions for data analysis. """
from math import radians, sin, cos, sqrt, atan2


def haversine(
        lon1: float,
        lat1: float,
        lon2: float,
        lat2: float
) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Based on:
    https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371  # Radius of earth in kilometers
    return c * r
