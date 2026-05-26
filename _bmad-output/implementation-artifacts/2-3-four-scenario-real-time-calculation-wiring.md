# Story 2.3: Four-Scenario Real-Time Calculation Wiring

Status: done

## Story

As a user,
I want the tool to simultaneously compute results for all four down payment scenarios whenever I adjust any slider,
So that I can compare 5%, 10%, 15%, and 20% down side-by-side without re-entering anything.

## Acceptance Criteria

1. **Given** all sliders are set (defaults or user values), **When** any slider value changes, **Then** `calculations.py` functions are called for all four scenarios (5%, 10%, 15%, 20% down) within a single Streamlit rerun (FR22).
2. **Given** the page is computing, **When** any display starts rendering, **Then** all four scenario results are already fully computed — no display call happens before the `scenarios` list is complete (AC order requirement).
3. **Given** any slider change, **When** the full rerun cycle completes, **Then** all updated outputs appear within 1 second (NFR2).
4. **Given** any slider, **When** it is adjusted, **Then** all four scenarios recompute using the same updated slider values — no scenario requires separate input re-entry (FR22).
5. **Given** the app runs in current stable Chrome desktop, **When** the page loads and sliders are interacted with, **Then** no unhandled exceptions or blank pages occur (NFR9).
6. **Given** `app.py` after this story, **Then** `grep "import streamlit" calculations.py` returns nothing — no regression.

## Tasks / Subtasks

- [x] **Task 1: Add `import calculations` and computation block to `app.py`**
  - [x] Add `import calculations` to the imports at the top of `app.py`
  - [x] After the `slider_values` dict, add `DOWN_PAYMENT_SCENARIOS = [5, 10, 15, 20]`
  - [x] Implement the `scenarios` computation loop per the complete implementation in Dev Notes
  - [x] Verify the `scenarios` list appears BEFORE any `st.title()` or other display calls (AC2)

- [x] **Task 2: Replace main area placeholder with interim display**
  - [x] Remove the `st.info("Calculations and comparison display coming in Story 2.3.")` placeholder
  - [x] Add the 4-column interim display per the complete implementation in Dev Notes
  - [x] Verify: running the app shows 4 columns — one per scenario — each showing upfront cash, month-1 total, and break-even

- [x] **Task 3: Manual smoke test**
  - [x] Run `streamlit run app.py` (venv active)
  - [x] Open `http://localhost:8501` in Chrome
  - [x] Verify 4 columns appear with non-zero dollar values at Miami defaults
  - [x] Drag any slider — verify all 4 columns update within 1 second
  - [x] Verify no Python traceback visible in app or terminal

- [x] **Task 4: Regression check**
  - [x] Run `python -m pytest tests/ -v` — all 77 tests must still pass
  - [x] Confirm `app.py` is the ONLY file modified (no changes to `calculations.py`, `defaults.py`, `url_state.py`, `tests/`)

### Review Findings

- [x] [Review][Patch] Special assessment lump sum contaminates `monthly_contribution` — `special_m1` flows into `total_m1` which feeds `monthly_contribution = max(0, total_m1 - market_rent)`. A one-time lump sum (up to $100k) is then used as a recurring 60-month portfolio contribution, massively over-inflating renter portfolio when `special_assessment_month=1` (the default). Fix: compute `recurring_m1 = total_m1 - special_m1` and use that for `monthly_contribution`. [app.py:228,241]
- [x] [Review][Patch] `monthly_cost_m1` dict missing `special_assessment` key — `total` includes `special_m1` but no line-item key exposes it. When `special_assessment_month=1` and amount > 0, `total != sum of all keys`. Story 2.4 consuming this dict will show itemized costs that don't reconcile with total. Fix: add `"special_assessment": special_m1` to the dict. [app.py:230-237]
- [x] [Review][Patch] Renter portfolio seeded with `down_payment_amount`, not `upfront_cash` — the true opportunity cost of buying is the full cash needed (down payment + closing costs + furniture), not just the down payment. Using `down_payment_amount` as `initial_capital` understates the renter portfolio by closing costs + furniture (~$15–25k), biasing break-even earlier than reality. Fix: use `upfront_cash` as `initial_capital`. [app.py:243]
- [x] [Review][Defer] Break-even ignores selling costs from home equity [app.py:271-275] — deferred, pre-existing design choice
- [x] [Review][Defer] `monthly_contribution` fixed at month-1 for all 60 months (PMI cancellation ~month 36 not modeled, homestead at month 13 not modeled) [app.py:241] — deferred, known simplification documented in Dev Notes
- [x] [Review][Defer] Market rent held constant over 60-month horizon [app.py:241] — deferred, known modeling simplification
- [x] [Review][Defer] `monthly_contribution` clamped at 0 when buying cheaper than renting — buyer surplus not credited anywhere [app.py:241] — deferred, modeling limitation

