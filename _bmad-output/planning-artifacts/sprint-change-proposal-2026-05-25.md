# Sprint Change Proposal — Pivot to Rent vs Buy Primary Comparison
**Date:** 2026-05-25 | **Project:** Miami Home Buying Decision Tool | **Status:** Approved

---

## Section 1: Issue Summary

**Trigger:** Strategic clarification during Epic 2 implementation. The original PRD treated the 4-down-payment scenario comparison as the primary display. After seeing the tool running, Cris identified that the real decision being made is binary — **Rent + Invest vs Buy + Invest** — and the 4-scenario comparison is a secondary analytical tool, not the main experience.

**New primary view:**
- **Option A:** Rent and invest the capital you didn't spend (down payment + monthly savings vs. buying)
- **Option B:** Buy (one chosen down payment %) and invest any monthly surplus when buying is cheaper than renting
- A **line chart** showing both options' total wealth growing over time
- An **annual breakdown table** (Year 1 through Year N)
- A **timeline slider** (5 / 10 / 15 / 20 / 25 / 30 years, step = 5)
- The 4-scenario comparison moves to a **separate Streamlit page** (code kept, polish deferred)

---

## Section 2: Impact Analysis

### Epic 1 — Financial Engine (Done, minor extension)

All calculation functions remain valid. One gap: functions are hardcoded to 60 months.

| Function | Current | Change needed |
|---|---|---|
| `calculate_amortization_schedule` | hardcoded 60 months | Accept `months` parameter |
| `calculate_investment_portfolio` | hardcoded 60 months | Accept `months` parameter |
| `calculate_buyer_investment_portfolio` | does not exist | New: monthly surplus list → compounded portfolio values |
| `get_annual_snapshots` | does not exist | New helper: extract year-end values from monthly list |

**Resolution:** Add Story 1.8 — Variable Horizon Engine Extension.

### Epic 2 — Functional Calculator (Major restructure)

| Story | Old purpose | New purpose | Action |
|---|---|---|---|
| 2.1 URL State | encode/decode | unchanged | Keep done |
| 2.2 Sidebar Sliders | 12 sliders | unchanged (timeline slider added in 2.6) | Keep done |
| 2.3 Four-Scenario Wiring | 4 scenarios × 60 months | Code stays; moves to Page 2 via story 2.4 | Keep done |
| 2.4 Monthly Cost Breakdown | 4-column monthly display | **Multi-page app setup** — move 4-scenario to `pages/scenarios.py` | Repurpose (backlog) |
| 2.5 Headline & Break-Even | fixed 5-year headline | **Rent vs Buy two-option calculation wiring** | Replace |
| 2.6 Year-5 Net Worth | point-in-time year-5 table | **Timeline slider + headline display** | Replace |
| 2.7 URL Sharing | encode/restore state | **Wealth-over-time chart** (Plotly, 2 lines) | Replace |
| 2.8 Error Handling | Chrome reliability | **Annual wealth breakdown table** | Replace |
| 2.9 (new) | — | **URL sharing** — updated param set for new inputs | Add |
| 2.10 (new) | — | **Error handling** — Chrome reliability (unchanged scope) | Add |

### Epic 3 — UX Polish (Moderate changes)

| Story | Change |
|---|---|
| 3.1 Theme | None |
| 3.2 DisclaimerBanner | None |
| 3.3 Sidebar Polish | Minor — add timeline slider to grouping |
| 3.4 HeadlineCard | Update: rent vs buy verdict at selected horizon |
| 3.5 ScenarioColumn ×4 | Replace → **Chart & Table Polish** (line chart styling, annual table formatting) |
| 3.6 ExitPathsTable | Replace → **Page 2 Polish** (4-scenario page; deferred, low priority) |
| 3.7 Number Formatting | None |
| 3.8 Accessibility | None |

### PRD updates needed

| Section | Change |
|---|---|
| "What Makes This Special" | Primary differentiator is now variable-horizon rent vs buy chart; 4-scenario comparison is a secondary page |
| FR22 | Single down payment slider; 4-scenario view on Page 2 |
| FR23–FR27 | Fixed 5-year horizon → selected horizon (5–30 years) |
| FR38 (new) | Line chart: two wealth lines over time, updates in real time |
| FR39 (new) | Annual breakdown table: Year 1–N showing rent wealth, buy wealth, difference |
| FR40 (new) | Timeline slider: 5 / 10 / 15 / 20 / 25 / 30 years |
| FR41 (new) | Multi-page app: Page 2 = 4-scenario comparison (code from 2.3/2.4, deferred polish) |

### Architecture updates needed

| Area | Change |
|---|---|
| App structure | Add `pages/` directory; create `pages/scenarios.py` |
| Chart library | Add `plotly` to `requirements.txt` |
| Calculation model | Variable horizon; buyer's side-investment portfolio |
| URL params | Add `yr` (horizon years); down payment uses existing `dp` as single value |

---

## Section 3: Recommended Approach

**Direct Adjustment — no rollback required.**

Epic 1 work is entirely valid and salvageable with one small extension story. Stories 2.1 and 2.2 stay done. Code from stories 2.3 and 2.4 moves intact to `pages/scenarios.py` — no work is discarded, only repositioned.

**Effort:** Medium (~4–5 implementation sessions for new Epic 2 stories)
**Risk:** Low — same financial model, reorganized and extended
**Timeline impact:** +2 stories in Epic 2 (2.9, 2.10); existing 2.5–2.8 rewritten to new scope

---

## Section 4: Revised Story Definitions

### Story 1.8: Variable Horizon Engine Extension

**As a developer**, I want the financial engine to support any time horizon up to 30 years,
so that the Rent vs Buy chart and table can show growth over any selected period.

