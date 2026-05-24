# Story 1.5: Investment Portfolio & Special Assessment Engine

Status: done

## Story

As a developer,
I want `calculations.py` to model the renter's investment portfolio with monthly compounding and apply special assessments at the correct month,
So that the opportunity cost comparison is financially accurate.

## Acceptance Criteria

1. **Given** initial capital, monthly contribution, annual return rate, and months, **When** `calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months)` is called, **Then** it returns a list of exactly `months` float values, one per month.
2. **Given** any call, **When** month 1 is computed, **Then** its value equals `(initial_capital + monthly_contribution) * (1 + annual_rate / 100 / 12)` (NFR8 — monthly compounding).
3. **Given** any call, **When** month N (N > 1) is computed, **Then** its value equals `(month_N-1_value + monthly_contribution) * (1 + annual_rate / 100 / 12)`.
4. **Given** `annual_rate = 0`, **When** `calculate_investment_portfolio(0, 1000, 0, 60)` is called, **Then** month 1 = $1,000.00 and month 60 = $60,000.00 (flat accumulation, no growth).
5. **Given** `special_assessment_amount > 0` and `special_assessment_month` is between 1 and 60, **When** `get_special_assessment_for_month(amount, assessment_month, current_month)` is called, **Then** it returns `amount` if `current_month == assessment_month`, else `0.0` (FR18).
6. **Given** `amount = 0`, **When** `get_special_assessment_for_month` is called for any month, **Then** it always returns `0.0`.
7. **Given** `calculations.py` after this story, **Then** ARCH-3 is maintained (no streamlit import).
8. **Given** `pytest` is run from the project root, **Then** ALL tests pass — including 25 from Stories 1.3 and 1.4 (no regressions).

## Tasks / Subtasks

- [x] **Task 1: Add FAILING tests to `tests/test_calculations.py`** (AC: 1–6, 8)
  - [x] Open existing `tests/test_calculations.py` — **append** new tests, do NOT replace existing ones
  - [x] Update the import line at the top to add `calculate_investment_portfolio` and `get_special_assessment_for_month`
  - [x] Add tests for `calculate_investment_portfolio` (see Dev Notes for exact tests)
  - [x] Add tests for `get_special_assessment_for_month` (see Dev Notes for exact tests)
  - [x] Run `pytest tests/ -v` — confirm new tests FAIL, existing 25 still pass

- [x] **Task 2: Implement both functions in `calculations.py`** (AC: 1–6)
  - [x] **Append** to existing `calculations.py` — do NOT touch any existing constants or functions
  - [x] Implement `calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60)` — see Dev Notes for exact spec
  - [x] Implement `get_special_assessment_for_month(amount, assessment_month, current_month)` — see Dev Notes for exact spec

- [x] **Task 3: Run all tests and verify** (AC: 7–8)
  - [x] Run: `pytest tests/ -v` — all tests (25 from 1.3–1.4 + new) must be GREEN
  - [x] Run ARCH-3 check: `python -c "import ast; tree = ast.parse(open('calculations.py').read()); sl = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and any('streamlit' in (getattr(n,'module','') or '') or any('streamlit' in a.name for a in getattr(n,'names',[])) for _ in [n])]; print('ARCH-3 PASS' if not sl else 'FAIL')"`

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  calculations.py           ← UPDATE (append two new functions — no other changes)
  tests/
    test_calculations.py    ← UPDATE (append new tests + update import line)
```

**CRITICAL: Both files already exist. APPEND only — never overwrite.**

### Current State of `calculations.py`

After Story 1.4, `calculations.py` contains exactly these items in order:
```
module docstring
PMI_ANNUAL_RATE = 0.008
calculate_amortization_schedule()    ← Story 1.3, DO NOT TOUCH
HOMESTEAD_EXEMPTION = 50_000
calculate_monthly_property_tax()     ← Story 1.4, DO NOT TOUCH
calculate_upfront_cash()             ← Story 1.4, DO NOT TOUCH
```

Append at the bottom:
```python
def calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60):
    """Returns list of `months` monthly portfolio values with monthly compounding."""
    monthly_rate = annual_rate / 100 / 12
    portfolio = []
    balance = initial_capital
    for _ in range(months):
        balance = (balance + monthly_contribution) * (1 + monthly_rate)
        portfolio.append(balance)
    return portfolio


