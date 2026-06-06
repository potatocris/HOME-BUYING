---
title: 'Summary header budget line + buying cost breakdown + renting card reorder'
type: 'feature'
created: '2026-06-06'
status: 'done'
baseline_commit: '3c4f2ef'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The monthly budget driving the whole model is buried in the sidebar; the buying card hides HOA/insurance/PMI behind one opaque "Other costs" row; and the renting card's order/contents don't tell a clear cost-then-investment story.

**Approach:** Three display-only changes to the main page (`app.py`): (1) add a budget line under the title, (2) expand the buying card's "Other costs" into its three components, and (3) reorder the renting card and add Total returns + Net total rows. No calculation, defaults, or URL-state changes.

## Boundaries & Constraints

**Always:** Route every dollar/percent through `formatting.fmt_dollar` / `fmt_pct_compact` (single source of truth, UX-DR10). Keep cards outcome-neutral (UX-DR11): Renting `#2B6CB0`, Buying `#6B46C1`, body text explicit `#1A1D2E`; no red/green. Negatives render as `($X)` via `fmt_dollar` (never `$-X`). Use values already computed in the calc block.

**Ask First:** Any change to `calculations.py`, `defaults.py`, `url_state.py`, or `pages/scenarios.py`. Adding Total returns / Net total to the *buying* card (not requested — confirm before doing).

**Never:** New sliders, new URL keys, new modules. Changing the wealth model or the chart/table. Touching the sidebar layout.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Budget line | `monthly_budget = 3500.0` | Line under title reads "Monthly budget: $3,500" | N/A |
| Buying cost breakdown | `hoa=350, ho6=2400/yr, pmi>0` | Card lists HOA $350, HO-6 Insurance $200, PMI $X as separate rows | N/A |
| Net total negative | renter Total returns $420,000, total rent $540,000 | Net total renders "($120,000)" — neutral color, parentheses | N/A |
| PMI absent | `down_pct >= 20` → `pmi == 0` | PMI row shows "$0" (row still present) | N/A |
| Calc error | `_calc_error == True` | Cards not rendered (existing error path unchanged) | Existing st.error |

</frozen-after-approval>

## Code Map

- `app.py:394` -- `st.title(...)`; insert budget line immediately after.
- `app.py:28-42` -- `_renting_card(...)`; reorder + add Total returns, Net total (signature change).
- `app.py:45-66` -- `_buying_card(...)`; replace `other` param with `hoa`, `insurance`, `pmi` (signature change).
- `app.py:416-423` -- `final_renter` computed here; available for renting card.
- `app.py:426-448` -- three-column render block; update call sites + month-1 cost vars.
- `formatting.py` -- `fmt_dollar` (handles negatives as `($X)`), `fmt_pct_compact`.

## Tasks & Acceptance

**Execution:**
- [x] `app.py` -- After `st.title("Miami Home Buying Decision Tool")` (line 394), add a markdown line: `Monthly budget: <strong>{formatting.fmt_dollar(monthly_budget)}</strong>`, color `#1A1D2E`, small top-negative margin to sit snug under the title. -- Surfaces the model's key driver.
- [x] `app.py` -- `_buying_card`: replace the single `other` param with `hoa`, `insurance`, `pmi`; in the table replace the "Other costs" row with three rows: "HOA", "HO-6 Insurance", "PMI" (each through `fmt_dollar`). Update the call site (line 441) to pass `hoa_monthly`, `ins_m1`, `rec0["pmi"]` instead of `other_m1`. Drop the now-unused `other_m1` var and its comment. -- Itemizes the opaque bundle.
- [x] `app.py` -- `_renting_card`: reorder to Monthly cost (starting rent + "grows X%/yr" caption) → Total cost (total rent over period) → Monthly invested (start) → Total returns over period → Net total. Add params `total_returns` (= `final_renter`) and `net_total` (= `final_renter - total_rent_paid`); render both via `fmt_dollar`. Update call site (line 436) accordingly. -- Tells cost-then-investment story; Net total can be negative.

**Acceptance Criteria:**
- Given the app loads with default inputs, when the main page renders, then a "Monthly budget: $3,500" line appears directly under the title and updates live when the Monthly Budget slider moves.
- Given a down payment < 20% (PMI active), when the buying card renders, then HOA, HO-6 Insurance, and PMI each appear as their own right-aligned dollar rows and their sum equals the previous "Other costs" figure.
- Given any horizon, when the renting card renders, then rows appear top-to-bottom in the order: Monthly cost, Total cost, Monthly invested, Total returns, Net total; Total returns equals the blue chart line's final value and Net total equals Total returns minus Total cost.
- Given Net total is negative, when rendered, then it shows as `($X)` in neutral text (no red/green, no `$-X`).

## Design Notes

`final_renter` (= `renter_annual[-1]`) and `total_rent_paid` already exist in the calc block before the render at line 434, so both renting-card additions need no new computation. The renting card's "Total returns" intentionally shows the full ending portfolio value (user decision), and "Net total" is that minus total rent paid (user decision) — these are distinct rows, not duplicates.

Renting card body sketch (order only; match existing inline-style idiom):
```
Renting (header, #2B6CB0)
$X /mo        — "Starting rent · grows Y%/yr"
Total rent over N years        $X
Invested monthly (start)       $X /mo
Total returns over N years     $X
Net total                      ($X)
```

## Verification

**Commands:**
- `python -m pytest -q` -- expected: existing suite still green (no engine changes; ~113 tests pass).

**Manual checks:**
- `streamlit run app.py` -- confirm: budget line under title tracks the slider; buying card shows HOA/HO-6 Insurance/PMI rows summing to the old "Other costs"; renting card row order matches spec; set down payment high + long horizon to force a negative Net total and confirm `($X)` neutral rendering.

## Suggested Review Order

**Title budget line**

- Entry point — new line under the title surfaces the model's key driver, reusing the live slider var.
  [`app.py:408`](../../app.py#L408)

**Buying card cost breakdown**

- Signature swaps `other` for `hoa`/`insurance`/`pmi`; table now itemizes the three rows.
  [`app.py:53`](../../app.py#L53)

- Call site passes `hoa_monthly`, `ins_m1`, `rec0["pmi"]`; `buying_total_m1` sums them inline (old `other_m1` removed).
  [`app.py:447`](../../app.py#L447)

**Renting card reorder + new rows**

- Reordered rows + `total_returns`/`net_total` params; net total may be negative → `fmt_dollar` renders `($X)`.
  [`app.py:28`](../../app.py#L28)

- Call site passes `final_renter` and `final_renter - total_rent_paid` (both already computed upstream).
  [`app.py:451`](../../app.py#L451)
