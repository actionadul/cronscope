"""Tests for cronscope.heatmap."""

import pytest

from cronscope.heatmap import (
    build_hour_heatmap,
    build_weekday_heatmap,
    format_hour_heatmap,
    format_weekday_heatmap,
)


def test_build_hour_heatmap_keys_are_valid_hours():
    heat = build_hour_heatmap("* * * * *", count=100)
    for hour in heat:
        assert 0 <= hour <= 23


def test_build_hour_heatmap_count_matches_total_runs():
    heat = build_hour_heatmap("* * * * *", count=120)
    assert sum(heat.values()) == 120


def test_build_hour_heatmap_specific_hour():
    # Runs only at 14:30 every day
    heat = build_hour_heatmap("30 14 * * *", count=10)
    assert heat.get(14, 0) == 10
    for h, v in heat.items():
        if h != 14:
            assert v == 0


def test_build_weekday_heatmap_keys_are_valid_weekdays():
    heat = build_weekday_heatmap("* * * * *", count=100)
    for wd in heat:
        assert 0 <= wd <= 6


def test_build_weekday_heatmap_count_matches_total_runs():
    heat = build_weekday_heatmap("* * * * *", count=200)
    assert sum(heat.values()) == 200


def test_build_weekday_heatmap_monday_only():
    # cron weekday 1 = Monday
    heat = build_weekday_heatmap("0 9 * * 1", count=4, timezone="UTC")
    # All runs should land on Monday (Python weekday 0 → Sun-based index 1)
    assert sum(heat.values()) == 4
    for wd, v in heat.items():
        if v > 0:
            # Sunday-based: Mon = index 1
            assert wd == 1


def test_format_hour_heatmap_contains_all_hours():
    heat = build_hour_heatmap("* * * * *", count=100)
    rendered = format_hour_heatmap(heat)
    for h in range(24):
        assert f"{h:02d}:00" in rendered


def test_format_hour_heatmap_returns_string():
    heat = {14: 5, 15: 3}
    result = format_hour_heatmap(heat)
    assert isinstance(result, str)
    assert "14:00" in result


def test_format_weekday_heatmap_contains_all_days():
    heat = build_weekday_heatmap("* * * * *", count=100)
    rendered = format_weekday_heatmap(heat)
    for label in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        assert label in rendered


def test_format_weekday_heatmap_empty_heat():
    result = format_weekday_heatmap({})
    assert isinstance(result, str)
    assert "Sun" in result
