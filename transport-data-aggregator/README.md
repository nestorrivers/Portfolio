# transport-data-aggregator

A framework-agnostic Python library for ingesting UK public RSS data (weather, traffic and more) and normalising it into typed, predictable objects that a transport management system can consume without knowing anything about feed formats.

> **Status: alpha (`0.1.0`).** The feed layer, configuration and weather normalisation are implemented. Traffic ingestion, the CLI handlers and the test suite are scaffolded but not yet built. See [Project status](#project-status).

| | |
|---|---|
| **Distribution name** | `public-data-aggregator` |
| **Import name** | `public_data` |
| **Python** | 3.11+ |

---

## Why this exists

Operational software such as scheduling, routing and dispatch tools benefits from context like weather and road conditions, but public feeds are inconsistent: different publishers, different formats, free-text fields and occasional outages. This library isolates that mess behind a small, stable interface:

- **Fetch** feeds reliably (timeouts, retries, explicit failure modes).
- **Parse** them once, generically.
- **Normalise** each domain into frozen, typed dataclasses with consistent units.

Consumers (a Django app, a CLI, a scheduled job) depend on the normalised schema, never on the feed.

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
- **Sources are pluggable.** A feed is described by a `FeedSource` subclass (name + URL). Adding a publisher never touches parsing or normalisation code.
- **Strict at the edges, lenient in the middle.** Network failures and malformed feeds raise (`FetchError`, `FeedError`). Normalisation is best-effort: a field that cannot be parsed becomes `None` rather than failing the whole batch.
- **Immutable data.** Configuration, feed objects and domain entries are all frozen dataclasses.
- **Centralised configuration.** All environment access goes through `config.py`; nothing else calls `os.getenv`.
- **Typed throughout.** The package ships as `Typing :: Typed` and is configured for `mypy --strict`.

## Project structure

```
src/
├── cli.py                          # argparse CLI (weather, traffic subcommands)
└── public_data/
    ├── config.py                   # immutable AppConfig loaded from environment
    ├── feeds/
    │   ├── base.py                 # FeedSource ABC
    │   ├── http.py                 # fetch_url: timeout + retry policy
    │   ├── rss.py                  # parse_rss, RssFeed, RssEntry
    │   └── errors.py               # FeedError, FetchError
    ├── domains/
    │   ├── weather/
    │   │   ├── schemas.py          # WeatherEntry
    │   │   ├── normaliser.py       # RssEntry → WeatherEntry
    │   │   ├── services.py         # fetch_weather, iter_weather
    │   │   ├── enums.py            # TemperatureDescription, WindDirection
    │   │   └── sources.py          # concrete weather sources (in progress)
    │   └── traffic/                # scaffolded, not yet implemented
    ├── services/                   # placeholder public service layer for the CLI
    └── utils/
examples/                           # fetch_weather.py, fetch_traffic.py (placeholders)
tests/                              # feeds/, weather/, traffic/ (not yet written)
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

Configuration is read from environment variables **once, at import time** (`public_data.config.CONFIG`), so set them before importing the package. `.env` files are not loaded automatically; export the variables in your shell or load the file with your process manager. `.env.example` lists the two most common settings.

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

### Command line

The CLI defines the interface below. **Handlers are currently stubs** that echo their arguments; see [Project status](#project-status).

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

All temperatures are °C, wind speed is km/h, humidity is a percentage (0–100).

| Field | Type |
|---|---|
| `day` | `date` |
| `description` | `str` |
| `min_temp_c`, `max_temp_c`, `avg_temp_c` | `float \| None` |
| `wind_speed_kmh` | `float \| None` |
| `wind_direction` | `str \| None` (cardinal: N, NE, E, …) |
| `humidity_percent` | `int \| None` |
| `location`, `country` | `str \| None` |

`avg_temp_c` is the mean of min and max when both are present, otherwise whichever one exists.

## Error handling and network behaviour

| Situation | Behaviour |
|---|---|
| Network-level failure (timeout, DNS, connection reset) | Retried up to `PUBLIC_DATA_HTTP_RETRIES` attempts with linear backoff, then `FetchError` |
| HTTP status ≥ 400 | **Not retried**; `FetchError` immediately |
| Malformed feed (feedparser `bozo` flag set) | `FeedError` |
| Unparseable field during normalisation | Field is `None`; the entry is still returned |

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

pytest                 # tests live under tests/ (HTTP mocked with `responses`)
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
| Weather schema, normaliser, service | Implemented |
| Concrete weather source | Not yet: `weather/sources.py` currently holds a usage snippet |
| Traffic domain | Scaffolded (empty modules) |
| CLI | Argument parsing only; handlers print `[stub]` |
| Tests | Not yet written |

### Known limitations

- **The `public-data` console script does not run yet.** `pyproject.toml` points at `public_data.cli:main`, but the CLI module lives at `src/cli.py` rather than inside the package. Moving it to `src/public_data/cli.py` resolves this.
- **Weather parsing assumes one description format**: comma-separated `Key: value` pairs such as `Maximum Temperature: 12°C, Wind Speed: 15 km/h, Humidity: 75%`. Values with extra text (for example `12°C (54°F)`) fail to parse and yield `None` for that entry's parsed fields.
- **Day fallback.** When a feed entry has no publish date, the normaliser tries to parse a weekday name from the title, which produces a placeholder date rather than a real one.
- **`--days` is accepted but unused** until the weather handler is implemented.

### Roadmap

- [ ] Concrete weather sources
- [ ] Traffic schema, normaliser and sources (England, Scotland, Wales)
- [ ] Wire CLI handlers to the service layer, with `rich` output
- [ ] Unit tests for `feeds/` and the normalisers, using recorded feed fixtures
- [ ] Use the `TemperatureDescription` and `WindDirection` enums in normalised output
- [ ] Runnable `examples/`