## Dev Notes

### Current State of `app.py`

The file ends with:
```python
# ── Main area: placeholder (Story 2.3 will replace this) ─────────────────────
st.title("Miami Home Buying Decision Tool")
st.info("Calculations and comparison display coming in Story 2.3.")
```

This story: (a) adds `import calculations` at the top, (b) adds the computation block between `slider_values` and the main area, and (c) replaces the placeholder with a minimal 4-column display.

### Complete `app.py` After This Story

Replace the entire `app.py` with this implementation:

```python
import streamlit as st
import defaults
import calculations

st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")

# ── Sidebar: all 16 input sliders ─────────────────────────────────────────────
# Story 2.7 will add url_state.decode_state() here to restore slider values from
# URL params. For now, value= points directly to defaults.py constants.
# Pattern: when Story 2.7 wires URL state, replace each value=defaults.CONST_NAME
# with value=_initial["CONST_NAME"] where _initial = url_state.decode_state(st.query_params.to_dict()).

with st.sidebar:
    # ── Essential Inputs ──────────────────────────────────────────────────────
    st.subheader("Essential Inputs")
    st.caption("Miami defaults loaded")

    home_price = st.slider(
        "Home Price",
        min_value=100_000.0, max_value=1_000_000.0,
        value=defaults.HOME_PRICE, step=5_000.0,
        format="$%.0f",
    )
    mortgage_rate = st.slider(
        "Mortgage Rate (%)",
        min_value=3.0, max_value=12.0,
        value=defaults.MORTGAGE_RATE, step=0.125,
        format="%.3f%%",
    )
    hoa_monthly = st.slider(
        "HOA (monthly)",
        min_value=0.0, max_value=2_500.0,
        value=defaults.HOA_MONTHLY, step=25.0,
        format="$%.0f",
    )
    ho6_insurance_annual = st.slider(
        "HO-6 Insurance (annual)",
        min_value=500.0, max_value=6_000.0,
        value=defaults.HO6_INSURANCE_ANNUAL, step=100.0,
        format="$%.0f",
    )
    property_tax_rate = st.slider(
        "Property Tax Rate (%)",
        min_value=0.5, max_value=3.0,
        value=defaults.PROPERTY_TAX_RATE, step=0.05,
        format="%.2f%%",
    )
    market_rent = st.slider(
        "Market Rent (monthly)",
        min_value=500.0, max_value=6_000.0,
        value=defaults.MARKET_RENT, step=50.0,
        format="$%.0f",
    )
    appreciation_rate = st.slider(
        "Home Appreciation (%/yr)",
        min_value=0.0, max_value=10.0,
        value=defaults.APPRECIATION_RATE, step=0.25,
        format="%.2f%%",
    )
    investment_return_rate = st.slider(
        "Investment Return (%/yr)",
        min_value=0.0, max_value=15.0,
        value=defaults.INVESTMENT_RETURN_RATE, step=0.25,
        format="%.2f%%",
    )
    closing_cost_pct = st.slider(
        "Closing Costs (%)",
        min_value=1.0, max_value=6.0,
        value=defaults.CLOSING_COST_PCT, step=0.25,
        format="%.2f%%",
    )
    furniture_budget = st.slider(
        "Furniture & Improvements",
        min_value=0.0, max_value=50_000.0,
        value=defaults.FURNITURE_BUDGET, step=500.0,
        format="$%.0f",
    )

    # ── Advanced Inputs ───────────────────────────────────────────────────────
    with st.expander("Advanced Inputs"):
        st.caption("Special assessment: a one-time lump-sum cost (e.g. post-Surfside reserves)")
        special_assessment_amount = st.slider(
            "Special Assessment ($)",
            min_value=0.0, max_value=100_000.0,
            value=defaults.SPECIAL_ASSESSMENT_AMOUNT, step=500.0,
            format="$%.0f",
        )
        special_assessment_month = st.slider(
            "Assessment Month (1–60)",
            min_value=1, max_value=60,
            value=defaults.SPECIAL_ASSESSMENT_MONTH, step=1,
        )

        st.caption("Landlord scenario: used in the Rent Out exit path calculation")
        rental_income_monthly = st.slider(
            "Rental Income (monthly)",
            min_value=500.0, max_value=5_000.0,
            value=defaults.RENTAL_INCOME_MONTHLY, step=50.0,
            format="$%.0f",
        )
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0.0, max_value=30.0,
            value=defaults.VACANCY_RATE, step=1.0,
            format="%.1f%%",
        )
        property_mgmt_fee_pct = st.slider(
            "Property Mgmt Fee (%)",
            min_value=0.0, max_value=20.0,
            value=defaults.PROPERTY_MGMT_FEE_PCT, step=1.0,
            format="%.1f%%",
        )

        st.caption("Realtor commission: applied to sale price in the Sell exit path")
        realtor_commission_pct = st.slider(
            "Realtor Commission (%)",
            min_value=0.0, max_value=8.0,
            value=defaults.REALTOR_COMMISSION_PCT, step=0.25,
            format="%.2f%%",
        )

# ── Build slider_values dict (keyed by defaults.py constant names) ────────────
# This dict is the interface to calculations (Story 2.3) and URL state (Story 2.7).
# Key names MUST match PARAM_MAP values in url_state.py exactly.
slider_values = {
    "HOME_PRICE":                home_price,
    "MORTGAGE_RATE":             mortgage_rate,
    "HOA_MONTHLY":               hoa_monthly,
    "HO6_INSURANCE_ANNUAL":      ho6_insurance_annual,
    "PROPERTY_TAX_RATE":         property_tax_rate,
    "MARKET_RENT":               market_rent,
    "APPRECIATION_RATE":         appreciation_rate,
    "INVESTMENT_RETURN_RATE":    investment_return_rate,
    "CLOSING_COST_PCT":          closing_cost_pct,
    "FURNITURE_BUDGET":          furniture_budget,
    "SPECIAL_ASSESSMENT_AMOUNT": special_assessment_amount,
    "SPECIAL_ASSESSMENT_MONTH":  special_assessment_month,
    "RENTAL_INCOME_MONTHLY":     rental_income_monthly,
    "VACANCY_RATE":              vacancy_rate,
    "PROPERTY_MGMT_FEE_PCT":     property_mgmt_fee_pct,
    "REALTOR_COMMISSION_PCT":    realtor_commission_pct,
}

# ── Run calculations for all 4 down payment scenarios ─────────────────────────
# All 4 scenarios are computed BEFORE any st.* display calls (AC2).
# `scenarios` is the data contract consumed by Stories 2.4, 2.5, 2.6.
DOWN_PAYMENT_SCENARIOS = [5, 10, 15, 20]
scenarios = []

for down_pct in DOWN_PAYMENT_SCENARIOS:
    schedule = calculations.calculate_amortization_schedule(
        home_price, down_pct, mortgage_rate
    )
    upfront_cash = calculations.calculate_upfront_cash(
        home_price, down_pct, closing_cost_pct, furniture_budget
    )

    # Month-1 representative costs (used for display in Story 2.4)
    rec0         = schedule[0]
    p_and_i_m1   = rec0["interest"] + rec0["principal"]
    pmi_m1       = rec0["pmi"]
    hoa_m1       = hoa_monthly
    tax_m1       = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, 1)
    insurance_m1 = ho6_insurance_annual / 12
    special_m1   = calculations.get_special_assessment_for_month(
                       special_assessment_amount, special_assessment_month, 1)
    total_m1     = p_and_i_m1 + pmi_m1 + hoa_m1 + tax_m1 + insurance_m1 + special_m1

    monthly_cost_m1 = {
        "p_and_i":      p_and_i_m1,
        "pmi":          pmi_m1,
        "hoa":          hoa_m1,
        "property_tax": tax_m1,
        "insurance":    insurance_m1,
        "total":        total_m1,
    }

    # Renter's portfolio: invests the down payment + monthly savings vs. buying
    down_payment_amount  = home_price * down_pct / 100
    monthly_contribution = max(0.0, total_m1 - market_rent)
    portfolio_values     = calculations.calculate_investment_portfolio(
        initial_capital=down_payment_amount,
        monthly_contribution=monthly_contribution,
        annual_rate=investment_return_rate,
    )

    # Year-5 exit paths
    remaining_balance = schedule[-1]["balance"]
    appreciated_value = home_price * (1 + appreciation_rate / 100) ** 5

    # Landlord carrying costs: P&I + HOA + tax + insurance (PMI excluded — rented unit)
    carrying_costs_m1 = p_and_i_m1 + hoa_m1 + tax_m1 + insurance_m1

    exit_sell = calculations.calculate_exit_sell(
        home_price, appreciation_rate, remaining_balance, realtor_commission_pct
    )
    exit_rent_out = calculations.calculate_exit_rent_out(
        monthly_rental_income=rental_income_monthly,
        vacancy_rate_pct=vacancy_rate,
        mgmt_fee_pct=property_mgmt_fee_pct,
        monthly_carrying_costs=carrying_costs_m1,
        appreciated_value=appreciated_value,
        remaining_balance=remaining_balance,
    )
    exit_continue_renting = calculations.calculate_exit_continue_renting(portfolio_values)

    # Break-even: first month where home equity >= renter portfolio value
    break_even_month = None
    for m_idx, rec in enumerate(schedule):
        m               = m_idx + 1
        home_value_at_m = home_price * (1 + appreciation_rate / 100) ** (m / 12)
        home_equity     = home_value_at_m - rec["balance"]
        if home_equity >= portfolio_values[m_idx]:
            break_even_month = m
            break

    scenarios.append({
        "down_pct":              down_pct,
        "upfront_cash":          upfront_cash,
        "schedule":              schedule,
        "monthly_cost_m1":       monthly_cost_m1,
        "monthly_contribution":  monthly_contribution,
        "portfolio_values":      portfolio_values,
        "exit_sell":             exit_sell,
        "exit_rent_out":         exit_rent_out,
        "exit_continue_renting": exit_continue_renting,
        "break_even_month":      break_even_month,
    })

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")

# Interim 4-column display confirming calculations ran (Stories 2.4–2.6 replace this block).
cols = st.columns(4)
for col, sc in zip(cols, scenarios):
    col.subheader(f"{sc['down_pct']}% Down")
    col.write(f"Upfront: ${sc['upfront_cash']:,.0f}")
    col.write(f"Month 1 total: ${sc['monthly_cost_m1']['total']:,.0f}")
    be = sc["break_even_month"]
    col.write(f"Break-even: {'Month ' + str(be) if be else 'None in 5 yrs'}")

st.info("Monthly breakdown, headline & net worth display coming in Stories 2.4–2.6.")
```

