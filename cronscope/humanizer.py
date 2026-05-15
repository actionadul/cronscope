"""Human-readable descriptions for cron expressions."""

from cronscope.parser import ParsedCron, parse

_WEEKDAYS = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]

_MONTHS = [
    "", "January", "February", "March", "April",
    "May", "June", "July", "August", "September",
    "October", "November", "December"
]


def _describe_field(value: str, kind: str) -> str:
    """Return a human-readable phrase for a single cron field."""
    if value == "*":
        return None

    if "/" in value:
        base, step = value.split("/", 1)
        unit = {
            "minute": "minute", "hour": "hour",
            "dom": "day", "month": "month", "dow": "weekday"
        }[kind]
        return f"every {step} {unit}(s)"

    if "-" in value:
        start, end = value.split("-", 1)
        if kind == "dow":
            return f"{_WEEKDAYS[int(start)]} through {_WEEKDAYS[int(end)]}"
        if kind == "month":
            return f"{_MONTHS[int(start)]} through {_MONTHS[int(end)]}"
        return f"{start} through {end}"

    if "," in value:
        parts = value.split(",")
        if kind == "dow":
            names = [_WEEKDAYS[int(p)] for p in parts]
        elif kind == "month":
            names = [_MONTHS[int(p)] for p in parts]
        else:
            names = parts
        return ", ".join(names)

    if kind == "dow":
        return _WEEKDAYS[int(value)]
    if kind == "month":
        return _MONTHS[int(value)]
    return value


def humanize(expr: str) -> str:
    """Return a human-readable description of a cron expression string."""
    parsed: ParsedCron = parse(expr)

    minute = _describe_field(parsed.minute, "minute")
    hour = _describe_field(parsed.hour, "hour")
    dom = _describe_field(parsed.dom, "dom")
    month = _describe_field(parsed.month, "month")
    dow = _describe_field(parsed.dow, "dow")

    if all(f is None for f in [minute, hour, dom, month, dow]):
        return "Every minute"

    parts = []

    if minute is None and hour is None:
        parts.append("every minute")
    elif minute is None:
        parts.append(f"every minute of hour {parsed.hour}")
    elif hour is None:
        parts.append(f"at minute {parsed.minute} of every hour")
    else:
        parts.append(f"at {parsed.hour.zfill(2) if parsed.hour.isdigit() else parsed.hour}:{parsed.minute.zfill(2) if parsed.minute.isdigit() else parsed.minute}")

    if month:
        parts.append(f"in {month}")
    if dom and dow:
        parts.append(f"on day {dom} of the month or on {dow}")
    elif dom:
        parts.append(f"on day {dom} of the month")
    elif dow:
        parts.append(f"on {dow}")

    return " ".join(parts).capitalize()


def humanize_parsed(parsed: ParsedCron) -> str:
    """Return a human-readable description from an already-parsed cron."""
    return humanize(f"{parsed.minute} {parsed.hour} {parsed.dom} {parsed.month} {parsed.dow}")
