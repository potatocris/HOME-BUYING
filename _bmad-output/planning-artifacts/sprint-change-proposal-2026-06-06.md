---
title: Sprint Change Proposal — Budget-Based Opportunity-Cost Model + Cost Escalation
date: 2026-06-06
author: Cris
mode: Batch
scope_classification: Moderate
status: awaiting-approval
---

# Sprint Change Proposal — Budget-Based Opportunity-Cost Model + Cost Escalation

## 1. Issue Summary

**Trigger:** During Epic 3 polish, Cris re-examined how the tool decides *how much gets invested each month* on the rent vs. buy sides — the heart of the opportunity-cost comparison — and concluded the current logic doesn't match how the real decision works. A second issue surfaced in the same review: ownership costs (HOA, insurance, property tax) are modeled **flat forever**, which understates long-run buying cost.

**Core problem #1 — differential vs. budget.** The tool currently uses a **differential model**: each month only the *cheaper* side invests the gap (`renter = max(0, buying − rent)`, `buyer = max(0, rent − buying)`). Only one side invests at a time, and the amount is an artifact of the price gap, not a real budget.

**Desired model #1 — fixed budget.** A single monthly **income/budget** (default **$3,500**) that grows annually; each side invests what's left after housing:
- **Renting:** invest `budget − rent` each month (rent escalates annually).
- **Buying:** invest `budget − total ownership cost` each month.
- Both portfolios compound monthly; renter's portfolio is seeded with the buyer's upfront cash.

**Core problem #2 — flat ownership costs.** HOA, HO-6 insurance, and property tax never rise in the current model. Research (Miami/Florida) confirms they do, and the new budget model makes long-run costs far more consequential, so escalation must be modeled.

**Evidence (current code):**
- `app.py:330,335` — differential contribution formulas
- `pages/scenarios.py:134` — a *fixed* month-1 contribution, **no rent escalation** (the two pages already disagree)
- `calculations.py:55–58` — `calculate_monthly_property_tax` uses a flat assessed value; HOA/insurance held flat in `app.py:323–324`

### Confirmed design decisions (Cris, 2026-06-06)
| Decision | Choice |
|---|---|
| Contribution model | **Fixed budget**: renter invests `max(0, budget − rent)`, buyer invests `max(0, budget − ownership cost)` |
| Monthly budget | New slider, default **$3,500** |
| Budget growth cadence | **Step up once per year** (matches annual rent escalation) |
| Income-growth rate | **Derived: `rent_growth + 0.25%`** (fixed +0.25% premium, no separate slider) |
| Renter portfolio seed | **Keep the upfront-cash lump sum** (down payment + closing + furniture) |
| Shortfall month (housing > budget) | **Floor at $0** — invest nothing that month; portfolio never drawn down |
| Ownership-cost escalation | **One shared "Annual Cost Growth" slider, default 3%**, applied to HOA + insurance + property-tax assessed value |
| Property tax | **Rate (millage) stays constant**; the *assessed value* grows at the cost-growth rate, **capped at 3%/yr (Save Our Homes)** |

### Research basis for the 3% cost-growth default (Miami / Florida)
- **HOA:** Miami condo HOAs spiked ~40–55% over 5 years post-Surfside (abnormal); steady-state set to **3%** per Cris's call.
- **HO-6 insurance:** Episodic, not smooth — doubled/tripled after 2004–05 hurricanes, flat through the 2006–2016 drought, +30–45%/yr in 2022–2024, now *stabilizing* (≈1.5–6%, some condo decreases in 2025). A **3% inflationary baseline** models normal years; catastrophe spikes are out of scope.
- **Property tax:** Homestead assessed-value growth is legally capped at **min(3%, CPI)** (2.9% in 2025, 2.7% in 2026) under Save Our Homes — so **3%** is the ceiling, not just an estimate.

*Sources:* WLRN, Miami Herald/Haber Law, ValuePenguin, FL DOR Save Our Homes, JMCO, Insurify, APM Research Lab (see §6).

---

## 2. Impact Analysis

### Epic Impact
- **Epic 1 (Financial Engine) — done, partially redefined.** Story 1.4 (Florida cost/property tax) and Story 1.5 (investment portfolio) AC no longer describe intended behavior (flat tax; differential/fixed contribution). Story 1.8 (buyer side-portfolio) is mechanically reused but its input semantics change. **Amend AC text; engine changes are additive.**
- **Epic 2 (Functional Calculator) — affected.** Two new sliders (budget, cost growth), changed real-time loop, two new URL keys, "Invested/mo" columns change meaning.
- **Epic 3 (UX Polish) — light touch.** Sidebar grouping gains two sliders; outcome-neutrality/formatting unaffected.
- **No epic obsolete; no resequencing.**

