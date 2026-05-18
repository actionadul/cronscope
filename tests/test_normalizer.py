"""Tests for cronscope.normalizer."""

import pytest

from cronscope.normalizer import normalize, normalize_many, NormalizeResult


def test_normalize_returns_normalize_result():
    result = normalize("* * * * *")
    assert isinstance(result, NormalizeResult)


def test_normalize_identity_for_clean_expression():
    result = normalize("0 12 * * 1")
    assert result.normalized == "0 12 * * 1"
    assert not result.changed


def test_normalize_step_one_collapsed():
    result = normalize("*/1 * * * *")
    assert result.normalized == "* * * * *"
    assert result.changed


def test_normalize_leading_zero_stripped():
    result = normalize("05 08 * * *")
    assert result.normalized == "5 8 * * *"
    assert result.changed


def test_normalize_range_same_values_collapses():
    result = normalize("5-5 * * * *")
    assert result.normalized == "5 * * * *"
    assert result.changed


def test_normalize_step_over_range_with_step_one():
    result = normalize("0-59/1 * * * *")
    assert result.normalized == "0-59 * * * *"
    assert result.changed


def test_normalize_deduplicates_list():
    result = normalize("1,2,1,3 * * * *")
    assert result.normalized == "1,2,3 * * * *"
    assert result.changed


def test_normalize_alias_expanded():
    result = normalize("@daily")
    assert result.was_alias is True
    assert result.normalized == "0 0 * * *"


def test_normalize_alias_original_preserved():
    result = normalize("@hourly")
    assert result.original == "@hourly"


def test_normalize_not_alias_flag():
    result = normalize("0 * * * *")
    assert result.was_alias is False


def test_normalize_invalid_expression_raises():
    with pytest.raises(ValueError):
        normalize("99 * * * *")


def test_normalize_many_skips_invalid():
    results = normalize_many(["* * * * *", "99 * * * *", "0 12 * * 1"])
    assert len(results) == 2


def test_normalize_many_returns_results_in_order():
    results = normalize_many(["@daily", "0 0 * * *"])
    assert results[0].original == "@daily"
    assert results[1].original == "0 0 * * *"


def test_normalize_complex_expression_unchanged_when_already_canonical():
    expr = "0,30 9-17 * * 1-5"
    result = normalize(expr)
    assert result.normalized == expr
    assert not result.changed
