"""Tests for cronscope.diff_expressions and cronscope.cli_diff."""

import io
import argparse
from datetime import datetime

import pytest

from cronscope.diff_expressions import diff_expressions, format_diff_report, ExpressionDiff
from cronscope.cli_diff import build_diff_parser, run_diff


START = datetime(2024, 1, 1, 0, 0, 0)


# ---------------------------------------------------------------------------
# diff_expressions
# ---------------------------------------------------------------------------

def test_diff_same_expression_has_no_unique_runs():
    diff = diff_expressions("* * * * *", "* * * * *", count=10, start=START)
    assert diff.only_in_a == []
    assert diff.only_in_b == []
    assert len(diff.shared) == 10


def test_diff_disjoint_hours():
    # Every minute at hour 0 vs every minute at hour 1 — no overlap
    diff = diff_expressions("* 0 * * *", "* 1 * * *", count=5, start=START)
    assert diff.shared == []
    assert len(diff.only_in_a) == 5
    assert len(diff.only_in_b) == 5


def test_diff_partial_overlap():
    # Every 30 min vs every 60 min — every-60 is a subset of every-30
    diff = diff_expressions("*/30 * * * *", "0 * * * *", count=48, start=START)
    assert len(diff.shared) > 0
    assert len(diff.only_in_a) > 0
    assert diff.only_in_b == []


def test_diff_similarity_pct_identical():
    diff = diff_expressions("0 * * * *", "0 * * * *", count=10, start=START)
    assert diff.similarity_pct == 100.0


def test_diff_similarity_pct_disjoint():
    diff = diff_expressions("* 0 * * *", "* 1 * * *", count=5, start=START)
    assert diff.similarity_pct == 0.0


def test_diff_human_fields_populated():
    diff = diff_expressions("0 9 * * 1", "0 17 * * 5", count=5, start=START)
    assert diff.human_a != ""
    assert diff.human_b != ""


def test_diff_total_counts():
    diff = diff_expressions("*/30 * * * *", "0 * * * *", count=48, start=START)
    assert diff.total_a == len(diff.only_in_a) + len(diff.shared)
    assert diff.total_b == len(diff.only_in_b) + len(diff.shared)


# ---------------------------------------------------------------------------
# format_diff_report
# ---------------------------------------------------------------------------

def test_format_diff_report_contains_expressions():
    diff = diff_expressions("* * * * *", "0 * * * *", count=10, start=START)
    report = format_diff_report(diff)
    assert "* * * * *" in report
    assert "0 * * * *" in report


def test_format_diff_report_contains_similarity():
    diff = diff_expressions("0 * * * *", "0 * * * *", count=5, start=START)
    report = format_diff_report(diff)
    assert "100.0%" in report


def test_format_diff_report_max_rows_truncates():
    diff = diff_expressions("* 0 * * *", "* 1 * * *", count=20, start=START)
    report = format_diff_report(diff, max_rows=3)
    assert "... and" in report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    defaults = dict(expr_a="* * * * *", expr_b="0 * * * *", count=10, max_rows=5)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_diff_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_diff_parser(sub)
    assert p is not None


def test_run_diff_exits_zero_for_valid_expressions():
    args = _make_args()
    out, err = io.StringIO(), io.StringIO()
    rc = run_diff(args, out=out, err=err)
    assert rc == 0


def test_run_diff_output_contains_similarity():
    args = _make_args(expr_a="0 * * * *", expr_b="0 * * * *")
    out = io.StringIO()
    run_diff(args, out=out, err=io.StringIO())
    assert "Similarity" in out.getvalue()


def test_run_diff_invalid_expr_a_returns_error():
    args = _make_args(expr_a="invalid")
    err = io.StringIO()
    rc = run_diff(args, out=io.StringIO(), err=err)
    assert rc == 1
    assert "Expression A" in err.getvalue()


def test_run_diff_invalid_expr_b_returns_error():
    args = _make_args(expr_b="99 99 99 99 99")
    err = io.StringIO()
    rc = run_diff(args, out=io.StringIO(), err=err)
    assert rc == 1
    assert "Expression B" in err.getvalue()
