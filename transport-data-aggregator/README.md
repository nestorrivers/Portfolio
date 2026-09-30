# transport-data-aggregator

A framework-agnostic Python library for ingesting UK public RSS data (weather, traffic and more) and normalising it into typed, predictable objects that a transport management system can consume without knowing anything about feed formats.

> **Status: alpha (`0.1.0`). Read this before the rest.**
> The **feed layer** (fetch, retry, parse), **configuration** and the **weather normaliser** work. The **traffic domain, the CLI handlers, the concrete weather sources and the test suite are not built yet**: those parts are scaffolding, and the project structure below marks each one. What exists is the architecture and one working vertical slice through it.

| | |
|---|---|
| **Distribution name** | `public-data-aggregator` |
| **Import name** | `public_data` |
| **Python** | 3.11+ |

---

## Why this exists

Operational software such as scheduling, routing and dispatch tools benefits from context like weather and road conditions, but public feeds are inconsistent: different publishers, different formats, free-text fields and occasional outages. This library separates the messy part from the useful part:

- **Fetch** feeds reliably (timeouts, retries, explicit failure modes).
- **Parse** them once, generically.
- **Normalise** each domain into frozen, typed dataclasses.

Consumers (a Django app, a CLI, a scheduled job) depend on the normalised schema and never on the feed.

## Architecture

Data flows through four layers. Each has one responsibility and knows only about the layer beneath it.

```
   RSS endpoint
        │
        ▼
 feeds.http.fetch_url          timeouts, retries, FetchError on failure
        │
        ▼
 feeds.rss.parse_rss           feedparser → RssFeed / RssEntry (generic, domain-agnostic)
        │
        ▼
 domains.<domain>.normaliser   RssEntry → typed domain schema (e.g. WeatherEntry)
        │
        ▼
 domains.<domain>.services     single entry point per domain (e.g. fetch_weather)
        │
        ▼
   CLI / your application
```

### Design decisions

