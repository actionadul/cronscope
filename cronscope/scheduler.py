"""Next-run time calculator for parsed cron expressions with timezone support."""

from datetime import datetime, timedelta
from typing import Iterator, List, Optional

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from cronscope.parser import ParsedCron, parse


def _matches_field(value: int, field_values: List[int]) -> bool:
    """Return True if value is in the list of allowed field values."""
    return value in field_values


def _next_run(
    cron: ParsedCron,
    after: datetime,
) -> datetime:
    """Return the next datetime (after `after`) that matches the cron expression.

    `after` should be timezone-aware if a tz was specified, or naive otherwise.
    Raises ValueError if no match is found within a reasonable search window.
    """
    # Advance by at least one minute
    candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

    # Search up to ~4 years to handle rare expressions
    limit = after + timedelta(days=366 * 4)

    while candidate <= limit:
        if not _matches_field(candidate.month, cron.month):
            # Jump to the first day of the next valid month
            candidate = candidate.replace(day=1, hour=0, minute=0)
            candidate += timedelta(days=32)
            candidate = candidate.replace(day=1)
            continue

        if not _matches_field(candidate.day, cron.day_of_month):
            candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
            continue

        if not _matches_field(candidate.weekday() + 1 if candidate.weekday() < 6 else 0,
                               cron.day_of_week):
            candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
            continue

        if not _matches_field(candidate.hour, cron.hour):
            candidate = candidate.replace(minute=0) + timedelta(hours=1)
            continue

        if not _matches_field(candidate.minute, cron.minute):
            candidate += timedelta(minutes=1)
            continue

        return candidate

    raise ValueError("No next run found within the search window.")


def next_runs(
    expression: str,
    count: int = 5,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
) -> List[datetime]:
    """Return the next `count` run times for a cron expression.

    Args:
        expression: A standard 5-field cron expression string.
        count: Number of upcoming run times to return.
        after: Start datetime (defaults to now in the specified timezone).
        timezone: IANA timezone name (e.g. 'America/New_York').

    Returns:
        A list of timezone-aware datetime objects.
    """
    tz = zoneinfo.ZoneInfo(timezone)
    cron = parse(expression)

    if after is None:
        after = datetime.now(tz=tz)
    elif after.tzinfo is None:
        after = after.replace(tzinfo=tz)

    results: List[datetime] = []
    current = after
    for _ in range(count):
        current = _next_run(cron, current)
        results.append(current)

    return results


def next_runs_iter(
    expression: str,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
) -> Iterator[datetime]:
    """Yield next run times indefinitely for a cron expression."""
    tz = zoneinfo.ZoneInfo(timezone)
    cron = parse(expression)

    if after is None:
        after = datetime.now(tz=tz)
    elif after.tzinfo is None:
        after = after.replace(tzinfo=tz)

    current = after
    while True:
        current = _next_run(cron, current)
        yield current
