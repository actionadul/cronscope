"""Annotate cron expressions with inline field-level comments."""

from cronscope.parser import parse, ParsedCron

_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]

_MONTH_NAMES = {
    "1": "Jan", "2": "Feb", "3": "Mar", "4": "Apr",
    "5": "May", "6": "Jun", "7": "Jul", "8": "Aug",
    "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

_DOW_NAMES = {
    "0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed",
    "4": "Thu", "5": "Fri", "6": "Sat", "7": "Sun",
}


def _annotate_field(raw: str, field: str) -> str:
    """Return a short human annotation for a single cron field token."""
    if raw == "*":
        return f"every {field.replace('_', ' ')}"

    if raw.startswith("*/"):
        step = raw[2:]
        return f"every {step} {field.replace('_', ' ')}(s)"

    if "-" in raw and "/" in raw:
        range_part, step = raw.split("/", 1)
        lo, hi = range_part.split("-", 1)
        return f"{field} {lo}-{hi} step {step}"

    if "-" in raw:
        lo, hi = raw.split("-", 1)
        if field == "month":
            lo = _MONTH_NAMES.get(lo, lo)
            hi = _MONTH_NAMES.get(hi, hi)
        elif field == "day_of_week":
            lo = _DOW_NAMES.get(lo, lo)
            hi = _DOW_NAMES.get(hi, hi)
        return f"{field} {lo} to {hi}"

    if "," in raw:
        parts = raw.split(",")
        if field == "month":
            parts = [_MONTH_NAMES.get(p, p) for p in parts]
        elif field == "day_of_week":
            parts = [_DOW_NAMES.get(p, p) for p in parts]
        return ", ".join(parts)

    if field == "month":
        return _MONTH_NAMES.get(raw, raw)
    if field == "day_of_week":
        return _DOW_NAMES.get(raw, raw)

    return raw


def annotate(expression: str) -> list[dict]:
    """Return a list of per-field annotation dicts for *expression*.

    Each dict has keys: ``field``, ``raw``, ``annotation``.
    Raises ``ValueError`` if the expression is invalid.
    """
    parsed: ParsedCron = parse(expression)
    fields = [
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    ]
    result = []
    for name, raw in zip(_FIELD_NAMES, fields):
        result.append({
            "field": name,
            "raw": raw,
            "annotation": _annotate_field(raw, name),
        })
    return result


def format_annotation(expression: str) -> str:
    """Return a multi-line string showing each field with its annotation."""
    annotations = annotate(expression)
    lines = [f"Expression: {expression}", ""]
    width = max(len(a["raw"]) for a in annotations)
    for a in annotations:
        lines.append(f"  {a['raw']:<{width}}  # {a['annotation']}")
    return "\n".join(lines)
