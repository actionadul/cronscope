"""Tests for cronscope.alias."""

import pytest

from cronscope.alias import (
    describe_alias,
    format_alias_table,
    is_alias,
    list_aliases,
    resolve,
)


# ---------------------------------------------------------------------------
# is_alias
# ---------------------------------------------------------------------------

def test_is_alias_recognises_at_daily():
    assert is_alias("@daily") is True


def test_is_alias_recognises_at_yearly():
    assert is_alias("@yearly") is True


def test_is_alias_case_insensitive():
    assert is_alias("@Daily") is True
    assert is_alias("@HOURLY") is True


def test_is_alias_rejects_regular_expression():
    assert is_alias("0 0 * * *") is False


def test_is_alias_rejects_unknown_alias():
    assert is_alias("@reboot") is False


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------

def test_resolve_at_daily():
    assert resolve("@daily") == "0 0 * * *"


def test_resolve_at_midnight_same_as_daily():
    assert resolve("@midnight") == "0 0 * * *"


def test_resolve_at_yearly():
    assert resolve("@yearly") == "0 0 1 1 *"


def test_resolve_at_annually_same_as_yearly():
    assert resolve("@annually") == "0 0 1 1 *"


def test_resolve_at_hourly():
    assert resolve("@hourly") == "0 * * * *"


def test_resolve_at_weekly():
    assert resolve("@weekly") == "0 0 * * 0"


def test_resolve_at_monthly():
    assert resolve("@monthly") == "0 0 1 * *"


def test_resolve_passthrough_regular_expression():
    expr = "30 6 * * 1-5"
    assert resolve(expr) == expr


def test_resolve_strips_surrounding_whitespace():
    assert resolve("  @daily  ") == "0 0 * * *"


# ---------------------------------------------------------------------------
# list_aliases
# ---------------------------------------------------------------------------

def test_list_aliases_returns_dict():
    result = list_aliases()
    assert isinstance(result, dict)


def test_list_aliases_contains_core_entries():
    result = list_aliases()
    assert "@daily" in result
    assert "@hourly" in result
    assert "@weekly" in result


def test_list_aliases_is_copy():
    a = list_aliases()
    a["@fake"] = "1 2 3 4 5"
    assert "@fake" not in list_aliases()


# ---------------------------------------------------------------------------
# describe_alias
# ---------------------------------------------------------------------------

def test_describe_alias_known():
    assert describe_alias("@hourly") == "0 * * * *"


def test_describe_alias_unknown_returns_none():
    assert describe_alias("0 * * * *") is None


# ---------------------------------------------------------------------------
# format_alias_table
# ---------------------------------------------------------------------------

def test_format_alias_table_returns_string():
    assert isinstance(format_alias_table(), str)


def test_format_alias_table_contains_all_aliases():
    table = format_alias_table()
    for alias in list_aliases():
        assert alias in table
