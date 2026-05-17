"""Rank and score cron expressions by various criteria."""

from dataclasses import dataclass, field
from typing import List

from cronscope.parser import parse, ParsedCron
from cronscope.summarizer import _estimate_runs_per_day, summarize_parsed


@dataclass
class RankResult:
    expression: str
    runs_per_day: float
    specificity_score: int
    human_readable: str
    rank: int = 0


def _specificity_score(parsed: ParsedCron) -> int:
    """Higher score means more specific (fewer wildcards)."""
    score = 0
    fields = [parsed.minute, parsed.hour, parsed.day, parsed.month, parsed.weekday]
    for f in fields:
        if f == "*":
            score += 0
        elif "/" in f:
            score += 1
        elif "-" in f:
            score += 2
        elif "," in f:
            score += 3
        else:
            score += 4
    return score


def rank_expressions(
    expressions: List[str],
    sort_by: str = "runs_per_day",
    ascending: bool = True,
) -> List[RankResult]:
    """Rank a list of cron expressions.

    Args:
        expressions: List of cron expression strings.
        sort_by: One of 'runs_per_day' or 'specificity'.
        ascending: Sort order.

    Returns:
        List of RankResult ordered by the chosen criterion.
    """
    results = []
    for expr in expressions:
        try:
            parsed = parse(expr)
        except ValueError:
            continue
        summary = summarize_parsed(parsed)
        rpd = _estimate_runs_per_day(parsed)
        spec = _specificity_score(parsed)
        results.append(
            RankResult(
                expression=expr,
                runs_per_day=rpd,
                specificity_score=spec,
                human_readable=summary["human_readable"],
            )
        )

    key_fn = (
        (lambda r: r.runs_per_day)
        if sort_by == "runs_per_day"
        else (lambda r: r.specificity_score)
    )
    results.sort(key=key_fn, reverse=not ascending)

    for i, result in enumerate(results, start=1):
        result.rank = i

    return results


def format_rank_report(results: List[RankResult]) -> str:
    """Format ranked results as a human-readable table."""
    if not results:
        return "No valid expressions to rank."

    lines = [
        f"{'Rank':<6} {'Expression':<25} {'Runs/Day':<12} {'Specificity':<13} Description",
        "-" * 80,
    ]
    for r in results:
        lines.append(
            f"{r.rank:<6} {r.expression:<25} {r.runs_per_day:<12.1f} {r.specificity_score:<13} {r.human_readable}"
        )
    return "\n".join(lines)
