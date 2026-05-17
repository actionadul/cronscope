"""CLI sub-command: annotate a cron expression field-by-field."""

from __future__ import annotations

import argparse
import sys

from cronscope.annotator import format_annotation


def build_annotator_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # noqa: SLF001
    """Register the *annotate* sub-command and return its parser."""
    p = subparsers.add_parser(
        "annotate",
        help="Show inline annotations for each field of a cron expression.",
    )
    p.add_argument("expression", help="Cron expression to annotate (quote it).")
    return p


def run_annotator(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the annotate sub-command.  Returns an exit code."""
    try:
        text = format_annotation(args.expression)
    except ValueError as exc:
        err.write(f"Error: {exc}\n")
        return 1

    out.write(text + "\n")
    return 0
