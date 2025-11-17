from math import radians, cos, sin, asin, sqrt
from typing import Tuple


class DistanceCalculator:
    EARTH_RADIUS_KM = 6371

    @classmethod
    def calculate_distance(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(
            radians,
            [lat1, lon1, lat2, lon2]
        )

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        distance = cls.EARTH_RADIUS_KM * c

        return round(distance, 2)

    @classmethod
    def calculate_distance_meters(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        distance_km = cls.calculate_distance(lat1, lon1, lat2, lon2)
        return int(distance_km * 1000)

    @classmethod
    def is_within_radius(cls, lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
        distance = cls.calculate_distance(lat1, lon1, lat2, lon2)
        return distance <= radius_km