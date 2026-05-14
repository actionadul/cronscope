"""Tests for cronscope.tz_scheduler."""

import pytest
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

from cronscope.tz_scheduler import next_runs_tz, next_runs_tz_from_expr
from cronscope.parser import parse


START_UTC = datetime(2024, 3, 15, 8, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_next_runs_tz_count():
    cron = parse("* * * * *")
    runs = next_runs_tz(cron, count=5, start=START_UTC, tz_name="UTC")
    assert len(runs) == 5


def test_next_runs_tz_all_aware():
    cron = parse("* * * * *")
    runs = next_runs_tz(cron, count=3, start=START_UTC, tz_name="America/New_York")
    for run in runs:
        assert run.tzinfo is not None


def test_next_runs_tz_offset_applied():
    """Runs returned in NY time should be 4 hours behind UTC (summer)."""
    # 2024-03-15 is after DST change (UTC-4)
    cron = parse("0 * * * *")  # every hour on the hour
    runs = next_runs_tz(cron, count=1, start=START_UTC, tz_name="America/New_York")
    assert runs[0].hour == (9 - 4) % 24  # first run is 09:00 UTC => 05:00 NY


def test_next_runs_tz_from_expr_basic():
    runs = next_runs_tz_from_expr("*/15 * * * *", count=4, start=START_UTC, tz_name="UTC")
    assert len(runs) == 4
    # minutes should be multiples of 15
    for run in runs:
        assert run.minute % 15 == 0


def test_next_runs_tz_naive_start_treated_as_tz():
    naive_start = datetime(2024, 3, 15, 8, 0, 0)  # no tzinfo
    cron = parse("* * * * *")
    runs = next_runs_tz(cron, count=3, start=naive_start, tz_name="Europe/Berlin")
    assert len(runs) == 3
    for run in runs:
        assert run.tzinfo == ZoneInfo("Europe/Berlin")


def test_next_runs_tz_invalid_timezone():
    cron = parse("* * * * *")
    with pytest.raises(ValueError, match="Unknown timezone"):
        next_runs_tz(cron, count=1, start=START_UTC, tz_name="Fake/Zone")
