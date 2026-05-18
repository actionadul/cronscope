"""Normalize cron expressions by expanding aliases, stripping redundant syntax,
and returning a canonical five-field string."""

from __future__ import annotations

from typing import NamedTuple

from cronscope.alias import is_alias, resolve
from cronscope.parser import parse, ParsedCron


class NormalizeResult(NamedTuple):
    original: str
    normalized: str
    was_alias: bool
    changed: bool


def _normalize_field(raw: str) -> str:
    """Return a canonical representation of a single cron field token."""
    # step-of-1 is redundant: */1 -> *
    if raw == "*/1":
        return "*"
    # leading zeros in numbers: 05 -> 5
    if raw.isdigit():
        return str(int(raw))
    # handle lists
    if "," in raw:
        parts = [_normalize_field(p) for p in raw.split(",")]
        # deduplicate while preserving order
        seen: set[str] = set()
        deduped = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        return ",".join(deduped)
    # handle ranges
    if "-" in raw and "/" not in raw:
        lo, hi = raw.split("-", 1)
        lo_n = _normalize_field(lo)
        hi_n = _normalize_field(hi)
        # range of same value collapses to that value
        if lo_n == hi_n:
            return lo_n
        return f"{lo_n}-{hi_n}"
    # handle step over range
    if "/" in raw:
        base, step = raw.split("/", 1)
        step_n = _normalize_field(step)
        base_n = _normalize_field(base)
        if step_n == "1":
            return base_n
        return f"{base_n}/{step_n}"
    return raw


def normalize(expression: str) -> NormalizeResult:
    """Normalize *expression* and return a :class:`NormalizeResult`.

    Raises ``ValueError`` if the expression (after alias expansion) is invalid.
    """
    original = expression.strip()
    was_alias = is_alias(original)
    expanded = resolve(original) if was_alias else original

    # validate by parsing (raises ValueError on bad input)
    parsed: ParsedCron = parse(expanded)

    fields = [expanded.split()[i] for i in range(5)]
    normalized_fields = [_normalize_field(f) for f in fields]
    normalized = " ".join(normalized_fields)

    return NormalizeResult(
        original=original,
        normalized=normalized,
        was_alias=was_alias,
        changed=(normalized != expanded),
    )


def normalize_many(expressions: list[str]) -> list[NormalizeResult]:
    """Normalize a list of expressions, skipping invalid ones."""
    results = []
    for expr in expressions:
        try:
            results.append(normalize(expr))
        except ValueError:
            pass
    return results
