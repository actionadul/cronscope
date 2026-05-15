"""Tests for cronscope.summarizer."""

import pytest
from cronscope.summarizer import summarize, summarize_parsed
from cronscope.parser import parse


def test_summarize_returns_expression():
    result = summarize("* * * * *")
    assert result["expression"] == "* * * * *"


def test_summarize_human_readable_every_minute():
    result = summarize("* * * * *")
    assert "minute" in result["human_readable"].lower()


def test_summarize_field_types_all_wildcard():
    result = summarize("* * * * *")
    for field_info in result["fields"].values():
        assert field_info["type"] == "wildcard"


def test_summarize_field_type_exact():
    result = summarize("30 9 * * *")
    assert result["fields"]["minute"]["type"] == "exact"
    assert result["fields"]["hour"]["type"] == "exact"
    assert result["fields"]["day"]["type"] == "wildcard"


def test_summarize_field_type_step():
    result = summarize("*/15 * * * *")
    assert result["fields"]["minute"]["type"] == "step"


def test_summarize_field_type_range():
    result = summarize("0 9-17 * * *")
    assert result["fields"]["hour"]["type"] == "range"


def test_summarize_field_type_list():
    result = summarize("0 8,12,18 * * *")
    assert result["fields"]["hour"]["type"] == "list"


def test_summarize_complexity_all_wildcard():
    result = summarize("* * * * *")
    assert result["complexity"] == 0


def test_summarize_complexity_two_constrained():
    result = summarize("30 9 * * *")
    assert result["complexity"] == 2


def test_summarize_estimated_runs_per_day_every_minute():
    result = summarize("* * * * *")
    assert result["estimated_runs_per_day"] == pytest.approx(1440, rel=0.05)


def test_summarize_estimated_runs_per_day_hourly():
    result = summarize("0 * * * *")
    assert result["estimated_runs_per_day"] == pytest.approx(24, rel=0.1)


def test_summarize_parsed_matches_summarize():
    expr = "0 6 * * 1"
    parsed = parse(expr)
    from_str = summarize(expr)
    from_parsed = summarize_parsed(parsed)
    assert from_str["human_readable"] == from_parsed["human_readable"]
    assert from_str["complexity"] == from_parsed["complexity"]


def test_summarize_field_raw_values():
    result = summarize("5 10 1 6 0")
    assert result["fields"]["minute"]["raw"] == "5"
    assert result["fields"]["hour"]["raw"] == "10"
    assert result["fields"]["month"]["raw"] == "6"
