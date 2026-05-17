"""CLI subcommand for ranking and comparing cron expressions by frequency and specificity."""

import argparse
import sys
from typing import List, Optional

from .ranker import rank_expressions, format_rank_report
from .parser import parse


def build_ranker_parser(subparsers=None) -> argparse.ArgumentParser:
    """Build and return the argument parser for the 'rank' subcommand.

    If *subparsers* is provided the parser is registered as a subcommand;
    otherwise a standalone parser is returned (useful for testing).
    """
    description = "Rank cron expressions by run frequency or specificity."

    if subparsers is not None:
        parser = subparsers.add_parser("rank", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="cronscope rank", description=description)

    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to rank (quote each one).",
    )
    parser.add_argument(
        "--by",
        choices=["runs", "specificity"],
        default="runs",
        help="Ranking criterion: 'runs' (runs per day) or 'specificity' (field specificity score). Default: runs.",
    )
    parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="desc",
        help="Sort order: 'asc' (least first) or 'desc' (most first). Default: desc.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        metavar="N",
        help="Number of upcoming runs used to estimate frequency. Default: 50.",
    )
    parser.add_argument(
        "--timezone",
        "-tz",
        default="UTC",
        metavar="TZ",
        help="Timezone for run estimation (e.g. 'America/New_York'). Default: UTC.",
    )

    return parser


def run_ranker(args: argparse.Namespace, output=sys.stdout, error=sys.stderr) -> int:
    """Execute the rank subcommand.

    Parameters
    ----------
    args:
        Parsed namespace from :func:`build_ranker_parser`.
    output:
        File-like object for normal output (default: stdout).
    error:
        File-like object for error messages (default: stderr).

    Returns
    -------
    int
        Exit code – 0 on success, 1 on error.
    """
    expressions: List[str] = args.expressions

    # Validate every expression before doing any work so we give a clear error.
    for expr in expressions:
        try:
            parse(expr)
        except ValueError as exc:
            error.write(f"Invalid expression {expr!r}: {exc}\n")
            return 1

    ascending: bool = args.order == "asc"

    try:
        results = rank_expressions(
            expressions,
            by=args.by,
            ascending=ascending,
            count=args.count,
            timezone=args.timezone,
        )
    except Exception as exc:  # pragma: no cover – unexpected runtime errors
        error.write(f"Error ranking expressions: {exc}\n")
        return 1

    report = format_rank_report(results)
    output.write(report)
    if not report.endswith("\n"):
        output.write("\n")

    return 0
