"""Tests for cronscope.matcher."""

from datetime import datetime

import pytest

from cronscope.matcher import filter_matching, first_match, matches


# ---------------------------------------------------------------------------
# matches()
# ---------------------------------------------------------------------------

def test_matches_every_minute_always_true():
    dt = datetime(2024, 3, 15, 10, 25)
    assert matches("* * * * *", dt) is True


def test_matches_specific_minute_true():
    dt = datetime(2024, 3, 15, 10, 30)
    assert matches("30 * * * *", dt) is True


def test_matches_specific_minute_false():
    dt = datetime(2024, 3, 15, 10, 25)
    assert matches("30 * * * *", dt) is False


def test_matches_specific_hour_and_minute():
    dt = datetime(2024, 3, 15, 14, 0)
    assert matches("0 14 * * *", dt) is True


def test_matches_specific_hour_wrong_minute():
    dt = datetime(2024, 3, 15, 14, 5)
    assert matches("0 14 * * *", dt) is False


def test_matches_day_of_month():
    dt = datetime(2024, 3, 1, 0, 0)
    assert matches("0 0 1 * *", dt) is True


def test_matches_day_of_month_mismatch():
    dt = datetime(2024, 3, 15, 0, 0)
    assert matches("0 0 1 * *", dt) is False


def test_matches_month():
    dt = datetime(2024, 12, 25, 0, 0)
    assert matches("0 0 25 12 *", dt) is True


def test_matches_month_mismatch():
    dt = datetime(2024, 11, 25, 0, 0)
    assert matches("0 0 25 12 *", dt) is False


def test_matches_weekday():
    # 2024-03-18 is a Monday -> weekday() == 0
    dt = datetime(2024, 3, 18, 9, 0)
    assert matches("0 9 * * 0", dt) is True


def test_matches_weekday_mismatch():
    # 2024-03-19 is a Tuesday -> weekday() == 1
    dt = datetime(2024, 3, 19, 9, 0)
    assert matches("0 9 * * 0", dt) is False


def test_matches_step_syntax():
    dt = datetime(2024, 3, 15, 10, 15)
    assert matches("*/15 * * * *", dt) is True


def test_matches_range_syntax():
    dt = datetime(2024, 3, 15, 10, 30)
    assert matches("0-30 * * * *", dt) is True


# ---------------------------------------------------------------------------
# filter_matching()
# ---------------------------------------------------------------------------

def test_filter_matching_returns_subset():
    dts = [datetime(2024, 3, 15, 10, m) for m in range(60)]
    result = filter_matching("0 * * * *", dts)
    assert result == [datetime(2024, 3, 15, 10, 0)]


def test_filter_matching_empty_list():
    assert filter_matching("* * * * *", []) == []


def test_filter_matching_all_match():
    dts = [datetime(2024, 3, 15, 10, m) for m in range(5)]
    result = filter_matching("* * * * *", dts)
    assert len(result) == 5


# ---------------------------------------------------------------------------
# first_match()
# ---------------------------------------------------------------------------

def test_first_match_returns_first():
    dts = [datetime(2024, 3, 15, 10, m) for m in range(60)]
    result = first_match("30 * * * *", dts)
    assert result == datetime(2024, 3, 15, 10, 30)


def test_first_match_returns_none_when_no_match():
    dts = [datetime(2024, 3, 15, 10, m) for m in range(30)]
    result = first_match("45 * * * *", dts)
    assert result is None
