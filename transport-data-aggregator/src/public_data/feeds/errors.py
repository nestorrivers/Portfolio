class FeedError(Exception):
    """Base class for feed-related errors."""


class FetchError(FeedError):
    """Raised when an HTTP fetch fails."""
