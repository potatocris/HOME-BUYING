# Story 2.5: Rent vs Buy Two-Option Calculation Wiring

Status: done

## Story

As a user,
I want the tool to compute both paths — renting+investing and buying+investing — over the selected horizon,
so that the chart and table have accurate data to display.

## Acceptance Criteria

1. **Given** a selected down payment % and horizon (years), **When** the page renders, **Then** a full amortization schedule is computed over `horizon_years × 12` months.
2. **Given** the amortization schedule and slider inputs, **When** calculations run, **Then** the renter's total wealth per month = renter portfolio value, where the portfolio starts at `upfront_cash` and compounds monthly at `investment_return_rate`, adding `max(0, buying_cost_m − market_rent)` each month.
3. **Given** the same inputs, **When** calculations run, **Then** the buyer's total wealth per month = home equity + buyer side portfolio, where home equity = `appreciated_value_m − remaining_balance_m` and the buyer side portfolio starts at $0 and compounds monthly, adding `max(0, market_rent − buying_cost_m)` each month.
4. **Given** the per-month calculations, **When** any month is evaluated, **Then** `buying_cost_m` = P&I + PMI + HOA + property tax + insurance (using the real per-month values — PMI cancels correctly, property tax uses homestead from month 13+).
5. **Given** both monthly series, **When** calculations complete, **Then** `renter_annual` and `buyer_annual` are produced via `get_annual_snapshots()` — one value per complete year.
6. **Given** all four datasets, **Then** all computation is complete before any `st.*` display call.
7. **Given** all existing tests, **When** `python -m pytest tests/ -v` is run, **Then** all 99 tests pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Add DOWN_PCT and HORIZON_YEARS to `defaults.py` (AC: 1, 2, 3)**
  - [x] Add `DOWN_PCT = 20.0` under `# -- Scenario Inputs --` section (see exact placement in Dev Notes)
  - [x] Add `HORIZON_YEARS = 10` below DOWN_PCT (Story 2.6 uses this as timeline slider default)
  - [x] No other changes to `defaults.py`

- [x] **Task 2: Add Down Payment % slider to `app.py` sidebar (AC: 1)**
  - [x] Add `import calculations` at top of `app.py` (was removed in Story 2.4)
  - [x] Add `down_pct` slider to Essential Inputs section of sidebar, immediately after `home_price` slider (see exact spec in Dev Notes)
  - [x] Verify slider reads `value=defaults.DOWN_PCT`

- [x] **Task 3: Wire two-path calculation loop in `app.py` (AC: 1–6)**
  - [x] Add `horizon_years = defaults.HORIZON_YEARS` line after sidebar block (Story 2.6 replaces this single line with the timeline slider widget)
  - [x] Add `total_months = horizon_years * 12`
  - [x] Build the renter path loop (see exact code in Dev Notes): `renter_monthly` list (length = total_months), `buyer_surplus_list`
  - [x] Call `calculations.calculate_buyer_investment_portfolio(buyer_surplus_list, investment_return_rate)` → `buyer_portfolio`
  - [x] Build `buyer_monthly` list from home equity + buyer portfolio (see Dev Notes)
  - [x] Call `calculations.get_annual_snapshots()` on both monthly series → `renter_annual`, `buyer_annual`
  - [x] Ensure ALL computation precedes ANY `st.*` display call

- [x] **Task 4: Update main area placeholder (AC: 6)**
  - [x] Replace `st.info("Rent vs Buy comparison coming in Stories 2.5–2.8.")` with a debug confirmation display showing both final-year wealth figures (see Dev Notes for exact code)
  - [x] Keep `st.title("Miami Home Buying Decision Tool")`
  - [x] Story 2.6 replaces this placeholder with the headline + chart controls

- [x] **Task 5: Regression check (AC: 7)**
  - [x] Run `python -m pytest tests/ -v` — all 99 tests pass (99/99 in 0.10s)
  - [x] Verify `calculations.py`, `url_state.py`, `tests/` are untouched

