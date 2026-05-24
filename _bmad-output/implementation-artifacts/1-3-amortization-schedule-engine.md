# Story 1.3: Amortization Schedule Engine

Status: done

## Story

As a developer,
I want `calculations.py` to produce a verified 60-month amortization schedule for any down payment scenario,
So that all monthly cost and equity figures are based on accurate, testable mortgage math.

## Acceptance Criteria

1. **Given** a home purchase price, down payment %, and annual interest rate, **When** `calculate_amortization_schedule(price, down_pct, annual_rate)` is called, **Then** it returns a list of exactly 60 dicts, each containing keys: `month`, `principal`, `interest`, `balance`, `pmi`.
2. **Given** a $300,000 home at 5% down and 6.5% rate, **When** the schedule is computed, **Then** month 1 interest is within $1.00 of $1,543.75 and month 1 balance is within $1.00 of $284,742.25 (NFR5).
3. **Given** a $300,000 home at 20% down and 6.5% rate, **When** the schedule is computed, **Then** month 1 has PMI > 0, and some month before month 60 has PMI = 0 (cancellation fires at correct threshold).
4. **Given** any schedule, **Then** the balance decreases every month, and month numbers run sequentially from 1 to 60.
5. **Given** any month where `balance > 78% of original purchase price`, **Then** `pmi > 0`; **Given** the first month where `balance ≤ 78% of original purchase price`, **Then** `pmi = 0` for that month and all subsequent months (NFR6).
6. **Given** `calculations.py` after this story, **Then** `grep "import streamlit" calculations.py` returns nothing (ARCH-3 maintained).
7. **Given** `pytest` is run from the project root, **Then** all tests in `tests/test_calculations.py` pass.

## Tasks / Subtasks

- [x] **Task 1: Install pytest and update requirements.txt** (AC: 7)
  - [x] Run: `pip install pytest`
  - [x] Regenerate requirements.txt **BOM-free** — use the exact command from Dev Notes
  - [x] Verify: `pytest --version` shows a version (no error)

