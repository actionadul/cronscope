"""CLI sub-command: cronscope heatmap — display activity heatmaps for a cron expression."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from cronscope.heatmap import (
    build_hour_heatmap,
    build_weekday_heatmap,
    format_hour_heatmap,
    format_weekday_heatmap,
)
from cronscope.parser import parse


def build_heatmap_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *heatmap* sub-command and return its parser."""
    p = subparsers.add_parser(
        "heatmap",
        help="Show activity heatmap for a cron expression",
    )
    p.add_argument("expression", help="Cron expression (quote if it contains spaces)")
    p.add_argument(
        "--timezone", "-z",
        default="UTC",
        help="Timezone name (default: UTC)",
    )
    p.add_argument(
        "--count", "-n",
        type=int,
        default=500,
        help="Number of future occurrences to sample (default: 500)",
    )
    p.add_argument(
        "--mode",
        choices=["hour", "weekday", "both"],
        default="both",
        help="Which heatmap to display (default: both)",
    )
    return p


def run_heatmap(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the heatmap sub-command.  Returns an exit code."""
    try:
        parse(args.expression)
    except ValueError as exc:
        err.write(f"Error: invalid expression — {exc}\n")
        return 1

    try:
        if args.mode in ("hour", "both"):
            heat = build_hour_heatmap(
                args.expression, count=args.count, timezone=args.timezone
            )
            out.write("=== Hourly Activity ===\n")
            out.write(format_hour_heatmap(heat))
            out.write("\n")

        if args.mode in ("weekday", "both"):
            heat_wd = build_weekday_heatmap(
                args.expression, count=args.count, timezone=args.timezone
            )
            out.write("\n=== Weekday Activity ===\n")
            out.write(format_weekday_heatmap(heat_wd))
            out.write("\n")
    except Exception as exc:  # pragma: no cover
        err.write(f"Error: {exc}\n")
        return 1

    return 0
