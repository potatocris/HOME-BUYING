"""Single source of truth for UX-DR10 number formatting (Story 3.7).

Pure Python (no Streamlit) so it is unit-testable in isolation, matching the
calculations.py convention. Every displayed number in app.py and
pages/scenarios.py must route through these helpers so the formatting rules
live in exactly one place.
"""


def fmt_dollar(v: float) -> str:
    """Nearest dollar, $ prefix, comma separator; negatives in parentheses.

    fmt_dollar(12400) -> '$12,400'   fmt_dollar(-4200) -> '($4,200)'
    (UX-DR10: negatives use parentheses, never a minus sign.)
    """
    if v < 0:
        return f"(${abs(v):,.0f})"
    return f"${v:,.0f}"


def fmt_pct(v: float) -> str:
    """Two decimal places + % suffix.  fmt_pct(6.5) -> '6.50%'."""
    return f"{v:.2f}%"


def fmt_pct_compact(v: float) -> str:
    """Percent with up to 1 decimal, trailing '.0' trimmed.

    fmt_pct_compact(20.0) -> '20%'   fmt_pct_compact(12.5) -> '12.5%'

    Used for the down-payment note, where the slider step is 0.5 so 12.5% is
    reachable and must not silently round to a misleading whole number.
    """
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return f"{s}%"


def fmt_month(n: int) -> str:
    """Whole-number 'month N'.  fmt_month(31) -> 'month 31'."""
    return f"month {int(round(n))}"