- [x] **Task 2: Create test file with FAILING tests first** (AC: 1–7)
  - [x] Create directory `tests/` at project root
  - [x] Create empty `tests/__init__.py`
  - [x] Create `tests/test_calculations.py` with all tests from Dev Notes
  - [x] Run `pytest tests/` — confirm tests FAIL (function doesn't exist yet)

- [x] **Task 3: Implement `calculate_amortization_schedule` in `calculations.py`** (AC: 1–6)
  - [x] Replace the stub docstring with the full module docstring + `PMI_ANNUAL_RATE` constant + the function — see Dev Notes for exact spec
  - [x] Function must return a list of 60 dicts with keys: `month`, `principal`, `interest`, `balance`, `pmi`
  - [x] Use the standard amortization formula from Dev Notes — do NOT approximate
  - [x] Apply PMI to original loan amount at `PMI_ANNUAL_RATE` — stops permanently at first month `balance ≤ 0.78 * price`
  - [x] Accept percentages as human-readable floats: `down_pct=5` means 5%, `annual_rate=6.5` means 6.5%

- [x] **Task 4: Run tests and verify all pass** (AC: 1–7)
  - [x] Run: `pytest tests/ -v` — all tests must be GREEN
  - [x] Run ARCH-3 check: `python -c "import ast, sys; tree = ast.parse(open('calculations.py').read()); sl = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and any('streamlit' in (getattr(n,'module','') or '') or any('streamlit' in a.name for a in getattr(n,'names',[])) for _ in [n])]; print('ARCH-3 PASS' if not sl else 'FAIL')"`

### Review Findings

- [x] [Review][Decision] PMI origination threshold wrong: 20% down (80% LTV) should be PMI-free from day 1 per Homeowners Protection Act, but code uses the 78% cancellation threshold as the only rule — charging ~27 months of PMI to 20%-down buyers who wouldn't owe it in reality. **FIXED:** Changed `pmi_cancelled = False` → `pmi_cancelled = (loan / price) <= 0.80`. Updated tests to reflect: 20% down has zero PMI all 60 months; added `test_pmi_applies_at_15pct_down` to cover the >80% LTV case. [`calculations.py:22`]

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  calculations.py       ← UPDATE (currently docstring stub)
  tests/
    __init__.py         ← NEW (empty)
    test_calculations.py ← NEW
  requirements.txt      ← UPDATE (add pytest)
```

### Installing pytest — BOM-Free Requirements Update

```powershell
# With venv active:
& ".venv\Scripts\pip.exe" install pytest

# Regenerate requirements.txt WITHOUT BOM (learned from Story 1.1 review):
$content = & ".venv\Scripts\pip.exe" freeze
[System.IO.File]::WriteAllLines(
    "C:\Users\criss\Documents\Home Buying\requirements.txt",
    $content,
    [System.Text.UTF8Encoding]::new($false)
)
```

### Mathematical Formula — Standard 30-Year Amortization

```
loan = price * (1 - down_pct / 100)
r    = annual_rate / 100 / 12        # monthly interest rate
n    = 360                            # total payments (30 years)

monthly_payment = loan * r * (1 + r)**n / ((1 + r)**n - 1)
```

Each month (1–60):
```
interest  = current_balance * r
principal = monthly_payment - interest
balance   = current_balance - principal
```

**Edge case:** If `annual_rate == 0`, use `monthly_payment = loan / 360` and `interest = 0`.

### PMI Logic

```python
PMI_ANNUAL_RATE = 0.008  # 0.8% of original loan amount per year (internal constant)

pmi_threshold = 0.78 * price          # e.g., $234,000 for a $300K home
pmi_cancelled = False
pmi_monthly   = loan * PMI_ANNUAL_RATE / 12  # fixed dollar amount per month

# Each month:
if pmi_cancelled or balance <= pmi_threshold:
    pmi_cancelled = True
    pmi = 0.0
else:
    pmi = pmi_monthly
```

**Critical:** Once `pmi_cancelled = True`, PMI stays 0 for all remaining months — even if balance somehow rose (it won't, but the flag prevents any re-activation). This matches the HPA one-way cancellation rule (NFR6).

### Function Signature and Return Type

```python
def calculate_amortization_schedule(
    price: float,       # purchase price in dollars (e.g., 300_000)
    down_pct: float,    # down payment percent as human-readable (e.g., 5 = 5%)
    annual_rate: float  # annual interest rate as human-readable (e.g., 6.5 = 6.5%)
) -> list[dict]:
    """
    Returns a list of 60 monthly amortization records.
    Each record: {month, principal, interest, balance, pmi}
    All values are floats in dollars. month is int (1-60).
    """
```

### Complete `calculations.py` After This Story

```python
"""
Financial calculation engine for the Miami Home Buying Decision Tool.

Pure Python only — no Streamlit imports. This module is independently
unit-testable against a reference spreadsheet.
"""

PMI_ANNUAL_RATE = 0.008  # 0.8% of original loan amount per year


def calculate_amortization_schedule(price, down_pct, annual_rate):
    """Returns list of 60 monthly records: month, principal, interest, balance, pmi."""
    loan = price * (1 - down_pct / 100)
    r = annual_rate / 100 / 12
    n = 360  # 30-year mortgage

    if r == 0:
        monthly_payment = loan / n
    else:
        monthly_payment = loan * r * (1 + r) ** n / ((1 + r) ** n - 1)

    pmi_threshold = 0.78 * price
    pmi_monthly = loan * PMI_ANNUAL_RATE / 12
    pmi_cancelled = False

    balance = loan
    schedule = []

    for month in range(1, 61):
        interest = balance * r
        principal = monthly_payment - interest
        balance -= principal

        if pmi_cancelled or balance <= pmi_threshold:
            pmi_cancelled = True
            pmi = 0.0
        else:
            pmi = pmi_monthly

        schedule.append({
            "month": month,
            "principal": principal,
            "interest": interest,
            "balance": balance,
            "pmi": pmi,
        })

    return schedule
```

### Test File — `tests/test_calculations.py`

```python
import pytest
from calculations import calculate_amortization_schedule


# ── Structure ────────────────────────────────────────────────────────────────

def test_returns_60_months():
    assert len(calculate_amortization_schedule(300_000, 5, 6.5)) == 60


def test_record_has_required_keys():
    record = calculate_amortization_schedule(300_000, 5, 6.5)[0]
    assert set(record.keys()) >= {"month", "principal", "interest", "balance", "pmi"}


def test_month_numbers_sequential():
    schedule = calculate_amortization_schedule(300_000, 5, 6.5)
    for i, record in enumerate(schedule):
        assert record["month"] == i + 1


def test_balance_strictly_decreasing():
    schedule = calculate_amortization_schedule(300_000, 10, 6.5)
    for i in range(1, len(schedule)):
        assert schedule[i]["balance"] < schedule[i - 1]["balance"]


# ── Financial Accuracy (NFR5: within $1/month of reference) ─────────────────

def test_month1_interest_5pct_down():
    # $285,000 loan * (6.5%/12) = $1,543.75
    record = calculate_amortization_schedule(300_000, 5, 6.5)[0]
    assert abs(record["interest"] - 1543.75) < 1.00


def test_month1_balance_5pct_down():
    # Reference: ~$284,742
    record = calculate_amortization_schedule(300_000, 5, 6.5)[0]
    assert abs(record["balance"] - 284_742) < 1.00


def test_month1_interest_20pct_down():
    # $240,000 loan * (6.5%/12) = $1,300.00
    record = calculate_amortization_schedule(300_000, 20, 6.5)[0]
    assert abs(record["interest"] - 1300.00) < 1.00


def test_principal_plus_interest_equals_payment():
    # P + I must equal the fixed monthly payment every month
    schedule = calculate_amortization_schedule(300_000, 10, 6.5)
    payment = schedule[0]["principal"] + schedule[0]["interest"]
    for record in schedule:
        assert abs((record["principal"] + record["interest"]) - payment) < 0.02


# ── PMI Logic (NFR6) ─────────────────────────────────────────────────────────

def test_pmi_applies_all_60_months_at_5pct_down():
    # 5% down: initial balance $285K, never reaches $234K (78% of $300K) in 5 years
    schedule = calculate_amortization_schedule(300_000, 5, 6.5)
    assert all(record["pmi"] > 0 for record in schedule)


def test_pmi_applies_initially_at_20pct_down():
    # 20% down: initial balance $240K > $234K threshold → PMI applies month 1
    record = calculate_amortization_schedule(300_000, 20, 6.5)[0]
    assert record["pmi"] > 0


def test_pmi_cancelled_by_month_60_at_20pct_down():
    # 20% down: PMI should cancel around month 27
    record = calculate_amortization_schedule(300_000, 20, 6.5)[-1]
    assert record["pmi"] == 0.0


def test_pmi_cancels_around_month_27_at_20pct_down():
    schedule = calculate_amortization_schedule(300_000, 20, 6.5)
    cancel_month = next(r["month"] for r in schedule if r["pmi"] == 0.0)
    # Tolerance: allow month 24–32 (formula precision variation)
    assert 24 <= cancel_month <= 32


def test_pmi_stays_cancelled_once_triggered():
    # Once PMI hits 0, it must remain 0 for all subsequent months
    schedule = calculate_amortization_schedule(300_000, 20, 6.5)
    pmi_values = [r["pmi"] for r in schedule]
    first_zero = next((i for i, v in enumerate(pmi_values) if v == 0), None)
    if first_zero is not None:
        assert all(v == 0 for v in pmi_values[first_zero:])


def test_no_pmi_at_20pct_down_after_loan_paid_past_threshold():
    # Sanity: final balance for 20% down must be well below 234K
    final = calculate_amortization_schedule(300_000, 20, 6.5)[-1]
    assert final["balance"] < 234_000
```

### Pre-Computed Reference Values

Use these to validate your implementation against independent sources (Excel PMT/IPMT, online amortization calculators):

| Scenario | Loan | Monthly Payment | Month 1 Interest | Month 1 Principal | Month 1 Balance |
|---|---|---|---|---|---|
| $300K, 5% down, 6.5% | $285,000 | ~$1,801.50 | $1,543.75 | ~$257.75 | ~$284,742 |
| $300K, 20% down, 6.5% | $240,000 | ~$1,516.81 | $1,300.00 | ~$216.81 | ~$239,783 |

**PMI cancellation for 20% down:** Threshold = 78% × $300,000 = $234,000. Balance crosses below ~month 27.

**Excel verification commands:**
- Monthly payment: `=PMT(6.5%/12, 360, -285000)` → should return ~$1,801.50
- Month 1 interest: `=IPMT(6.5%/12, 1, 360, -285000)` → should return ~$1,543.75
- Month 1 principal: `=PPMT(6.5%/12, 1, 360, -285000)` → should return ~$257.75

### Story Learnings from 1.1 & 1.2

- **Use `python` not `python3`** on this Windows machine
- **Venv:** `.venv\Scripts\Activate.ps1` or use full path `.venv\Scripts\python.exe`
- **BOM-free requirements.txt:** Use `[System.IO.File]::WriteAllLines` with `UTF8Encoding::new($false)` — not PowerShell `>` redirect or `Out-File -Encoding utf8`
- **Bash tool works better than PowerShell** for running Python verification one-liners
- **ARCH-3 invariant:** `calculations.py` must never import streamlit — verify after every change

### What This Story Does NOT Do

- Does NOT implement property tax, HOA, insurance calculations (Story 1.4)
- Does NOT implement investment portfolio (Story 1.5)
- Does NOT implement exit path calculations (Story 1.6)
- Does NOT wire calculations into the UI (Epic 2)
- Does NOT add PMI rate as a user-configurable slider — it is an internal constant
- Does NOT change `defaults.py`, `app.py`, or `url_state.py`

### Cross-Story Context

| Story | Uses output of 1.3 |
|---|---|
| 1.4 | `calculate_amortization_schedule` result feeds property tax and upfront cash calc |
| 1.6 | Schedule's `balance[-1]` used for exit sell and rent-out equity calculations |
| 2.3 | Called 4× (for 5%, 10%, 15%, 20% down) on every slider change |

### References

- [Source: epics.md — Story 1.3 Acceptance Criteria]
- [Source: prd.md — NFR5, NFR6, FR13, FR14]
- [Source: architecture.md — ARCH-3 invariant]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- pytest already installed in venv (9.0.3); Task 1 was primarily a requirements.txt update.
- RED phase confirmed: ImportError on `calculate_amortization_schedule` before implementation.
- GREEN phase: all 14 tests passed on first run after implementation.
- ARCH-3 check passed: no streamlit import detected in calculations.py.

### Completion Notes List

- Implemented `calculate_amortization_schedule(price, down_pct, annual_rate)` returning 60 monthly dicts.
- Standard 30-year amortization formula with edge case for zero interest rate.
- PMI at 0.8% annual of original loan, cancelled permanently once balance ≤ 78% of purchase price.
- 14 pytest tests cover structure, financial accuracy (NFR5 within $1/month), and PMI logic (NFR6).
- All 14 tests GREEN; ARCH-3 invariant maintained (no streamlit import).

### File List

- `calculations.py` (modified — added PMI_ANNUAL_RATE constant and calculate_amortization_schedule function)
- `tests/__init__.py` (new — empty)
- `tests/test_calculations.py` (new — 14 pytest tests covering all ACs)
- `requirements.txt` (modified — added pytest==9.0.3, BOM-free regeneration)

## Change Log

- 2026-05-23: Implemented Story 1.3 — amortization schedule engine with PMI logic; 14 tests all pass.
