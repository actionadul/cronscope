"""Timezone-aware scheduling helpers built on top of scheduler and timezone modules."""

from datetime import datetime
from typing import Iterator, List, Optional

from cronscope.parser import ParsedCron, parse
from cronscope.scheduler import next_runs_iter
from cronscope.timezone import get_timezone, localize, to_utc, now_in


def next_runs_tz(
    cron: ParsedCron,
    count: int = 5,
    start: Optional[datetime] = None,
    tz_name: str = "UTC",
) -> List[datetime]:
    """Return the next *count* run times for *cron* expressed in *tz_name*.

    Parameters
    ----------
    cron:
        A parsed cron expression.
    count:
        Number of upcoming run times to return.
    start:
        Reference datetime.  Defaults to the current time in *tz_name*.
        Naive datetimes are treated as being in *tz_name*.
    tz_name:
        IANA timezone name, e.g. ``"America/New_York"``.
    """
    tz = get_timezone(tz_name)

    if start is None:
        start = now_in(tz_name)
    else:
        start = localize(start, tz_name)

    # scheduler works in UTC; convert start to UTC
    start_utc = to_utc(start)

    results_utc = list(next_runs_iter(cron, count=count, start=start_utc))

    # Convert each result back to the requested timezone
    return [dt.astimezone(tz) for dt in results_utc]


def next_runs_tz_from_expr(
    expression: str,
    count: int = 5,
    start: Optional[datetime] = None,
    tz_name: str = "UTC",
) -> List[datetime]:
    """Convenience wrapper: parse *expression* then call :func:`next_runs_tz`."""
    cron = parse(expression)
    return next_runs_tz(cron, count=count, start=start, tz_name=tz_name)