def get_special_assessment_for_month(amount, assessment_month, current_month):
    """Returns special assessment cash outflow for current_month (FR18)."""
    if amount > 0 and current_month == assessment_month:
        return float(amount)
    return 0.0
```

### Monthly Compounding Formula — Why It Works This Way (NFR8)

Each month the renter's portfolio grows by:
1. Adding the monthly contribution (savings from not paying a mortgage)
2. Earning interest on the total at the monthly rate

```
monthly_rate = annual_rate / 100 / 12

Month 1: (initial_capital + monthly_contribution) * (1 + monthly_rate)
Month 2: (month_1_value  + monthly_contribution) * (1 + monthly_rate)
...
Month N: (month_N-1_value + monthly_contribution) * (1 + monthly_rate)
```

**This is monthly compounding — NOT annual.** If annual_rate = 7%, monthly_rate = 0.5833%, NOT 7%/12 rounded. NFR8 explicitly requires monthly compounding.

Edge case: `annual_rate = 0` → `monthly_rate = 0` → `balance = (balance + contribution) * 1.0` = flat accumulation. No special-case code needed.

### Special Assessment Logic

The special assessment is a one-time cash outflow that hits the **buyer** in a specific month — like a surprise condo building repair bill. It has no effect on the renter's portfolio; it only adds to the buyer's costs for that one month.

```python
# Usage pattern in Story 2.3:
monthly_buyer_cost = pi + pmi + hoa + property_tax + insurance
monthly_buyer_cost += get_special_assessment_for_month(
    amount=special_assessment_amount,
    assessment_month=special_assessment_month,
    current_month=month
)
```

If `amount = 0` (the default in `defaults.py`), the function always returns 0 — no branching needed in the caller.

### Current Import Line in `tests/test_calculations.py`

After Story 1.4 the top of the test file is:
```python
import pytest
from calculations import (
    calculate_amortization_schedule,
    calculate_monthly_property_tax,
    calculate_upfront_cash,
)
```

Update to:
```python
import pytest
from calculations import (
    calculate_amortization_schedule,
    calculate_monthly_property_tax,
    calculate_upfront_cash,
    calculate_investment_portfolio,
    get_special_assessment_for_month,
)
```

### Tests to Append to `tests/test_calculations.py`

```python
# ── calculate_investment_portfolio (Story 1.5) ────────────────────────────────

def test_portfolio_returns_correct_length():
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    assert len(result) == 60


def test_portfolio_month1_formula():
    # (initial + contribution) * (1 + monthly_rate)
    # (10_000 + 500) * (1 + 0.07/12) = 10_500 * 1.005833 = 10_561.25
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    expected = (10_000 + 500) * (1 + 7 / 100 / 12)
    assert abs(result[0] - expected) < 0.01


def test_portfolio_month2_compounds_month1():
    # Month 2 must compound month 1 value, not initial_capital
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    expected_m2 = (result[0] + 500) * (1 + 7 / 100 / 12)
    assert abs(result[1] - expected_m2) < 0.01


def test_portfolio_zero_rate_flat_accumulation():
    # No growth: each month just adds contribution
    result = calculate_investment_portfolio(0, 1_000, 0, 60)
    assert abs(result[0] - 1_000) < 0.01
    assert abs(result[59] - 60_000) < 0.01


def test_portfolio_zero_contribution_compounds_only():
    # Only initial capital, no monthly savings: pure compound growth
    # $10K at 12% annual (1%/month): month 1 = $10,100
    result = calculate_investment_portfolio(10_000, 0, 12, 60)
    assert abs(result[0] - 10_100) < 0.01


def test_portfolio_grows_over_time():
    # Balance at month 60 must exceed balance at month 1
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    assert result[59] > result[0]


def test_portfolio_monthly_not_annual_compounding():
    # At 12% annual, monthly compounding gives 1.01^12 = ~1.1268 growth
    # Annual compounding would give exactly 1.12 — they must differ
    result_monthly = calculate_investment_portfolio(10_000, 0, 12, 12)
    annual_simple = 10_000 * 1.12
    assert result_monthly[11] > annual_simple  # monthly > annual for same rate


def test_portfolio_custom_months_length():
    result = calculate_investment_portfolio(5_000, 200, 5, 12)
    assert len(result) == 12


# ── get_special_assessment_for_month (Story 1.5) ─────────────────────────────

def test_special_assessment_returns_amount_on_correct_month():
    result = get_special_assessment_for_month(5_000, 12, 12)
    assert result == 5_000.0


