"""Tests for cronscope.differ."""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

import pytest

from cronscope.differ import compute_gaps, summarize_gaps, _format_gap, _td_to_components
from datetime import timedelta


# ---------------------------------------------------------------------------
# _td_to_components
# ---------------------------------------------------------------------------

def test_td_to_components_one_day():
    parts = _td_to_components(timedelta(days=1))
    assert parts == {"days": 1, "hours": 0, "minutes": 0, "seconds": 0}


def test_td_to_components_mixed():
    td = timedelta(days=0, hours=2, minutes=30, seconds=15)
    parts = _td_to_components(td)
    assert parts["hours"] == 2
    assert parts["minutes"] == 30
    assert parts["seconds"] == 15


# ---------------------------------------------------------------------------
# _format_gap
# ---------------------------------------------------------------------------

def test_format_gap_minutes_only():
    assert _format_gap(timedelta(minutes=5)) == "5m 0s"


def test_format_gap_zero():
    assert _format_gap(timedelta(seconds=0)) == "0s"


def test_format_gap_days_and_hours():
    result = _format_gap(timedelta(days=1, hours=3))
    assert "1d" in result
    assert "3h" in result


# ---------------------------------------------------------------------------
# compute_gaps
# ---------------------------------------------------------------------------

@pytest.fixture
def start_dt():
    return datetime(2024, 1, 1, 0, 0, 0, tzinfo=dt_timezone.utc)


def test_compute_gaps_every_minute_count(start_dt):
    gaps = compute_gaps("* * * * *", count=5, timezone="UTC", start=start_dt)
    assert len(gaps) == 5


def test_compute_gaps_every_minute_gap_seconds(start_dt):
    gaps = compute_gaps("* * * * *", count=3, timezone="UTC", start=start_dt)
    for gap in gaps:
        assert gap["gap_seconds"] == 60


def test_compute_gaps_every_minute_gap_human(start_dt):
    gaps = compute_gaps("* * * * *", count=2, timezone="UTC", start=start_dt)
    assert gaps[0]["gap_human"] == "1m 0s"


def test_compute_gaps_has_from_and_to_keys(start_dt):
    gaps = compute_gaps("* * * * *", count=2, timezone="UTC", start=start_dt)
    assert "from_dt" in gaps[0]
    assert "to_dt" in gaps[0]


def test_compute_gaps_hourly(start_dt):
    gaps = compute_gaps("0 * * * *", count=3, timezone="UTC", start=start_dt)
    for gap in gaps:
        assert gap["gap_seconds"] == 3600


def test_compute_gaps_empty_when_count_zero(start_dt):
    gaps = compute_gaps("* * * * *", count=0, timezone="UTC", start=start_dt)
    assert gaps == []


# ---------------------------------------------------------------------------
# summarize_gaps
# ---------------------------------------------------------------------------

def test_summarize_gaps_empty():
    result = summarize_gaps([])
    assert result["count"] == 0
    assert result["min_seconds"] is None


def test_summarize_gaps_uniform():
    gaps = [{"gap_seconds": 60, "gap_human": "1m 0s"} for _ in range(5)]
    result = summarize_gaps(gaps)
    assert result["count"] == 5
    assert result["min_seconds"] == 60
    assert result["max_seconds"] == 60
    assert result["avg_seconds"] == 60.0


def test_summarize_gaps_varied():
    gaps = [{"gap_seconds": s, "gap_human": ""} for s in [60, 120, 180]]
    result = summarize_gaps(gaps)
    assert result["min_seconds"] == 60
    assert result["max_seconds"] == 180
    assert result["avg_seconds"] == 120.0


def test_summarize_gaps_human_keys():
    gaps = [{"gap_seconds": 3600, "gap_human": "1h 0s"}]
    result = summarize_gaps(gaps)
    assert "min_human" in result
    assert "max_human" in result
