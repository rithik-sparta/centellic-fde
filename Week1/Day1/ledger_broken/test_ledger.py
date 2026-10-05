"""Tests written against the ledger's stated behaviour. Synthetic data only."""

from decimal import Decimal

from Day1.starter.src.ledger import Entry, add_entry, total


def test_total_sums_amounts() -> None:
    book = [
        Entry("SYN-001", Decimal("10.10")),
        Entry("SYN-002", Decimal("20.20")),
        Entry("SYN-003", Decimal("5.05")),
    ]
    assert total(book) == Decimal("35.35")


def test_add_entry_starts_from_an_empty_ledger() -> None:
    first = add_entry("SYN-001", Decimal("10.10"))
    second = add_entry("SYN-002", Decimal("20.20"))
    assert len(first) == 1
    assert len(second) == 1
