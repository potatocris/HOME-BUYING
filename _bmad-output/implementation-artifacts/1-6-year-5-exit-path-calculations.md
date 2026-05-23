# Story 1.6: Year-5 Exit Path Calculations

Status: review

## Story

As a developer,
I want `calculations.py` to compute all three year-5 exit path values for a given scenario,
So that the net worth comparison across Sell, Rent Out, and Continue Renting is accurate and reconcilable.

## Acceptance Criteria

1. **Given** price, appreciation rate, loan balance at month 60, and realtor commission %, **When** `calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct)` is called, **Then** it returns: `appreciated_value − realtor_fee − florida_doc_stamp − remaining_balance` where `appreciated_value = price * (1 + appreciation_rate/100)^5` and `florida_doc_stamp = appreciated_value * 0.007` (FR19).
2. **Given** a $300K home, 3% appreciation, 3% commission, $0 remaining balance, **When** `calculate_exit_sell` is called, **Then** the result is within $1.00 of $334,914 (appreciated value $347,782 − $10,433 − $2,435 − $0).
3. **Given** monthly rental income, vacancy %, management fee %, monthly carrying costs, appreciated home value, and remaining loan balance, **When** `calculate_exit_rent_out(monthly_rental_income, vacancy_rate_pct, mgmt_fee_pct, monthly_carrying_costs, appreciated_value, remaining_balance)` is called, **Then** it returns: `(net_monthly_cashflow × 60) + (appreciated_value − remaining_balance)` where `net_monthly_cashflow = monthly_rental_income × (1 − vacancy/100) × (1 − mgmt_fee/100) − monthly_carrying_costs` (FR20).
4. **Given** a portfolio values list from `calculate_investment_portfolio`, **When** `calculate_exit_continue_renting(portfolio_values)` is called, **Then** it returns `portfolio_values[-1]` — the renter's portfolio value at month 60 (FR21).
5. **Given** any scenario, **Then** net worth reconciles: cumulative monthly cash flows + terminal asset value = the exit function's return value (NFR7).
6. **Given** `calculations.py` after this story, **Then** ARCH-3 is maintained (no streamlit import).
7. **Given** `pytest` is run from the project root, **Then** ALL 39 existing tests pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Add FAILING tests to `tests/test_calculations.py`** (AC: 1–5, 7)
  - [x] Open existing `tests/test_calculations.py` — **append** new tests, do NOT replace existing ones
  - [x] Update the import line at the top to add all three new exit functions
  - [x] Add tests for `calculate_exit_sell` (see Dev Notes)
  - [x] Add tests for `calculate_exit_rent_out` (see Dev Notes)
  - [x] Add tests for `calculate_exit_continue_renting` (see Dev Notes)
  - [x] Run `pytest tests/ -v` — confirm new tests FAIL, existing 39 still pass

- [x] **Task 2: Add `FL_DOC_STAMP_RATE` constant and implement all three functions in `calculations.py`** (AC: 1–5)
  - [x] **Append** to existing `calculations.py` — do NOT touch any existing code
  - [x] Add constant: `FL_DOC_STAMP_RATE = 0.007` (Florida documentary stamp tax, 0.70% of sale price)
  - [x] Implement `calculate_exit_sell` — see Dev Notes for exact spec
  - [x] Implement `calculate_exit_rent_out` — see Dev Notes for exact spec (6 parameters, see note)
  - [x] Implement `calculate_exit_continue_renting` — see Dev Notes

- [x] **Task 3: Run all tests and verify** (AC: 6–7)
  - [x] Run: `pytest tests/ -v` — all tests must be GREEN (39 existing + new)
  - [x] Run ARCH-3 check: `python -c "import ast; tree = ast.parse(open('calculations.py').read()); sl = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and any('streamlit' in (getattr(n,'module','') or '') or any('streamlit' in a.name for a in getattr(n,'names',[])) for _ in [n])]; print('ARCH-3 PASS' if not sl else 'FAIL')"`

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  calculations.py           ← UPDATE (append FL_DOC_STAMP_RATE + 3 new functions)
  tests/
    test_calculations.py    ← UPDATE (update import line + append new tests)
```

**CRITICAL: Both files already exist. APPEND only — never overwrite.**

### Current State of `calculations.py`

After Story 1.5, `calculations.py` contains in order:
```
module docstring
PMI_ANNUAL_RATE = 0.008
calculate_amortization_schedule()    ← Stories 1.3, DO NOT TOUCH
HOMESTEAD_EXEMPTION = 50_000
calculate_monthly_property_tax()     ← Story 1.4, DO NOT TOUCH
calculate_upfront_cash()             ← Story 1.4, DO NOT TOUCH
calculate_investment_portfolio()     ← Story 1.5, DO NOT TOUCH
get_special_assessment_for_month()   ← Story 1.5, DO NOT TOUCH
```

Append at the bottom:
```python
FL_DOC_STAMP_RATE = 0.007  # Florida documentary stamp tax (0.70% of sale price)


def calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct):
    """Returns net proceeds from selling at year 5 (FR19)."""
    appreciated_value = price * (1 + appreciation_rate / 100) ** 5
    realtor_fee = appreciated_value * (realtor_commission_pct / 100)
    doc_stamp = appreciated_value * FL_DOC_STAMP_RATE
    return appreciated_value - realtor_fee - doc_stamp - remaining_balance


def calculate_exit_rent_out(monthly_rental_income, vacancy_rate_pct, mgmt_fee_pct,
                             monthly_carrying_costs, appreciated_value, remaining_balance):
    """Returns 60-month net landlord cash flow + home equity at month 60 (FR20)."""
    effective_income = monthly_rental_income * (1 - vacancy_rate_pct / 100)
    net_monthly_income = effective_income * (1 - mgmt_fee_pct / 100)
    monthly_net_cashflow = net_monthly_income - monthly_carrying_costs
    cumulative_cashflow = monthly_net_cashflow * 60
    home_equity = appreciated_value - remaining_balance
    return cumulative_cashflow + home_equity


def calculate_exit_continue_renting(portfolio_values):
    """Returns renter's portfolio value at month 60 (FR21)."""
    return portfolio_values[-1]
```

### Design Note: `calculate_exit_rent_out` Parameter Deviation from Epics

The epics spec listed 5 parameters for `calculate_exit_rent_out`. This story uses **6 parameters** — adding `appreciated_value` before `remaining_balance`. This is required because computing home equity at month 60 needs both the appreciated home value AND the outstanding loan balance. Omitting it would make equity calculations incorrect. The epics spec was high-level and did not account for this dependency. Story 2.3 (which calls all exit functions) will pass `appreciated_value` from `calculate_exit_sell`'s intermediate computation.

### Mathematical Formulas

**`calculate_exit_sell`:**
```
appreciated_value = price * (1 + appreciation_rate / 100) ** 5
realtor_fee       = appreciated_value * (realtor_commission_pct / 100)
doc_stamp         = appreciated_value * 0.007
return            = appreciated_value - realtor_fee - doc_stamp - remaining_balance
```

**`calculate_exit_rent_out`:**
```
effective_income     = monthly_rental_income * (1 - vacancy_rate_pct / 100)
net_monthly_income   = effective_income * (1 - mgmt_fee_pct / 100)
monthly_net_cashflow = net_monthly_income - monthly_carrying_costs
cumulative_cashflow  = monthly_net_cashflow * 60
home_equity          = appreciated_value - remaining_balance
return               = cumulative_cashflow + home_equity
```

**`calculate_exit_continue_renting`:**
```
return = portfolio_values[-1]   # index 59, value at month 60
```

### Current Import Line in `tests/test_calculations.py`

After Story 1.5, the import block is:
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
)
```

### Tests to Append to `tests/test_calculations.py`

