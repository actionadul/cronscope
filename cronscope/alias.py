"""Resolve common cron aliases (@yearly, @monthly, etc.) to standard expressions."""

from __future__ import annotations

from typing import Dict, Optional

# Standard cron aliases mapping to 5-field expressions
_ALIASES: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
}


def is_alias(expression: str) -> bool:
    """Return True if *expression* is a recognised cron alias."""
    return expression.strip().lower() in _ALIASES


def resolve(expression: str) -> str:
    """Resolve a cron alias to its canonical 5-field expression.

    If *expression* is not an alias it is returned unchanged, allowing callers
    to pass any expression without checking first.

    Parameters
    ----------
    expression:
        A cron alias (e.g. ``@daily``) or a regular cron expression.

    Returns
    -------
    str
        The resolved 5-field cron expression.
    """
    return _ALIASES.get(expression.strip().lower(), expression)


def list_aliases() -> Dict[str, str]:
    """Return a copy of the full alias-to-expression mapping."""
    return dict(_ALIASES)


def describe_alias(expression: str) -> Optional[str]:
    """Return the canonical expression for *expression* if it is an alias,
    otherwise return ``None``.
    """
    return _ALIASES.get(expression.strip().lower())


def format_alias_table() -> str:
    """Return a human-readable table of all supported aliases."""
    lines = ["Supported aliases:", ""]
    width = max(len(k) for k in _ALIASES)
    for alias, expr in sorted(_ALIASES.items()):
        lines.append(f"  {alias:<{width}}  ->  {expr}")
    return "\n".join(lines)
