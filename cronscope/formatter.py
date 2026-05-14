"""Human-readable formatting for cron next-run previews."""

from datetime import datetime
from typing import List, Optional

from cronscope.scheduler import next_runs

DATE_FORMAT = "%Y-%m-%d %H:%M %Z"


def format_next_runs(
    expression: str,
    count: int = 5,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
    date_format: str = DATE_FORMAT,
) -> str:
    """Return a formatted multi-line string listing the next run times.

    Example output::

        Next 5 runs for '0 9 * * 1-5' (UTC):
          1. 2024-01-08 09:00 UTC
          2. 2024-01-09 09:00 UTC
          ...

    Args:
        expression: A standard 5-field cron expression string.
        count: Number of upcoming run times to include.
        after: Optional reference datetime (defaults to now).
        timezone: IANA timezone name.
        date_format: strftime-compatible format string for each run time.

    Returns:
        A formatted string ready for display.
    """
    runs = next_runs(expression, count=count, after=after, timezone=timezone)
    lines: List[str] = [
        f"Next {count} run(s) for '{expression}' ({timezone}):"
    ]
    for i, run in enumerate(runs, start=1):
        lines.append(f"  {i:>2}. {run.strftime(date_format)}")
    return "\n".join(lines)


def format_single_next_run(
    expression: str,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
    date_format: str = DATE_FORMAT,
) -> str:
    """Return a one-line string describing the immediate next run.

    Example output::

        '*/5 * * * *' will next run at 2024-01-08 12:05 UTC

    Args:
        expression: A standard 5-field cron expression string.
        after: Optional reference datetime (defaults to now).
        timezone: IANA timezone name.
        date_format: strftime-compatible format string.

    Returns:
        A single-line formatted string.
    """
    runs = next_runs(expression, count=1, after=after, timezone=timezone)
    return f"'{expression}' will next run at {runs[0].strftime(date_format)}"


def tabulate_next_runs(
    expressions: List[str],
    count: int = 3,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
    date_format: str = "%Y-%m-%d %H:%M",
) -> str:
    """Return a simple table comparing next runs for multiple expressions.

    Args:
        expressions: List of cron expression strings.
        count: Number of next runs per expression.
        after: Optional reference datetime.
        timezone: IANA timezone name.
        date_format: strftime-compatible format string.

    Returns:
        A formatted table string.
    """
    col_width = max(len(e) for e in expressions) + 2
    header = f"{'Expression':<{col_width}}" + "".join(
        f"  Run #{i + 1:<12}" for i in range(count)
    )
    separator = "-" * len(header)
    rows = [header, separator]

    for expr in expressions:
        runs = next_runs(expr, count=count, after=after, timezone=timezone)
        run_cols = "".join(f"  {r.strftime(date_format):<14}" for r in runs)
        rows.append(f"{expr:<{col_width}}{run_cols}")

    return "\n".join(rows)
