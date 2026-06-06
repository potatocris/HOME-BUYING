---
title: 'Three-column rent vs buy summary + rent-growth slider'
type: 'feature'
created: '2026-06-06'
status: 'done'
baseline_commit: 'f10369261d7c0beb2ce7907ec29c76250b06613c'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The main page jumps straight to a single "$X better over Y years" headline with no breakdown of what renting vs buying actually costs month-to-month or in total. The model also assumes rent never rises, which understates the true cost of renting over long horizons.

**Approach:** Add a `Rent Increase (%/yr)` slider threaded through the whole calculation model so rent escalates annually (consistently in the chart, headline, and totals). Above the existing headline, add a three-column summary: **Renting** (starting rent + total rent paid), **Buying** (Zillow-style monthly breakdown — Principal, Interest, Property Tax, Other costs — + total paid), and **Headline** (the existing card, moved into the third column).

## Boundaries & Constraints

**Always:**
- Rent escalates **annually** (step function): rent in month `m` = `base_rent * (1 + g/100) ** ((m-1)//12)`. Year 1 = base rent exactly.
- New slider is URL-encoded like every other input (round-trip shareable) with a default in `defaults.py`.
- Reuse `formatting.fmt_dollar` / `fmt_pct_compact` for all numbers — no new formatters, no raw f-string dollars.
- Outcome neutrality (UX-DR11): no red/green good-bad signaling. Match existing palette (`#2B6CB0`, `#6B46C1`, `#1A1D2E`); column cards mirror the style already in `pages/scenarios.py`.
- Monthly breakdown uses **month-1** values (snapshot, like Zillow). Period totals sum **actual** monthly amounts across all months.
- Buying "total spent" = sum of monthly payments (principal + interest + property tax + insurance + HOA + PMI). Excludes upfront cash.

**Ask First:**
- Adding rent escalation to `pages/scenarios.py` (currently out of scope — it keeps flat rent).
- Any change to how home equity, buyer surplus, or break-even are computed beyond substituting escalated rent.

**Never:**
- Do not modify `formatting.py`, the chart styling, the annual table, or the sidebar's other sliders.
- Do not add upfront cash to the buying total.
- Do not compound rent monthly (annual steps only).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Rent growth 0% | `rg=0` | Escalated rent == base rent every month; totals match flat-rent behavior | N/A |
| Rent growth 3%, month 13 | base 2000, g=3 | rent = 2000*1.03 = 2060 (year 2 starts) | N/A |
| Rent growth, month 1–12 | base 2000, g=3 | rent = 2000 (year 1, no increase yet) | N/A |
| URL round-trip | `rg=3.0` in query | decodes to `RENT_GROWTH_RATE=3.0` (float) | invalid/`inf`/`nan` → default |
| Renting column total | 10yr, g=3 | sum of 120 escalating monthly rents, fmt_dollar | N/A |

</frozen-after-approval>

## Code Map

- `defaults.py` -- add `RENT_GROWTH_RATE = 3.0` in Renting section.
- `url_state.py` -- add `'rg': 'RENT_GROWTH_RATE'` to `PARAM_MAP` (float, not in `INT_PARAMS`).
- `calculations.py` -- add pure helper `escalated_rent(base_rent, annual_growth_pct, month)`.
- `app.py` -- add slider; thread escalated rent into renter contribution + buyer surplus loop; accumulate `total_rent_paid` and `total_buying_paid`; capture month-1 breakdown; render `st.columns(3)` summary above headline; move `_headline_card` into 3rd column.
- `tests/test_calculations.py` -- add `escalated_rent` cases.
- `tests/test_url_state.py` -- existing dynamic tests auto-cover `rg` once default exists; no edit needed unless an assertion hardcodes count.
- `pages/scenarios.py` -- REFERENCE ONLY for card markup pattern; do not edit.

## Tasks & Acceptance

