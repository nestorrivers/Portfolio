from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class WeatherEntry:
    """
    Normalised weather data for a single day or time period.

    All temperatures are Celsius.
    Humidity is a percentage (0-100).
    Wind speed is in km/h, wind direction is cardinal (N, NE, E, ...).
    """

    day: date
    description: str

    min_temp_c: Optional[float] = None
    max_temp_c: Optional[float] = None
    avg_temp_c: Optional[float] = None

    wind_speed_kmh: Optional[float] = None
    wind_direction: Optional[str] = None
    humidity_percent: Optional[int] = None

    location: Optional[str] = None
    country: Optional[str] = None