```python
# ── calculate_exit_sell (Story 1.6) ──────────────────────────────────────────

def test_exit_sell_zero_appreciation_zero_balance():
    # No appreciation, no balance: proceeds = price - fees
    # $300K, 0% appreciation, 3% realtor, 0 balance
    # doc_stamp = 300_000 * 0.007 = 2,100
    # realtor = 300_000 * 0.03 = 9,000
    # return = 300_000 - 9,000 - 2,100 - 0 = 288,900
    result = calculate_exit_sell(300_000, 0, 0, 3)
    assert abs(result - 288_900) < 1.00


def test_exit_sell_appreciation_increases_value():
    # With appreciation, net proceeds are higher than without
    no_appreciation = calculate_exit_sell(300_000, 0, 0, 3)
    with_appreciation = calculate_exit_sell(300_000, 3, 0, 3)
    assert with_appreciation > no_appreciation


def test_exit_sell_reference_values():
    # $300K, 3% appreciation, 3% commission, $0 remaining balance
    # appreciated = 300_000 * (1.03)^5 = ~$347,782
    # realtor = 347,782 * 0.03 = ~$10,433
    # doc_stamp = 347,782 * 0.007 = ~$2,435
    # net = 347,782 - 10,433 - 2,435 - 0 = ~$334,914
    result = calculate_exit_sell(300_000, 3, 0, 3)
    assert abs(result - 334_914) < 1.00


def test_exit_sell_deducts_remaining_balance():
    # Higher balance = lower net proceeds
    low_balance = calculate_exit_sell(300_000, 3, 100_000, 3)
    high_balance = calculate_exit_sell(300_000, 3, 200_000, 3)
    assert low_balance > high_balance
    assert abs(high_balance - low_balance - 100_000) < 0.01


def test_exit_sell_can_be_negative():
    # Underwater: balance > appreciated value − fees → negative return
    result = calculate_exit_sell(300_000, 0, 400_000, 3)
    assert result < 0


def test_exit_sell_doc_stamp_applied_to_appreciated_value():
    # FL doc stamp is on the appreciated value, not original price
    # price=200K, 50% appreciation → sale price ≈ $200K * (1.5)^(1/5*5) = hard to compute
    # Use zero appreciation for clean verification:
    # doc_stamp = price * 0.007
    result_zero_fees = calculate_exit_sell(200_000, 0, 0, 0)
    expected = 200_000 - (200_000 * 0.007)
    assert abs(result_zero_fees - expected) < 0.01


# ── calculate_exit_rent_out (Story 1.6) ──────────────────────────────────────

def test_exit_rent_out_positive_cashflow():
    # Income $2,000, 5% vacancy, 10% mgmt, $1,000 carrying costs, $350K appreciated, $270K balance
    # effective = 2000 * 0.95 = 1900; net_income = 1900 * 0.90 = 1710
    # monthly_net = 1710 - 1000 = 710; cumulative = 710 * 60 = 42,600
    # equity = 350_000 - 270_000 = 80,000
    # total = 42,600 + 80,000 = 122,600
    result = calculate_exit_rent_out(2_000, 5, 10, 1_000, 350_000, 270_000)
    assert abs(result - 122_600) < 1.00


def test_exit_rent_out_negative_cashflow_offset_by_equity():
    # Landlording at a loss but equity wins
    # $2K income, 0% vacancy, 0% mgmt, $2,500 carrying → net = -$500/month → -$30K over 60
    # Equity = 350_000 - 270_000 = 80,000; total = 50,000
    result = calculate_exit_rent_out(2_000, 0, 0, 2_500, 350_000, 270_000)
    assert abs(result - 50_000) < 1.00


def test_exit_rent_out_zero_vacancy_zero_mgmt():
    # Full gross income kept, simple check
    # income=1_000, 0 vacancy, 0 mgmt, 0 carrying, appreciated=200_000, balance=150_000
    # cumulative = 1_000 * 60 = 60_000; equity = 50_000; total = 110_000
    result = calculate_exit_rent_out(1_000, 0, 0, 0, 200_000, 150_000)
    assert abs(result - 110_000) < 1.00


def test_exit_rent_out_equity_component():
    # Isolate equity: zero income, zero costs → result equals equity alone
    result = calculate_exit_rent_out(0, 0, 0, 0, 300_000, 200_000)
    assert abs(result - 100_000) < 0.01


def test_exit_rent_out_vacancy_reduces_income():
    # Higher vacancy → lower result
    low_vacancy = calculate_exit_rent_out(2_000, 5, 0, 1_000, 300_000, 200_000)
    high_vacancy = calculate_exit_rent_out(2_000, 20, 0, 1_000, 300_000, 200_000)
    assert low_vacancy > high_vacancy


# ── calculate_exit_continue_renting (Story 1.6) ──────────────────────────────

def test_exit_continue_renting_returns_last_value():
    portfolio = [100 * i for i in range(1, 61)]  # [100, 200, ..., 6000]
    result = calculate_exit_continue_renting(portfolio)
    assert result == 6_000


def test_exit_continue_renting_uses_calculate_investment_portfolio():
    # Integration: portfolio from Story 1.5 function feeds directly in
    portfolio = calculate_investment_portfolio(0, 1_000, 0, 60)
    result = calculate_exit_continue_renting(portfolio)
    assert abs(result - 60_000) < 0.01


def test_exit_continue_renting_with_growth():
    # With 7% return, final value exceeds simple sum of contributions
    portfolio = calculate_investment_portfolio(15_000, 0, 7, 60)
    result = calculate_exit_continue_renting(portfolio)
    assert result > 15_000  # grew beyond initial capital
```

### Pre-Computed Reference Values

