"""Tests for the next-run scheduler module."""

from datetime import datetime

import pytest

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from cronscope.scheduler import next_runs, next_runs_iter

UTC = zoneinfo.ZoneInfo("UTC")


def dt(year, month, day, hour=0, minute=0, tz=UTC) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=tz)


class TestNextRuns:
    def test_every_minute_returns_count(self):
        runs = next_runs("* * * * *", count=5, after=dt(2024, 1, 1, 12, 0))
        assert len(runs) == 5

    def test_every_minute_increments_by_one(self):
        runs = next_runs("* * * * *", count=3, after=dt(2024, 1, 1, 12, 0))
        assert runs[0] == dt(2024, 1, 1, 12, 1)
        assert runs[1] == dt(2024, 1, 1, 12, 2)
        assert runs[2] == dt(2024, 1, 1, 12, 3)

    def test_hourly_at_minute_30(self):
        runs = next_runs("30 * * * *", count=2, after=dt(2024, 1, 1, 12, 0))
        assert runs[0] == dt(2024, 1, 1, 12, 30)
        assert runs[1] == dt(2024, 1, 1, 13, 30)

    def test_daily_midnight(self):
        runs = next_runs("0 0 * * *", count=2, after=dt(2024, 1, 1, 0, 1))
        assert runs[0] == dt(2024, 1, 2, 0, 0)
        assert runs[1] == dt(2024, 1, 3, 0, 0)

    def test_specific_day_of_month(self):
        runs = next_runs("0 9 15 * *", count=2, after=dt(2024, 1, 1, 0, 0))
        assert runs[0] == dt(2024, 1, 15, 9, 0)
        assert runs[1] == dt(2024, 2, 15, 9, 0)

    def test_step_syntax(self):
        runs = next_runs("*/15 * * * *", count=4, after=dt(2024, 1, 1, 12, 0))
        assert runs[0] == dt(2024, 1, 1, 12, 15)
        assert runs[1] == dt(2024, 1, 1, 12, 30)
        assert runs[2] == dt(2024, 1, 1, 12, 45)
        assert runs[3] == dt(2024, 1, 1, 13, 0)

    def test_timezone_awareness(self):
        tz = zoneinfo.ZoneInfo("America/New_York")
        runs = next_runs("0 9 * * *", count=1, timezone="America/New_York")
        assert runs[0].tzinfo is not None
        assert runs[0].hour == 9

    def test_after_defaults_to_now(self):
        runs = next_runs("* * * * *", count=1)
        assert len(runs) == 1
        assert runs[0] > datetime.now(tz=zoneinfo.ZoneInfo("UTC"))

    def test_naive_after_gets_tz_attached(self):
        naive = datetime(2024, 6, 1, 10, 0)
        runs = next_runs("0 11 * * *", count=1, after=naive, timezone="UTC")
        assert runs[0].tzinfo is not None
        assert runs[0].hour == 11

    def test_monthly_expression(self):
        runs = next_runs("0 0 1 */3 *", count=2, after=dt(2024, 1, 1, 0, 1))
        assert runs[0].month in (1, 4, 7, 10)
        assert runs[1].month in (1, 4, 7, 10)


class TestNextRunsIter:
    def test_yields_correct_sequence(self):
        gen = next_runs_iter("0 * * * *", after=dt(2024, 1, 1, 0, 0))
        first = next(gen)
        second = next(gen)
        assert first == dt(2024, 1, 1, 1, 0)
        assert second == dt(2024, 1, 1, 2, 0)

    def test_yields_indefinitely(self):
        gen = next_runs_iter("* * * * *", after=dt(2024, 1, 1, 0, 0))
        results = [next(gen) for _ in range(10)]
        assert len(results) == 10
        assert results[-1] == dt(2024, 1, 1, 0, 10)
