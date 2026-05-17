"""Heatmap generator for cron expression activity across hours and weekdays."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional

from cronscope.tz_scheduler import next_runs_tz_from_expr

# Labels for display
_HOUR_LABELS = [f"{h:02d}" for h in range(24)]
_DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def build_hour_heatmap(
    expression: str,
    count: int = 500,
    timezone: str = "UTC",
) -> Dict[int, int]:
    """Return a mapping of hour -> run count over the next *count* occurrences."""
    runs = next_runs_tz_from_expr(expression, count=count, timezone=timezone)
    heat: Dict[int, int] = defaultdict(int)
    for dt in runs:
        heat[dt.hour] += 1
    return dict(heat)


def build_weekday_heatmap(
    expression: str,
    count: int = 500,
    timezone: str = "UTC",
) -> Dict[int, int]:
    """Return a mapping of weekday (0=Sun … 6=Sat) -> run count."""
    runs = next_runs_tz_from_expr(expression, count=count, timezone=timezone)
    heat: Dict[int, int] = defaultdict(int)
    for dt in runs:
        # Python's weekday(): Mon=0 … Sun=6 — convert to Sun=0 … Sat=6
        wd = (dt.weekday() + 1) % 7
        heat[wd] += 1
    return dict(heat)


def format_hour_heatmap(heat: Dict[int, int], bar_width: int = 20) -> str:
    """Render the hour heatmap as an ASCII bar chart string."""
    max_val = max(heat.values(), default=1)
    lines: List[str] = ["Hour  Runs  Chart"]
    lines.append("-" * (bar_width + 16))
    for h in range(24):
        val = heat.get(h, 0)
        bar_len = int(val / max_val * bar_width) if max_val else 0
        bar = "█" * bar_len
        lines.append(f"{h:02d}:00  {val:4d}  {bar}")
    return "\n".join(lines)


def format_weekday_heatmap(heat: Dict[int, int], bar_width: int = 20) -> str:
    """Render the weekday heatmap as an ASCII bar chart string."""
    max_val = max(heat.values(), default=1)
    lines: List[str] = ["Day   Runs  Chart"]
    lines.append("-" * (bar_width + 16))
    for wd in range(7):
        val = heat.get(wd, 0)
        bar_len = int(val / max_val * bar_width) if max_val else 0
        bar = "█" * bar_len
        lines.append(f"{_DAY_LABELS[wd]}   {val:4d}  {bar}")
    return "\n".join(lines)