- [x] **Task 6: Syntax and smoke check**
  - [x] AST parse clean for `app.py` and `defaults.py`
  - [x] Calculation invariants verified: renter_monthly=120, buyer_monthly=120, renter_annual=10, buyer_annual=10
  - [x] Miami defaults (20% down, 10yr): Renting year-10 → $240,604 | Buying year-10 → $199,712

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py          ← MODIFY (add down_pct slider, import calculations, add calculation loop)
  defaults.py     ← MODIFY (add DOWN_PCT, HORIZON_YEARS constants)
  calculations.py ← DO NOT TOUCH
  url_state.py    ← DO NOT TOUCH
  tests/          ← DO NOT TOUCH (99 tests must stay green)
  pages/          ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v` (or `.venv\Scripts\pytest.exe tests/ -v`)
- Activate venv in PowerShell: `.venv\Scripts\Activate.ps1`
- Use PowerShell tool for venv activation, not Bash tool

### Task 1 — Exact additions to `defaults.py`

Add this block after the `# -- Upfront Costs ---` section and before `# -- Special Assessment ---`:

```python
# -- Scenario Inputs -----------------------------------------------------------
DOWN_PCT = 20.0           # Default down payment % for rent-vs-buy main page (conventional, no PMI)
HORIZON_YEARS = 10        # Default comparison horizon (years); Story 2.6 uses as timeline slider default
```

Full defaults.py ordering after this change:
```
# -- Property --
HOME_PRICE, APPRECIATION_RATE, PROPERTY_TAX_RATE, HOA_MONTHLY, HO6_INSURANCE_ANNUAL
# -- Mortgage --
MORTGAGE_RATE, CLOSING_COST_PCT
# -- Renting / Opportunity Cost --
MARKET_RENT, INVESTMENT_RETURN_RATE
# -- Upfront Costs --
FURNITURE_BUDGET
# -- Scenario Inputs --         ← NEW SECTION
DOWN_PCT, HORIZON_YEARS
# -- Special Assessment --
SPECIAL_ASSESSMENT_AMOUNT, SPECIAL_ASSESSMENT_MONTH
# -- Landlord Scenario --
RENTAL_INCOME_MONTHLY, VACANCY_RATE, PROPERTY_MGMT_FEE_PCT
# -- Exit Costs --
REALTOR_COMMISSION_PCT
# -- Metadata --
DEFAULTS_LAST_UPDATED
```

### Task 2 — Down Payment % slider in `app.py`

Add immediately after `home_price` slider (after its closing paren) and before `mortgage_rate` slider:

```python
    down_pct = st.slider(
        "Down Payment (%)",
        min_value=3.0, max_value=30.0,
        value=defaults.DOWN_PCT, step=0.5,
        format="%.1f%%",
    )
```

Also restore `import calculations` at the top of `app.py` (was removed in Story 2.4):

```python
import streamlit as st
import defaults
import calculations
```

### Task 3 — Calculation loop (exact code for `app.py`)

Place this block immediately after the `with st.sidebar:` block closes (before main area title):

```python
# ── Rent vs Buy Two-Path Calculation ──────────────────────────────────────────
# Story 2.6 replaces the next line with the timeline slider widget.
horizon_years = defaults.HORIZON_YEARS
total_months  = horizon_years * 12

schedule    = calculations.calculate_amortization_schedule(
    home_price, down_pct, mortgage_rate, months=total_months
)
upfront_cash = calculations.calculate_upfront_cash(
    home_price, down_pct, closing_cost_pct, furniture_budget
)
monthly_rate = investment_return_rate / 100 / 12

# Pass 1: renter portfolio (variable contributions) + buyer surplus list
renter_balance    = upfront_cash
renter_monthly    = []
buyer_surplus_list = []

for month_idx, rec in enumerate(schedule):
    m        = month_idx + 1
    p_and_i  = rec["interest"] + rec["principal"]
    pmi_m    = rec["pmi"]
    tax_m    = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, m)
    ins_m    = ho6_insurance_annual / 12
    buying_cost_m = p_and_i + pmi_m + hoa_monthly + tax_m + ins_m

    renter_contribution = max(0.0, buying_cost_m - market_rent)
    renter_balance      = (renter_balance + renter_contribution) * (1 + monthly_rate)
    renter_monthly.append(renter_balance)

    buyer_surplus_list.append(max(0.0, market_rent - buying_cost_m))

# Buyer side portfolio: $0 start, grows from monthly surpluses
buyer_portfolio = calculations.calculate_buyer_investment_portfolio(
    buyer_surplus_list, investment_return_rate
)

# Pass 2: buyer total wealth = home equity + side portfolio
buyer_monthly = []
for month_idx, rec in enumerate(schedule):
    m                  = month_idx + 1
    appreciated_value_m = home_price * (1 + appreciation_rate / 100) ** (m / 12)
    home_equity_m      = appreciated_value_m - rec["balance"]
    buyer_monthly.append(home_equity_m + buyer_portfolio[month_idx])

# Annual snapshots: Story 2.7 (chart) and Story 2.8 (table) consume these
renter_annual = calculations.get_annual_snapshots(renter_monthly)
buyer_annual  = calculations.get_annual_snapshots(buyer_monthly)
```

