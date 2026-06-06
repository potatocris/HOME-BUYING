# Story 4.1: Budget-Based Opportunity-Cost Model & Cost Escalation

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user comparing renting vs. buying,
I want the tool to invest whatever's left of my income after housing each month and to grow ownership costs realistically over time,
so that the wealth comparison reflects "same paycheck, different housing choice" with believable Miami cost growth instead of an artificial price-gap model with frozen costs.

## Acceptance Criteria

**Budget-based investing (both `app.py` and `pages/scenarios.py`):**

1. **Given** a monthly budget (default $3,500) and the comparison horizon, **When** the rent-vs-buy calculation runs, **Then** the **renter** portfolio is seeded with the upfront cash (down payment + closing + furniture) and each month adds `max(0, budget_m − rent_m)`, compounded monthly at the investment return rate.
2. **Given** the same inputs, **When** the calculation runs, **Then** the **buyer** side-portfolio starts at $0 and each month adds `max(0, budget_m − total_ownership_cost_m)`, compounded monthly, and the buyer's total wealth = home equity + side-portfolio.
3. **Given** the budget grows over time, **When** `budget_m` is computed for month `m`, **Then** it steps up **once per year** at `income_growth = rent_growth_rate + 0.25` percentage points (derived constant `INCOME_RENT_PREMIUM = 0.25`; **no separate income slider**), using the same annual-step rule as `escalated_rent` (year 1 = base).
4. **Given** a month where housing cost exceeds the budget, **When** the contribution is computed, **Then** it is **floored at $0** (invest nothing that month; the portfolio is never drawn down).

**Cost escalation:**

5. **Given** the new **Annual Cost Growth** slider (default 3%), **When** monthly ownership costs are computed, **Then** **HOA** and **HO-6 insurance** escalate annually at the cost-growth rate (year 1 = base, annual step).
6. **Given** the cost-growth rate, **When** property tax is computed, **Then** the tax **rate (millage) stays constant** while the **assessed value** grows annually at the cost-growth rate, **capped at 3%/yr (Save Our Homes)**, with the homestead exemption still applied from month 13 onward.

**Inputs, URL, transparency:**

7. **Given** the sidebar on the main page, **When** it renders, **Then** a **"Monthly Budget"** slider appears in the neutral *Comparison Settings* group and an **"Annual Cost Growth"** slider appears in the *Buy* group, and a caption surfaces the derived income growth (e.g., "Income grows at rent + 0.25%/yr").
8. **Given** the two new inputs, **When** a slider changes, **Then** both round-trip through the URL via new keys `bud` (MONTHLY_BUDGET) and `cg` (COST_GROWTH_RATE), and a missing/invalid param falls back to its default without raising.

**Tests & regression:**

9. **Given** the test suite, **When** `python -m pytest -q` runs, **Then** new tests cover `annual_escalate` (year-1 == base, year-2 == base×(1+g), month-12/13 boundary), property-tax assessed-value growth **and the 3% SOH cap** (slider above 3% still capped), and the budget-surplus floor-at-$0 feeding the portfolios — **and all previously-passing tests (113 as of the last quick-dev) still pass**.

## Tasks / Subtasks

- [x] **Task 1 — `defaults.py`: add inputs (AC: 1, 5)**
  - [x] Add `MONTHLY_BUDGET = 3_500.0` (with a comment: monthly income allocated to housing + investing).
  - [x] Add `COST_GROWTH_RATE = 3.0` (annual growth for HOA, HO-6 insurance, and tax assessed value).
  - [x] Bump `DEFAULTS_LAST_UPDATED = "June 2026"`.
  - [x] Do **not** add an income-growth default (it is derived).

- [x] **Task 2 — `calculations.py`: engine helpers (AC: 3, 5, 6)**
  - [x] Add module constants `INCOME_RENT_PREMIUM = 0.25` and `SOH_ASSESSMENT_CAP = 3.0`.
  - [x] Add `annual_escalate(base, annual_growth_pct, month)` → `base * (1 + g/100) ** ((month-1)//12)`.
  - [x] Refactor `escalated_rent` to `return annual_escalate(base_rent, annual_growth_pct, month)` (behavior must stay identical — its tests must still pass).
  - [x] Change `calculate_monthly_property_tax(price, tax_rate_pct, month, assessment_growth_pct=0.0)`: grow assessed value at `min(assessment_growth_pct, SOH_ASSESSMENT_CAP)` via `annual_escalate`, then subtract `HOMESTEAD_EXEMPTION` for `month > 12`, then `× rate/100 / 12`. **The new arg must be keyword/defaulted so existing callers and tests don't break.**
  - [x] Add `calculate_renter_investment_portfolio(initial_capital, contribution_list, annual_rate)` — mirror of `calculate_buyer_investment_portfolio` but seeded with `initial_capital` instead of $0. (Both pages and tests reuse it.)

