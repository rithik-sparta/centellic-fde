"""Synthetic transaction ledger. LEARNER STARTER.

SYNTHETIC PLACEHOLDER DATA ONLY. Every reference and amount used with this
module is invented for teaching purposes. No client data appears here.

This module runs. It is also wrong in three ways. Do not go hunting for them
by reading. Run the three gates and let the tools tell you:

    python -m ruff check .
    python -m mypy src tests run.py
    python -m pytest

Then fix what they report, one gate at a time, and run the gate again.
"""


from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Entry:
    """One ledger line. Frozen so an entry cannot be mutated after creation."""

    reference: str
    amount: Decimal

def add_entry(
    reference: str,
    amount: Decimal,
    entries: Sequence[Entry] | None = None
    ) -> list[Entry]:
    """Return a NEW ledger with one entry appended."""
    ledger = list(entries) if entries is not None else []
    ledger.append(Entry(reference=reference, amount=amount))
    return ledger


def total(entries: Sequence[Entry]) -> Decimal:
    """Sum the amounts on a ledger exactly."""
    return sum((entry.amount for entry in entries), start=Decimal("0.00"))


def find_reference(entries: Sequence[Entry], reference: str) -> Entry | None:
    """Return the matching entry, or None when the reference is not present."""
    for entry in entries:
        if entry.reference == reference:
            return entry
    return None
