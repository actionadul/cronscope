"""Summarize cron expression statistics and metadata."""

from typing import Any
from datetime import datetime, timezone

from cronscope.parser import ParsedCron, parse
from cronscope.humanizer import humanize_parsed
from cronscope.scheduler import next_runs


def _field_type(field: str) -> str:
    """Classify a cron field as wildcard, step, range, list, or exact."""
    if field == "*":
        return "wildcard"
    if "/" in field:
        return "step"
    if "-" in field and "," not in field:
        return "range"
    if "," in field:
        return "list"
    return "exact"


def _estimate_runs_per_day(parsed: ParsedCron) -> float:
    """Rough estimate of how many times the expression fires per day."""
    start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    runs = next_runs(parsed, start, count=1440)
    if not runs:
        return 0.0
    span_seconds = (runs[-1] - runs[0]).total_seconds()
    if span_seconds <= 0:
        return float(len(runs))
    runs_per_second = (len(runs) - 1) / span_seconds
    return round(runs_per_second * 86400, 4)


def summarize(expr: str) -> dict[str, Any]:
    """Return a summary dict for a cron expression string."""
    parsed = parse(expr)
    field_names = ["minute", "hour", "day", "month", "weekday"]
    raw_fields = [parsed.minute, parsed.hour, parsed.day, parsed.month, parsed.weekday]

    field_summary = {
        name: {"raw": raw, "type": _field_type(raw)}
        for name, raw in zip(field_names, raw_fields)
    }

    return {
        "expression": expr,
        "fields": field_summary,
        "human_readable": humanize_parsed(parsed),
        "estimated_runs_per_day": _estimate_runs_per_day(parsed),
        "complexity": sum(
            0 if v["type"] == "wildcard" else 1
            for v in field_summary.values()
        ),
    }


def summarize_parsed(parsed: ParsedCron) -> dict[str, Any]:
    """Return a summary dict for an already-parsed cron expression."""
    expr = " ".join([
        parsed.minute, parsed.hour, parsed.day,
        parsed.month, parsed.weekday,
    ])
    return summarize(expr)
