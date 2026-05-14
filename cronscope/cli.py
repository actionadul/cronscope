"""Command-line interface for cronscope."""

import argparse
import sys
from datetime import datetime

from cronscope.parser import parse
from cronscope.formatter import format_next_runs, tabulate_next_runs
from cronscope.tz_scheduler import next_runs_tz_from_expr
from cronscope.timezone import now_in


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and validate cron expressions with next-run previews.",
    )
    p.add_argument("expression", help="Cron expression (5 fields, quoted)")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of next runs to show (default: 5)",
    )
    p.add_argument(
        "-z",
        "--timezone",
        default="UTC",
        metavar="TZ",
        help="Timezone name, e.g. America/New_York (default: UTC)",
    )
    p.add_argument(
        "--tabulate",
        action="store_true",
        help="Display results in a table format",
    )
    p.add_argument(
        "--validate",
        action="store_true",
        help="Only validate the expression; do not show next runs",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        parsed = parse(args.expression)
    except ValueError as exc:
        print(f"Invalid cron expression: {exc}", file=sys.stderr)
        return 1

    if args.validate:
        print(f"Valid cron expression: {args.expression}")
        print(f"  minute  : {parsed.minute}")
        print(f"  hour    : {parsed.hour}")
        print(f"  day     : {parsed.day}")
        print(f"  month   : {parsed.month}")
        print(f"  weekday : {parsed.weekday}")
        return 0

    try:
        start: datetime = now_in(args.timezone)
    except Exception as exc:
        print(f"Invalid timezone: {exc}", file=sys.stderr)
        return 1

    runs = next_runs_tz_from_expr(args.expression, n=args.count, tz=args.timezone, start=start)

    if args.tabulate:
        print(tabulate_next_runs(runs, tz_label=args.timezone))
    else:
        print(format_next_runs(runs, tz_label=args.timezone))

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