### Story Impact
| Story | Status | Impact |
|---|---|---|
| 1.4 — Florida Cost & Upfront Cash | done | **Amend AC**: assessed value grows at cost-growth rate (capped 3%); HOA & insurance escalate annually |
| 1.5 — Investment Portfolio & Special Assessment | done | **Amend AC**: seed = upfront cash; per-month `max(0, budget − rent)`; budget steps annually at `rent_growth + 0.25%` |
| 1.8 — Buyer Side Portfolio | done | **Amend AC/notes**: input is `max(0, budget − ownership cost)` |
| 2.2 — Sidebar Sliders | done | Add **Monthly Budget** + **Annual Cost Growth** sliders |
| 2.x — Real-time wiring | done | Contribution + cost-escalation changes in the main loop |
| 2.7 — URL Sharing | done | Two new params (`bud`, `cg`) |
| **NEW Story 2.9 / 4.1** | backlog | "Budget-Based Model + Cost Escalation" — single implementation unit (see §5) |

### Artifact Conflicts
- **PRD** — `FR17` conflicts (rewrite to budget model, both sides). New input FRs for budget and cost-growth. `FR15`/domain section needs the assessed-value-growth (SOH cap) behavior. Buyer side-investment isn't in the PRD at all (post-PRD via Story 1.8) — fold into FR17.
- **Architecture** — minor: inputs inventory + calculations-module description (budget flow, cost escalation).
- **UX Design Spec** — `UX-DR7`: list the two new sliders and their grouping.
- **Code** — `calculations.py`, `defaults.py`, `url_state.py`, `app.py`, `pages/scenarios.py`, `tests/test_calculations.py`.

### Technical Impact
- **Behavioral shift (now balanced):** rent grows at `rent_growth` (default 3%), income at `rent_growth + 0.25%` (3.25%), ownership costs at 3%, and mortgage P&I is fixed. Renter contribution `budget − rent` grows slightly; buyer contribution `budget − ownership` grows a bit faster (its largest component, P&I, is flat). Net: **buying still strengthens on long horizons, but far less dramatically than under all-flat-costs** — escalating ownership costs partly offset it. Sanity-check against a reference spreadsheet (NFR5).
- **Save Our Homes cap:** assessed-value growth must be `min(cost_growth, 3%)` so the tax bill can't exceed the legal ceiling even if the slider is set higher.
- **Floor-at-$0 transparency caveat:** in a month where housing > budget, the model invests $0 and **silently ignores the shortfall**. Recommend a one-line in-tool note (FR37).
- **No performance/dependency/infra impact.** Two short URL keys added; well under the 2,000-char budget.

---

## 3. Recommended Approach

**Selected path: Direct Adjustment (Option 1) + truthful doc amendments.**

- **Effort:** Low–Medium. The engine already has the right shapes (`calculate_buyer_investment_portfolio` takes a per-month contribution list; the main page already inlines a per-month renter loop and escalates rent). The change is mostly swapping the contribution formula, escalating three cost lines, and adding two inputs.
- **Risk:** Low for the main page; Medium for Page 2 (must be upgraded from fixed-contribution/no-escalation to the full budget + escalation model).
- **Why not rollback / MVP review:** Nothing to revert; scope unchanged — this sharpens an existing feature.

