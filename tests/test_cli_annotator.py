"""Tests for cronscope.cli_annotator."""

import argparse
import io

import pytest

from cronscope.cli_annotator import build_annotator_parser, run_annotator


def _make_args(expression: str) -> argparse.Namespace:
    return argparse.Namespace(expression=expression)


def test_build_annotator_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    p = build_annotator_parser(sub)
    assert p is not None
    parsed = root.parse_args(["annotate", "* * * * *"])
    assert parsed.expression == "* * * * *"


def test_run_annotator_exits_zero_for_valid_expression():
    out, err = io.StringIO(), io.StringIO()
    code = run_annotator(_make_args("* * * * *"), out=out, err=err)
    assert code == 0


def test_run_annotator_output_contains_expression():
    out, err = io.StringIO(), io.StringIO()
    run_annotator(_make_args("0 12 * * 1-5"), out=out, err=err)
    assert "0 12 * * 1-5" in out.getvalue()


def test_run_annotator_output_contains_annotations():
    out, err = io.StringIO(), io.StringIO()
    run_annotator(_make_args("*/10 * * * *"), out=out, err=err)
    assert "every 10 minute(s)" in out.getvalue()


def test_run_annotator_invalid_expression_returns_error():
    out, err = io.StringIO(), io.StringIO()
    code = run_annotator(_make_args("99 * * * *"), out=out, err=err)
    assert code == 1
    assert "Error" in err.getvalue()


def test_run_annotator_invalid_expression_no_stdout():
    out, err = io.StringIO(), io.StringIO()
    run_annotator(_make_args("* * * * 9"), out=out, err=err)
    # invalid dow=9 should not write to stdout
    assert out.getvalue() == ""
