"""SYNTHETIC DATA ONLY."""

from decimal import Decimal

from reconcile import reconcile, worst_line


def test_a_matching_statement() -> None:
    result = reconcile(["10.00", "20.00"], "30.00")
    assert result.matched is True
    assert result.variance == Decimal("0.00")


def test_a_short_statement() -> None:
    result = reconcile(["10.00"], "30.00")
    assert result.matched is False
    assert result.variance == Decimal("-20.00")


def test_an_empty_statement() -> None:
    result = reconcile([], "94.99")
    assert result.matched is False
    assert result.variance == Decimal("-94.99")


def test_worst_line_picks_the_largest_absolute_value() -> None:
    """Rule 1. Negatives count by magnitude."""
    assert worst_line(["10.00", "-42.50", "33.00"]) == "-42.50"


def test_worst_line_returns_the_first_on_a_tie() -> None:
    """Rule 2. Both are 42.50 by magnitude. The first one wins."""
    assert worst_line(["42.50", "-42.50"]) == "42.50"


def test_worst_line_on_an_empty_statement() -> None:
    """Rule 3."""
    assert worst_line([]) is None


def test_worst_line_comparison_is_exact() -> None:
    """Rule 4."""
    assert worst_line(["0.070", "0.07"]) == "0.070"


def test_worst_line_returns_the_original_string() -> None:
    """Rule 5. Trailing zeroes survive untouched."""
    assert worst_line(["1.50", "99.900"]) == "99.900"
