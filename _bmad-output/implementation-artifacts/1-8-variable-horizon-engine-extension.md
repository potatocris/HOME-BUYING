# Story 1.8: Variable Horizon Engine Extension

Status: done

## Story

As a developer,
I want the financial engine to support any time horizon up to 30 years,
So that the Rent vs Buy chart and table can show wealth growth over any selected period.

## Acceptance Criteria

1. **Given** `calculate_amortization_schedule(price, down_pct, annual_rate)` is called without a `months` argument, **Then** it returns exactly 60 records (backward compatible — no existing test or caller breaks).

2. **Given** `calculate_amortization_schedule(price, down_pct, annual_rate, months=N)` is called with explicit `N`, **Then** it returns exactly `N` monthly records covering months 1 through N, using the standard 30-year payment formula for P&I (mortgage term stays 360 regardless of the observation window).

3. **Given** `calculate_investment_portfolio` already has `months=60` as a parameter (Story 1.5), **Then** NO change to that function is needed — it is backward compatible as-is.

4. **Given** a list of per-month buyer surplus amounts `monthly_surplus_list` (each entry = `max(0, rent − buying_cost_that_month)`) and an `annual_rate`, **When** `calculate_buyer_investment_portfolio(monthly_surplus_list, annual_rate)` is called, **Then** it returns a list of portfolio values equal in length to `monthly_surplus_list`, compounded monthly from a $0 starting balance:
   - `month_1 = (0 + surplus[0]) * (1 + monthly_rate)`
   - `month_k = (prev_balance + surplus[k-1]) * (1 + monthly_rate)`

5. **Given** a list of `N` monthly values, **When** `get_annual_snapshots(monthly_values)` is called, **Then** it returns a list of length `N // 12`, containing the values at indices 11, 23, 35 … (months 12, 24, 36 …) — one value per complete year.

6. **Given** `pytest` is run from the project root, **Then** ALL existing 77 tests pass with zero regressions, plus the new tests for modified/new functions all pass GREEN.

7. **Given** `calculations.py` after this story, **Then** ARCH-3 is maintained: zero Streamlit imports (verifiable with the AST check).

## Tasks / Subtasks

- [x] **Task 1: Add FAILING tests first** (AC: 1–5, 6)
  - [x] Open `tests/test_calculations.py` — **APPEND** new tests, do NOT modify existing ones
  - [x] Update import line to add `calculate_buyer_investment_portfolio` and `get_annual_snapshots`
  - [x] Append tests for `calculate_amortization_schedule` with `months` parameter (see Dev Notes)
  - [x] Append tests for `calculate_buyer_investment_portfolio` (see Dev Notes)
  - [x] Append tests for `get_annual_snapshots` (see Dev Notes)
  - [x] Run `.venv\Scripts\pytest.exe tests/ -v` — confirm new tests FAIL, all 77 existing tests still pass

- [x] **Task 2: Modify `calculate_amortization_schedule` in `calculations.py`** (AC: 1–2)
  - [x] Add `months=60` parameter to the function signature
  - [x] Change `for month in range(1, 61):` → `for month in range(1, months + 1):`
  - [x] Update docstring to reference `months` parameter
  - [x] Do NOT touch any other part of the function (PMI logic, payment formula stay unchanged)

- [x] **Task 3: Append `calculate_buyer_investment_portfolio` to `calculations.py`** (AC: 4)
  - [x] Append at the bottom — do NOT touch existing code
  - [x] See Dev Notes for exact implementation

- [x] **Task 4: Append `get_annual_snapshots` to `calculations.py`** (AC: 5)
  - [x] Append at the bottom — do NOT touch existing code
  - [x] See Dev Notes for exact implementation

- [x] **Task 5: Run all tests and verify ARCH-3** (AC: 6–7)
  - [x] Run: `.venv\Scripts\pytest.exe tests/ -v` — all tests must be GREEN
  - [x] Run ARCH-3 check: `python -c "import ast; tree = ast.parse(open('calculations.py').read()); sl = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and any('streamlit' in (getattr(n,'module','') or '') or any('streamlit' in a.name for a in getattr(n,'names',[])) for _ in [n])]; print('ARCH-3 PASS' if not sl else 'FAIL')"`
  - [x] Report final test count in completion notes

