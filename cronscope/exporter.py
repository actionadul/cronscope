"""Export cron schedule data to JSON and CSV formats."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import List, Optional

from cronscope.tz_scheduler import next_runs_tz_from_expr
from cronscope.summarizer import summarize


def _dt_to_str(dt: datetime) -> str:
    """Serialize a datetime (aware or naive) to ISO 8601 string."""
    return dt.isoformat()


def export_json(
    expression: str,
    count: int = 10,
    timezone: str = "UTC",
    start: Optional[datetime] = None,
    indent: int = 2,
) -> str:
    """Return a JSON string with schedule metadata and next run times."""
    runs = next_runs_tz_from_expr(expression, count=count, tz_name=timezone, start=start)
    summary = summarize(expression, tz=timezone)

    payload = {
        "expression": expression,
        "timezone": timezone,
        "human_readable": summary["human_readable"],
        "estimated_runs_per_day": summary["estimated_runs_per_day"],
        "next_runs": [_dt_to_str(r) for r in runs],
    }
    return json.dumps(payload, indent=indent)


def export_csv(
    expression: str,
    count: int = 10,
    timezone: str = "UTC",
    start: Optional[datetime] = None,
) -> str:
    """Return a CSV string with one next-run timestamp per row."""
    runs = next_runs_tz_from_expr(expression, count=count, tz_name=timezone, start=start)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["index", "scheduled_time", "timezone"])
    for idx, run in enumerate(runs, start=1):
        writer.writerow([idx, _dt_to_str(run), timezone])
    return buf.getvalue()


def export(
    expression: str,
    fmt: str = "json",
    count: int = 10,
    timezone: str = "UTC",
    start: Optional[datetime] = None,
) -> str:
    """Dispatch to the appropriate exporter based on *fmt* ('json' or 'csv')."""
    fmt = fmt.lower()
    if fmt == "json":
        return export_json(expression, count=count, timezone=timezone, start=start)
    if fmt == "csv":
        return export_csv(expression, count=count, timezone=timezone, start=start)
    raise ValueError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'csv'.")
