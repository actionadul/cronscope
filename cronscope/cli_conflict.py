"""CLI sub-command: check cron expressions for scheduling conflicts."""

import argparse
import sys
from typing import List, Optional

from cronscope.conflict import check_expressions, format_conflict_report


def build_conflict_parser(subparsers) -> argparse.ArgumentParser:
    """Register the 'conflict' sub-command onto *subparsers*."""
    parser = subparsers.add_parser(
        "conflict",
        help="Check cron expressions for scheduling conflicts or anomalies.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to check (quote each one).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any warnings are found.",
    )
    return parser


def run_conflict(args: argparse.Namespace, out=None, err=None) -> int:
    """Execute the conflict check and write results.  Returns an exit code."""
    if out is None:
        out = sys.stdout
    if err is None:
        err = sys.stderr

    reports = check_expressions(args.expressions)
    any_invalid = False
    any_warning = False

    for report in reports:
        print(format_conflict_report(report), file=out)
        print("", file=out)  # blank line separator
        if not report.is_valid:
            any_invalid = True
        if report.warnings:
            any_warning = True

    if any_invalid:
        return 2
    if args.strict and any_warning:
        return 1
    return 0