- **Domain-agnostic feed layer.** `RssEntry` carries only `title`, `link`, `summary` and `published`. Anything domain-specific lives in `domains/`.
- **Sources are pluggable.** A feed is described by a `FeedSource` subclass (name and URL). Adding a publisher never touches parsing or normalisation code.
- **Strict at the edges, lenient in the middle.** Network failures and malformed feeds raise (`FetchError`, `FeedError`). Normalisation is best-effort: an entry that can't be parsed comes back with `None` fields and doesn't fail the whole batch. (The granularity of that leniency is per entry, not per field: see [Known limitations](#known-limitations).)
- **Immutable data.** Configuration, feed objects and domain entries are all frozen dataclasses.
- **Centralised configuration.** All environment access goes through `config.py`; nothing else calls `os.getenv`.
- **Typed throughout.** The package is marked `Typing :: Typed` and configured for `mypy --strict`.

## Project structure

```
src/
├── cli.py                          # argparse CLI: parsing only, handlers are stubs (misplaced, see limitations)
└── public_data/
    ├── config.py                   # ✅ immutable AppConfig loaded from environment
    ├── feeds/
    │   ├── base.py                 # ✅ FeedSource ABC
    │   ├── http.py                 # ✅ fetch_url: timeout + retry policy
    │   ├── rss.py                  # ✅ parse_rss, RssFeed, RssEntry
    │   └── errors.py               # ✅ FeedError, FetchError
    ├── domains/
    │   ├── weather/
    │   │   ├── schemas.py          # ✅ WeatherEntry
    │   │   ├── normaliser.py       # ✅ RssEntry → WeatherEntry (one description format)
    │   │   ├── services.py         # ✅ fetch_weather, iter_weather
    │   │   ├── enums.py            # ⚠️ defined but not yet used by the normaliser
    │   │   └── sources.py          # ❌ contains a usage snippet, not a source (fails on import)
    │   └── traffic/                # ❌ scaffolded, empty modules
    ├── services/                   # ❌ placeholder public service layer for the CLI
    └── utils/
examples/                           # ❌ placeholders
tests/                              # ❌ directories exist, no tests written
```

## Installation

```bash
git clone <repository-url>
cd transport-data-aggregator

python -m venv .venv
source .venv/bin/activate

pip install -e .            # library only
pip install -e ".[cli]"     # adds rich for CLI output
pip install -e ".[dev]"     # adds pytest, responses, ruff, mypy
```

Runtime dependencies: `requests`, `feedparser`, `pydantic`, `python-dateutil`, `typing-extensions`.

## Configuration

Configuration is read from environment variables **once, at import time** (`public_data.config.CONFIG`), so set them before importing the package. `.env` files are not loaded automatically; export the variables in your shell or load the file with your process manager.

| Variable | Default | Description |
|---|---|---|
| `PUBLIC_DATA_ENV` | `development` | Environment name |
| `PUBLIC_DATA_LOG_LEVEL` | `INFO` | Log level |
| `PUBLIC_DATA_HTTP_TIMEOUT` | `10` | Per-request timeout, in seconds |
| `PUBLIC_DATA_HTTP_RETRIES` | `3` | Total attempts per fetch (not additional retries) |
| `PUBLIC_DATA_HTTP_BACKOFF` | `0.5` | Base backoff in seconds; sleep is `backoff × attempt` between attempts |

A non-integer value for `PUBLIC_DATA_HTTP_TIMEOUT` or `PUBLIC_DATA_HTTP_RETRIES` raises `ValueError` at import.

## Usage

### As a library

Describe a feed by subclassing `FeedSource`, then pass it to the domain's service function. Optional `location` and `country` attributes on the source are copied onto each normalised entry; `location` falls back to `source.name`, and `country` to `"Unknown"`.

```python
from public_data.domains.weather.services import fetch_weather
from public_data.feeds.base import FeedSource
from public_data.feeds.errors import FeedError


class ExampleWeatherSource(FeedSource):
    location = "Nottingham"
    country = "UK"

    @property
    def name(self) -> str:
        return "Example Weather"

    @property
    def url(self) -> str:
        return "https://example.com/weather/nottingham.rss"  # your feed URL


try:
    for entry in fetch_weather(ExampleWeatherSource()):
        print(entry.day, entry.min_temp_c, entry.max_temp_c, entry.description)
except FeedError as exc:  # also catches FetchError
    print(f"Feed unavailable: {exc}")
```

The weather normaliser expects the feed's description in this shape, which is what the examples and any source you write should produce:

```
Maximum Temperature: 12°C, Minimum Temperature: 5°C, Wind Direction: NE, Wind Speed: 15 km/h, Humidity: 75%
```

### Command line

The CLI defines the interface below, but **the handlers are stubs** that echo their arguments, and the `public-data` console script doesn't run yet (see [Known limitations](#known-limitations)).

```bash
public-data weather --location <code-or-slug> [--days 3]
public-data traffic [--country england|scotland|wales|all]
```

## Data model

### `RssEntry` / `RssFeed` (generic)

| Field | Type | Notes |
|---|---|---|
| `title`, `link`, `summary` | `str` | Whitespace-stripped; empty string if absent |
| `published` | `datetime \| None` | Naive datetime built from the feed's parsed timestamp |

### `WeatherEntry` (normalised)

| Field | Type | Notes |
|---|---|---|
| `day` | `date` | From the entry's publish date (see the day-fallback limitation) |
| `description` | `str` | The entry's summary, or its title if there's no summary |
| `min_temp_c`, `max_temp_c`, `avg_temp_c` | `float \| None` | `avg` is the mean of min and max when both are present, otherwise whichever one exists |
| `wind_speed_kmh` | `float \| None` | Read from the number in the feed's `Wind Speed` field; **the unit isn't checked or converted, so the feed must already report km/h** |
| `wind_direction` | `str \| None` | Stored **as the feed writes it** (e.g. `NE`); no mapping to a fixed set of values yet |
| `humidity_percent` | `int \| None` | 0 to 100 |
| `location`, `country` | `str \| None` | From the source |

## Error handling and network behaviour

| Situation | Behaviour |
|---|---|
| Network-level failure (timeout, DNS, connection reset) | Retried up to `PUBLIC_DATA_HTTP_RETRIES` attempts with linear backoff, then `FetchError` |
| HTTP status ≥ 400 | **Not retried**; `FetchError` immediately |
| Malformed feed (feedparser `bozo` flag set) | `FeedError`. This check is strict: it also fires for problems feedparser could recover from, such as an encoding mismatch |
| Unparseable description during normalisation | That entry's parsed fields are all `None`; the entry is still returned |

`FetchError` subclasses `FeedError`, so catching `FeedError` covers both.

## Extending

**Add a publisher to an existing domain:** subclass `FeedSource` (optionally with `location` / `country`) and pass it to the domain's service function. No other code changes.

**Add a domain:** create `domains/<name>/` with:

1. `schemas.py`: a frozen dataclass for the normalised record
2. `normaliser.py`: a function from `Iterable[RssEntry]` to a list of that dataclass
3. `services.py`: a single `fetch_<name>(source)` entry point
4. `sources.py`: concrete `FeedSource` implementations

Then expose it through `services/` and a CLI subcommand.

## Development

```bash
pip install -e ".[dev]"

pytest                 # tests live under tests/ (HTTP mocked with `responses`); none written yet
ruff check .           # lint (E, F, B, I, UP, SIM)
mypy src               # strict mode
```

## Project status

| Component | State |
|---|---|
| Config loading | Implemented |
| HTTP fetch with timeout and retry | Implemented |
| RSS parsing | Implemented |
| `FeedSource` abstraction | Implemented |
| Weather schema, normaliser, service | Implemented, for one description format |
| Concrete weather source | Not built: `weather/sources.py` holds a usage snippet that references an undefined `BbcWeatherSource` |
| Traffic domain | Scaffolded (empty modules) |
| CLI | Argument parsing only; handlers print `[stub]` |
| Tests | Not written |

### Known limitations

These are behaviours I've confirmed by running the code, listed roughly by how much they'd affect a real deployment.

- **Weather parsing handles exactly one description format.** A realistic feed value such as `Maximum Temperature: 12°C (54°F)` or `Wind Speed: 15mph` fails to parse, and because all fields are parsed in one block, **one bad field sets every parsed field on that entry to `None`**, not just the bad one. Parsing each field independently (and using regular expressions instead of string replacement) is the next fix.
- **Units are assumed, not converted.** Wind speed is read as a bare number and treated as km/h, whatever unit the feed states. The schema promises consistent units, so this needs either conversion or a stricter parse.
- **Wind direction isn't normalised.** The README's schema aims for cardinal directions, but the value is stored as written, so `NE` and `North Easterly` would both come through unchanged. The `WindDirection` enum exists for this and isn't wired in yet.
- **The `day` fallback is unreliable.** When a feed entry has no publish date, the normaliser tries to read a weekday name from the title, which produces a placeholder date (`1900-01-01`). If the title has no weekday, `day` is `None`, even though the field is typed as `date`.
- **The `public-data` console script doesn't run.** `pyproject.toml` points at `public_data.cli:main`, but the CLI lives at `src/cli.py`, outside the package. Moving it to `src/public_data/cli.py` fixes this.
- **`weather/sources.py` fails on import** with a `NameError` (it's a snippet, not a module).
- **`--days` is accepted but unused** until the weather handler is written.

### Roadmap

In order of value:

- [ ] Tests for `feeds/` and the weather normaliser using recorded feed fixtures, including the failure cases above
- [ ] Per-field parsing with unit handling, and wiring in the `TemperatureDescription` and `WindDirection` enums
- [ ] One concrete, working weather source
- [ ] Move the CLI into the package and wire its handlers to the service layer
- [ ] Traffic schema, normaliser and sources (England, Scotland, Wales)
- [ ] Runnable `examples/`