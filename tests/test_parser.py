"""Tests for cronscope.parser module."""

import pytest
from cronscope.parser import parse, ParsedCron


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_parse_every_minute():
    result = parse("* * * * *")
    assert isinstance(result, ParsedCron)
    assert result.minute == "*"
    assert result.raw == "* * * * *"


def test_parse_specific_values():
    result = parse("30 6 1 1 0")
    assert result.minute == "30"
    assert result.hour == "6"
    assert result.day == "1"
    assert result.month == "1"
    assert result.weekday == "0"


def test_parse_step_syntax():
    result = parse("*/5 * * * *")
    assert result.minute == "*/5"


def test_parse_range_syntax():
    result = parse("0 9-17 * * 1-5")
    assert result.hour == "9-17"
    assert result.weekday == "1-5"


def test_parse_list_syntax():
    result = parse("0 8,12,18 * * *")
    assert result.hour == "8,12,18"


def test_as_dict_returns_correct_keys():
    result = parse("15 10 * * 3")
    d = result.as_dict()
    assert set(d.keys()) == {"minute", "hour", "day", "month", "weekday"}
    assert d["minute"] == "15"


# ---------------------------------------------------------------------------
# Error / validation tests
# ---------------------------------------------------------------------------

def test_too_few_fields_raises():
    with pytest.raises(ValueError, match="Expected 5 fields"):
        parse("* * * *")


def test_too_many_fields_raises():
    with pytest.raises(ValueError, match="Expected 5 fields"):
        parse("* * * * * *")


def test_minute_out_of_range_raises():
    with pytest.raises(ValueError, match="out of bounds"):
        parse("60 * * * *")


def test_hour_out_of_range_raises():
    with pytest.raises(ValueError, match="out of bounds"):
        parse("0 25 * * *")


def test_invalid_range_order_raises():
    with pytest.raises(ValueError, match="out of bounds|Range"):
        parse("0 18-9 * * *")


def test_step_zero_raises():
    with pytest.raises(ValueError, match="Step value cannot be zero"):
        parse("*/0 * * * *")


def test_unrecognised_token_raises():
    with pytest.raises(ValueError, match="Unrecognised token"):
        parse("abc * * * *")
