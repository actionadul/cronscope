"""CLI sub-command: show previous run times for a cron expression."""

import argparse
import sys
from datetime import datetime, timezone

from cronscope.history import prev_runs_from_expr
from cronscope.parser import parse
from cronscope.formatter import format_single_next_run


def build_history_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # noqa: SLF001
    p = subparsers.add_parser(
        "history",
        help="Show the N most recent past run times for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression (quoted), e.g. '*/5 * * * *'")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of previous runs to show (default: 5).",
    )
    p.add_argument(
        "--before",
        default=None,
        metavar="DATETIME",
        help=(
            "Reference datetime in ISO-8601 format (default: now). "
            "Example: 2024-06-01T12:00:00"
        ),
    )
    return p


def run_history(args: argparse.Namespace) -> int:
    """Execute the history sub-command; return an exit code."""
    # Validate expression first.
    try:
        parse(args.expression)
    except ValueError as exc:
        print(f"Error: invalid cron expression — {exc}", file=sys.stderr)
        return 1

    # Parse the reference datetime.
    if args.before:
        try:
            before = datetime.fromisoformat(args.before)
        except ValueError:
            print(
                f"Error: --before value '{args.before}' is not a valid ISO-8601 datetime.",
                file=sys.stderr,
            )
            return 1
    else:
        before = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    if args.count <= 0:
        print("Error: --count must be a positive integer.", file=sys.stderr)
        return 1

    runs = prev_runs_from_expr(args.expression, before, count=args.count)
    print(f"Previous {args.count} run(s) for '{args.expression}':")
    for i, dt in enumerate(runs, start=1):
        print(f"  {i:>2}. {format_single_next_run(dt)}")

    return 0
