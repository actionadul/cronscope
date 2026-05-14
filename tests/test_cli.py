"""Tests for the cronscope CLI."""

import pytest
from unittest.mock import patch

from cronscope.cli import run


def test_valid_expression_default_count(capsys):
    exit_code = run(["* * * * *"])
    assert exit_code == 0
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l.strip()]
    assert len(lines) == 5


def test_custom_count(capsys):
    exit_code = run(["0 * * * *", "-n", "3"])
    assert exit_code == 0
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l.strip()]
    assert len(lines) == 3


def test_invalid_expression_returns_error(capsys):
    exit_code = run(["99 * * * *"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Invalid cron expression" in captured.err


def test_invalid_timezone_returns_error(capsys):
    exit_code = run(["* * * * *", "--timezone", "Not/AReal_Zone"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Invalid timezone" in captured.err


def test_validate_flag_no_runs(capsys):
    exit_code = run(["30 8 * * 1", "--validate"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Valid cron expression" in captured.out
    assert "minute" in captured.out
    assert "weekday" in captured.out


def test_tabulate_flag(capsys):
    exit_code = run(["0 0 * * *", "--tabulate", "-n", "2"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_timezone_flag(capsys):
    exit_code = run(["* * * * *", "--timezone", "Europe/London", "-n", "2"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_no_args_prints_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run([])
    assert exc_info.value.code != 0