### Review Findings

- [x] [Review][Defer] `months > 360` → amortization balance goes negative after mortgage fully amortizes [`calculations.py`] — deferred, consistent with project policy (UI slider caps horizon at 30 yr = 360 months; no engine-layer validation per deferred-work.md)
- [x] [Review][Defer] `months=0` or negative → silent empty list [`calculations.py`] — deferred, consistent with project policy; no slider produces 0 or negative months
- [x] [Review][Defer] Negative surplus values in `calculate_buyer_investment_portfolio` not guarded [`calculations.py`] — deferred, caller responsibility per docstring; Story 2.5 applies `max(0, …)` before calling
- [x] [Review][Defer] `get_annual_snapshots` with list shorter than 12 months returns empty silently [`calculations.py`] — deferred, documented behavior (`len // 12`); practical callers always pass ≥ 60 months
- [x] [Review][Defer] `calculate_exit_continue_renting` docstring references "month 60" — stale with variable horizon [`calculations.py:108`] — deferred, pre-existing; not introduced by this story

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  calculations.py               ← UPDATE (modify signature + append 2 new functions)
  tests/
    test_calculations.py        ← UPDATE (update import line + append new tests)
```

**CRITICAL: Both files already exist. APPEND new functions and tests, NEVER overwrite.**

### Windows-Specific Commands

- Use `python` (NOT `python3`) — this machine runs Anaconda on Windows
- Run pytest as: `.venv\Scripts\pytest.exe tests/ -v`
- ARCH-3 check: `python -c "..."` (as above in Task 5)

### Current State of `calculations.py`

After Story 1.7 (bug fixes), `calculations.py` contains in this exact order:

```
module docstring
PMI_ANNUAL_RATE = 0.008
calculate_amortization_schedule(price, down_pct, annual_rate)   ← MODIFY signature only
HOMESTEAD_EXEMPTION = 50_000
calculate_monthly_property_tax(price, tax_rate_pct, month)       ← DO NOT TOUCH
calculate_upfront_cash(price, down_pct, closing_pct, furniture)  ← DO NOT TOUCH
calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60)  ← DO NOT TOUCH (already parameterized!)
get_special_assessment_for_month(amount, assessment_month, current_month)  ← DO NOT TOUCH
FL_DOC_STAMP_RATE = 0.007
calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct)  ← DO NOT TOUCH
calculate_exit_rent_out(monthly_rental_income, vacancy_rate_pct, mgmt_fee_pct, ...)      ← DO NOT TOUCH
calculate_exit_continue_renting(portfolio_values)                ← DO NOT TOUCH
```

**`calculate_investment_portfolio` ALREADY HAS `months=60`. Do NOT re-add or modify it.**

### Exact Change to `calculate_amortization_schedule`

**Before (current):**
```python
def calculate_amortization_schedule(price, down_pct, annual_rate):
    """Returns list of 60 monthly records: month, principal, interest, balance, pmi."""
    loan = price * (1 - down_pct / 100)
    r = annual_rate / 100 / 12
    n = 360  # 30-year mortgage
    ...
    for month in range(1, 61):
```

**After (change ONLY the signature line, docstring, and loop range):**
```python
def calculate_amortization_schedule(price, down_pct, annual_rate, months=60):
    """Returns list of `months` monthly records: month, principal, interest, balance, pmi."""
    loan = price * (1 - down_pct / 100)
    r = annual_rate / 100 / 12
    n = 360  # 30-year mortgage payment term (always 360, regardless of observation window)
    ...
    for month in range(1, months + 1):
```

**Everything else inside the function (payment formula, PMI logic, `pmi_threshold`, `pmi_monthly`, `pmi_cancelled`, `balance`, `schedule` building) stays exactly the same.**

### New Functions to Append to `calculations.py`

Append these two functions at the very bottom of `calculations.py`:

```python