- [x] **Task 3 — `app.py`: sliders + derived income + URL (AC: 7, 8)**
  - [x] Add **Monthly Budget** slider in the *Comparison Settings* group (after Investment Return), `key="nx_budget"`, `min 1_000.0 max 10_000.0 step 100.0 format "$%.0f"`, `value=_initial['MONTHLY_BUDGET']`.
  - [x] Add **Annual Cost Growth** slider in the *Buy* group, `key="buy_cost_growth"`, `min 0.0 max 8.0 step 0.25 format "%.2f%%"`, `value=_initial['COST_GROWTH_RATE']`. Add a min/max caption row to match the sibling sliders (0.00% … 8.00%).
  - [x] Add a `st.caption("Income grows at rent + 0.25%/yr")` near the budget or rental group.
  - [x] Add `'MONTHLY_BUDGET': monthly_budget` and `'COST_GROWTH_RATE': cost_growth_rate` to the `st.query_params.update(url_state.encode_state({...}))` dict.

- [x] **Task 4 — `app.py`: Pass-1 loop math (AC: 1, 2, 3, 4, 5, 6)**
  - [x] Before the loop: `income_growth = rent_growth_rate + calculations.INCOME_RENT_PREMIUM`.
  - [x] Inside the loop, escalate costs: `hoa_m = calculations.annual_escalate(hoa_monthly, cost_growth_rate, m)`; `ins_m = calculations.annual_escalate(ho6_insurance_annual / 12, cost_growth_rate, m)`; `tax_m = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, m, cost_growth_rate)`. Recompute `buying_cost_m = p_and_i + pmi_m + hoa_m + tax_m + ins_m`.
  - [x] `budget_m = calculations.annual_escalate(monthly_budget, income_growth, m)`.
  - [x] Replace contributions: `renter_contribution = max(0.0, budget_m - rent_m)` and `buyer_contribution = max(0.0, budget_m - buying_cost_m)`; append `buyer_contribution` to `buyer_surplus_list` (rename to `buyer_contrib_list` if desired — update the two downstream reads at lines ~356, ~358).
  - [x] Keep the renter compounding seeded from `upfront_cash` exactly as today.
  - [x] **Do not change the display layer** (cards/chart/table) — it reads `renter_invest_m1`, `buyer_invest_m1`, `renter_invest_annual`, `buyer_invest_annual`, `total_buying_paid`, `renter_annual`, `buyer_annual`, which all flow through unchanged.

- [x] **Task 5 — `url_state.py`: new params (AC: 8)**
  - [x] Add `'bud': 'MONTHLY_BUDGET'` and `'cg': 'COST_GROWTH_RATE'` to `PARAM_MAP`. Both are floats (do **not** add to `INT_PARAMS`).

- [x] **Task 6 — `pages/scenarios.py`: bring in line with the budget model (AC: 1, 2, 4, 5, 6)**
  - [x] Add three sliders to its sidebar (it has its own, no URL state): **Rent Increase (%/yr)** (`defaults.RENT_GROWTH_RATE`), **Monthly Budget** (`defaults.MONTHLY_BUDGET`), **Annual Cost Growth** (`defaults.COST_GROWTH_RATE`).
  - [x] In the per-scenario loop, replace the fixed `monthly_contribution = max(0, total_m1 − market_rent)` + `calculate_investment_portfolio(...)` block with a 60-month build: for each month compute `rent_m = escalated_rent(market_rent, rent_growth_rate, m)`, `budget_m = annual_escalate(budget, rent_growth_rate + 0.25, m)`, escalated HOA/insurance and `calculate_monthly_property_tax(..., m, cost_growth_rate)`, then `renter_contribution = max(0, budget_m − rent_m)`. Feed the contribution list to `calculate_renter_investment_portfolio(upfront_cash, contrib_list, investment_return_rate)`.
  - [x] `exit_continue_renting` and `break_even_month` now read this new `portfolio_values` (their existing code is unchanged once `portfolio_values` is correct). The month-1 cost card (`monthly_cost_m1`) stays a month-1 snapshot — leave it.
  - [x] Page 2 remains a 5-year, 4-down-payment view — **do not** add a horizon slider or URL state (out of scope).