**Execution:**
- [x] `calculations.py` -- add `escalated_rent(base_rent, annual_growth_pct, month)` returning `base_rent * (1 + annual_growth_pct/100) ** ((month-1)//12)` -- pure, unit-testable escalation.
- [x] `defaults.py` -- add `RENT_GROWTH_RATE = 3.0` -- default for new slider.
- [x] `url_state.py` -- add `'rg': 'RENT_GROWTH_RATE'` to `PARAM_MAP` -- shareable URL state.
- [x] `app.py` -- add `Rent Increase (%/yr)` slider (min 0.0, max 10.0, step 0.25, `format="%.2f%%"`, value from `_initial`) directly after Market Rent; add to `encode_state` dict.
- [x] `app.py` -- in the calc loop, replace `market_rent` in `renter_contribution` and `buyer_surplus_list` with `calculations.escalated_rent(market_rent, rent_growth_rate, m)`; accumulate `total_rent_paid += rent_m` and `total_buying_paid += buying_cost_m`.
- [x] `app.py` -- render `st.columns(3)` above the headline: col1 Renting card (starting rent /mo + total rent paid + "+X%/yr" caption), col2 Buying card (est. payment /mo + Principal/Interest/Property Tax/Other costs rows from month-1 values + total paid), col3 the existing `_headline_card`.
- [x] `tests/test_calculations.py` -- test `escalated_rent`: year-1 flat, year-2 step, 0% growth, month-13 boundary.

**Acceptance Criteria:**
- Given rent growth = 0%, when the page renders, then the headline "$X better" value is unchanged from current flat-rent behavior.
- Given rent growth = 3% and a 10-year horizon, when the page renders, then the Renting total exceeds 120 × starting rent, and the chart/headline reflect the same escalation.
- Given the three columns, when displayed, then col2's four breakdown rows (Principal + Interest + Property Tax + Other) sum to the displayed est. monthly payment, and no row uses red/green.
- Given a shared URL with `rg=3.0`, when reopened, then the Rent Increase slider restores to 3.0%.
- Given `python -m pytest`, when run, then all tests pass (≥109 + new escalation tests).

## Design Notes

"Other costs" bundles **HOA + HO-6 insurance/12 + PMI** (month-1). At the 20% default down payment PMI is $0, so Other = HOA + insurance. P&I is fixed monthly; Principal/Interest split is taken from `schedule[0]`. Mirror the card markup in `pages/scenarios.py:189–206` (explicit `color:#1A1D2E`, `#F5F7FA` bg, `formatting.fmt_dollar`) — split the single P&I row into separate Principal and Interest rows. Label col1's rent as "Starting rent" since it escalates.

## Verification

**Commands:**
- `python -m pytest -q` -- expected: all pass, including new `escalated_rent` tests.

**Manual checks:**
- `python -m streamlit run app.py`: three columns render above headline; sliding Rent Increase up raises the Renting total, shifts the chart, and can flip the headline winner; col2 breakdown rows sum to the monthly total; sharing the URL and reopening restores the Rent Increase value.

## Suggested Review Order

**Rent escalation (the model change)**

- Pure annual-step escalation — the single source of truth for rising rent.
  [`calculations.py:129`](../../calculations.py#L129)
- Escalated rent now feeds both renter contribution and buyer surplus; totals accumulate here.
  [`app.py:273`](../../app.py#L273)

**Input plumbing**

- New slider default in the Renting/opportunity-cost block.
  [`defaults.py:22`](../../defaults.py#L22)
- Shareable URL key for the new input.
  [`url_state.py:15`](../../url_state.py#L15)
- `Rent Increase (%/yr)` slider, placed right after Market Rent.
  [`app.py:154`](../../app.py#L154)
- Slider value written to URL state.
  [`app.py:234`](../../app.py#L234)

**Three-column summary UI**

- The render: month-1 breakdown computed, then Renting · Buying · Headline columns.
  [`app.py:344`](../../app.py#L344)
- Card builders mirroring the `scenarios.py` style; P&I split into Principal + Interest.
  [`app.py:28`](../../app.py#L28)

**Tests**

- Escalation boundaries: year-1 flat, year-2 step, 0% growth, annual compounding.
  [`test_calculations.py:527`](../../tests/test_calculations.py#L527)
