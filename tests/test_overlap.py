"""Tests for cronscope.overlap."""

from datetime import datetime

import pytest

from cronscope.overlap import (
    OverlapResult,
    compare_expressions,
    find_overlaps,
    format_overlap_report,
)


START = datetime(2024, 1, 1, 0, 0, 0)


def test_every_minute_overlaps_with_itself():
    result = find_overlaps("* * * * *", "* * * * *", start=START, count=10)
    assert result.overlap_count == 10
    assert result.has_overlap


def test_no_overlap_different_hours():
    # one fires at minute 0, the other at minute 30 — they share no slot in 1 hour
    result = find_overlaps("0 * * * *", "30 * * * *", start=START, count=24)
    assert result.overlap_count == 0
    assert not result.has_overlap


def test_overlap_at_specific_shared_minute():
    # both fire at minute 0 of every hour
    result = find_overlaps("0 * * * *", "0 */2 * * *", start=START, count=48)
    assert result.overlap_count > 0
    for dt in result.shared_times:
        assert dt.minute == 0


def test_overlap_result_fields():
    result = find_overlaps("* * * * *", "*/5 * * * *", start=START, count=20)
    assert result.expr_a == "* * * * *"
    assert result.expr_b == "*/5 * * * *"
    assert isinstance(result.shared_times, list)


def test_compare_expressions_returns_all_pairs():
    exprs = ["* * * * *", "*/5 * * * *", "0 * * * *"]
    results = compare_expressions(exprs, start=START, count=60)
    assert len(results) == 3  # C(3,2)
    pairs = {(r.expr_a, r.expr_b) for r in results}
    assert ("* * * * *", "*/5 * * * *") in pairs
    assert ("* * * * *", "0 * * * *") in pairs
    assert ("*/5 * * * *", "0 * * * *") in pairs


def test_compare_expressions_single_returns_empty():
    results = compare_expressions(["* * * * *"], start=START, count=10)
    assert results == []


def test_format_overlap_report_no_overlap():
    result = OverlapResult(
        expr_a="0 * * * *",
        expr_b="30 * * * *",
        shared_times=[],
        overlap_count=0,
    )
    report = format_overlap_report(result)
    assert "No shared run times" in report
    assert "0 * * * *" in report


def test_format_overlap_report_with_overlap():
    shared = [datetime(2024, 1, 1, h, 0) for h in range(3)]
    result = OverlapResult(
        expr_a="0 * * * *",
        expr_b="* * * * *",
        shared_times=shared,
        overlap_count=3,
    )
    report = format_overlap_report(result)
    assert "Overlaps    : 3" in report
    assert "2024-01-01" in report


def test_format_overlap_report_truncates_long_list():
    shared = [datetime(2024, 1, 1, 0, m) for m in range(15)]
    result = OverlapResult(
        expr_a="* * * * *",
        expr_b="* * * * *",
        shared_times=shared,
        overlap_count=15,
    )
    report = format_overlap_report(result)
    assert "... and 5 more" in report
