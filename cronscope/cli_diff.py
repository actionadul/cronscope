"""CLI sub-command: diff two cron expressions."""

import argparse
import sys
from typing import List

from cronscope.diff_expressions import diff_expressions, format_diff_report
from cronscope.parser import parse


def build_diff_parser(subparsers) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "diff",
        help="Compare the schedules of two cron expressions.",
    )
    p.add_argument("expr_a", help="First cron expression")
    p.add_argument("expr_b", help="Second cron expression")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=60,
        help="Number of future runs to compare (default: 60)",
    )
    p.add_argument(
        "--max-rows",
        type=int,
        default=5,
        dest="max_rows",
        help="Max rows to display per section (default: 5)",
    )
    return p


def run_diff(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    for attr, label in (("expr_a", "Expression A"), ("expr_b", "Expression B")):
        expr = getattr(args, attr)
        try:
            parse(expr)
        except ValueError as exc:
            err.write(f"Error in {label}: {exc}\n")
            return 1

    diff = diff_expressions(args.expr_a, args.expr_b, count=args.count)
    out.write(format_diff_report(diff, max_rows=args.max_rows))
    out.write("\n")
    return 0