### Task 4 — Main area debug display

Replace the old `st.info(...)` with:

```python
# ── Main area ─────────────────────────────────────────────────────────────────
# Story 2.6 replaces this placeholder with the headline + timeline slider.
# Story 2.7 adds the Plotly chart. Story 2.8 adds the annual table.
st.title("Miami Home Buying Decision Tool")
st.info(
    f"Calculations ready — {horizon_years}-year horizon, {down_pct:.1f}% down. "
    f"Year {horizon_years}: Renting → ${renter_annual[-1]:,.0f} | "
    f"Buying → ${buyer_annual[-1]:,.0f}. "
    f"Chart and headline coming in Stories 2.6–2.7."
)
```

### Why special assessment is excluded from `buying_cost_m`

The sprint change proposal lists buying_cost_m = "P&I + PMI + HOA + tax + insurance" — five components only. Special assessment is excluded, consistent with Story 2.3's established pattern (`recurring_m1 = total_m1 - special_m1`). The design treats special assessment as a one-time lump-sum outside the recurring cost model. The deferred-work.md already documents this as an accepted simplification.

### The `horizon_years` variable name pattern (critical for Story 2.6)

Story 2.6 adds the timeline slider. When it does, it will replace this single line:
```python
horizon_years = defaults.HORIZON_YEARS
```
with:
```python
    horizon_years = st.select_slider("Comparison Horizon (years)", options=[5, 10, 15, 20, 25, 30], value=defaults.HORIZON_YEARS)
```
(moved inside the `with st.sidebar:` block). Everything else in the calculation loop stays identical. This makes Story 2.6's diff minimal.

### Calculation model summary

| Path | Starting capital | Monthly contribution | Final wealth |
|---|---|---|---|
| Renter | `upfront_cash` | `max(0, buying_cost_m − rent)` | `renter_monthly[-1]` |
| Buyer | $0 (side portfolio) | `max(0, rent − buying_cost_m)` | `home_equity_m + buyer_portfolio[-1]` |

**Renter logic:** If buying is more expensive than renting, the renter invests the difference. Starts with all the capital they didn't spend on a down payment.

**Buyer logic:** If renting would have been more expensive, the buyer invests that difference. Starts with $0 in the side portfolio (they spent their capital on the purchase). Home equity builds from appreciation + principal paydown.

### `buying_cost_m` month-by-month changes

- **PMI:** Cancels automatically when `loan_balance ≤ 78% of price`. At 20% down (default), PMI is $0 from day one. At 5–15% down, PMI cancels mid-schedule.
- **Property tax:** Months 1–12 use full assessed value; months 13+ apply $50,000 Florida homestead exemption (tax drops ~$54/mo at default 1.3% rate).
- **P&I:** Constant over the horizon (30-year fixed payment formula).

These real per-month values are what makes this model more accurate than the fixed month-1 approach used in the 4-scenario page.

### Testing approach

No new unit tests for this story. All sub-computations use already-tested functions from `calculations.py`:
- `calculate_amortization_schedule` — 12 tests covering months parameter, balances, PMI
- `calculate_monthly_property_tax` — 6 tests covering homestead exemption
- `calculate_upfront_cash` — 5 tests
- `calculate_buyer_investment_portfolio` — 10 tests covering variable surpluses
- `get_annual_snapshots` — 6 tests covering lengths and indices

Validation gates:
1. All 99 existing tests pass (no regressions)
2. `ast.parse` clean on `app.py` and `defaults.py`
3. Manual smoke test: app loads, down payment slider visible, debug info shows non-zero wealth figures

