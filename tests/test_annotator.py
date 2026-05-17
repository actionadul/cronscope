"""Tests for cronscope.annotator."""

import pytest

from cronscope.annotator import annotate, format_annotation


def test_annotate_returns_five_fields():
    result = annotate("* * * * *")
    assert len(result) == 5


def test_annotate_field_names():
    result = annotate("* * * * *")
    names = [r["field"] for r in result]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_annotate_wildcard_minute():
    result = annotate("* * * * *")
    assert result[0]["annotation"] == "every minute"


def test_annotate_step_syntax():
    result = annotate("*/15 * * * *")
    assert result[0]["annotation"] == "every 15 minute(s)"


def test_annotate_specific_value():
    result = annotate("30 * * * *")
    assert result[0]["annotation"] == "30"


def test_annotate_range():
    result = annotate("0 9-17 * * *")
    assert result[1]["annotation"] == "hour 9 to 17"


def test_annotate_range_with_step():
    result = annotate("0 0-23/2 * * *")
    assert result[1]["annotation"] == "hour 0-23 step 2"


def test_annotate_list():
    result = annotate("0 8,12,18 * * *")
    assert result[1]["annotation"] == "8, 12, 18"


def test_annotate_month_name():
    result = annotate("0 0 1 6 *")
    assert result[3]["annotation"] == "Jun"


def test_annotate_month_range_names():
    result = annotate("0 0 1 3-5 *")
    assert result[3]["annotation"] == "month Mar to May"


def test_annotate_dow_name():
    result = annotate("0 9 * * 1")
    assert result[4]["annotation"] == "Mon"


def test_annotate_dow_range_names():
    result = annotate("0 9 * * 1-5")
    assert result[4]["annotation"] == "day_of_week Mon to Fri"


def test_annotate_invalid_expression_raises():
    with pytest.raises(ValueError):
        annotate("99 * * * *")


def test_format_annotation_contains_expression():
    text = format_annotation("0 * * * *")
    assert "0 * * * *" in text


def test_format_annotation_contains_field_annotations():
    text = format_annotation("*/5 * * * *")
    assert "every 5 minute(s)" in text
    assert "every hour" in text
