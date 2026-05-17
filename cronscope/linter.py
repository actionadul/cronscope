"""Lint cron expressions for common mistakes and style issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronscope.parser import parse, ParsedCron
from cronscope.alias import is_alias, resolve


@dataclass
class LintResult:
    expression: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    @property
    def clean(self) -> bool:
        return self.ok and len(self.warnings) == 0


def _check_redundant_wildcard(parsed: ParsedCron, warnings: List[str]) -> None:
    """Warn when both day-of-month and day-of-week are wildcards (ambiguous intent)."""
    if parsed.day == "*" and parsed.weekday == "*":
        warnings.append(
            "Both day-of-month and day-of-week are '*'; consider being explicit."
        )


def _check_step_one(parsed: ParsedCron, warnings: List[str]) -> None:
    """Warn about */1 which is equivalent to *."""
    for fname, fval in [
        ("minute", parsed.minute),
        ("hour", parsed.hour),
        ("day", parsed.day),
        ("month", parsed.month),
        ("weekday", parsed.weekday),
    ]:
        if fval in ("*/1", "0-59/1", "0-23/1", "1-12/1", "0-6/1", "1-31/1"):
            warnings.append(
                f"Field '{fname}' uses a step of 1 ('{fval}'), which is equivalent to '*'."
            )


def _check_alias_suggestion(expression: str, warnings: List[str]) -> None:
    """Suggest an alias when the expression matches a well-known one."""
    alias_map = {
        "0 0 * * *": "@daily",
        "0 0 * * 0": "@weekly",
        "0 0 1 * *": "@monthly",
        "0 0 1 1 *": "@yearly",
        "* * * * *": "@every_minute",
        "0 * * * *": "@hourly",
    }
    if expression.strip() in alias_map:
        alias = alias_map[expression.strip()]
        warnings.append(
            f"Expression matches '{alias}'; consider using the alias for clarity."
        )


def lint(expression: str) -> LintResult:
    """Lint a single cron expression and return a LintResult."""
    result = LintResult(expression=expression)

    actual_expr = expression
    if is_alias(expression):
        actual_expr = resolve(expression)

    try:
        parsed = parse(actual_expr)
    except ValueError as exc:
        result.errors.append(str(exc))
        return result

    _check_redundant_wildcard(parsed, result.warnings)
    _check_step_one(parsed, result.warnings)
    _check_alias_suggestion(actual_expr, result.warnings)

    return result


def format_lint_report(result: LintResult) -> str:
    """Return a human-readable lint report."""
    lines = [f"Expression : {result.expression}"]
    if result.clean:
        lines.append("Status     : OK (no issues found)")
        return "\n".join(lines)
    if result.errors:
        lines.append("Status     : INVALID")
        for err in result.errors:
            lines.append(f"  ERROR   : {err}")
    else:
        lines.append("Status     : OK (with warnings)")
    for warn in result.warnings:
        lines.append(f"  WARNING : {warn}")
    return "\n".join(lines)