def test_special_assessment_returns_zero_before_month():
    result = get_special_assessment_for_month(5_000, 12, 11)
    assert result == 0.0


def test_special_assessment_returns_zero_after_month():
    result = get_special_assessment_for_month(5_000, 12, 13)
    assert result == 0.0


def test_special_assessment_zero_amount_always_zero():
    # Default state: no assessment
    assert get_special_assessment_for_month(0, 12, 12) == 0.0
    assert get_special_assessment_for_month(0, 1, 1) == 0.0


def test_special_assessment_first_month():
    result = get_special_assessment_for_month(10_000, 1, 1)
    assert result == 10_000.0


def test_special_assessment_last_month():
    result = get_special_assessment_for_month(7_500, 60, 60)
    assert result == 7_500.0
```

### Pre-Computed Reference Values

| Scenario | Month | Expected Value |
|---|---|---|
| initial=0, contrib=$1,000, rate=0%, months=60 | 1 | $1,000.00 |
| initial=0, contrib=$1,000, rate=0%, months=60 | 60 | $60,000.00 |
| initial=$10,000, contrib=0, rate=12% | 1 | $10,100.00 |
| initial=$10,000, contrib=$500, rate=7% | 1 | $10,561.25 |

Special assessment reference:
- `get_special_assessment_for_month(5_000, 12, 12)` → $5,000.00
- `get_special_assessment_for_month(5_000, 12, any_other)` → $0.00

### Story Learnings from 1.1–1.4

- **Use `python` not `python3`** on this Windows machine
- **Run pytest as:** `.venv\Scripts\pytest.exe tests/ -v`
- **APPEND to existing files** — never overwrite
- **Update the import line at the top** of `test_calculations.py` — it uses a multi-line import block
- **ARCH-3 invariant:** no streamlit import — verify after every change
- **RED phase first:** confirm new tests fail before implementing

### What This Story Does NOT Do

- Does NOT wire the portfolio into UI (Story 2.3)
- Does NOT compute the renter's monthly savings/contribution (that's Story 2.3 — it subtracts buying costs from renting costs)
- Does NOT model the investment portfolio for the landlord scenario (Story 1.6)
- Does NOT modify `defaults.py`, `app.py`, or `url_state.py`
- Does NOT change `SPECIAL_ASSESSMENT_AMOUNT` or `SPECIAL_ASSESSMENT_MONTH` defaults in `defaults.py`

### Cross-Story Context

| Story | Uses output of 1.5 |
|---|---|
| 1.6 | `calculate_investment_portfolio(...)[-1]` = renter's portfolio at month 60 for continue-renting exit |
| 2.3 | Both functions called per scenario per slider change; `monthly_contribution` derived from (buyer_cost − renter_cost) |
| 2.6 | `portfolio[-1]` displayed in the "Continue Renting" row of the exit paths table |

### References

- [Source: epics.md — Story 1.5 Acceptance Criteria, FR17, FR18, NFR8]
- [Source: prd.md — NFR8 (monthly compounding), FR17 (portfolio model), FR18 (special assessment lump sum)]
- [Source: architecture.md — ARCH-3 invariant]
- [Source: defaults.py — SPECIAL_ASSESSMENT_AMOUNT = 0.0, SPECIAL_ASSESSMENT_MONTH = 1, INVESTMENT_RETURN_RATE = 7.0]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- RED phase confirmed: ImportError on `calculate_investment_portfolio` before implementation.
- GREEN phase: all 39 tests passed on first run after appending both functions.
- ARCH-3 check passed.
- No new pip installs required.

### Completion Notes List

- Appended `calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60)`: monthly compounding loop — each month adds contribution then multiplies by (1 + monthly_rate). Zero-rate edge case handled naturally (multiply by 1.0).
- Appended `get_special_assessment_for_month(amount, assessment_month, current_month)`: single conditional — returns float(amount) only when amount > 0 and month matches, else 0.0.
- Updated import block in `tests/test_calculations.py` to include both new functions.
- Appended 14 new tests (8 portfolio, 6 special assessment); 39 total, all GREEN. Zero regressions.
- ARCH-3 invariant maintained.

### File List

- `calculations.py` (modified — appended calculate_investment_portfolio, get_special_assessment_for_month)
- `tests/test_calculations.py` (modified — updated import line, appended 14 new tests)

## Change Log

- 2026-05-23: Implemented Story 1.5 — investment portfolio with monthly compounding and special assessment lookup; 39/39 tests pass.