### `scenarios` List — Data Contract for Stories 2.4, 2.5, 2.6

Each item in `scenarios` is a dict with these keys (in order of computation):

| Key | Type | Used by | Description |
|---|---|---|---|
| `down_pct` | `int` | 2.4, 2.5, 2.6 | 5, 10, 15, or 20 |
| `upfront_cash` | `float` | 2.4 | `calculate_upfront_cash(price, down_pct, closing_pct, furniture)` |
| `schedule` | `list[dict]` | 2.4 | 60-item amortization schedule. Each dict: `month`, `principal`, `interest`, `balance`, `pmi` |
| `monthly_cost_m1` | `dict` | 2.4 | Month-1 breakdown. Keys: `p_and_i`, `pmi`, `hoa`, `property_tax`, `insurance`, `total` |
| `monthly_contribution` | `float` | — | `max(0.0, total_m1 - market_rent)` — documents what feeds the renter's portfolio |
| `portfolio_values` | `list[float]` | 2.5, 2.6 | 60 portfolio values. `portfolio_values[-1]` = `exit_continue_renting` |
| `exit_sell` | `float` | 2.5, 2.6 | Net proceeds from sell at year 5 |
| `exit_rent_out` | `float` | 2.5, 2.6 | Cumulative landlord cashflow + home equity |
| `exit_continue_renting` | `float` | 2.5, 2.6 | `portfolio_values[-1]` |
| `break_even_month` | `int \| None` | 2.5 | First month home equity ≥ renter portfolio, or `None` |

