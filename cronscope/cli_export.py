"""CLI sub-command: export cron schedule to JSON or CSV."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from cronscope.exporter import export
from cronscope.parser import parse


def build_export_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *export* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "export",
        help="Export next-run schedule to JSON or CSV.",
    )
    p.add_argument("expression", help="Cron expression (quote if it contains spaces).")
    p.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        dest="fmt",
        help="Output format (default: json).",
    )
    p.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        metavar="N",
        help="Number of next runs to include (default: 10).",
    )
    p.add_argument(
        "-z", "--timezone",
        default="UTC",
        metavar="TZ",
        help="IANA timezone name (default: UTC).",
    )
    p.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    return p


def run_export(args: argparse.Namespace) -> int:
    """Execute the export sub-command; return exit code."""
    try:
        parse(args.expression)  # validate early
    except ValueError as exc:
        print(f"Error: invalid cron expression — {exc}", file=sys.stderr)
        return 1

    try:
        result = export(
            args.expression,
            fmt=args.fmt,
            count=args.count,
            timezone=args.timezone,
            start=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(result)
        except OSError as exc:
            print(f"Error writing file: {exc}", file=sys.stderr)
            return 1
    else:
        print(result)

    return 0
