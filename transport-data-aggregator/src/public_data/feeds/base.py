from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from public_data.feeds.rss import RssEntry, RssFeed


class FeedSource(ABC):
    """
    Abstract base class for an RSS feed source.

    Concrete implementations should:
    - define where the feed comes from
    - expose a stable identifier
    - return parsed RSS data only
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable source name.
        Example: "BBC Weather"
        """

    @property
    @abstractmethod
    def url(self) -> str:
        """
        Fully-qualified RSS feed URL.
        """

    def fetch(self) -> RssFeed:
        """
        Fetch and parse the RSS feed.

        Default implementation delegates to feeds.rss.
        """
        from public_data.feeds.rss import parse_rss

        return parse_rss(self.url)

    def iter_entries(self) -> Iterable[RssEntry]:
        """
        Convenience iterator over feed entries.
        """
        return self.fetch().entries
