"""Tests for cronscope.linter."""

import pytest
from cronscope.linter import lint, format_lint_report, LintResult


def test_lint_returns_lint_result():
    result = lint("* * * * *")
    assert isinstance(result, LintResult)


def test_lint_valid_expression_is_ok():
    result = lint("30 8 * * 1")
    assert result.ok


def test_lint_invalid_expression_has_error():
    result = lint("99 * * * *")
    assert not result.ok
    assert len(result.errors) == 1


def test_lint_wildcard_both_day_fields_warns():
    result = lint("0 12 * * *")
    assert result.ok
    assert any("day-of-month" in w for w in result.warnings)


def test_lint_no_warning_when_weekday_specified():
    result = lint("0 12 * * 1")
    assert result.ok
    # day-of-month is *, but weekday is explicit — no redundant-wildcard warning
    assert not any("day-of-month" in w for w in result.warnings)


def test_lint_step_one_warns():
    result = lint("*/1 * * * *")
    assert result.ok
    assert any("step of 1" in w for w in result.warnings)


def test_lint_step_non_one_does_not_warn():
    result = lint("*/5 * * * *")
    assert not any("step of 1" in w for w in result.warnings)


def test_lint_alias_suggestion_daily():
    result = lint("0 0 * * *")
    assert result.ok
    assert any("@daily" in w for w in result.warnings)


def test_lint_alias_suggestion_hourly():
    result = lint("0 * * * *")
    assert any("@hourly" in w for w in result.warnings)


def test_lint_clean_expression():
    result = lint("15 6 * * 1-5")
    assert result.clean


def test_lint_alias_input_resolves():
    result = lint("@daily")
    assert result.ok


def test_format_lint_report_clean():
    result = lint("15 6 * * 1-5")
    report = format_lint_report(result)
    assert "OK" in report
    assert "no issues" in report


def test_format_lint_report_with_warnings():
    result = lint("0 0 * * *")
    report = format_lint_report(result)
    assert "WARNING" in report


def test_format_lint_report_with_errors():
    result = lint("invalid")
    report = format_lint_report(result)
    assert "INVALID" in report
    assert "ERROR" in report


def test_lint_result_clean_false_when_warnings():
    result = lint("0 0 * * *")
    assert result.ok
    assert not result.clean
