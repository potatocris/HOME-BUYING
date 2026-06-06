"""Tests for the shared number-formatting utility (Story 3.7, UX-DR10).

formatting.py is pure Python (no Streamlit), so it is imported and asserted
directly, mirroring tests/test_calculations.py.
"""

import formatting


class TestFmtDollar:
    def test_positive_with_comma(self):
        assert formatting.fmt_dollar(12400) == "$12,400"

    def test_large_value(self):
        assert formatting.fmt_dollar(1_234_567) == "$1,234,567"

    def test_zero(self):
        assert formatting.fmt_dollar(0) == "$0"

    def test_negative_uses_parentheses_not_minus(self):
        # UX-DR10: negatives are ($X), never $-X
        assert formatting.fmt_dollar(-4200) == "($4,200)"

    def test_negative_large(self):
        assert formatting.fmt_dollar(-12_345) == "($12,345)"

    def test_sub_dollar_rounds_to_nearest_dollar(self):
        # Python ',.0f' uses round-half-to-even (banker's rounding)
        assert formatting.fmt_dollar(0.49) == "$0"
        assert formatting.fmt_dollar(0.5) == "$0"
        assert formatting.fmt_dollar(1.5) == "$2"

    def test_tiny_negative_rounds_into_parentheses_zero(self):
        # Documented edge: a value just below zero renders ($0). Preserves the
        # exact behavior of the original app.py _fmt_dollar this consolidates.
        assert formatting.fmt_dollar(-0.4) == "($0)"


class TestFmtPct:
    def test_two_decimals(self):
        assert formatting.fmt_pct(6.5) == "6.50%"

    def test_zero(self):
        assert formatting.fmt_pct(0) == "0.00%"

    def test_rounds_to_two_decimals(self):
        assert formatting.fmt_pct(12.345) == "12.35%"


class TestFmtPctCompact:
    def test_trims_trailing_zero(self):
        assert formatting.fmt_pct_compact(20.0) == "20%"

    def test_keeps_one_decimal_when_needed(self):
        # The down-payment slider step is 0.5, so 12.5% must not round to 13%.
        assert formatting.fmt_pct_compact(12.5) == "12.5%"

    def test_zero(self):
        assert formatting.fmt_pct_compact(0.0) == "0%"


class TestFmtMonth:
    def test_basic(self):
        assert formatting.fmt_month(31) == "month 31"

    def test_one(self):
        assert formatting.fmt_month(1) == "month 1"
