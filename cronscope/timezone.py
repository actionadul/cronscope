"""Timezone utilities for cronscope."""

from datetime import datetime
from typing import Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore


UTC = ZoneInfo("UTC")


def get_timezone(tz_name: str) -> ZoneInfo:
    """Return a ZoneInfo object for the given timezone name.

    Raises:
        ValueError: if the timezone name is not recognized.
    """
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError):
        raise ValueError(f"Unknown timezone: {tz_name!r}")


def localize(dt: datetime, tz_name: str) -> datetime:
    """Attach timezone info to a naive datetime or convert an aware one.

    If *dt* is naive it is treated as being in *tz_name*.
    If *dt* is already aware it is converted to *tz_name*.
    """
    tz = get_timezone(tz_name)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def to_utc(dt: datetime) -> datetime:
    """Convert an aware datetime to UTC.

    Raises:
        ValueError: if *dt* is naive.
    """
    if dt.tzinfo is None:
        raise ValueError("Cannot convert naive datetime to UTC; attach a timezone first.")
    return dt.astimezone(UTC)


def now_in(tz_name: str) -> datetime:
    """Return the current time in the given timezone."""
    tz = get_timezone(tz_name)
    return datetime.now(tz=tz)


def format_with_offset(dt: datetime) -> str:
    """Return an ISO-8601 string with UTC offset, e.g. '2024-03-15 09:00:00+05:30'."""
    if dt.tzinfo is None:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d %H:%M:%S%z")