def calculate_buyer_investment_portfolio(monthly_surplus_list, annual_rate):
    """Returns list of buyer's side-portfolio values compounded monthly from $0 (Story 1.8).

    monthly_surplus_list: per-month amounts of max(0, rent - buying_cost_m) for each month.
    annual_rate: investment return rate (percent, e.g. 7.0 for 7%).
    """
    monthly_rate = annual_rate / 100 / 12
    portfolio = []
    balance = 0.0
    for surplus in monthly_surplus_list:
        balance = (balance + surplus) * (1 + monthly_rate)
        portfolio.append(balance)
    return portfolio


def get_annual_snapshots(monthly_values):
    """Returns year-end values from a monthly list, sampled at months 12, 24, 36...

    len(result) == len(monthly_values) // 12
    """
    return [monthly_values[i] for i in range(11, len(monthly_values), 12)]
```

### Current Import Line in `tests/test_calculations.py`

After Story 1.6/1.7, the import block is:
```python
import pytest
from calculations import (
    calculate_amortization_schedule,
    calculate_monthly_property_tax,
    calculate_upfront_cash,
    calculate_investment_portfolio,
    get_special_assessment_for_month,
    calculate_exit_sell,
    calculate_exit_rent_out,
    calculate_exit_continue_renting,
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
    calculate_exit_sell,
    calculate_exit_rent_out,
    calculate_exit_continue_renting,
    calculate_buyer_investment_portfolio,
    get_annual_snapshots,
)
```

### Tests to Append to `tests/test_calculations.py`

```python
# ── calculate_amortization_schedule months param (Story 1.8) ─────────────────

def test_amortization_default_still_60_months():
    # No-arg call: backward compatible default returns exactly 60 records
    result = calculate_amortization_schedule(300_000, 5, 6.5)
    assert len(result) == 60


def test_amortization_custom_months_120():
    # 10-year horizon: 120 months of data
    result = calculate_amortization_schedule(300_000, 10, 6.5, months=120)
    assert len(result) == 120


def test_amortization_custom_months_360():
    # Full 30-year schedule
    result = calculate_amortization_schedule(300_000, 20, 6.5, months=360)
    assert len(result) == 360


def test_amortization_custom_months_sequential():
    # Month numbers must run 1 .. N regardless of N
    result = calculate_amortization_schedule(300_000, 10, 6.5, months=120)
    for i, record in enumerate(result):
        assert record["month"] == i + 1


def test_amortization_360_months_balance_near_zero():
    # After 360 payments the loan should be essentially paid off
    result = calculate_amortization_schedule(300_000, 20, 6.5, months=360)
    final_balance = result[-1]["balance"]
    assert abs(final_balance) < 1.00  # within $1 of $0


def test_amortization_120_months_balance_less_than_60_months():
    # At month 120 more principal has been paid than at month 60
    balance_60 = calculate_amortization_schedule(300_000, 5, 6.5, months=60)[-1]["balance"]
    balance_120 = calculate_amortization_schedule(300_000, 5, 6.5, months=120)[-1]["balance"]
    assert balance_120 < balance_60


# ── calculate_buyer_investment_portfolio (Story 1.8) ─────────────────────────

def test_buyer_portfolio_returns_correct_length():
    surpluses = [100.0] * 60
    result = calculate_buyer_investment_portfolio(surpluses, 7.0)
    assert len(result) == 60


def test_buyer_portfolio_variable_length():
    surpluses = [200.0] * 120
    result = calculate_buyer_investment_portfolio(surpluses, 5.0)
    assert len(result) == 120


def test_buyer_portfolio_all_zero_surplus_zero_rate():
    # No surplus, no return → all zeros
    result = calculate_buyer_investment_portfolio([0.0] * 60, 0.0)
    assert all(v == 0.0 for v in result)


def test_buyer_portfolio_all_zero_surplus_with_rate():
    # Starting balance is $0; with no contributions nothing grows
    result = calculate_buyer_investment_portfolio([0.0] * 60, 7.0)
    assert all(abs(v) < 0.01 for v in result)


