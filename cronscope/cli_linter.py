"""CLI sub-command: lint a cron expression."""

from __future__ import annotations

import argparse
import sys

from cronscope.linter import lint, format_lint_report


def build_linter_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the 'lint' sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "lint",
        help="Lint a cron expression for common mistakes and style issues.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to lint (quote if it contains spaces).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with a non-zero code when warnings are present.",
    )
    return parser


def run_linter(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the lint sub-command. Returns an exit code."""
    result = lint(args.expression)
    report = format_lint_report(result)
    print(report, file=out)

    if not result.ok:
        return 1
    if args.strict and not result.clean:
        return 2
    return 0