| Function | Inputs | Expected Output |
|---|---|---|
| `calculate_exit_sell` | $300K, 3% appr, $0 balance, 3% commission | ~$334,914 |
| `calculate_exit_sell` | $300K, 0% appr, $0 balance, 0% commission | ~$297,900 ($300K − doc stamp $2,100) |
| `calculate_exit_rent_out` | $2K income, 5% vac, 10% mgmt, $1K carrying, $350K, $270K | $122,600 |
| `calculate_exit_rent_out` | $0 income, 0 costs, $300K, $200K | $100,000 (equity only) |
| `calculate_exit_continue_renting` | output of `calculate_investment_portfolio(0, 1000, 0, 60)` | $60,000 |

**Florida documentary stamp tax breakdown for $300K → $347,782 sale:**
- Rate: $0.70 per $100 = 0.70%
- Tax: $347,782 × 0.007 = $2,434.47

### Story Learnings from 1.1–1.5

- **Use `python` not `python3`** on this Windows machine
- **Run pytest as:** `.venv\Scripts\pytest.exe tests/ -v`
- **APPEND to existing files** — never overwrite
- **Update the import block at top** of `test_calculations.py` — it's a multi-line block
- **ARCH-3 invariant:** no streamlit import — verify after every change
- **RED phase first:** confirm tests fail before implementing

### What This Story Does NOT Do

- Does NOT compute break-even month (Story 2.5)
- Does NOT compute the renter's monthly contribution (that's Story 2.3's job — it subtracts buying costs from renting costs and passes the result to `calculate_investment_portfolio`)
- Does NOT implement the monthly cost breakdown display (Epic 2)
- Does NOT change `defaults.py`, `app.py`, or `url_state.py`
- Does NOT compute the landlord scenario's monthly carrying costs — those come from amortization + property tax + HOA + insurance, assembled in Story 2.3

### Cross-Story Context

| Story | Uses output of 1.6 |
|---|---|
| 2.3 | All 3 exit functions called per scenario on every slider change; `appreciated_value` computed once from `calculate_exit_sell`'s formula and shared with `calculate_exit_rent_out` |
| 2.5 | Break-even month derived by comparing renting cost vs. buying cost month-by-month |
| 2.6 | All 3 exit values populate the 3×4 exit paths table |

### References

- [Source: epics.md — Story 1.6 Acceptance Criteria, FR19, FR20, FR21, NFR7]
- [Source: prd.md — FR19 (sell: appreciated value − commission − doc stamp − balance), FR20 (rent-out: net cashflow + equity), FR21 (continue renting: portfolio at month 60)]
- [Source: architecture.md — ARCH-3 invariant]
- [Source: defaults.py — APPRECIATION_RATE=3.0, REALTOR_COMMISSION_PCT=3.0, RENTAL_INCOME_MONTHLY=2_000, VACANCY_RATE=5.0, PROPERTY_MGMT_FEE_PCT=10.0]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- RED phase confirmed: ImportError on all three exit functions before implementation.
- GREEN phase: 52/53 passed after initial implementation; `test_exit_sell_deducts_remaining_balance` failed due to operand order in assertion (`high_balance - low_balance` should be `low_balance - high_balance` — the implementation is correct, the test had a sign error).
- Fixed test assertion; 53/53 passed.
- ARCH-3 check: PASS.

### Completion Notes List

- Appended `FL_DOC_STAMP_RATE = 0.007` — Florida documentary stamp tax constant.
- Appended `calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct)`: 5-year appreciation compounding, then deducts realtor fee, doc stamp, and remaining balance. All deductions applied to appreciated value except remaining_balance.
- Appended `calculate_exit_rent_out(monthly_rental_income, vacancy_rate_pct, mgmt_fee_pct, monthly_carrying_costs, appreciated_value, remaining_balance)`: 6-parameter design (deviation from epics 5-param spec — `appreciated_value` added as required for equity computation). Chains vacancy → mgmt fee → carrying cost deductions, then adds home equity.
- Appended `calculate_exit_continue_renting(portfolio_values)`: one-liner returning `portfolio_values[-1]`.
- Updated import block in `tests/test_calculations.py` to include all three new functions.
- Appended 14 new tests (6 for exit_sell, 5 for exit_rent_out, 3 for exit_continue_renting); 53 total, all GREEN.
- ARCH-3 invariant maintained.

### File List

- `calculations.py` (modified — appended FL_DOC_STAMP_RATE, calculate_exit_sell, calculate_exit_rent_out, calculate_exit_continue_renting)
- `tests/test_calculations.py` (modified — updated import line, appended 14 new tests)

## Change Log

- 2026-05-23: Implemented Story 1.6 — year-5 exit path calculations (sell, rent-out, continue renting); 53/53 tests pass.
