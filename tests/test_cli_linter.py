"""Tests for cronscope.cli_linter."""

import argparse
import io
import pytest

from cronscope.cli_linter import build_linter_parser, run_linter


def _make_args(expression: str, strict: bool = False) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, strict=strict)


def test_build_linter_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    parser = build_linter_parser(sub)
    assert parser is not None


def test_run_linter_exits_zero_for_clean_expression():
    args = _make_args("15 6 * * 1-5")
    assert run_linter(args, out=io.StringIO(), err=io.StringIO()) == 0


def test_run_linter_exits_one_for_invalid_expression():
    args = _make_args("99 * * * *")
    assert run_linter(args, out=io.StringIO(), err=io.StringIO()) == 1


def test_run_linter_output_contains_expression():
    args = _make_args("30 8 * * 1")
    out = io.StringIO()
    run_linter(args, out=out, err=io.StringIO())
    assert "30 8 * * 1" in out.getvalue()


def test_run_linter_output_contains_ok_for_valid():
    args = _make_args("15 6 * * 1-5")
    out = io.StringIO()
    run_linter(args, out=out, err=io.StringIO())
    assert "OK" in out.getvalue()


def test_run_linter_output_contains_invalid_for_bad_expression():
    args = _make_args("bad expr")
    out = io.StringIO()
    run_linter(args, out=out, err=io.StringIO())
    assert "INVALID" in out.getvalue()


def test_run_linter_strict_exits_two_when_warnings():
    # "0 0 * * *" triggers the @daily alias suggestion warning
    args = _make_args("0 0 * * *", strict=True)
    code = run_linter(args, out=io.StringIO(), err=io.StringIO())
    assert code == 2


def test_run_linter_strict_exits_zero_when_clean():
    args = _make_args("15 6 * * 1-5", strict=True)
    code = run_linter(args, out=io.StringIO(), err=io.StringIO())
    assert code == 0


def test_run_linter_non_strict_exits_zero_when_warnings():
    args = _make_args("0 0 * * *", strict=False)
    code = run_linter(args, out=io.StringIO(), err=io.StringIO())
    assert code == 0
