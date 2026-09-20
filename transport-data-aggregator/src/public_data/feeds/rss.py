from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

import feedparser

from public_data.feeds.http import fetch_url
from public_data.feeds.errors import FeedError


@dataclass(frozen=True)
class RssEntry:
    """
    A minimal, normalised RSS entry.

    This is intentionally generic.
    Domain-specific logic belongs elsewhere.
    """

    title: str
    link: str
    summary: str
    published: Optional[datetime]


@dataclass(frozen=True)
class RssFeed:
    """
    Parsed RSS feed with metadata and entries.
    """

    title: str
    link: str
    entries: tuple[RssEntry, ...]


def _parse_datetime(struct_time) -> Optional[datetime]:
    if struct_time is None:
        return None
    try:
        return datetime(*struct_time[:6])
    except Exception:
        return None


def parse_rss(url: str) -> RssFeed:
    """
    Fetch and parse an RSS feed.

    - Handles HTTP via feeds.http
    - Uses feedparser for correctness
    - Never raises feedparser-specific exceptions
    """

    response = fetch_url(url)

    parsed = feedparser.parse(response.content)

    if parsed.bozo:
        raise FeedError(
            f"Malformed RSS feed at {url}: {parsed.bozo_exception}"
        )

    entries: list[RssEntry] = []

    for entry in parsed.entries:
        entries.append(
            RssEntry(
                title=entry.get("title", "").strip(),
                link=entry.get("link", "").strip(),
                summary=entry.get("summary", "").strip(),
                published=_parse_datetime(
                    entry.get("published_parsed")
                ),
            )
        )

    return RssFeed(
        title=parsed.feed.get("title", "").strip(),
        link=parsed.feed.get("link", "").strip(),
        entries=tuple(entries),
    )


def iter_entries(url: str) -> Iterable[RssEntry]:
    """
    Convenience generator for streaming-style consumption.
    """

    feed = parse_rss(url)
    return feed.entries