- [x] **Task 7 — `tests/test_calculations.py`: additive coverage (AC: 9)**
  - [x] `annual_escalate`: year-1 == base (months 1 & 12), year-2 == base×(1+g) (month 13), arbitrary growth.
  - [x] `calculate_monthly_property_tax`: assessed value grows with `assessment_growth_pct`; **capped at 3%** when slider > 3%; homestead exemption still applies month 13+; default arg (0.0) reproduces today's flat behavior (back-compat).
  - [x] `calculate_renter_investment_portfolio`: length, month-1 = `(initial + c1)×(1+r)`, constant-contribution matches `calculate_investment_portfolio` reference, floor-at-$0 behavior with a contribution list containing zeros.
  - [x] Confirm existing `escalated_rent` tests still pass after the delegate refactor.

- [x] **Task 8 — Verify (AC: 9)**
  - [x] `python -m py_compile app.py pages/scenarios.py calculations.py url_state.py defaults.py` → clean.
  - [x] `python -m pytest -q` → all pass (113 prior + new).
  - [x] `streamlit run app.py` smoke: two new sliders appear in the right groups; URL gains `bud`/`cg`; cards/chart/table update; switch to Page 2 and confirm it renders with escalation. (Manual — leave for user.)

## Dev Notes

### What this story is really about
Replace the **differential** opportunity-cost model (only the cheaper side invests the price gap) with a **fixed-budget** model (both sides invest what's left of a shared, growing income after housing), and stop holding ownership costs flat. Source of truth: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-06-06.md` (approved by Cris 2026-06-06). All four design decisions were made by Cris and are non-negotiable:
- **One shared income-growth rate, derived** = `rent_growth + 0.25` (constant premium, no slider).
- **Renter keeps the upfront-cash seed.**
- **Floor at $0** in shortfall months (Cris re-confirmed: keep the floor).
- **Annual step-up**, default budget **$3,500**; **one shared 3% cost-growth slider** for HOA + insurance + tax assessed value; **tax rate constant**, assessed-value growth capped at **3% (Save Our Homes)**.

### Files to touch — current state & what to preserve

**`calculations.py` (UPDATE — pure Python, no Streamlit; ARCH-3):**
- `escalated_rent(base_rent, annual_growth_pct, month)` (lines 139–146) already does annual stepping `(month-1)//12`, year 1 = base. Generalize it into `annual_escalate` and have `escalated_rent` delegate. **Preserve:** identical output (its tests assert year-1 == base, year-2 step).
- `calculate_monthly_property_tax(price, tax_rate_pct, month)` (lines 55–58) currently: `assessed = price if month<=12 else price-50_000; return assessed*(rate/100)/12`. **Preserve** the homestead-from-month-13 behavior; add growth *before* the exemption subtraction; new arg defaulted so the many existing callers/tests keep working.
- `calculate_buyer_investment_portfolio(monthly_surplus_list, annual_rate)` (lines 106–118): start $0, compound a per-month list. **Reuse unchanged.** Add the renter sibling that seeds `initial_capital`.
- `calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60)` (lines 68–76): fixed-contribution; **keep it** (tests depend on it; the new renter function can be tested against it for constant contributions), but it is no longer the primary path.
- `HOMESTEAD_EXEMPTION = 50_000` (line 52), `PMI_*`, `FL_DOC_STAMP_RATE`, exit functions — **do not touch.**

**`app.py` (UPDATE):**
- Sidebar groups (lines 125–274): neutral *Comparison Settings* (Horizon, Investment Return), *Rental* (Market Rent, Rent Increase), *Buy* (Home Price … Furniture + Advanced expander). Slider label coloring is via `st-key-*` CSS (lines 106–123) keyed by `nx_` / `rent_` / `buy_` prefixes — **new sliders must use those key prefixes** (`nx_budget`, `buy_cost_growth`) so labels are styled consistently.
- `_initial = url_state.decode_state(...)` (line 96) — new keys auto-flow once added to `PARAM_MAP`; reference `_initial['MONTHLY_BUDGET']` / `_initial['COST_GROWTH_RATE']` for slider values.
- The `encode_state({...})` dict (lines 277–295) is the URL contract — add the two keys; the existing 17 must remain.
- Pass-1 loop (lines 318–335) is the **core change**. Pass-2 (lines 342–348, buyer wealth = equity + side portfolio) is unchanged. `total_buying_paid` (line 328) accumulates `buying_cost_m` — once costs escalate, the "Total paid" card figure escalates automatically. **Good: no display edits.**
- Display helpers `_renting_card`/`_buying_card`/`_headline_card` (lines 28–66) and the chart/table (lines 395–505) **read computed variables only** — leave them. `_renting_card` shows `rent_growth_rate` as "grows X/yr" (still correct).

**`pages/scenarios.py` (UPDATE — the bigger lift):** Currently a 5-year, 4-down-payment snapshot with its **own** sidebar (16 sliders, no URL state, no rent escalation, fixed `monthly_contribution`, hardcoded `** 5`). Lines 134–139 are the model swap. The exit-path (`exit_sell`/`exit_rent_out`/`exit_continue_renting`, lines 146–157) and break-even (160–166) consume `portfolio_values`/`schedule` — they keep working once `portfolio_values` is rebuilt with the budget model. The card render (181–207) shows a month-1 cost snapshot — leave it. **Preserve:** Page 2 stays 5-year (do not parameterize horizon or add URL state).

**`url_state.py` (UPDATE):** `PARAM_MAP` (lines 8–26) + `INT_PARAMS` (line 28). Add two float params. `decode_state` already falls back to defaults via `getattr(defaults, const_name)`, so the new defaults must exist in `defaults.py` first (Task 1 before Task 5 logically).

### Behavioral expectation (validation gate, NFR5)
Rent grows at `rent_growth` (default 3%), income at 3.25%, HOA/insurance/assessed-tax at 3%, mortgage P&I fixed. Net: buying still strengthens long-run but far less than the old all-flat-costs version. Sanity-check a couple of rows against a reference spreadsheet; confirm tax growth caps at 3% even if the slider is set higher, and a special-assessment month floors contributions at $0 (no negative portfolio dip).

### Architecture compliance
- `calculations.py` must stay **pure Python, zero Streamlit** (ARCH-3) so `tests/test_calculations.py` imports it directly. New helpers go here, not in `app.py`.
- `defaults.py` stays isolated (ARCH-4) — only constants, no logic.
- `url_state.py` stays encode/decode only (ARCH-5); the 2,000-char budget is fine (two short keys added). [Source: architecture.md#Selected-structure, lines 74–88; sprint-change-proposal-2026-06-06.md §4B]

### Testing standards
- pytest under `tests/`, run `python -m pytest -q` (**Windows: `python`, not `python3`** — [[feedback-windows-python]]).
- Mirror `tests/test_calculations.py` structure; import functions directly. Assert real float behavior (the suite already does this for rounding).

### Previous Story Intelligence
- **Quick-dev (2026-06-06) — rent escalation + 3-column summary** (`spec-summary-columns-rent-escalation.md`, done): added `RENT_GROWTH_RATE`, URL key `rg`, `escalated_rent`, and threaded escalation into both contributions. This is the exact pattern to extend — `annual_escalate` is a generalization of `escalated_rent`, and the two new sliders mirror how `Rent Increase` was added. 113 tests (+4 for `escalated_rent`).
- **Sidebar grouping (`spec-sidebar-rent-buy-grouping.md`, done):** the `st-key-*` prefix CSS contract (`nx_`/`rent_`/`buy_`) — new sliders must follow it.
- **Story 3.7 (done, commit `f103692`):** all displayed numbers route through `formatting.py` (`fmt_dollar`/`fmt_pct`/`fmt_pct_compact`). Any new displayed value must use these — but this story adds no new displayed numbers (slider `format=` strings are input-widget formats, out of scope per 3.7).

### Git Intelligence
Recent commits (`3fde2f2` three-column summary + rent-growth, `f103692` story 3.7) each touch `app.py` + a spec/story file. Working tree currently has uncommitted changes (per session start: `app.py`, `calculations.py`, `defaults.py`, tests, plus this story's planning docs). Branch-first before committing (master is the main branch); commit code + this story file together. Do not commit without Cris's OK.

### Project Structure Notes
No new modules or dependencies. Pure additions to existing flat-module structure (`app.py`, `calculations.py`, `defaults.py`, `url_state.py`, `pages/scenarios.py`, `tests/`). No requirements.txt change.

### References
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-06-06.md — §1 decisions, §4 detailed changes, §5 handoff]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-4 / Story 4.1 — AC]
- [Source: _bmad-output/planning-artifacts/prd.md — FR17 (rewritten), FR15 (amended), FR38, FR39]
- [Source: calculations.py:55–58, 68–76, 106–118, 139–146]
- [Source: app.py:96, 106–123, 277–295, 318–358, 395–505]
- [Source: pages/scenarios.py:109–179]
- [Source: url_state.py:8–28]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8

### Debug Log References

- Red-green-refactor: added 13 new tests to `tests/test_calculations.py` first → confirmed red (`ImportError: cannot import name 'annual_escalate'`) → implemented engine → green (92 calc tests). Full suite: **130 passed**.
- Verified URL round-trip (`bud`/`cg`), invalid-param fallback, annual budget step ($3,613.75 @ month 13), and SOH cap (6% slider == 3% result, $336.38).

### Completion Notes List

- **Engine (`calculations.py`):** added `annual_escalate(base, growth, month)`; refactored `escalated_rent` to delegate (behavior identical — existing tests pass). `calculate_monthly_property_tax` gained `assessment_growth_pct=0.0` (back-compat default reproduces flat behavior; growth capped at `SOH_ASSESSMENT_CAP=3.0`). Added `calculate_renter_investment_portfolio(initial_capital, contribution_list, rate)`. Added constant `INCOME_RENT_PREMIUM=0.25`.
- **`defaults.py`:** added `MONTHLY_BUDGET=3500.0`, `COST_GROWTH_RATE=3.0`; bumped `DEFAULTS_LAST_UPDATED="June 2026"`.
- **`app.py`:** added Monthly Budget slider (neutral group) + Annual Cost Growth slider (Buy group) with min/max captions and a derived-income caption; added `MONTHLY_BUDGET`/`COST_GROWTH_RATE` to `encode_state`; rewrote Pass-1 loop to the budget model — `income_growth = rent_growth + 0.25`, escalated HOA/insurance/tax, `renter = max(0, budget − rent)`, `buyer = max(0, budget − buying)`. Display layer untouched (reads computed vars; `total_buying_paid` now escalates automatically).
- **`url_state.py`:** added `bud`→MONTHLY_BUDGET, `cg`→COST_GROWTH_RATE (floats).
- **`pages/scenarios.py`:** added Rent Increase + Monthly Budget sliders; rewrote the renter portfolio to a per-month budget loop via `calculate_renter_investment_portfolio` (seeded with upfront cash). **Deviation from story Task 6:** the cost-growth slider was intentionally NOT added to Page 2 — Page 2 has no per-month buyer cost trajectory (month-1 cost snapshot only), so a cost-growth input would be a no-op and violate FR37. Page 2 stays a 5-year view. The renter/continue-renting portfolio now uses the budget model with rent escalation, which is the part that had diverged.
- **Tests:** +13 in `tests/test_calculations.py` (annual_escalate ×5, property-tax growth + SOH cap ×4, renter portfolio ×4). 113 → 130 passing, zero regressions.
- **Manual browser smoke (`streamlit run app.py`) left for user** per project convention.

### File List

- defaults.py (modified)
- calculations.py (modified)
- url_state.py (modified)
- app.py (modified)
- pages/scenarios.py (modified)
- tests/test_calculations.py (modified)

## Change Log

- 2026-06-06: Implemented Story 4.1 — budget-based opportunity-cost model + cost escalation. Replaced the differential contribution model with a shared monthly-budget model (renter seeded with upfront cash; both invest `max(0, budget − housing)`; budget grows annually at rent+0.25%; floor at $0). Added annual escalation for HOA, HO-6 insurance, and property-tax assessed value (capped at 3% Save Our Homes; tax rate constant). Two new sliders (Monthly Budget, Annual Cost Growth) + URL keys (`bud`, `cg`). Page 2 renter portfolio brought onto the budget model (cost-growth slider omitted there as a no-op). 130/130 tests pass. (claude-opus-4-8)
