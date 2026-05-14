"""Tests for cronscope.timezone."""

import pytest
from datetime import datetime

from cronscope.timezone import (
    get_timezone,
    localize,
    to_utc,
    format_with_offset,
)

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore


def test_get_timezone_valid():
    tz = get_timezone("America/New_York")
    assert tz == ZoneInfo("America/New_York")


def test_get_timezone_invalid():
    with pytest.raises(ValueError, match="Unknown timezone"):
        get_timezone("Mars/Olympus")


def test_localize_naive():
    naive = datetime(2024, 6, 1, 12, 0, 0)
    aware = localize(naive, "Europe/London")
    assert aware.tzinfo is not None
    assert aware.year == 2024
    assert aware.hour == 12


def test_localize_aware_converts():
    utc_dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    ny_dt = localize(utc_dt, "America/New_York")
    # UTC-4 in summer
    assert ny_dt.hour == 8


def test_to_utc_aware():
    ny_tz = ZoneInfo("America/New_York")
    ny_dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=ny_tz)  # UTC-5 in winter
    utc_dt = to_utc(ny_dt)
    assert utc_dt.hour == 5
    assert str(utc_dt.tzinfo) == "UTC"


def test_to_utc_naive_raises():
    with pytest.raises(ValueError, match="naive datetime"):
        to_utc(datetime(2024, 1, 1, 0, 0, 0))


def test_format_with_offset_aware():
    tz = ZoneInfo("UTC")
    dt = datetime(2024, 3, 15, 9, 0, 0, tzinfo=tz)
    result = format_with_offset(dt)
    assert result.startswith("2024-03-15 09:00:00")
    assert "+" in result or result.endswith("+0000")


def test_format_with_offset_naive():
    dt = datetime(2024, 3, 15, 9, 0, 0)
    result = format_with_offset(dt)
    assert result == "2024-03-15 09:00:00"
