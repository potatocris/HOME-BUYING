# Story 1.4: Florida Cost & Upfront Cash Engine

Status: done

## Story

As a developer,
I want `calculations.py` to correctly model Florida-specific property costs and total upfront cash requirements,
So that the calculator reflects Miami's real cost structure.

## Acceptance Criteria

1. **Given** purchase price, property tax rate, and a month number (1–60), **When** `calculate_monthly_property_tax(price, tax_rate_pct, month)` is called, **Then** months 1–12 return `price * (tax_rate_pct / 100) / 12` and months 13–60 return `(price - 50_000) * (tax_rate_pct / 100) / 12` (Florida homestead exemption, FR15).
2. **Given** a $300K home at 1.3% tax rate, **When** `calculate_monthly_property_tax` is called for month 1, **Then** the result is within $0.01 of $325.00.
3. **Given** a $300K home at 1.3% tax rate, **When** `calculate_monthly_property_tax` is called for month 13, **Then** the result is within $0.01 of $270.83 (homestead applied: $250K × 1.3% / 12).
4. **Given** purchase price, down payment %, closing cost %, and furniture budget, **When** `calculate_upfront_cash(price, down_pct, closing_pct, furniture)` is called, **Then** it returns exactly: `(price * down_pct / 100) + (price * closing_pct / 100) + furniture` (FR16).
5. **Given** a $300K home, 5% down, 3.5% closing, $15K furniture, **When** `calculate_upfront_cash` is called, **Then** the result is within $0.01 of $40,500.
6. **Given** `calculations.py` after this story, **Then** `grep "import streamlit" calculations.py` returns nothing (ARCH-3 maintained).
7. **Given** `pytest` is run from the project root, **Then** ALL tests in `tests/test_calculations.py` pass — including the 14 from Story 1.3 (no regressions).

## Tasks / Subtasks

- [x] **Task 1: Add FAILING tests to `tests/test_calculations.py`** (AC: 1–5, 7)
  - [x] Open the existing `tests/test_calculations.py` — **append** new tests, do NOT replace existing ones
  - [x] Add tests for `calculate_monthly_property_tax` (see Dev Notes for exact tests)
  - [x] Add tests for `calculate_upfront_cash` (see Dev Notes for exact tests)
  - [x] Run `pytest tests/ -v` — confirm the new tests FAIL (ImportError or NameError), existing 14 still pass

- [x] **Task 2: Implement both functions in `calculations.py`** (AC: 1–5)
  - [x] **Append** to the existing `calculations.py` — do NOT overwrite the module docstring, `PMI_ANNUAL_RATE`, or `calculate_amortization_schedule`
  - [x] Add constant: `HOMESTEAD_EXEMPTION = 50_000` at module level (after PMI_ANNUAL_RATE)
  - [x] Implement `calculate_monthly_property_tax(price, tax_rate_pct, month)` — see Dev Notes for exact spec
  - [x] Implement `calculate_upfront_cash(price, down_pct, closing_pct, furniture)` — see Dev Notes for exact spec

- [x] **Task 3: Run all tests and verify** (AC: 6–7)
  - [x] Run: `pytest tests/ -v` — all tests (14 from 1.3 + new) must be GREEN
  - [x] Run ARCH-3 check: `python -c "import ast, sys; tree = ast.parse(open('calculations.py').read()); sl = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and any('streamlit' in (getattr(n,'module','') or '') or any('streamlit' in a.name for a in getattr(n,'names',[])) for _ in [n])]; print('ARCH-3 PASS' if not sl else 'FAIL')"`

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  calculations.py           ← UPDATE (append two new functions + HOMESTEAD_EXEMPTION)
  tests/
    test_calculations.py    ← UPDATE (append new tests — do NOT replace existing)
```

**CRITICAL: Both files already exist from Stories 1.1–1.3. APPEND only — never overwrite.**

### Current State of `calculations.py`

After Story 1.3, `calculations.py` contains:
```python
"""..."""                         # module docstring — DO NOT TOUCH
PMI_ANNUAL_RATE = 0.008           # constant — DO NOT TOUCH
calculate_amortization_schedule() # function — DO NOT TOUCH
```

Append at the bottom:
```python
HOMESTEAD_EXEMPTION = 50_000  # Florida statutory exemption (dollars, year 2+)


def calculate_monthly_property_tax(price, tax_rate_pct, month):
    """Returns monthly property tax in dollars for the given month (1-60)."""
    assessed = price if month <= 12 else price - HOMESTEAD_EXEMPTION
    return assessed * (tax_rate_pct / 100) / 12


