"""Compute diffs and gaps between consecutive next-run timestamps."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any

from cronscope.tz_scheduler import next_runs_tz_from_expr


def _td_to_components(td: timedelta) -> Dict[str, int]:
    """Break a timedelta into days, hours, minutes, seconds."""
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}


def _format_gap(td: timedelta) -> str:
    """Return a human-readable string for a timedelta gap."""
    parts = _td_to_components(td)
    segments = []
    if parts["days"]:
        segments.append(f"{parts['days']}d")
    if parts["hours"]:
        segments.append(f"{parts['hours']}h")
    if parts["minutes"]:
        segments.append(f"{parts['minutes']}m")
    if parts["seconds"] or not segments:
        segments.append(f"{parts['seconds']}s")
    return " ".join(segments)


def compute_gaps(
    expression: str,
    count: int = 10,
    timezone: str = "UTC",
    start: datetime | None = None,
) -> List[Dict[str, Any]]:
    """Return a list of gap records between consecutive scheduled runs.

    Each record contains:
      - ``from_dt``: ISO-formatted start of the interval
      - ``to_dt``:   ISO-formatted end of the interval
      - ``gap_seconds``: gap in total seconds
      - ``gap_human``:   human-readable gap string
    """
    runs = next_runs_tz_from_expr(expression, count=count + 1, timezone=timezone, start=start)
    if len(runs) < 2:
        return []

    records: List[Dict[str, Any]] = []
    for a, b in zip(runs, runs[1:]):
        td = b - a
        records.append(
            {
                "from_dt": a.isoformat(),
                "to_dt": b.isoformat(),
                "gap_seconds": int(td.total_seconds()),
                "gap_human": _format_gap(td),
            }
        )
    return records


def summarize_gaps(gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return min, max, and average gap statistics from a gaps list."""
    if not gaps:
        return {"count": 0, "min_seconds": None, "max_seconds": None, "avg_seconds": None}

    seconds = [g["gap_seconds"] for g in gaps]
    return {
        "count": len(seconds),
        "min_seconds": min(seconds),
        "max_seconds": max(seconds),
        "avg_seconds": round(sum(seconds) / len(seconds), 2),
        "min_human": _format_gap(timedelta(seconds=min(seconds))),
        "max_human": _format_gap(timedelta(seconds=max(seconds))),
    }
