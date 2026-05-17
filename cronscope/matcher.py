"""Match arbitrary datetimes against cron expressions."""

from __future__ import annotations

from datetime import datetime
from typing import List

from .parser import parse
from .scheduler import _matches_field


def matches(expression: str, dt: datetime) -> bool:
    """Return True if *dt* satisfies *expression*.

    Parameters
    ----------
    expression:
        A standard five-field cron expression.
    dt:
        The datetime to test.  Timezone information is ignored for
        matching purposes; callers should normalise before calling.
    """
    parsed = parse(expression)
    return (
        _matches_field(parsed.minute, dt.minute, 0, 59)
        and _matches_field(parsed.hour, dt.hour, 0, 23)
        and _matches_field(parsed.day_of_month, dt.day, 1, 31)
        and _matches_field(parsed.month, dt.month, 1, 12)
        and _matches_field(parsed.day_of_week, dt.weekday(), 0, 6)
    )


def filter_matching(expression: str, datetimes: List[datetime]) -> List[datetime]:
    """Return the subset of *datetimes* that match *expression*.

    Parameters
    ----------
    expression:
        A standard five-field cron expression.
    datetimes:
        An iterable of datetime objects to filter.
    """
    parsed = parse(expression)

    def _ok(dt: datetime) -> bool:
        return (
            _matches_field(parsed.minute, dt.minute, 0, 59)
            and _matches_field(parsed.hour, dt.hour, 0, 23)
            and _matches_field(parsed.day_of_month, dt.day, 1, 31)
            and _matches_field(parsed.month, dt.month, 1, 12)
            and _matches_field(parsed.day_of_week, dt.weekday(), 0, 6)
        )

    return [dt for dt in datetimes if _ok(dt)]


def first_match(expression: str, datetimes: List[datetime]) -> datetime | None:
    """Return the first datetime in *datetimes* that matches *expression*,
    or ``None`` if none match.
    """
    for dt in datetimes:
        if matches(expression, dt):
            return dt
    return None
