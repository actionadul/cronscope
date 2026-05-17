"""Tests for cronscope.cli_overlap."""

import argparse
from io import StringIO

import pytest

from cronscope.cli_overlap import build_overlap_parser, run_overlap


def _make_args(expressions, count=100):
    ns = argparse.Namespace()
    ns.expressions = expressions
    ns.count = count
    return ns


def test_build_overlap_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_overlap_parser(sub)
    assert p is not None


def test_run_overlap_requires_two_expressions():
    out, err = StringIO(), StringIO()
    rc = run_overlap(_make_args(["* * * * *"]), out=out, err=err)
    assert rc == 2
    assert "at least two" in err.getvalue()


def test_run_overlap_invalid_expression_returns_error():
    out, err = StringIO(), StringIO()
    rc = run_overlap(_make_args(["* * * * *", "not-valid"]), out=out, err=err)
    assert rc == 1
    assert "invalid expression" in err.getvalue()


def test_run_overlap_no_overlap_exits_zero():
    out, err = StringIO(), StringIO()
    rc = run_overlap(_make_args(["0 * * * *", "30 * * * *"], count=24), out=out, err=err)
    assert rc == 0
    assert "No overlaps found" in out.getvalue()


def test_run_overlap_detects_overlap():
    out, err = StringIO(), StringIO()
    rc = run_overlap(_make_args(["* * * * *", "*/5 * * * *"], count=20), out=out, err=err)
    assert rc == 0
    assert "Overlapping expressions detected" in out.getvalue()


def test_run_overlap_three_expressions():
    out, err = StringIO(), StringIO()
    exprs = ["* * * * *", "*/5 * * * *", "0 * * * *"]
    rc = run_overlap(_make_args(exprs, count=60), out=out, err=err)
    assert rc == 0
    output = out.getvalue()
    # Three pairs should each produce a report block
    assert output.count("Expressions") == 3


def test_run_overlap_report_contains_expressions():
    out, err = StringIO(), StringIO()
    run_overlap(_make_args(["0 * * * *", "0 */2 * * *"], count=48), out=out, err=err)
    output = out.getvalue()
    assert "0 * * * *" in output
    assert "0 */2 * * *" in output
