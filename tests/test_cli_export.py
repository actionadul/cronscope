"""Tests for cronscope.cli_export."""

from __future__ import annotations

import argparse
import json
from unittest.mock import patch

import pytest

from cronscope.cli_export import build_export_parser, run_export


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expression": "* * * * *",
        "fmt": "json",
        "count": 5,
        "timezone": "UTC",
        "output": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_export_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    p = build_export_parser(subs)
    assert p is not None


def test_run_export_json_exits_zero(capsys):
    code = run_export(_make_args())
    assert code == 0


def test_run_export_json_stdout_is_valid_json(capsys):
    run_export(_make_args())
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "next_runs" in data


def test_run_export_csv_exits_zero(capsys):
    code = run_export(_make_args(fmt="csv"))
    assert code == 0


def test_run_export_csv_stdout_has_header(capsys):
    run_export(_make_args(fmt="csv"))
    captured = capsys.readouterr()
    assert "scheduled_time" in captured.out


def test_run_export_invalid_expression_returns_1(capsys):
    code = run_export(_make_args(expression="not a cron"))
    assert code == 1


def test_run_export_invalid_expression_prints_error(capsys):
    run_export(_make_args(expression="bad expr"))
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_run_export_writes_to_file(tmp_path, capsys):
    out_file = tmp_path / "schedule.json"
    code = run_export(_make_args(output=str(out_file)))
    assert code == 0
    data = json.loads(out_file.read_text())
    assert "expression" in data


def test_run_export_file_write_error_returns_1(capsys):
    code = run_export(_make_args(output="/nonexistent_dir/out.json"))
    assert code == 1
