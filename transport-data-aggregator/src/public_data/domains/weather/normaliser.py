from __future__ import annotations

from datetime import datetime
from typing import Iterable

from public_data.domains.weather.schemas import WeatherEntry
from public_data.feeds.rss import RssEntry


def normalise_weather_entries(
    rss_entries: Iterable[RssEntry],
    location: str,
    country: str,
) -> list[WeatherEntry]:
    """
    Convert generic RssEntry objects into typed WeatherEntry objects.

    Handles:
    - extracting min/max temperatures
    - calculating average temperature
    - parsing wind speed/direction
    - parsing humidity
    - mapping the day

    All failures are silently converted to None for optional fields.
    """

    normalised: list[WeatherEntry] = []

    for entry in rss_entries:
        # Default values
        min_temp = max_temp = avg_temp = None
        wind_speed = None
        wind_dir = None
        humidity = None
        day = None

        # Attempt to parse day
        try:
            if entry.published:
                day = entry.published.date()
            else:
                # fallback: attempt to parse first part of title
                day = datetime.strptime(entry.title.split(":")[0].strip(), "%A").date()
        except Exception:
            pass

        desc = entry.summary or entry.title

        # Attempt to extract min/max temperatures from description
        try:
            # Example description: "Maximum Temperature: 12°C, Minimum Temperature: 5°C, Wind Direction: NE, Wind Speed: 15 km/h, Humidity: 75%"
            parts = {p.split(":")[0].strip(): p.split(":")[1].strip() for p in desc.split(",") if ":" in p}

            if "Maximum Temperature" in parts:
                max_temp = float(parts["Maximum Temperature"].replace("°C", "").strip())
            if "Minimum Temperature" in parts:
                min_temp = float(parts["Minimum Temperature"].replace("°C", "").strip())
            if min_temp is not None and max_temp is not None:
                avg_temp = (min_temp + max_temp) / 2
            elif min_temp is not None:
                avg_temp = min_temp
            elif max_temp is not None:
                avg_temp = max_temp

            if "Wind Speed" in parts:
                wind_speed = float(parts["Wind Speed"].split()[0].strip())
            if "Wind Direction" in parts:
                wind_dir = parts["Wind Direction"]
            if "Humidity" in parts:
                humidity = int(parts["Humidity"].replace("%", "").strip())

        except Exception:
            # Any parsing failure just leaves the field as None
            pass

        normalised.append(
            WeatherEntry(
                day=day,
                description=desc,
                min_temp_c=min_temp,
                max_temp_c=max_temp,
                avg_temp_c=avg_temp,
                wind_speed_kmh=wind_speed,
                wind_direction=wind_dir,
                humidity_percent=humidity,
                location=location,
                country=country,
            )
        )

    return normalised
