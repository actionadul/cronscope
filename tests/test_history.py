"""Tests for cronscope.history — reverse scheduling (previous runs)."""

from datetime import datetime

import pytest

from cronscope.parser import parse
from cronscope.history import prev_runs, prev_runs_from_expr, prev_runs_iter


@pytest.fixture
def ref():
    """A fixed reference datetime: 2024-03-15 12:30:00."""
    return datetime(2024, 3, 15, 12, 30, 0)


def test_prev_runs_returns_correct_count(ref):
    parsed = parse("* * * * *")
    result = prev_runs(parsed, ref, count=5)
    assert len(result) == 5


def test_prev_runs_strictly_before_reference(ref):
    parsed = parse("* * * * *")
    result = prev_runs(parsed, ref, count=10)
    for dt in result:
        assert dt < ref


def test_prev_runs_every_minute_decrements_by_one(ref):
    parsed = parse("* * * * *")
    result = prev_runs(parsed, ref, count=3)
    assert result[0] == datetime(2024, 3, 15, 12, 29)
    assert result[1] == datetime(2024, 3, 15, 12, 28)
    assert result[2] == datetime(2024, 3, 15, 12, 27)


def test_prev_runs_hourly_at_minute_0(ref):
    # ref is 12:30 — last run at minute 0 was 12:00
    parsed = parse("0 * * * *")
    result = prev_runs(parsed, ref, count=3)
    assert result[0] == datetime(2024, 3, 15, 12, 0)
    assert result[1] == datetime(2024, 3, 15, 11, 0)
    assert result[2] == datetime(2024, 3, 15, 10, 0)


def test_prev_runs_specific_hour(ref):
    # Expression fires only at 09:00 every day
    parsed = parse("0 9 * * *")
    result = prev_runs(parsed, ref, count=2)
    assert result[0] == datetime(2024, 3, 15, 9, 0)
    assert result[1] == datetime(2024, 3, 14, 9, 0)


def test_prev_runs_invalid_count_raises(ref):
    parsed = parse("* * * * *")
    with pytest.raises(ValueError):
        prev_runs(parsed, ref, count=0)


def test_prev_runs_from_expr_basic(ref):
    result = prev_runs_from_expr("* * * * *", ref, count=3)
    assert len(result) == 3
    assert all(dt < ref for dt in result)


def test_prev_runs_iter_yields_indefinitely(ref):
    parsed = parse("* * * * *")
    gen = prev_runs_iter(parsed, ref)
    values = [next(gen) for _ in range(20)]
    assert len(values) == 20
    assert all(values[i] > values[i + 1] for i in range(len(values) - 1))


def test_prev_runs_weekday_filter():
    # Monday = weekday 0 in cron (but Python uses 0=Monday too)
    # Expression: every minute on Fridays only (weekday 4 in Python)
    ref = datetime(2024, 3, 15, 0, 5)  # Friday 2024-03-15
    parsed = parse("* * * * 5")  # cron weekday 5 = Friday
    result = prev_runs(parsed, ref, count=3)
    for dt in result:
        # Python weekday: Friday == 4
        assert dt.weekday() == 4