def calculate_upfront_cash(price, down_pct, closing_pct, furniture):
    """Returns total upfront cash: down payment + closing costs + furniture."""
    down_payment = price * (down_pct / 100)
    closing_costs = price * (closing_pct / 100)
    return down_payment + closing_costs + furniture
```

### Florida Homestead Exemption — Why It Works This Way

Florida Statutes §196.031 grants a $50,000 reduction to assessed value for a primary residence. The exemption requires the buyer to apply by March 1 of the year after purchase. For simplicity this tool models it as: full tax in year 1 (months 1–12), exemption in years 2–5 (months 13–60). The $50K is subtracted from the assessed value **before** applying the tax rate — not from the tax bill itself.

Edge case: if `price ≤ $50,000`, the exemption would produce zero or negative assessed value. This is impossible for Miami real estate at any realistic price, so no guard is needed.

### Mathematical Formula

**Property tax (months 1–12):**
```
assessed    = price
annual_tax  = assessed * (tax_rate_pct / 100)
monthly_tax = annual_tax / 12
```

**Property tax (months 13–60, homestead applied):**
```
assessed    = price - 50_000
annual_tax  = assessed * (tax_rate_pct / 100)
monthly_tax = annual_tax / 12
```

**Upfront cash:**
```
down_payment   = price * (down_pct / 100)
closing_costs  = price * (closing_pct / 100)
upfront_cash   = down_payment + closing_costs + furniture
```

### Function Signatures

```python
def calculate_monthly_property_tax(
    price: float,       # purchase price in dollars (e.g., 300_000)
    tax_rate_pct: float, # annual property tax rate as human-readable % (e.g., 1.3 = 1.3%)
    month: int          # month number 1-60
) -> float:
    """Returns monthly property tax in dollars for the given month (1-60)."""

def calculate_upfront_cash(
    price: float,       # purchase price in dollars (e.g., 300_000)
    down_pct: float,    # down payment percent as human-readable (e.g., 5 = 5%)
    closing_pct: float, # closing cost percent as human-readable (e.g., 3.5 = 3.5%)
    furniture: float    # furniture and improvements budget in dollars (e.g., 15_000)
) -> float:
    """Returns total upfront cash: down payment + closing costs + furniture."""
```

### Tests to Append to `tests/test_calculations.py`

```python
from calculations import calculate_monthly_property_tax, calculate_upfront_cash


# ── calculate_monthly_property_tax ───────────────────────────────────────────

def test_property_tax_month1_no_exemption():
    # $300K * 1.3% / 12 = $325.00
    result = calculate_monthly_property_tax(300_000, 1.3, 1)
    assert abs(result - 325.00) < 0.01


def test_property_tax_month12_no_exemption():
    # Month 12 is still year 1 — no exemption
    result = calculate_monthly_property_tax(300_000, 1.3, 12)
    assert abs(result - 325.00) < 0.01


def test_property_tax_month13_with_exemption():
    # ($300K - $50K) * 1.3% / 12 = $250K * 0.013 / 12 = $270.83
    result = calculate_monthly_property_tax(300_000, 1.3, 13)
    assert abs(result - 270.83) < 0.01


def test_property_tax_month60_with_exemption():
    # Month 60 still uses homestead
    result = calculate_monthly_property_tax(300_000, 1.3, 60)
    assert abs(result - 270.83) < 0.01


def test_property_tax_exemption_boundary():
    # Month 12 (no exemption) must be greater than month 13 (exemption)
    tax_year1 = calculate_monthly_property_tax(300_000, 1.3, 12)
    tax_year2 = calculate_monthly_property_tax(300_000, 1.3, 13)
    assert tax_year1 > tax_year2


def test_property_tax_zero_rate():
    # Edge case: zero tax rate → $0
    assert calculate_monthly_property_tax(300_000, 0, 1) == 0.0
    assert calculate_monthly_property_tax(300_000, 0, 13) == 0.0


# ── calculate_upfront_cash ───────────────────────────────────────────────────

def test_upfront_cash_5pct_down():
    # 5% down: $15K + closing $10.5K + furniture $15K = $40,500
    result = calculate_upfront_cash(300_000, 5, 3.5, 15_000)
    assert abs(result - 40_500) < 0.01


def test_upfront_cash_10pct_down():
    # 10% down: $30K + $10.5K + $15K = $55,500
    result = calculate_upfront_cash(300_000, 10, 3.5, 15_000)
    assert abs(result - 55_500) < 0.01


def test_upfront_cash_20pct_down():
    # 20% down: $60K + $10.5K + $15K = $85,500
    result = calculate_upfront_cash(300_000, 20, 3.5, 15_000)
    assert abs(result - 85_500) < 0.01


