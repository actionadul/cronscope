"""Detect overlapping or conflicting cron expressions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

from cronscope.parser import parse
from cronscope.scheduler import next_runs


@dataclass
class OverlapResult:
    expr_a: str
    expr_b: str
    shared_times: List[datetime]
    overlap_count: int

    @property
    def has_overlap(self) -> bool:
        return self.overlap_count > 0


def find_overlaps(
    expr_a: str,
    expr_b: str,
    start: datetime | None = None,
    count: int = 100,
) -> OverlapResult:
    """Return times when both expressions fire within the same minute."""
    if start is None:
        start = datetime.utcnow().replace(second=0, microsecond=0)

    parsed_a = parse(expr_a)
    parsed_b = parse(expr_b)

    runs_a = set(next_runs(parsed_a, start=start, count=count))
    runs_b = set(next_runs(parsed_b, start=start, count=count))

    shared = sorted(runs_a & runs_b)
    return OverlapResult(
        expr_a=expr_a,
        expr_b=expr_b,
        shared_times=shared,
        overlap_count=len(shared),
    )


def compare_expressions(
    expressions: List[str],
    start: datetime | None = None,
    count: int = 100,
) -> List[OverlapResult]:
    """Compare all pairs of expressions and return overlap results."""
    results: List[OverlapResult] = []
    for i in range(len(expressions)):
        for j in range(i + 1, len(expressions)):
            result = find_overlaps(expressions[i], expressions[j], start=start, count=count)
            results.append(result)
    return results


def format_overlap_report(result: OverlapResult) -> str:
    """Render a human-readable overlap report for a pair of expressions."""
    lines = [
        f"Expressions : {result.expr_a!r}  vs  {result.expr_b!r}",
        f"Overlaps    : {result.overlap_count}",
    ]
    if result.shared_times:
        lines.append("Shared runs :")
        for dt in result.shared_times[:10]:
            lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M UTC')}")
        if result.overlap_count > 10:
            lines.append(f"  ... and {result.overlap_count - 10} more")
    else:
        lines.append("No shared run times found in the sampled window.")
    return "\n".join(lines)
