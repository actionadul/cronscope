"""Compute previous run times for a cron expression (reverse scheduling)."""

from datetime import datetime, timedelta
from typing import Iterator, List

from cronscope.parser import parse, ParsedCron
from cronscope.scheduler import _matches_field


def _prev_run(parsed: ParsedCron, after: datetime) -> datetime:
    """Return the most recent run time strictly before *after*."""
    # Step back one minute from the reference point and scan backwards.
    candidate = after.replace(second=0, microsecond=0) - timedelta(minutes=1)

    # Guard against infinite loops: search at most 4 years back.
    limit = after - timedelta(days=366 * 4)

    while candidate >= limit:
        if (
            _matches_field(parsed.minute, candidate.minute, 0, 59)
            and _matches_field(parsed.hour, candidate.hour, 0, 23)
            and _matches_field(parsed.day, candidate.day, 1, 31)
            and _matches_field(parsed.month, candidate.month, 1, 12)
            and _matches_field(parsed.weekday, candidate.weekday(), 0, 6)
        ):
            return candidate
        candidate -= timedelta(minutes=1)

    raise ValueError("No previous run found within the search window.")


def prev_runs_iter(parsed: ParsedCron, before: datetime) -> Iterator[datetime]:
    """Yield previous run times in reverse chronological order indefinitely."""
    current = before
    while True:
        current = _prev_run(parsed, current)
        yield current


def prev_runs(parsed: ParsedCron, before: datetime, count: int = 5) -> List[datetime]:
    """Return *count* most-recent run times before *before*."""
    if count <= 0:
        raise ValueError("count must be a positive integer")
    results: List[datetime] = []
    for dt in prev_runs_iter(parsed, before):
        results.append(dt)
        if len(results) >= count:
            break
    return results


def prev_runs_from_expr(
    expression: str, before: datetime, count: int = 5
) -> List[datetime]:
    """Parse *expression* and return *count* previous run times before *before*."""
    parsed = parse(expression)
    return prev_runs(parsed, before, count)
