"""Tests for cronscope.conflict."""

import pytest
from cronscope.conflict import (
    check_expression,
    check_expressions,
    format_conflict_report,
    ConflictReport,
)


def test_valid_every_minute_is_too_frequent():
    report = check_expression("* * * * *")
    assert report.is_valid
    assert report.is_too_frequent
    assert not report.is_too_rare
    assert report.runs_per_day == pytest.approx(1440, rel=0.01)


def test_hourly_not_flagged():
    report = check_expression("0 * * * *")
    assert report.is_valid
    assert not report.is_too_frequent
    assert not report.is_too_rare


def test_daily_not_flagged():
    report = check_expression("0 9 * * *")
    assert report.is_valid
    assert not report.is_too_frequent
    assert not report.is_too_rare
    assert len(report.warnings) == 0


def test_monthly_is_too_rare():
    report = check_expression("0 0 1 * *")
    assert report.is_valid
    assert report.is_too_rare
    assert not report.is_too_frequent
    assert report.runs_per_day < 1


def test_invalid_expression_returns_invalid_report():
    report = check_expression("99 99 99 99 99")
    assert not report.is_valid
    assert report.parse_error is not None
    assert report.runs_per_day is None
    assert len(report.warnings) > 0


def test_check_expressions_returns_one_per_input():
    exprs = ["* * * * *", "0 9 * * *", "bad expr"]
    reports = check_expressions(exprs)
    assert len(reports) == 3
    assert isinstance(reports[0], ConflictReport)


def test_format_conflict_report_valid_no_warnings():
    report = check_expression("0 9 * * *")
    text = format_conflict_report(report)
    assert "valid" in text
    assert "No conflicts" in text


def test_format_conflict_report_too_frequent():
    report = check_expression("* * * * *")
    text = format_conflict_report(report)
    assert "WARNING" in text
    assert "frequently" in text.lower() or "times/day" in text


def test_format_conflict_report_invalid():
    report = check_expression("not a cron")
    text = format_conflict_report(report)
    assert "INVALID" in text


def test_warnings_list_populated_for_frequent():
    report = check_expression("*/5 * * * *")
    # 288 runs/day — above threshold
    assert report.is_too_frequent
    assert any("times/day" in w for w in report.warnings)
