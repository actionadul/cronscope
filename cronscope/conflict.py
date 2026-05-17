"""Detect scheduling conflicts: expressions that never fire or fire too frequently."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronscope.parser import parse
from cronscope.summarizer import _estimate_runs_per_day


THRESHOLD_TOO_FREQUENT = 60   # more than 60 runs/day is "frequent"
THRESHOLD_RARE = 1             # fewer than 1 run/day is "rare"


@dataclass
class ConflictReport:
    expression: str
    is_valid: bool
    parse_error: Optional[str]
    runs_per_day: Optional[float]
    is_too_frequent: bool
    is_too_rare: bool
    warnings: List[str] = field(default_factory=list)


def _collect_warnings(runs_per_day: float, expression: str) -> List[str]:
    warnings: List[str] = []
    if runs_per_day > THRESHOLD_TOO_FREQUENT:
        warnings.append(
            f"Expression fires ~{runs_per_day:.0f} times/day — consider a less frequent schedule."
        )
    if runs_per_day < THRESHOLD_RARE:
        warnings.append(
            f"Expression fires less than once per day (~{runs_per_day:.4f}/day)."
        )
    return warnings


def check_expression(expression: str) -> ConflictReport:
    """Analyse a single cron expression for potential scheduling conflicts."""
    try:
        parsed = parse(expression)
    except ValueError as exc:
        return ConflictReport(
            expression=expression,
            is_valid=False,
            parse_error=str(exc),
            runs_per_day=None,
            is_too_frequent=False,
            is_too_rare=False,
            warnings=[str(exc)],
        )

    rpd = _estimate_runs_per_day(parsed)
    warnings = _collect_warnings(rpd, expression)
    return ConflictReport(
        expression=expression,
        is_valid=True,
        parse_error=None,
        runs_per_day=rpd,
        is_too_frequent=rpd > THRESHOLD_TOO_FREQUENT,
        is_too_rare=rpd < THRESHOLD_RARE,
        warnings=warnings,
    )


def check_expressions(expressions: List[str]) -> List[ConflictReport]:
    """Check multiple expressions and return a report for each."""
    return [check_expression(expr) for expr in expressions]


def format_conflict_report(report: ConflictReport) -> str:
    """Return a human-readable summary of a ConflictReport."""
    lines = [f"Expression : {report.expression}"]
    if not report.is_valid:
        lines.append(f"Status     : INVALID — {report.parse_error}")
        return "\n".join(lines)

    lines.append("Status     : valid")
    lines.append(f"Runs/day   : ~{report.runs_per_day:.2f}")
    if report.warnings:
        for w in report.warnings:
            lines.append(f"WARNING    : {w}")
    else:
        lines.append("No conflicts detected.")
    return "\n".join(lines)
