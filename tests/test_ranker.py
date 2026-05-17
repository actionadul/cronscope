"""Tests for cronscope.ranker."""

import pytest
from cronscope.ranker import rank_expressions, format_rank_report, RankResult


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY_NOON = "0 12 * * *"
WEEKLY = "0 9 * * 1"
MONTHLY = "0 8 1 * *"


def test_rank_returns_list_of_rank_results():
    results = rank_expressions([EVERY_MINUTE, HOURLY, DAILY_NOON])
    assert all(isinstance(r, RankResult) for r in results)


def test_rank_assigns_sequential_ranks():
    results = rank_expressions([EVERY_MINUTE, HOURLY, DAILY_NOON])
    ranks = [r.rank for r in results]
    assert ranks == list(range(1, len(results) + 1))


def test_rank_by_runs_per_day_ascending():
    results = rank_expressions(
        [EVERY_MINUTE, HOURLY, DAILY_NOON], sort_by="runs_per_day", ascending=True
    )
    rpd_values = [r.runs_per_day for r in results]
    assert rpd_values == sorted(rpd_values)


def test_rank_by_runs_per_day_descending():
    results = rank_expressions(
        [EVERY_MINUTE, HOURLY, DAILY_NOON], sort_by="runs_per_day", ascending=False
    )
    rpd_values = [r.runs_per_day for r in results]
    assert rpd_values == sorted(rpd_values, reverse=True)


def test_rank_by_specificity_ascending():
    results = rank_expressions(
        [EVERY_MINUTE, HOURLY, WEEKLY], sort_by="specificity", ascending=True
    )
    scores = [r.specificity_score for r in results]
    assert scores == sorted(scores)


def test_every_minute_has_highest_runs_per_day():
    results = rank_expressions(
        [EVERY_MINUTE, HOURLY, DAILY_NOON], sort_by="runs_per_day", ascending=False
    )
    assert results[0].expression == EVERY_MINUTE


def test_invalid_expression_skipped():
    results = rank_expressions(["not_valid", HOURLY])
    expressions = [r.expression for r in results]
    assert "not_valid" not in expressions
    assert HOURLY in expressions


def test_empty_input_returns_empty_list():
    assert rank_expressions([]) == []


def test_all_invalid_returns_empty_list():
    assert rank_expressions(["bad expr", "also bad"]) == []


def test_human_readable_populated():
    results = rank_expressions([HOURLY])
    assert results[0].human_readable != ""


def test_format_rank_report_contains_expression():
    results = rank_expressions([DAILY_NOON, MONTHLY])
    report = format_rank_report(results)
    assert DAILY_NOON in report
    assert MONTHLY in report


def test_format_rank_report_empty():
    report = format_rank_report([])
    assert "No valid" in report


def test_format_rank_report_has_header():
    results = rank_expressions([HOURLY])
    report = format_rank_report(results)
    assert "Rank" in report
    assert "Runs/Day" in report
