"""Cron expression parser and validator for cronscope."""

import re
from dataclasses import dataclass
from typing import Optional

CRON_FIELDS = ["minute", "hour", "day", "month", "weekday"]

FIELD_RANGES = {
    "minute":  (0, 59),
    "hour":    (0, 23),
    "day":     (1, 31),
    "month":   (1, 12),
    "weekday": (0, 7),  # 7 is Sunday alias
}


@dataclass
class ParsedCron:
    minute: str
    hour: str
    day: str
    month: str
    weekday: str
    raw: str

    def as_dict(self) -> dict:
        return {
            "minute": self.minute,
            "hour": self.hour,
            "day": self.day,
            "month": self.month,
            "weekday": self.weekday,
        }


def _validate_field(value: str, field: str) -> Optional[str]:
    """Return an error message if the field value is invalid, else None."""
    lo, hi = FIELD_RANGES[field]

    if value == "*":
        return None

    # Step syntax: */n or value/n
    step_match = re.fullmatch(r"(\*|\d+)/(\d+)", value)
    if step_match:
        step = int(step_match.group(2))
        if step == 0:
            return f"Step value cannot be zero in field '{field}'"
        return None

    # Range: a-b
    range_match = re.fullmatch(r"(\d+)-(\d+)", value)
    if range_match:
        a, b = int(range_match.group(1)), int(range_match.group(2))
        if not (lo <= a <= hi and lo <= b <= hi and a <= b):
            return f"Range {a}-{b} out of bounds [{lo},{hi}] for field '{field}'"
        return None

    # List: a,b,c
    if "," in value:
        for part in value.split(","):
            err = _validate_field(part.strip(), field)
            if err:
                return err
        return None

    # Plain integer
    if re.fullmatch(r"\d+", value):
        n = int(value)
        if not (lo <= n <= hi):
            return f"Value {n} out of bounds [{lo},{hi}] for field '{field}'"
        return None

    return f"Unrecognised token '{value}' in field '{field}'"


def parse(expression: str) -> ParsedCron:
    """Parse a cron expression string into a ParsedCron.

    Raises ValueError on invalid expressions.
    """
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Expected 5 fields, got {len(parts)}: '{expression}'"
        )

    errors = []
    for field, value in zip(CRON_FIELDS, parts):
        err = _validate_field(value, field)
        if err:
            errors.append(err)

    if errors:
        raise ValueError("Invalid cron expression — " + "; ".join(errors))

    return ParsedCron(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        weekday=parts[4],
        raw=expression,
    )
