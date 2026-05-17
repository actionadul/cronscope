"""CLI sub-command: overlap — compare two or more cron expressions for shared run times."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronscope.overlap import compare_expressions, find_overlaps, format_overlap_report
from cronscope.parser import parse


def build_overlap_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "overlap",
        help="Detect shared run times between two or more cron expressions.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions (quote each one).",
    )
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=100,
        metavar="N",
        help="Number of future runs to sample per expression (default: 100).",
    )
    return p


def run_overlap(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    if len(args.expressions) < 2:
        err.write("error: at least two expressions are required\n")
        return 2

    # Validate each expression first
    for expr in args.expressions:
        try:
            parse(expr)
        except ValueError as exc:
            err.write(f"error: invalid expression {expr!r}: {exc}\n")
            return 1

    start = datetime.utcnow().replace(second=0, microsecond=0)
    results = compare_expressions(args.expressions, start=start, count=args.count)

    any_overlap = False
    for result in results:
        report = format_overlap_report(result)
        out.write(report + "\n\n")
        if result.has_overlap:
            any_overlap = True

    if any_overlap:
        out.write("⚠  Overlapping expressions detected.\n")
    else:
        out.write("✓  No overlaps found in the sampled window.\n")

    return 0