### Current state of `app.py` (Story 2.4 output)

```python
import streamlit as st
import defaults
# (import calculations was removed in Story 2.4 — restore it in Task 2)

st.set_page_config(...)
with st.sidebar:
    st.subheader("Essential Inputs")
    st.caption("Miami defaults loaded")
    home_price = st.slider(...)          # ← add down_pct slider after this
    mortgage_rate = st.slider(...)
    # ... 14 more sliders ...

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")
st.info("Rent vs Buy comparison coming in Stories 2.5–2.8.")   # ← replace this
```

### Cross-story context

| Story | Uses output of 2.5 |
|---|---|
| 2.6 | Replaces `horizon_years = defaults.HORIZON_YEARS` with timeline slider; adds headline above chart |
| 2.7 | Plotly line chart consumes `renter_monthly`, `buyer_monthly` (or annual snapshots for smoother chart) |
| 2.8 | Annual breakdown table consumes `renter_annual`, `buyer_annual` |
| 2.9 | URL state adds `dp` (single down payment %) and `yr` (horizon years) to param set |

### What `renter_annual` and `buyer_annual` contain

Given `HORIZON_YEARS = 10` (default):
- `total_months = 120`
- `renter_monthly` = 120 values (monthly renter wealth)
- `buyer_monthly` = 120 values (monthly buyer total wealth)
- `renter_annual` = 10 values (wealth at months 12, 24, 36, 48, 60, 72, 84, 96, 108, 120)
- `buyer_annual` = 10 values (same months)

Stories 2.7 and 2.8 use `renter_annual` and `buyer_annual` for display.

### Review Findings

- [x] [Review][Defer] `renter_annual[-1]` / `buyer_annual[-1]` will crash if annual list is empty — Story 2.6 must set timeline slider min ≥ 1 year (5 in practice) or add a guard before `st.info` [app.py display block] — deferred, pre-existing trap; actionable in Story 2.6
- [x] [Review][Defer] `calculate_monthly_property_tax` docstring says "(1-60)" but is now called with `m` up to 120 (10yr) or 360 (30yr) — stale docstring, logic is correct for any m > 12 [calculations.py] — deferred, pre-existing; cosmetic
- [x] [Review][Defer] Furniture budget ($15K default) is included in renter's `upfront_cash` opportunity cost, but renter would also buy furniture — inflates renter portfolio by ~$29K at 10yr — known simplification from Story 2.3 design, accepted [app.py] — deferred, pre-existing

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_No issues. All tasks implemented in one pass. Calculation invariants verified via direct Python execution._

### Completion Notes List

- Added `DOWN_PCT = 20.0` and `HORIZON_YEARS = 10` to `defaults.py` under new `# -- Scenario Inputs --` section.
- Restored `import calculations` at top of `app.py` (removed in Story 2.4, needed again for two-path loop).
- Added `down_pct` slider (3.0–30.0%, step=0.5, default=`defaults.DOWN_PCT`) to Essential Inputs in sidebar, immediately after `home_price`.
- Wired two-path calculation loop: Pass 1 builds `renter_monthly` (variable contributions from upfront_cash) and `buyer_surplus_list`. Pass 2 builds `buyer_monthly` (home equity + buyer side portfolio). Both annual series produced via `get_annual_snapshots`.
- `buying_cost_m` = P&I + PMI + HOA + property_tax_m + insurance; special assessment excluded (intentional per Story 2.3 design).
- `horizon_years = defaults.HORIZON_YEARS` (single line; Story 2.6 replaces with timeline slider).
- All computation precedes any `st.*` display call (AC6 satisfied).
- Verification with Miami defaults (20% down, 10yr): renter_annual[-1]=$240,604, buyer_annual[-1]=$199,712; all list lengths correct.
- 99/99 tests pass, zero regressions.

### File List

- `defaults.py` (modified — added DOWN_PCT, HORIZON_YEARS constants)
- `app.py` (modified — import calculations restored; down_pct slider added; two-path calculation loop wired; main area debug display)

### Change Log

- 2026-05-29: Story 2.5 complete — two-path rent vs buy calculation wired in app.py; DOWN_PCT and HORIZON_YEARS added to defaults.py; 99/99 tests pass
