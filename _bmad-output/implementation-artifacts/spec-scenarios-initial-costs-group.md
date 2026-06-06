---
title: 'Scenarios Page — Per-Scenario Initial Costs Group'
type: 'feature'
created: '2026-06-06'
status: 'done'
route: 'one-shot'
---

# Scenarios Page — Per-Scenario Initial Costs Group

## Intent

**Problem:** Each of the 4 down-payment scenario cards on the Scenarios page (Page 2) showed only a single `Upfront: $X` figure and the recurring monthly-cost table. There was no breakdown of what the upfront/initial costs actually consist of, so the four down-payment options couldn't be compared on their initial-cost composition.

**Approach:** Add a grouped "Initial Costs" table to each scenario card showing Home Price, Loan Amount (muted context rows), then Down Payment, Improvements, Closing Fees, and a bold "Cash Needed" total that ties out exactly to the existing `upfront_cash`. Values are derived inside the existing per-scenario loop; the pre-existing `Upfront:` line is kept. Context rows (Home Price, Loan Amount) are visually separated from the cash-additive rows so the column sums correctly to Cash Needed.

## Suggested Review Order

1. [`../../pages/scenarios.py` — initial-costs derivation](../../pages/scenarios.py) — the `initial_costs` dict built in the scenario loop; confirm `cash_needed == down_payment + closing_fees + improvements` and that it equals `upfront_cash`.
2. [`../../pages/scenarios.py` — card render block](../../pages/scenarios.py) — the new Initial Costs `<table>`: muted context rows (Home Price, Loan Amount), separator, cash-additive rows, bold Cash Needed total.
3. [`deferred-work.md` — deferred findings](./deferred-work.md) — the DRY duplication (#6) and table a11y semantics (#8) deferred from the adversarial review.
