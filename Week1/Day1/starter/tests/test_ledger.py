"""Tests for the ledger. LEARNER STARTER. Synthetic data only.

CA-3: three of these are written for you as a shape to copy. The rest raise
NotImplementedError. Replace each one with a real assertion.
"""

from decimal import Decimal

import pytest

from Day1.starter.src.ledger import Entry, add_entry, find_reference, total


@pytest.fixture
def sample_ledger():
    """Three synthetic entries whose amounts are chosen to break float maths.

    A fixture exists so the same data is not copy-pasted into six tests. When
    the shape of an entry changes, it changes here once.
    """
    return [
        Entry("SYN-001", Decimal("10.10")),
        Entry("SYN-002", Decimal("20.20")),
        Entry("SYN-003", Decimal("5.05")),
    ]


def test_total_is_exact(sample_ledger):
    """Written for you. Run it and read the number in the failure carefully."""
    assert total(sample_ledger) == Decimal("35.35")


def test_total_of_an_empty_ledger_is_zero():
    """TODO (CA-3): assert the total of an empty ledger."""
    assert total([]) == Decimal("0.00")


def test_add_entry_does_not_leak_between_calls():
    """TODO (CA-3): call add_entry twice with no ledger argument, and assert
    that each call returns a ledger of length 1."""
    call1 = add_entry("SYN-001", Decimal("3.0"))
    call2 = add_entry("SYN-002", Decimal("2.0"))
    assert len(call1) == 1
    assert len(call2) == 1


def test_add_entry_returns_a_new_list(sample_ledger):
    """TODO (CA-3): add an entry to sample_ledger and assert the original is
    still length 3 while the returned ledger is length 4."""
    call1 = add_entry("SYN-001",Decimal("3.0"),sample_ledger)
    assert(len(call1) == 4)
    assert(len(sample_ledger) == 3)


def test_find_reference_hit(sample_ledger):
    """TODO (CA-3): assert a present reference is found."""
    res = find_reference(sample_ledger, "SYN-001")
    assert res is not None
    assert res.amount == Decimal("10.10")
    assert res == Entry("SYN-001", Decimal("10.10"))


def test_find_reference_miss_returns_none(sample_ledger):
    """TODO (CA-3): assert an absent reference returns None."""
    res = find_reference(sample_ledger, "SYN-100")
    assert res is None
