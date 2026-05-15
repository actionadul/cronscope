"""Tests for cronscope.humanizer."""

import pytest
from cronscope.humanizer import humanize, humanize_parsed
from cronscope.parser import parse


def test_every_minute():
    assert humanize("* * * * *") == "Every minute"


def test_specific_time():
    result = humanize("30 9 * * *")
    assert "09:30" in result


def test_hourly_at_minute_0():
    result = humanize("0 * * * *")
    assert "minute" in result.lower()
    assert "0" in result


def test_specific_weekday():
    result = humanize("0 9 * * 1")
    assert "Monday" in result


def test_weekday_range():
    result = humanize("0 9 * * 1-5")
    assert "Monday" in result
    assert "Friday" in result


def test_specific_month():
    result = humanize("0 0 1 6 *")
    assert "June" in result


def test_month_list():
    result = humanize("0 0 1 1,7 *")
    assert "January" in result
    assert "July" in result


def test_step_syntax_minute():
    result = humanize("*/15 * * * *")
    assert "15" in result
    assert "minute" in result.lower()


def test_step_syntax_hour():
    result = humanize("0 */2 * * *")
    assert "2" in result
    assert "hour" in result.lower()


def test_dom_specific():
    result = humanize("0 12 15 * *")
    assert "15" in result


def test_humanize_parsed_roundtrip():
    parsed = parse("30 8 * * 5")
    result = humanize_parsed(parsed)
    assert "08:30" in result
    assert "Friday" in result


def test_result_is_string():
    assert isinstance(humanize("* * * * *"), str)
    assert isinstance(humanize("0 0 * * *"), str)