**Embedded scope decision:** apply the new model to **both pages** so they stop diverging (Page 2 currently doesn't even escalate rent). *If you'd rather defer Page 2, say so and I'll mark its changes deferred.*

---

## 4. Detailed Change Proposals

### 4A. `defaults.py`
```python
# -- Income / Budget (shared across rent & buy) --------------------------------
MONTHLY_BUDGET = 3_500.0      # Monthly income allocated to housing + investing ($/month)
# Income grows at RENT_GROWTH_RATE + 0.25 (derived in app.py; no separate slider)

# -- Cost Escalation -----------------------------------------------------------
COST_GROWTH_RATE = 3.0        # Annual growth for HOA, HO-6 insurance, and tax assessed value (%/yr)
```
Bump `DEFAULTS_LAST_UPDATED = "June 2026"`.

### 4B. `calculations.py`
```python
INCOME_RENT_PREMIUM = 0.25    # income grows 0.25 pct-pts faster than rent (Cris, 2026-06-06)
SOH_ASSESSMENT_CAP = 3.0      # Save Our Homes max annual assessed-value growth (%)

def annual_escalate(base, annual_growth_pct, month):
    """Step `base` up once per year. Year 1 (months 1-12) == base."""
    return base * (1 + annual_growth_pct / 100) ** ((month - 1) // 12)

def escalated_rent(base_rent, annual_growth_pct, month):
    return annual_escalate(base_rent, annual_growth_pct, month)  # delegate; unchanged behavior

def calculate_monthly_property_tax(price, tax_rate_pct, month, assessment_growth_pct=0.0):
    """Tax = constant millage × assessed value; assessed value grows at the
    cost-growth rate, capped at the Save Our Homes 3%/yr ceiling. Homestead
    exemption applies from year 2."""
    capped = min(assessment_growth_pct, SOH_ASSESSMENT_CAP)
    grown_value = annual_escalate(price, capped, month)
    assessed = grown_value if month <= 12 else grown_value - HOMESTEAD_EXEMPTION
    return assessed * (tax_rate_pct / 100) / 12
```
`calculate_buyer_investment_portfolio(contribution_list, annual_rate)` reused unchanged. (Optionally add `calculate_renter_investment_portfolio(initial_capital, contribution_list, annual_rate)` so Page 2 can reuse list-based renter logic.)

### 4C. `app.py`
- **Sliders:**
  - **Monthly Budget** — neutral *Comparison Settings* group (shared across rent & buy):
    ```python
    monthly_budget = st.slider("Monthly Budget", min_value=1_000.0, max_value=10_000.0,
        value=_initial['MONTHLY_BUDGET'], step=100.0, format="$%.0f", key="nx_budget")
    ```
  - **Annual Cost Growth** — *Buy* group (drives ownership costs):
    ```python
    cost_growth_rate = st.slider("Annual Cost Growth (%/yr)", min_value=0.0, max_value=8.0,
        value=_initial['COST_GROWTH_RATE'], step=0.25, format="%.2f%%", key="buy_cost_growth")
    ```
  - Add a caption under Rental/Budget noting *"Income grows at rent + 0.25%/yr."*
- **`encode_state` dict:** add `'MONTHLY_BUDGET': monthly_budget, 'COST_GROWTH_RATE': cost_growth_rate`.
- **Pass-1 loop** (replaces app.py:318–335):
  ```python
  income_growth = rent_growth_rate + calculations.INCOME_RENT_PREMIUM
  ...
  budget_m  = calculations.annual_escalate(monthly_budget, income_growth, m)
  hoa_m     = calculations.annual_escalate(hoa_monthly, cost_growth_rate, m)
  ins_m     = calculations.annual_escalate(ho6_insurance_annual / 12, cost_growth_rate, m)
  tax_m     = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, m, cost_growth_rate)
  buying_cost_m = p_and_i + pmi_m + hoa_m + tax_m + ins_m
  rent_m    = calculations.escalated_rent(market_rent, rent_growth_rate, m)

  renter_contribution = max(0.0, budget_m - rent_m)   # seeded with upfront_cash
  buyer_contribution  = max(0.0, budget_m - buying_cost_m)  # $0 seed
  buyer_surplus_list.append(buyer_contribution)
  ```
  (Rename `buyer_surplus_list` → `buyer_contrib_list` optional.)

### 4D. `url_state.py`
```python
'bud': 'MONTHLY_BUDGET',
'cg':  'COST_GROWTH_RATE',
```
(Both floats.)

### 4E. `pages/scenarios.py` *(scope decision in §3)*
Replace the fixed `monthly_contribution = max(0, total_m1 − market_rent)` with the same per-month budget loop: escalate rent, escalate budget (`rent_growth + 0.25%`), escalate HOA/insurance/assessed-value at cost-growth, `renter_contribution = max(0, budget_m − rent_m)`, buyer side via `max(0, budget_m − ownership_m)`. Reuse the engine helpers.

### 4F. `tests/test_calculations.py` (additive)
- `test_annual_escalate_*` (year-1 == base; year-2 == base×(1+g); month-12/13 boundary).
- `test_property_tax_grows_with_assessment` + `test_property_tax_growth_capped_at_3pct` (slider above 3% still capped) + homestead-from-year-2 still holds.
- Budget-surplus floor-at-0 feeding the portfolios.
- Existing portfolio tests remain valid (signatures unchanged; new tax arg is defaulted).

### 4G. PRD — `prd.md`
- **Rewrite FR17** to the budget model (both sides; renter seeded with upfront cash; budget steps annually at `rent_growth + 0.25%`; floor at $0).
- **Add input FRs** (suggested): **FR38** monthly budget slider; **FR39** annual cost-growth slider.
- **Amend FR15 / Domain section:** property-tax assessed value grows at the cost-growth rate capped at the Save Our Homes 3% ceiling; rate stays constant. Note the floor-at-$0 shortfall behavior under Assumption Transparency.

### 4H. Epics — `epics.md`
- **Amend Story 1.4 AC** (assessed-value growth + SOH cap; HOA/insurance escalation).
- **Amend Story 1.5 AC** (budget model + seed + annual step + floor at 0).
- **Amend Story 1.8 AC/notes** (input = `max(0, budget − ownership cost)`).
- **Add Story 2.9 (or 4.1): "Budget-Based Model + Cost Escalation"** — the single implementation unit: two sliders, derived income growth, escalated HOA/insurance/assessed-tax, both pages, URL params, tests.

### 4I. Architecture & UX spec — light updates
- `architecture.md`: add budget + cost-growth to the inputs inventory; note budget-based portfolio + cost-escalation flow.
- `ux-design-specification.md` (UX-DR7): Monthly Budget in the neutral group; Annual Cost Growth in the Buy group.

---

## 5. Implementation Handoff

**Scope classification: Moderate** (doc touch-up + one focused implementation story across engine, UI, URL, both pages, tests, four docs).

**Handoff plan:**
1. **PO/Dev (docs):** PRD FR17 rewrite + new input FRs + FR15/domain amendment; amend Story 1.4/1.5/1.8 AC; create the new model story in `epics.md`. Light architecture & UX-spec updates.
2. **Dev (implementation):** execute §4A–4F (and §4E if Page 2 is in scope) as one story. Verify with `python -m pytest -q` (Windows: `python`) and a `streamlit run app.py` smoke test.
3. **Validation gate (NFR5):** spot-check new trajectories against a reference spreadsheet — confirm (a) tax growth is capped at 3%, (b) escalating ownership costs partly offset the long-run "buying strengthens" effect, (c) a special-assessment month floors at $0, not negative.

**Success criteria:**
- Both pages use one shared budget model; rent, budget, HOA, insurance, and tax assessed value all escalate annually (budget at `rent_growth + 0.25%`, costs at the cost-growth rate, tax capped at 3%).
- Renter portfolio = upfront-cash seed + Σ `max(0, budget − rent)`, compounded monthly.
- Buyer side portfolio = Σ `max(0, budget − ownership cost)`, compounded monthly, on top of home equity.
- Two new sliders present and round-tripped through the URL; income growth shown as derived.
- All prior tests pass; new escalation/tax/budget tests added.

---

## 6. Change Navigation Checklist — Status
- **§1 Trigger & Context** — [x] Done (differential→budget; flat→escalating costs; new requirement from product owner)
- **§2 Epic Impact** — [x] Done (Epics 1–3 amended, none obsolete, no resequence)
- **§3 Artifact Conflicts** — [x] Done (PRD FR15/FR17 conflicts; arch/UX/code touchpoints identified)
- **§4 Path Forward** — [x] Done (Option 1 Direct Adjustment; rollback & MVP-review rejected)
- **§5 Proposal Components** — [x] Done (this document)
- **§6 Final Review & Handoff** — [!] Action-needed (awaiting Cris's approval; then update sprint status if a new story is added)

### Research sources
- HOA: [WLRN](https://www.wlrn.org/business/2025-12-05/hoa-condo-costs-florida), [Miami Herald via Haber Law](https://www.haber.law/wp-content/uploads/2024/08/Miami_condo_HOA_fees_rose_double_digits_each_year_since_2019%20_%20Miami_Herald.pdf)
- HO-6 insurance: [WLRN — condo unit insurance](https://www.wlrn.org/business/2025-09-25/condominium-unit-insurance), [JMCO — stabilizing](https://www.jmco.com/articles/real-estate/florida-home-insurance-costs-show-signs-of-stabilizing-after-years-of-increases/), [ValuePenguin HO-6](https://www.valuepenguin.com/florida-condo-insurance-ho6), [APM Research Lab](https://www.apmresearchlab.org/fl-property-insurance-crisis-five-graphs)
- Property tax: [FL DOR — Save Our Homes](https://floridarevenue.com/property/Documents/SaveOurHomes.pdf), [Palm Beach County PAO — assessment caps](https://pbcpao.gov/assessment-caps.htm)