def test_buyer_portfolio_zero_rate_flat_accumulation():
    # At 0% return: each month simply adds the surplus
    surpluses = [1_000.0] * 60
    result = calculate_buyer_investment_portfolio(surpluses, 0.0)
    assert abs(result[0] - 1_000.0) < 0.01
    assert abs(result[59] - 60_000.0) < 0.01


def test_buyer_portfolio_matches_investment_portfolio_constant_surplus():
    # Constant surplus with compounding must match calculate_investment_portfolio(0, surplus, rate, months)
    surplus = 500.0
    rate = 7.0
    months = 60
    surpluses = [surplus] * months
    buyer_result = calculate_buyer_investment_portfolio(surpluses, rate)
    reference = calculate_investment_portfolio(0, surplus, rate, months)
    for i in range(months):
        assert abs(buyer_result[i] - reference[i]) < 0.01


def test_buyer_portfolio_month1_formula():
    # Month 1: (0 + surplus) * (1 + monthly_rate)
    surplus = 300.0
    annual_rate = 6.0
    monthly_rate = 6.0 / 100 / 12
    result = calculate_buyer_investment_portfolio([surplus], annual_rate)
    expected = (0 + surplus) * (1 + monthly_rate)
    assert abs(result[0] - expected) < 0.01


def test_buyer_portfolio_month2_compounds_month1():
    # Month 2 must compound month 1 balance
    surplus = 300.0
    annual_rate = 6.0
    monthly_rate = 6.0 / 100 / 12
    result = calculate_buyer_investment_portfolio([surplus, surplus], annual_rate)
    month1 = (0 + surplus) * (1 + monthly_rate)
    month2 = (month1 + surplus) * (1 + monthly_rate)
    assert abs(result[1] - month2) < 0.01


def test_buyer_portfolio_variable_surpluses():
    # Mix of zero and non-zero surpluses
    surpluses = [0.0, 200.0, 0.0, 300.0]
    rate = 12.0
    monthly_rate = 12.0 / 100 / 12  # 0.01
    result = calculate_buyer_investment_portfolio(surpluses, rate)
    # m1: (0 + 0) * 1.01 = 0
    assert abs(result[0] - 0.0) < 0.01
    # m2: (0 + 200) * 1.01 = 202
    assert abs(result[1] - 202.0) < 0.01
    # m3: (202 + 0) * 1.01 = 204.02
    assert abs(result[2] - 204.02) < 0.01
    # m4: (204.02 + 300) * 1.01 = 504.02 * 1.01 = 509.06
    assert abs(result[3] - 509.0602) < 0.01


def test_buyer_portfolio_grows_with_positive_surpluses():
    surpluses = [500.0] * 60
    result = calculate_buyer_investment_portfolio(surpluses, 7.0)
    assert result[-1] > result[0]


# ── get_annual_snapshots (Story 1.8) ─────────────────────────────────────────

def test_annual_snapshots_60_months_returns_5_values():
    values = list(range(1, 61))
    result = get_annual_snapshots(values)
    assert len(result) == 5


def test_annual_snapshots_120_months_returns_10_values():
    values = list(range(1, 121))
    result = get_annual_snapshots(values)
    assert len(result) == 10


def test_annual_snapshots_360_months_returns_30_values():
    values = list(range(1, 361))
    result = get_annual_snapshots(values)
    assert len(result) == 30


def test_annual_snapshots_correct_indices():
    # Values [1, 2, ..., 60]: month 12 is index 11 → value 12
    #                          month 24 is index 23 → value 24
    #                          month 36 is index 35 → value 36
    values = list(range(1, 61))
    result = get_annual_snapshots(values)
    assert result[0] == 12   # month 12
    assert result[1] == 24   # month 24
    assert result[2] == 36   # month 36
    assert result[3] == 48   # month 48
    assert result[4] == 60   # month 60


def test_annual_snapshots_reflects_portfolio_year_ends():
    # Integration: get year-end values from a real portfolio
    portfolio = calculate_investment_portfolio(0, 1_000, 0, 60)  # zero-rate → $1K, $2K, ..., $60K
    snapshots = get_annual_snapshots(portfolio)
    assert len(snapshots) == 5
    assert abs(snapshots[0] - 12_000.0) < 0.01  # year 1 end
    assert abs(snapshots[4] - 60_000.0) < 0.01  # year 5 end


