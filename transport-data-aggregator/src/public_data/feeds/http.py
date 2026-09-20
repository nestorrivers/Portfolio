from __future__ import annotations

import time
from typing import Final

import requests
from requests import Response
from requests.exceptions import RequestException

from public_data.config import CONFIG
from public_data.feeds.errors import FetchError


DEFAULT_HEADERS: Final[dict[str, str]] = {
    "User-Agent": "public-data-aggregator/0.1 (+https://example.com)"
}


def fetch_url(
    url: str,
    *,
    timeout: int | None = None,
    retries: int | None = None,
    backoff: float | None = None,
) -> Response:
    """
    Fetch a URL with retries and timeout.

    This function:
    - retries on network-level failures
    - does NOT retry on HTTP error status codes
    - returns a requests.Response on success
    - raises FetchError on failure
    """

    timeout = timeout if timeout is not None else CONFIG.http_timeout
    retries = retries if retries is not None else CONFIG.http_retries
    backoff = backoff if backoff is not None else CONFIG.http_backoff

    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers=DEFAULT_HEADERS,
            )

            # Explicitly fail on HTTP error codes
            if response.status_code >= 400:
                raise FetchError(
                    f"HTTP {response.status_code} while fetching {url}"
                )

            return response

        except RequestException as exc:
            last_error = exc

            if attempt >= retries:
                break

            time.sleep(backoff * attempt)

    raise FetchError(
        f"Failed to fetch {url} after {retries} attempts"
    ) from last_error
