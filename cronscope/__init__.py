"""
cronscope — Visualizer and validator for cron expressions
with next-run previews and timezone awareness.

Public API surface for the cronscope package.
"""

from cronscope.parser import parse, ParsedCron
from cronscope.scheduler import next_runs, next_runs_iter
from cronscope.tz_scheduler import next_runs_tz, next_runs_tz_from_expr
from cronscope.formatter import format_next_runs, format_single_next_run, tabulate_next_runs
from cronscope.timezone import get_timezone, localize, to_utc, now_in, format_with_offset

__version__ = "0.1.0"
__author__ = "cronscope contributors"
__all__ = [
    # Parser
    "parse",
    "ParsedCron",
    # Scheduler
    "next_runs",
    "next_runs_iter",
    # Timezone-aware scheduler
    "next_runs_tz",
    "next_runs_tz_from_expr",
    # Formatter
    "format_next_runs",
    "format_single_next_run",
    "tabulate_next_runs",
    # Timezone utilities
    "get_timezone",
    "localize",
    "to_utc",
    "now_in",
    "format_with_offset",
]