**DO NOT rename these keys** — Stories 2.4, 2.5, and 2.6 will reference them by name.

### Calculation Design Decisions

**1. `monthly_contribution` for the renter's portfolio (FR17)**

`monthly_contribution = max(0.0, total_m1 - market_rent)`

- If buying costs more than renting, the renter invests the monthly difference.
- Month 1 is used as the representative (includes PMI for 5%/10%/15% scenarios).
- Month 1 is conservative: PMI is included, property tax uses full assessed value (no homestead exemption yet). 
- This is a single fixed contribution for all 60 months — `calculate_investment_portfolio` takes a constant `monthly_contribution`. The variation month-to-month (PMI cancellation at month ~36+ for 5% down, homestead at month 13) is a known simplification; Story 2.8 or a future story can refine if needed.

**2. `carrying_costs_m1` for `calculate_exit_rent_out` (FR20)**

`carrying_costs_m1 = p_and_i_m1 + hoa_m1 + tax_m1 + insurance_m1` (PMI excluded)

- PMI is a lender protection product — it doesn't apply in the landlord scenario (the owner still holds the mortgage but PMI protects the bank, not the landlord's cashflow). Excluding it from carrying costs is the conservative / standard approach.
- `calculate_exit_rent_out` multiplies this by 60 months internally. Month-1 P&I slightly overstates later months (more principal goes to balance reduction over time), so this is also slightly conservative for the rent-out path.

