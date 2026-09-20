from __future__ import annotations

import argparse
import sys
from typing import NoReturn


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="public-data",
        description="Fetch and normalise UK public RSS data (weather, traffic).",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ---- weather -------------------------------------------------
    weather = subparsers.add_parser(
        "weather",
        help="Fetch normalised weather data",
    )
    weather.add_argument(
        "--location",
        required=True,
        help="Location identifier (e.g. BBC weather code or slug)",
    )
    weather.add_argument(
        "--days",
        type=int,
        default=3,
        help="Number of forecast days to fetch (default: 3)",
    )

    # ---- traffic -------------------------------------------------
    traffic = subparsers.add_parser(
        "traffic",
        help="Fetch normalised traffic data",
    )
    traffic.add_argument(
        "--country",
        choices=["england", "scotland", "wales", "all"],
        default="all",
        help="Country to fetch traffic data for",
    )

    return parser


def main() -> NoReturn:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "weather":
        handle_weather(
            location=args.location,
            days=args.days,
        )
    elif args.command == "traffic":
        handle_traffic(
            country=args.country,
        )
    else:
        parser.error("Unknown command")


def handle_weather(*, location: str, days: int) -> None:
    # NOTE: implementation will live in services.weather
    print(f"[stub] weather: location={location}, days={days}")


def handle_traffic(*, country: str) -> None:
    # NOTE: implementation will live in services.traffic
    print(f"[stub] traffic: country={country}")


if __name__ == "__main__":
    sys.exit(main())