def test_upfront_cash_components():
    # Verify formula: down + closing + furniture, all independent
    result = calculate_upfront_cash(400_000, 10, 2.0, 20_000)
    expected = 40_000 + 8_000 + 20_000  # = $68,000
    assert abs(result - expected) < 0.01


def test_upfront_cash_zero_furniture():
    result = calculate_upfront_cash(300_000, 20, 3.5, 0)
    assert abs(result - 70_500) < 0.01  # $60K down + $10.5K closing
```

### Pre-Computed Reference Values

| Scenario | Month | Assessed Value | Annual Tax | Monthly Tax |
|---|---|---|---|---|
| $300K, 1.3% | 1–12 | $300,000 | $3,900 | $325.00 |
| $300K, 1.3% | 13–60 | $250,000 | $3,250 | $270.83 |

| Scenario | Down | Closing | Furniture | Upfront Cash |
|---|---|---|---|---|
| $300K, 5%, 3.5%, $15K | $15,000 | $10,500 | $15,000 | **$40,500** |
| $300K, 10%, 3.5%, $15K | $30,000 | $10,500 | $15,000 | **$55,500** |
| $300K, 15%, 3.5%, $15K | $45,000 | $10,500 | $15,000 | **$70,500** |
| $300K, 20%, 3.5%, $15K | $60,000 | $10,500 | $15,000 | **$85,500** |

### Story Learnings from 1.1–1.3

- **Use `python` not `python3`** on this Windows machine
- **Venv pytest:** Run as `.venv\Scripts\pytest.exe tests/ -v` — or just `pytest tests/ -v` with venv active
- **Bash tool works better than PowerShell** for running Python verification one-liners
- **ARCH-3 invariant:** `calculations.py` must never import streamlit — verify after every change
- **APPEND to existing files:** `calculations.py` and `tests/test_calculations.py` both exist — never overwrite
- **BOM-free requirements:** Not needed this story — no new pip installs required
- **RED phase first:** Always confirm tests fail before implementing

### What This Story Does NOT Do

- Does NOT change the property tax rate to be configurable by month — the rate is constant, only the assessed value changes
- Does NOT calculate HO-6 insurance (delivered separately as part of monthly cost display in Epic 2)
- Does NOT calculate HOA (passed through directly from slider in Epic 2)
- Does NOT implement investment portfolio compounding (Story 1.5)
- Does NOT touch `app.py`, `defaults.py`, or `url_state.py`

### Cross-Story Context

| Story | Uses output of 1.4 |
|---|---|
| 1.5 | `calculate_monthly_property_tax` is part of monthly carrying costs for rent-out exit |
| 1.6 | Monthly costs feed into exit path net worth reconciliation (NFR7) |
| 2.3 | Both functions called for all 4 down-payment scenarios on every slider change |
| 2.4 | `calculate_monthly_property_tax` result displayed as "Property Tax" line item per scenario |

### References

- [Source: epics.md — Story 1.4 Acceptance Criteria, FR15, FR16]
- [Source: prd.md — FR15 (homestead exemption), FR16 (upfront cash components)]
- [Source: architecture.md — ARCH-3 invariant]
- [Source: defaults.py — PROPERTY_TAX_RATE = 1.3, CLOSING_COST_PCT = 3.5, FURNITURE_BUDGET = 15_000]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- RED phase confirmed: ImportError on `calculate_monthly_property_tax` before implementation; existing 14 tests not affected.
- GREEN phase: all 25 tests passed on first run after appending functions.
- ARCH-3 check passed: no streamlit import detected in calculations.py.
- No new pip installs required — pytest already present from Story 1.3.

### Completion Notes List

- Appended `HOMESTEAD_EXEMPTION = 50_000` constant to `calculations.py`.
- Implemented `calculate_monthly_property_tax(price, tax_rate_pct, month)`: months 1–12 use full assessed value; months 13–60 subtract $50K homestead exemption before applying rate.
- Implemented `calculate_upfront_cash(price, down_pct, closing_pct, furniture)`: down payment + closing costs + furniture, all as human-readable % inputs.
- Appended 11 new tests to `tests/test_calculations.py` covering month boundaries (12/13), reference values, zero-rate edge case, and all 4 down scenarios for upfront cash.
- Total test suite: 25 tests, all GREEN. No regressions to Story 1.3.
- ARCH-3 invariant maintained.

### File List

- `calculations.py` (modified — appended HOMESTEAD_EXEMPTION, calculate_monthly_property_tax, calculate_upfront_cash)
- `tests/test_calculations.py` (modified — appended 11 new tests for Story 1.4 functions)

## Change Log

- 2026-05-23: Implemented Story 1.4 — Florida property tax with homestead exemption and upfront cash engine; 25/25 tests pass.
