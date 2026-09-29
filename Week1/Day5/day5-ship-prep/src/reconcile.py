"""Reconcile a synthetic statement. SYNTHETIC DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

PENNY = Decimal("0.01")


@dataclass(frozen=True)
class Reconciliation:
    variance: Decimal
    matched: bool


def reconcile(lines: Sequence[str], expected_total: str) -> Reconciliation:
    """Return the exact variance between the statement lines and the expected total."""
    total = sum((Decimal(line) for line in lines), start=Decimal("0.00"))
    variance = (total - Decimal(expected_total)).quantize(PENNY)
    return Reconciliation(variance=variance, matched=variance == Decimal("0.00"))


def worst_line(lines: Sequence[str]) -> str | None:
    """Return the line with the largest absolute value, or None on an empty statement.

    `max` returns the FIRST maximal element, which satisfies the tie rule for free.
    The key is a Decimal, so comparison is exact. And because `max` selects from
    `lines` rather than from converted values, the original string is returned
    unchanged.
    """
    if not lines:
        return None
    return max(lines, key=lambda line: abs(Decimal(line)))