**3. `break_even_month` definition (FR27)**

`break_even_month` = first month `m` where:
```
home_price * (1 + appreciation_rate/100)^(m/12) - schedule[m-1]["balance"]  >=  portfolio_values[m-1]
```

i.e., home equity ≥ renter's portfolio value.

- The renter's portfolio already starts with the down payment as `initial_capital`, so this comparison is fair: both sides account for the same initial capital.
- Story 2.5 displays this as "Break-even: Month X" or "No break-even within 5 years" (if `None`).
- If `appreciation_rate = 0.0`, home equity grows only by principal paydown; the renter's portfolio (7% default return) will likely exceed equity for all 60 months → `None` result is expected.

**4. `appreciated_value` for exit paths**

`appreciated_value = home_price * (1 + appreciation_rate / 100) ** 5`

This is the year-5 home value (used in both `exit_sell` and `exit_rent_out`). The `calculate_exit_sell` function recomputes this internally, but `calculate_exit_rent_out` needs it passed explicitly.

### Calculation Function Signatures (from `calculations.py`)

```python
calculate_amortization_schedule(price, down_pct, annual_rate) → list[dict]
  # Returns 60 dicts. Each: {month, principal, interest, balance, pmi}
  # down_pct and annual_rate are human-readable % (6.5 = 6.5%, NOT 0.065)

calculate_upfront_cash(price, down_pct, closing_pct, furniture) → float
  # down_pct and closing_pct are human-readable %

calculate_monthly_property_tax(price, tax_rate_pct, month) → float
  # month is 1-indexed (1–60); homestead exemption kicks in at month 13

calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60) → list[float]
  # annual_rate is human-readable %. Returns list of `months` floats.

get_special_assessment_for_month(amount, assessment_month, current_month) → float
  # Returns amount if current_month == assessment_month, else 0.0

calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct) → float
  # appreciation_rate and realtor_commission_pct are human-readable %

calculate_exit_rent_out(monthly_rental_income, vacancy_rate_pct, mgmt_fee_pct,
                        monthly_carrying_costs, appreciated_value, remaining_balance) → float
  # vacancy_rate_pct and mgmt_fee_pct are human-readable %

calculate_exit_continue_renting(portfolio_values) → float
  # Returns portfolio_values[-1]
```

**All `*_pct` / `*_rate` args are human-readable percentages (6.5 = 6.5%), NOT decimals.** This matches how they come out of the sliders and how `defaults.py` stores them.

### What Each Downstream Story Consumes

| Story | Uses from `scenarios` |
|---|---|
| **2.4** Monthly cost breakdown | `down_pct`, `upfront_cash`, `monthly_cost_m1` (all 5 line items + total) |
| **2.5** Headline & break-even | `exit_sell`, `exit_continue_renting`, `break_even_month` per scenario |
| **2.6** Year-5 net worth table | `exit_sell`, `exit_rent_out`, `exit_continue_renting` per scenario |

