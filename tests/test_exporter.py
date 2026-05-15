"""Tests for cronscope.exporter."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

import pytest

from cronscope.exporter import export, export_csv, export_json

START = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
EXPR_EVERY_MIN = "* * * * *"
EXPR_HOURLY = "0 * * * *"


def test_export_json_returns_valid_json():
    result = export_json(EXPR_EVERY_MIN, count=5, timezone="UTC", start=START)
    data = json.loads(result)
    assert isinstance(data, dict)


def test_export_json_contains_expected_keys():
    data = json.loads(export_json(EXPR_EVERY_MIN, count=3, timezone="UTC", start=START))
    for key in ("expression", "timezone", "human_readable", "estimated_runs_per_day", "next_runs"):
        assert key in data


def test_export_json_next_runs_count():
    data = json.loads(export_json(EXPR_EVERY_MIN, count=7, timezone="UTC", start=START))
    assert len(data["next_runs"]) == 7


def test_export_json_expression_preserved():
    data = json.loads(export_json(EXPR_HOURLY, count=2, timezone="UTC", start=START))
    assert data["expression"] == EXPR_HOURLY


def test_export_json_timezone_preserved():
    data = json.loads(export_json(EXPR_EVERY_MIN, count=2, timezone="UTC", start=START))
    assert data["timezone"] == "UTC"


def test_export_csv_returns_string():
    result = export_csv(EXPR_EVERY_MIN, count=3, timezone="UTC", start=START)
    assert isinstance(result, str)


def test_export_csv_header_row():
    result = export_csv(EXPR_EVERY_MIN, count=3, timezone="UTC", start=START)
    reader = csv.reader(io.StringIO(result))
    header = next(reader)
    assert header == ["index", "scheduled_time", "timezone"]


def test_export_csv_row_count():
    result = export_csv(EXPR_EVERY_MIN, count=4, timezone="UTC", start=START)
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    # header + 4 data rows
    assert len(rows) == 5


def test_export_csv_index_column():
    result = export_csv(EXPR_EVERY_MIN, count=3, timezone="UTC", start=START)
    reader = csv.reader(io.StringIO(result))
    next(reader)  # skip header
    indices = [int(row[0]) for row in reader]
    assert indices == [1, 2, 3]


def test_export_dispatch_json():
    result = export(EXPR_EVERY_MIN, fmt="json", count=2, timezone="UTC", start=START)
    data = json.loads(result)
    assert "next_runs" in data


def test_export_dispatch_csv():
    result = export(EXPR_EVERY_MIN, fmt="csv", count=2, timezone="UTC", start=START)
    assert "scheduled_time" in result


def test_export_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported export format"):
        export(EXPR_EVERY_MIN, fmt="xml", count=2, timezone="UTC", start=START)
