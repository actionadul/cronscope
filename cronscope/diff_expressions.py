"""Compare two cron expressions and report differences in their schedules."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronscope.parser import parse
from cronscope.scheduler import next_runs
from cronscope.humanizer import humanize
from cronscope.summarizer import summarize


@dataclass
class ExpressionDiff:
    expr_a: str
    expr_b: str
    only_in_a: List[datetime] = field(default_factory=list)
    only_in_b: List[datetime] = field(default_factory=list)
    shared: List[datetime] = field(default_factory=list)
    human_a: str = ""
    human_b: str = ""

    @property
    def total_a(self) -> int:
        return len(self.only_in_a) + len(self.shared)

    @property
    def total_b(self) -> int:
        return len(self.only_in_b) + len(self.shared)

    @property
    def similarity_pct(self) -> float:
        total = self.total_a + self.total_b - len(self.shared)
        if total == 0:
            return 100.0
        return round(len(self.shared) / total * 100, 1)


def diff_expressions(
    expr_a: str,
    expr_b: str,
    count: int = 60,
    start: datetime | None = None,
) -> ExpressionDiff:
    """Compute the schedule diff between two cron expressions."""
    parsed_a = parse(expr_a)
    parsed_b = parse(expr_b)

    kwargs = {"count": count}
    if start is not None:
        kwargs["start"] = start

    runs_a = set(next_runs(parsed_a, **kwargs))
    runs_b = set(next_runs(parsed_b, **kwargs))

    shared = sorted(runs_a & runs_b)
    only_a = sorted(runs_a - runs_b)
    only_b = sorted(runs_b - runs_a)

    return ExpressionDiff(
        expr_a=expr_a,
        expr_b=expr_b,
        only_in_a=only_a,
        only_in_b=only_b,
        shared=shared,
        human_a=humanize(parsed_a),
        human_b=humanize(parsed_b),
    )


def format_diff_report(diff: ExpressionDiff, max_rows: int = 5) -> str:
    """Return a human-readable diff report."""
    lines = [
        f"Expression A : {diff.expr_a}",
        f"  Meaning    : {diff.human_a}",
        f"Expression B : {diff.expr_b}",
        f"  Meaning    : {diff.human_b}",
        "",
        f"Shared runs  : {len(diff.shared)}",
        f"Only in A    : {len(diff.only_in_a)}",
        f"Only in B    : {len(diff.only_in_b)}",
        f"Similarity   : {diff.similarity_pct}%",
    ]

    def _fmt_rows(label: str, runs: List[datetime]) -> List[str]:
        if not runs:
            return []
        out = [f"\n{label}:"]
        for dt in runs[:max_rows]:
            out.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}")
        if len(runs) > max_rows:
            out.append(f"  ... and {len(runs) - max_rows} more")
        return out

    lines += _fmt_rows("Only in A", diff.only_in_a)
    lines += _fmt_rows("Only in B", diff.only_in_b)
    lines += _fmt_rows("Shared", diff.shared)

    return "\n".join(lines)