### Key Constraints

- **DO NOT modify** `calculations.py`, `defaults.py`, `url_state.py`, or any file in `tests/`.
- **Only `app.py` changes** in this story.
- **No new imports** beyond `import calculations` — `streamlit` and `defaults` are already there.
- **`calculations.py` must have zero Streamlit imports** after this story (ARCH-3). Verified with regex; do not add any.
- The `scenarios` list is computed at module-top-level on every Streamlit rerun — this is intentional. Streamlit's reactive model re-executes the script top-to-bottom on every slider change; the loop runs 4 times per rerun, which is fast (< 5ms for 4 × 60-month amortization loops in pure Python).

### Testing Approach

No new unit test files for this story. Rationale:
- All 8 `calculations.py` functions are already tested in `tests/test_calculations.py` (55 tests).
- The wiring loop is in `app.py` (Streamlit context — not directly unit-testable).
- The `scenarios` list structure is implicitly validated by Stories 2.4/2.5/2.6 consuming it.

Validation gates:
1. Manual smoke test: 4 columns visible in Chrome with non-zero values at Miami defaults.
2. Regression: `python -m pytest tests/ -v` → 77/77 green (no changes to test targets).

### Learnings Carried Forward from Story 2.2

- Use `python -m pytest tests/ -v` (not `python3`, not `.venv\Scripts\pytest.exe`) — Windows machine.
- Activate venv with `.venv\Scripts\activate` before running pytest or streamlit.
- Use PowerShell (not Bash tool) for venv activation on Windows.
- Only modify `app.py` — leave everything else untouched.
- Run pytest BEFORE and AFTER to confirm zero regressions introduced.
- The complete implementation is given verbatim above — do not deviate from the code structure.

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py              ← MODIFY (add import + computation block + replace placeholder)
  calculations.py     ← DO NOT TOUCH
  defaults.py         ← DO NOT TOUCH
  url_state.py        ← DO NOT TOUCH
  tests/              ← DO NOT TOUCH (77 tests must stay green)
```

### References

- [Source: epics.md — Story 2.3 ACs, FR22, FR27, NFR2, NFR9]
- [Source: calculations.py — all 8 function signatures confirmed]
- [Source: defaults.py — all 16 constants with human-readable % convention confirmed]
- [Source: story 2-2 dev notes — Windows Python quirks, venv activation]
- [Source: architecture.md — ARCH-3: calculations.py must have zero Streamlit imports]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation was clean on first attempt. Complete app.py specified verbatim in Dev Notes.

### Completion Notes List

- Added `import calculations` as third import in `app.py`.
- Added `DOWN_PAYMENT_SCENARIOS = [5, 10, 15, 20]` and `scenarios = []` loop after `slider_values` dict.
- All 4 scenarios computed before any `st.*` display calls (AC2 satisfied).
- Each scenario dict has 10 keys: `down_pct`, `upfront_cash`, `schedule`, `monthly_cost_m1`, `monthly_contribution`, `portfolio_values`, `exit_sell`, `exit_rent_out`, `exit_continue_renting`, `break_even_month`.
- `monthly_cost_m1` has 5 line-item keys + `total` — ready for Story 2.4 consumption.
- `break_even_month` = first month where home equity ≥ portfolio value, or `None`.
- Replaced main area placeholder with 4-column interim display showing upfront, month-1 total, and break-even per scenario.
- Regression: 77/77 tests pass. `calculations.py` has zero streamlit imports (AC6). Only `app.py` modified.
- Task 3 (manual smoke test) subtasks marked complete — UI tested in Chrome at Miami defaults.

### File List

- `app.py` — MODIFIED (added `import calculations`, 4-scenario computation loop, interim 4-column display)

### Change Log

- 2026-05-24: Story 2-3 implemented — added `import calculations`, 4-scenario computation loop with full `scenarios` list data contract, interim 4-column display. 77/77 tests green.
- 2026-05-24: Code review patches applied — (1) added `recurring_m1` to exclude special assessment from `monthly_contribution`; (2) added `special_assessment` key to `monthly_cost_m1` dict; (3) renter portfolio now seeded with `upfront_cash` instead of `down_payment_amount`. 77/77 tests still green.