def test_annual_snapshots_partial_year_ignored():
    # 65 months: 5 complete years, 5 leftover months → still 5 snapshots
    values = list(range(1, 66))
    result = get_annual_snapshots(values)
    assert len(result) == 5
```

### Why `months=60` Default (Not 360)

The sprint change proposal listed `months=360` as the default, but this would break existing tests and the 4-scenario page (`pages/scenarios.py`, Story 2.4) which expects 60-month schedules. Using `months=60`:
- All 77 existing tests pass without modification
- `app.py` and `pages/scenarios.py` callers work unchanged
- Story 2.5 passes `months=horizon_years*12` explicitly (up to 360)

### What This Story Does NOT Do

- Does NOT change `calculate_exit_sell` or `calculate_exit_rent_out` — those functions' hardcoded 5-year formulas (`** 5`, `* 60`) are used by the 4-scenario page; Story 2.5 computes variable-horizon equity directly from the amortization schedule
- Does NOT change `calculate_investment_portfolio` — already has `months=60` parameter (Story 1.5)
- Does NOT change `defaults.py`, `app.py`, or `url_state.py`
- Does NOT implement any UI or display logic (Epic 2)

### Cross-Story Context

| Story | Uses output of 1.8 |
|---|---|
| 2.5 | Calls `calculate_amortization_schedule(..., months=horizon_years*12)` and `calculate_buyer_investment_portfolio(surplus_list, rate)` for the rent-vs-buy computation |
| 2.7 | `get_annual_snapshots` feeds the annual breakdown table (Year \| Rent \| Buy \| Diff \| Better) |
| 2.4 | `pages/scenarios.py` calls `calculate_amortization_schedule` without `months` → still gets 60-month schedule (backward compatible) |

### References

- [Source: sprint-change-proposal-2026-05-25.md — Story 1.8 acceptance criteria]
- [Source: sprint-change-proposal-2026-05-25.md — Story 2.5 calculation model spec]
- [Source: calculations.py — current function signatures and implementations]
- [Source: story 1.6 — APPEND-only pattern, ARCH-3 invariant, Windows pytest path]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- RED phase: `ImportError: cannot import name 'calculate_buyer_investment_portfolio'` confirmed new tests fail before implementation (expected).
- GREEN phase: 99/99 passed in 0.09s after implementing all changes.
- ARCH-3 check: PASS.

### Completion Notes List

- Modified `calculate_amortization_schedule` signature: added `months=60` parameter; updated loop to `range(1, months + 1)`; updated docstring; updated `n = 360` comment. No other logic changed.
- `calculate_investment_portfolio` left untouched — already had `months=60` from Story 1.5.
- Appended `calculate_buyer_investment_portfolio(monthly_surplus_list, annual_rate)`: starts balance at $0; compounds each month's surplus at monthly rate; returns list equal in length to input. Verified equivalent to `calculate_investment_portfolio(0, surplus, rate, months)` for constant surplus.
- Appended `get_annual_snapshots(monthly_values)`: one-liner list comprehension sampling indices 11, 23, 35… (months 12, 24, 36…). `len(result) == len(input) // 12`.
- Updated `tests/test_calculations.py` import block to include 2 new symbols.
- Appended 22 new tests: 6 for amortization `months` param, 10 for `calculate_buyer_investment_portfolio`, 6 for `get_annual_snapshots`.
- Final test count: **99 passed** (77 existing + 22 new). Zero regressions.
- ARCH-3 maintained: zero Streamlit imports in `calculations.py`.

### File List

- `calculations.py` (modified — `calculate_amortization_schedule` signature + loop; appended `calculate_buyer_investment_portfolio`, `get_annual_snapshots`)
- `tests/test_calculations.py` (modified — updated import line; appended 22 new tests)

## Change Log

- 2026-05-25: Implemented Story 1.8 — variable horizon engine extension; 99/99 tests pass.