**Acceptance Criteria:**
- `calculate_amortization_schedule(price, down_pct, annual_rate, months=360)` — `months` is now a parameter; existing callers passing no `months` still work (backward compatible)
- `calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=360)` — same pattern
- New `calculate_buyer_investment_portfolio(monthly_surplus_list, annual_rate)` — accepts a list of per-month surplus amounts (max(0, rent − buying_cost) for each month), compounds monthly, returns list of portfolio values equal in length to input list
- New `get_annual_snapshots(monthly_values)` — returns a list of values sampled at months 12, 24, 36… (one value per year); length = len(monthly_values) // 12
- All new/modified functions covered by unit tests
- `calculations.py` remains zero Streamlit imports

---

### Story 2.4 (Repurposed): Multi-Page App Setup

**As a developer**, I want the existing 4-scenario comparison to live on a dedicated second page,
so that the main page can be rebuilt as the Rent vs Buy primary view without losing existing work.

**Acceptance Criteria:**
- `pages/` directory created in project root
- `pages/scenarios.py` created; all 4-scenario calculation and display code moved from `app.py` to this file
- `pages/scenarios.py` renders identically to today's main page (no regression)
- `app.py` main area is cleared (sidebar stays; main area shows placeholder or empty layout ready for new stories)
- Streamlit multipage navigation works: both "Home" (`app.py`) and "Scenario Comparison" (`pages/scenarios.py`) accessible via sidebar nav
- No test regressions — all existing tests pass

---

### Story 2.5 (Revised): Rent vs Buy Two-Option Calculation Wiring

**As a user**, I want the tool to compute both paths — renting+investing and buying+investing — over the selected horizon,
so that the chart and table have accurate data to display.

**Acceptance Criteria:**
- For a single selected down payment % and selected horizon (years):
  - Full amortization schedule computed over `horizon_years × 12` months
  - **Renter path:** portfolio compounds initial capital (upfront cash) + monthly contribution of max(0, buying_cost_m − rent) each month
  - **Buyer path:** side portfolio compounds monthly surplus of max(0, rent − buying_cost_m) each month; home equity = appreciated value − remaining balance at each month
  - Buyer total wealth per month = home equity + buyer side portfolio
  - Renter total wealth per month = renter portfolio value
- Annual snapshots produced for both paths (one value per year, via `get_annual_snapshots`)
- All four datasets (renter monthly, buyer monthly, renter annual, buyer annual) computed before any display call
- Calculations use real per-month buying cost (P&I + PMI + HOA + tax + insurance); PMI cancels at correct month

---

### Story 2.6 (Revised): Timeline Slider + Headline Display

**As a user**, I want a timeline slider and a plain-English headline telling me which path wins over my selected horizon,
so that I can immediately see the key verdict at the timeframe that matters to me.

**Acceptance Criteria:**
- Timeline slider in sidebar: values 5, 10, 15, 20, 25, 30 (step=5, label shows "years"); defaults to 10
- Headline in main area: "**Renting is better by $X over Y years**" or "**Buying is better by $X over Y years**"
- Sub-line: "Break-even at year N" or "No break-even within Y years"
- Renting-wins and buying-wins headlines use identical CSS (no color difference)
- All elements update in real time on any slider change

---

### Story 2.7 (Revised): Wealth-Over-Time Chart

**As a user**, I want a line chart showing how both options' total wealth grow over time,
so that I can see not just the final outcome but the whole trajectory of the decision.

**Acceptance Criteria:**
- Plotly line chart rendered in main area below headline
- Two lines: "Rent + Invest" and "Buy + Invest"
- X-axis: Year 0 through selected horizon; Y-axis: total net wealth ($)
- If the lines cross within the horizon, a marker or annotation labels the crossover point ("Break-even: year N")
- Chart title describes what is being shown (e.g., "Total wealth over time")
- Dollar amounts on Y-axis formatted with $ and comma separator
- Chart updates in real time on any slider change

---

### Story 2.8 (Revised): Annual Wealth Breakdown Table

**As a user**, I want a year-by-year table comparing both paths,
so that I can see exactly how the wealth gap evolves each year.

**Acceptance Criteria:**
- Table displayed below chart with columns: Year | Rent + Invest | Buy + Invest | Difference | Better
- Rows from Year 1 to selected horizon (matches timeline slider)
- "Better" column shows "Renting" or "Buying" as plain text (no color coding)
- Dollar amounts formatted: nearest dollar, $ prefix, comma separator, parentheses for negatives
- Table updates in real time on any slider change

---

### Story 2.9 (Shifted): URL Sharing & Page Load State Restore

*(Unchanged scope from original 2.7 — shifted to accommodate new stories)*

Updated param set: adds `yr` for horizon years; `dp` now carries a single down payment % value.

---

### Story 2.10 (Shifted): Error Handling & Chrome Reliability

*(Unchanged scope from original 2.8 — shifted to accommodate new stories)*

---

## Section 5: Implementation Handoff

**Scope: Moderate — Developer + Product Owner**

| Action | Owner | Priority |
|---|---|---|
| Update PRD (FR22, FR23–27, add FR38–41) | Cris via `/bmad-edit-prd` | Before Story 2.5 |
| Update Architecture (multi-page, Plotly) | Developer during Story 2.4 | Before Story 2.4 |
| Create Story 1.8 | Developer | **First** — unblocks 2.5 |
| Create Story 2.4 | Developer | Second |
| Continue: 2.5 → 2.6 → 2.7 → 2.8 → 2.9 → 2.10 | Developer | Sequential |

**Immediate next step:** Create Story 1.8 — Variable Horizon Engine Extension.
