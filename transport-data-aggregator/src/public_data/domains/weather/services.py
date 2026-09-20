from __future__ import annotations

from typing import Iterable

from public_data.domains.weather.normaliser import normalise_weather_entries
from public_data.domains.weather.schemas import WeatherEntry
from public_data.feeds.base import FeedSource


def fetch_weather(source: FeedSource) -> list[WeatherEntry]:
    """
    Fetch weather data from a FeedSource and return a list of normalised WeatherEntry objects.

    This function is the **single entry point** for services or CLI.
    """

    rss_feed = source.fetch()  # type: ignore
    entries = rss_feed.entries

    normalised = normalise_weather_entries(
        rss_entries=entries,
        location=getattr(source, "location", None) or source.name,
        country=getattr(source, "country", None) or "Unknown",
    )

    return normalised


def iter_weather(source: FeedSource) -> Iterable[WeatherEntry]:
    """
    Convenience generator version of fetch_weather.
    Useful for streaming-style consumption.
    """
    for entry in fetch_weather(source):
        yield entry
