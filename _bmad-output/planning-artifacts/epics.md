---
stepsCompleted: ["step-01-validate-prerequisites", "step-02-design-epics", "step-03-create-stories", "step-04-final-validation"]
status: complete
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
  - "_bmad-output/planning-artifacts/ux-design-specification.md"
---

# Miami Home Buying Decision Tool - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for the Miami Home Buying Decision Tool, decomposing requirements from the PRD, Architecture, and UX Design Specification into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: User can set home purchase price via slider
FR2: User can set mortgage interest rate (30-year fixed) via slider
FR3: User can set monthly HOA fee via slider
FR4: User can set annual homeowner's insurance cost (HO-6) via slider
FR5: User can set property tax rate via slider
FR6: User can set monthly market rent via slider
FR7: User can set expected annual investment return rate via slider
FR8: User can set expected annual home appreciation rate via slider
FR9: User can set closing cost percentage via slider
FR10: User can set furniture and improvements budget via slider
FR11: User can set a one-time special assessment dollar amount and the specific month it occurs
FR12: User can set landlord scenario inputs: expected monthly rental income, vacancy rate, and property management fee percentage
FR13: The system calculates a full 60-month amortization schedule for each down payment scenario, tracking principal, interest, and remaining loan balance month by month
FR14: The system automatically cancels PMI when the loan balance reaches 78% of the original purchase price
FR15: The system applies the Florida homestead exemption ($50,000 assessed value deduction) to property tax starting in year 2; year-1 taxes calculated on full assessed value
FR16: The system calculates total upfront cash as the sum of down payment, closing costs, and furniture/improvements
FR17: The system models the renter's investment portfolio as down payment capital plus monthly savings (when renting costs less than buying), compounded at the user-set return rate over 60 months
FR18: The system applies the special assessment as a single lump-sum cash outflow at the user-specified month
FR19: The system calculates year-5 sell exit value as gross sale price minus realtor commission (user-configurable, default 5.5%) and Florida documentary stamp tax (~0.7%)
FR20: The system calculates year-5 rent-out exit as cumulative net cash flow (rental income minus vacancy, management fee, and carrying costs) plus remaining equity
FR21: The system calculates year-5 continue-renting exit as the renter's accumulated investment portfolio value
FR22: The system displays all four down payment scenarios (5%, 10%, 15%, 20%) simultaneously without requiring re-entry of inputs
FR23: The system displays a plain-language headline identifying which path is financially better and by how much (e.g., "Renting is better by $12,400 over 5 years")
FR24: The system displays a monthly cost breakdown per down payment scenario: mortgage (P&I), PMI, HOA, property tax, insurance, and total
FR25: The system displays net worth at year 5 for all three exit paths across all four down payment scenarios
FR26: The system distinguishes liquid assets (investment portfolio) from illiquid assets (home equity) in all net worth comparisons
FR27: The system displays break-even month per down payment scenario in plain language
FR28: All outputs update in real time on any slider change, without page reload
FR29: The system pre-populates all sliders with Miami-specific defaults on first load
FR30: The system displays the date Miami-specific defaults were last reviewed
FR31: The system displays a permanent disclaimer: financial calculator, no lender affiliation, not financial advice
FR32: The disclaimer is visible without scrolling on first load
FR33: The system encodes all current slider values into the page URL on any input change
FR34: The system decodes slider values from the URL on page load, restoring the exact scenario
FR35: Any person opening a shared URL can interact with all sliders without an account or login
FR36: The headline correctly identifies the financially superior path regardless of direction — renting wins are stated as renting wins
FR37: Every numerical output is traceable to a visible, user-adjustable input — no hidden constants or undisclosed assumptions
FR38: User can set a monthly income/budget via slider; income grows annually at the rent-growth rate + 0.25 pct-pts (derived) — *added via Sprint Change 2026-06-06*
FR39: User can set an annual cost-growth rate via slider, applied to HOA, HO-6 insurance, and the property-tax assessed value — *added via Sprint Change 2026-06-06*

### NonFunctional Requirements

NFR1: Initial page load completes within 30 seconds on Streamlit Cloud, including cold start
NFR2: Any slider interaction produces updated outputs within 1 second
NFR3: URL state encoding and decoding completes in under 100ms
NFR4: Total URL length (all slider values as query parameters) must not exceed 2,000 characters
NFR5: Amortization schedule output must match a verified reference implementation within $1 per month
NFR6: PMI cancellation fires in the first month the loan balance falls at or below 78% of original purchase price
NFR7: Year-5 net worth figures must reconcile — sum of all monthly cash flows plus terminal asset values equals the displayed net worth
NFR8: Renter's investment portfolio compounds monthly, not annually
NFR9: The tool functions correctly in the current stable version of Google Chrome on desktop
NFR10: No calculation error or unhandled exception produces a visible incorrect output — failures display a clear error message or fall back to default state

### Additional Requirements

- ARCH-1: Set up Python virtual environment (Python 3.10–3.14) with Streamlit latest stable; create `requirements.txt` with pinned dependencies
- ARCH-2: Create modular project structure: `app.py` (Streamlit UI entry), `calculations.py` (financial engine), `defaults.py` (Miami defaults + last-updated date), `url_state.py` (encode/decode + URL length validation), `requirements.txt`
- ARCH-3: `calculations.py` must contain zero Streamlit imports — pure Python only, enabling independent unit testing against a reference spreadsheet
- ARCH-4: `defaults.py` must be isolated from the engine so Miami-specific values can be updated without touching calculation logic
- ARCH-5: `url_state.py` must validate that serialized URL length does not exceed 2,000 characters; abbreviate parameter keys as needed

### UX Design Requirements

UX-DR1: Implement Streamlit `config.toml` theme with Design Direction A tokens — `primaryColor = "#2B6CB0"`, `backgroundColor = "#FFFFFF"`, `secondaryBackgroundColor = "#F5F7FA"`, `textColor = "#1A1D2E"`
UX-DR2: Implement Split View layout — `st.sidebar` contains all 12 input sliders; main area contains headline, 4-column comparison, and exit paths table
UX-DR3: Build HeadlineCard custom component — large dollar amount (~2.5rem, weight 700, `#2B6CB0`), label text, result text ("Renting/Buying is better by X over 5 years"), best-scenario note; buying-wins and renting-wins states visually identical
UX-DR4: Build ScenarioColumn custom component × 4 — header (down %, upfront cost), monthly total, line items (P&I → PMI → HOA → Tax → Insurance → Total), break-even month; "best" state adds `#2B6CB0` border and `#EBF4FF` background
UX-DR5: Build ExitPathsTable custom component — 3 exit paths × 4 scenarios; "Continue renting" row distinguished as liquid/investment portfolio via label text, not color
UX-DR6: Build DisclaimerBanner — `#EBF4FF` strip visible on first load without scrolling; left: disclaimer text; right: "Defaults last updated: [date]"
UX-DR7: Implement sidebar input grouping — Essential Inputs section (always visible: home price, rate, HOA, rent, appreciation, investment return, closing costs, furniture) + Advanced Inputs section (in `st.expander`: special assessment amount + month, landlord inputs, realtor commission)
UX-DR8: Implement slider label format — label name left-aligned, current value right-aligned on same line; range hints at track ends for non-obvious ranges
UX-DR9: Display "Miami defaults loaded" caption below Essential Inputs subheader in sidebar on first load
UX-DR10: Enforce number formatting — dollar amounts nearest dollar with comma separator and $ prefix; percentages to 2 decimal places with % suffix; months as "month N"; negative values as parentheses not minus sign
UX-DR11: Enforce outcome neutrality — no red/green color for any outcome; "Best" badge uses `#2B6CB0` accent only; renting-wins and buying-wins headline states use identical CSS
UX-DR12: Add `aria-label` attributes to all custom HTML components (HeadlineCard, ScenarioColumn, ExitPathsTable, DisclaimerBanner)
UX-DR13: Enforce display consistency — all 4 scenario columns always visible simultaneously (no tabs/hiding); line items in fixed order P&I → PMI → HOA → Tax → Insurance; exit paths in fixed order Sell → Rent Out → Continue Renting

### FR Coverage Map

| Requirement | Epic | Rationale |
|---|---|---|
| FR1–FR12 | Epic 2 | All 12 slider inputs — part of functional calculator |
| FR13–FR21 | Epic 1 | Financial engine calculations (amortization, PMI, exit paths) |
| FR22–FR29 | Epic 2 | Display, real-time updates, Miami defaults pre-population |
| FR30 | Epic 3 | Defaults last-updated date — transparency requirement |
| FR31–FR32 | Epic 3 | Disclaimer visible on load — trust requirement |
| FR33–FR35 | Epic 2 | URL encode/decode/share — core calculator feature |
| FR36–FR37 | Epic 3 | Unbiased output, traceable numbers — integrity requirements |
| NFR1–NFR4 | Epic 2 | Performance targets (load, slider response, URL budget) |
| NFR5–NFR8 | Epic 1 | Financial correctness targets (amortization accuracy, PMI, compounding) |
| NFR9–NFR10 | Epic 2 | Chrome reliability, error fallback |
| ARCH-1–5 | Epic 1 | Project setup and modular structure |
| UX-DR1–13 | Epic 3 | Full UX spec implementation (theme, layout, components, formatting)

## Epic List

### Epic 1: Project Foundation & Verified Financial Engine

**Goal:** Establish the project scaffold and build a verified, pure-Python financial calculation engine that produces accurate results before any UI is wired up.

**Requirements covered:** ARCH-1, ARCH-2, ARCH-3, ARCH-4, ARCH-5, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, NFR5, NFR6, NFR7, NFR8

---

### Story 1.1: Project Scaffold & Module Structure

As a developer,
I want a working project scaffold with all required module files and pinned dependencies,
So that I can run the app locally and have a clean structure to build into.

**Acceptance Criteria:**

**Given** I have Python 3.10–3.14 installed
**When** I follow the setup steps (create venv, `pip install -r requirements.txt`)
**Then** `streamlit run app.py` launches without error (placeholder page is fine)
**And** the project contains exactly these files: `app.py`, `calculations.py`, `defaults.py`, `url_state.py`, `requirements.txt`
**And** `calculations.py` contains zero Streamlit imports (verifiable by search)
**And** `requirements.txt` has pinned version numbers for all dependencies (e.g., `streamlit==X.X.X`)

---

### Story 1.2: Miami Defaults Module

As a developer,
I want a single isolated `defaults.py` file containing all Miami-specific input values and a last-reviewed date,
So that Miami defaults can be updated without touching any calculation logic.

**Acceptance Criteria:**

**Given** `defaults.py` exists in the project root
**When** it is imported in Python
**Then** it exposes constants for all 12 slider inputs: home price, mortgage rate, HOA, HO-6 insurance, property tax rate, market rent, investment return rate, home appreciation rate, closing cost %, furniture budget, special assessment amount + month, rental income, vacancy rate, property management fee %, and realtor commission %
**And** it exposes a `DEFAULTS_LAST_UPDATED` string constant in `"Month YYYY"` format
**And** `defaults.py` contains no Streamlit imports and no calculation logic
**And** changing any value in `defaults.py` requires no changes to `calculations.py` or any other module

---

### Story 1.3: Amortization Schedule Engine

As a developer,
I want `calculations.py` to produce a verified 60-month amortization schedule for any down payment scenario,
So that all monthly cost and equity figures are based on accurate, testable mortgage math.

**Acceptance Criteria:**

**Given** a home purchase price, down payment %, and annual interest rate
**When** `calculate_amortization_schedule(price, down_pct, annual_rate)` is called
**Then** it returns a list of 60 monthly records, each containing: month number, principal paid, interest paid, remaining loan balance, and PMI amount
**And** each monthly P&I payment matches the standard amortization formula within $0.01
**And** results match a verified reference spreadsheet within $1.00 per month on every row (NFR5)
**And** PMI is included in any month where the loan balance exceeds 78% of the original purchase price
**And** PMI is $0 in the first month the loan balance is ≤ 78% of original purchase price, and remains $0 for all subsequent months (NFR6)
**And** the function accepts plain Python numbers only — no Streamlit objects

---

### Story 1.4: Florida Cost & Upfront Cash Engine

As a developer,
I want `calculations.py` to correctly model Florida-specific property costs and total upfront cash requirements,
So that the calculator reflects Miami's real cost structure.

**Acceptance Criteria:**

**Given** purchase price, property tax rate, closing cost %, and furniture budget
**When** monthly property costs are calculated for a given month number
**Then** months 1–12 use the full assessed value for property tax
**And** months 13–60 apply the $50,000 Florida homestead exemption deduction before calculating property tax (FR15)
**When** `calculate_upfront_cash(price, down_pct, closing_pct, furniture)` is called
**Then** it returns exactly: down payment + (price × closing_pct) + furniture budget (FR16)
**And** all functions accept plain Python numbers — no Streamlit imports

> **Amended by Sprint Change 2026-06-06:** The property-tax *rate* stays constant, but the *assessed value* now grows annually at the cost-growth rate, capped at 3%/yr (Save Our Homes). HOA and HO-6 insurance also escalate annually at the cost-growth rate. `calculate_monthly_property_tax` gains an `assessment_growth_pct` argument (defaulted for back-compat). See `sprint-change-proposal-2026-06-06.md` §4B/§4F.

---

### Story 1.5: Investment Portfolio & Special Assessment Engine

As a developer,
I want `calculations.py` to model the renter's investment portfolio with monthly compounding and apply special assessments at the correct month,
So that the opportunity cost comparison is financially accurate.

**Acceptance Criteria:**

**Given** initial capital (down payment amount), monthly contribution, annual return rate, and 60-month horizon
**When** `calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months)` is called
**Then** it returns a list of 60 portfolio values, one per month
**And** compounding is applied monthly: `monthly_rate = annual_rate / 12` (NFR8)
**And** month 1 value = `(initial_capital + monthly_contribution) × (1 + monthly_rate)`
**And** each subsequent month compounds the previous balance plus the new contribution
**When** `special_assessment_amount > 0` and `special_assessment_month` is between 1 and 60
**Then** the buyer's cash outflow for that specific month includes the special assessment as a lump sum (FR18)
**And** the special assessment affects no other month

> **Amended by Sprint Change 2026-06-06:** The opportunity-cost model changes from differential to **fixed-budget**. The renter portfolio is seeded with the upfront cash and each month adds `max(0, budget − rent)`; the buyer side-portfolio (engine Story 1.8) each month adds `max(0, budget − total ownership cost)`. The budget steps up once per year at the income-growth rate (`rent_growth + 0.25%`); monthly contributions floor at $0. Implemented under **Epic 4 / Story 4.1**. See `sprint-change-proposal-2026-06-06.md`.

---

### Story 1.6: Year-5 Exit Path Calculations

As a developer,
I want `calculations.py` to compute all three year-5 exit path values for a given scenario,
So that the net worth comparison across Sell, Rent Out, and Continue Renting is accurate and reconcilable.

**Acceptance Criteria:**

**Given** a completed 60-month amortization schedule and the scenario inputs
**When** `calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct)` is called
**Then** it returns: appreciated home value − realtor commission − Florida documentary stamp tax (0.70% of sale price) − remaining loan balance (FR19)
**When** `calculate_exit_rent_out(monthly_rental_income, vacancy_rate, mgmt_fee_pct, monthly_carrying_costs, remaining_balance)` is called
**Then** it returns: cumulative net rental cash flow over 60 months + remaining equity at month 60 (FR20)
**When** `calculate_exit_continue_renting(portfolio_values)` is called
**Then** it returns the portfolio value at month 60 (FR21)
**And** for every scenario, the displayed net worth reconciles: sum of all monthly cash flows + terminal asset value = net worth figure (NFR7)
**And** all functions accept plain Python numbers — no Streamlit imports

---

### Epic 2: Functional Calculator — Inputs, Real-Time Display & URL Sharing

**Goal:** Deliver a fully working calculator where all 12 sliders drive real-time outputs across 4 scenarios, Miami defaults pre-populate on load, URL state encoding/decoding enables sharing, and all performance and reliability targets are met.

**Requirements covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR11, FR12, FR22, FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR33, FR34, FR35, NFR1, NFR2, NFR3, NFR4, NFR9, NFR10

---

### Story 2.1: URL State Module (Encode/Decode + Budget Validation)

As a developer,
I want `url_state.py` to encode all slider values into a URL query string and decode them back reliably,
So that the URL sharing feature has a tested, validated foundation before the UI is wired up.

**Acceptance Criteria:**

**Given** a dictionary of all 12 slider values
**When** `encode_state(slider_values)` is called
**Then** it returns a URL query string with abbreviated parameter keys (e.g., `hp` for home price)
**And** the total encoded URL length does not exceed 2,000 characters (NFR4)
**And** if encoded length would exceed 2,000 characters, the function raises a clear error rather than silently truncating (ARCH-5)
**When** `decode_state(query_params)` is called with the encoded parameters
**Then** it returns a dictionary matching the original slider values
**And** any missing or invalid parameter falls back to the Miami default without raising an exception
**And** encoding and decoding each complete in under 100ms (NFR3)
**And** `url_state.py` contains no calculation logic — encode/decode only

---

### Story 2.2: Sidebar Input Sliders with Miami Defaults

As a user,
I want all 12 input sliders pre-populated with Miami-specific defaults when I first open the tool,
So that I immediately see a realistic Miami scenario without entering any data.

**Acceptance Criteria:**

**Given** the tool loads with no URL parameters
**When** the page renders
**Then** `st.sidebar` displays all 12 sliders grouped into Essential Inputs (always visible) and Advanced Inputs (in `st.expander`)
**And** Essential Inputs contains: home price, mortgage rate, HOA, market rent, home appreciation, investment return, closing costs %, furniture budget
**And** Advanced Inputs contains: special assessment amount + month, rental income, vacancy rate, property management fee %, realtor commission %
**And** all sliders are pre-populated with values from `defaults.py` (FR29)
**And** each slider has an appropriate min, max, and step size reflecting realistic Miami ranges
**And** any slider change triggers an immediate Streamlit rerun producing updated outputs within 1 second (NFR2)

---

### Story 2.3: Four-Scenario Real-Time Calculation Wiring

As a user,
I want the tool to simultaneously compute results for all four down payment scenarios whenever I adjust any slider,
So that I can compare 5%, 10%, 15%, and 20% down side-by-side without re-entering anything.

**Acceptance Criteria:**

**Given** all 12 sliders are set (defaults or user values)
**When** any slider value changes
**Then** `calculations.py` functions are called for all four scenarios (5%, 10%, 15%, 20% down) within a single Streamlit rerun
**And** all four results are computed before any output is rendered
**And** the full cycle (slider change → recalculation → display refresh) completes within 1 second (NFR2)
**And** no scenario requires re-entry of inputs — all four share the same slider values (FR22)
**And** the tool functions correctly in the current stable version of Google Chrome on desktop (NFR9)

---

### Story 2.4: Monthly Cost Breakdown Display

As a user,
I want to see a detailed monthly cost breakdown for each down payment scenario,
So that I understand exactly what I would pay each month and how costs differ by scenario.

**Acceptance Criteria:**

**Given** calculations have run for all four scenarios
**When** the main area renders
**Then** each scenario column displays monthly line items in fixed order: P&I → PMI → HOA → Property Tax → Insurance → Total (FR24)
**And** PMI shows as $0 for the 20% down scenario (no PMI at 80% LTV)
**And** all dollar amounts are formatted as nearest dollar with $ prefix and comma separator (e.g., $1,234)
**And** home equity is labeled as illiquid and the investment portfolio as liquid wherever assets are displayed (FR26)
**And** all values update in real time on any slider change (FR28)

---

### Story 2.5: Headline & Break-Even Display

As a user,
I want a plain-language headline telling me which path is financially better and by how much, plus break-even months per scenario,
So that the key insight is immediately visible without reading tables.

**Acceptance Criteria:**

**Given** calculations have run for all four scenarios
**When** the main area renders
**Then** a headline displays which path is superior and by how much over 5 years (FR23), e.g., "Renting is better by $12,400 over 5 years"
**And** the headline correctly identifies the superior path regardless of direction — renting wins are stated as renting wins, buying wins as buying wins (FR36)
**And** each scenario column displays the break-even month in plain language, e.g., "Break-even: month 43" (FR27)
**And** if break-even does not occur within 60 months, the display reads "No break-even within 5 years"
**And** all values update in real time on any slider change (FR28)

---

### Story 2.6: Year-5 Net Worth Display (All Exit Paths, All Scenarios)

As a user,
I want to see year-5 net worth for all three exit paths across all four scenarios in one table,
So that I can evaluate long-term outcomes across every combination at a glance.

**Acceptance Criteria:**

**Given** calculations have run for all four scenarios
**When** the exit paths section renders
**Then** a table displays 3 rows × 4 columns: rows are Sell, Rent Out, Continue Renting; columns are 5%, 10%, 15%, 20% down (FR25)
**And** exit paths appear in fixed order: Sell → Rent Out → Continue Renting
**And** the "Continue Renting" row is labeled to indicate it represents a liquid investment portfolio (FR26)
**And** all net worth values are formatted as nearest dollar with $ prefix and comma separator
**And** negative values display with parentheses, not a minus sign, e.g., ($3,200)
**And** all values update in real time on any slider change (FR28)

---

### Story 2.7: URL Sharing & Page Load State Restore

As a user,
I want the URL to automatically reflect my current slider values so I can share or bookmark my exact scenario,
So that anyone opening the link sees the same inputs and outputs I configured.

**Acceptance Criteria:**

**Given** the user changes any slider value
**When** the page reruns
**Then** `st.query_params` is updated with the encoded slider state via `url_state.encode_state()` (FR33)
**And** the total URL length does not exceed 2,000 characters (NFR4)
**When** a user opens a URL containing query parameters
**Then** `url_state.decode_state()` restores all slider values from the parameters (FR34)
**And** the page renders with the restored values — no sliders revert to defaults
**And** any missing or unrecognized parameter falls back to the Miami default for that input
**When** a second user opens the shared URL
**Then** they can interact with all sliders freely — no account or login required (FR35)

---

### Story 2.8: Error Handling & Chrome Reliability

As a user,
I want the tool to display a clear error message if a calculation fails rather than showing a wrong number silently,
So that I can trust every result I see is accurate.

**Acceptance Criteria:**

**Given** the tool is running in current stable Google Chrome on desktop (NFR9)
**When** any `calculations.py` function raises an exception
**Then** the affected output area displays a clear user-readable error message (e.g., "Unable to calculate — please check your inputs")
**And** no incorrect numerical value is shown in place of a failed calculation (NFR10)
**And** unaffected outputs continue to display correctly
**When** the URL contains an invalid or out-of-range parameter value
**Then** that parameter silently falls back to its Miami default and the tool loads successfully
**And** no Python traceback or raw exception text is ever visible to the user

---

### Epic 3: Trust, Transparency & UX Polish

**Goal:** Implement the complete UX design specification — theme, layout, all 4 custom components, number formatting, outcome neutrality, accessibility attributes — and add the transparency/trust elements (disclaimer, defaults date, traceable numbers).

**Requirements covered:** FR30, FR31, FR32, FR36, FR37, UX-DR1, UX-DR2, UX-DR3, UX-DR4, UX-DR5, UX-DR6, UX-DR7, UX-DR8, UX-DR9, UX-DR10, UX-DR11, UX-DR12, UX-DR13

---

### Story 3.1: Streamlit Theme & Global Styles

As a developer,
I want the Streamlit app to use the Direction A color palette configured in `config.toml`,
So that the visual foundation matches the UX specification without requiring custom CSS overrides.

**Acceptance Criteria:**

**Given** a `.streamlit/config.toml` file exists in the project
**When** `streamlit run app.py` launches
**Then** the app uses these theme tokens: `primaryColor = "#2B6CB0"`, `backgroundColor = "#FFFFFF"`, `secondaryBackgroundColor = "#F5F7FA"`, `textColor = "#1A1D2E"` (UX-DR1)
**And** Streamlit native elements (buttons, sliders, expanders) inherit the theme colors without additional CSS
**And** the sidebar background uses `#F5F7FA` automatically via Streamlit theming

---

### Story 3.2: DisclaimerBanner Component

As a user,
I want to see a permanent disclaimer and the defaults last-updated date immediately when the page loads,
So that I know this is a financial calculator — not lender advice — before I interact with any numbers.

**Acceptance Criteria:**

**Given** the tool loads in a standard Chrome desktop viewport (≥1,280px)
**When** the page renders without scrolling
**Then** a disclaimer banner is visible at the top of the main area with background color `#EBF4FF` (UX-DR6)
**And** the left side displays: "Financial calculator only. No lender affiliation. Not financial advice." (FR31)
**And** the right side displays: "Defaults last updated: [DEFAULTS_LAST_UPDATED value from defaults.py]" (FR30)
**And** the banner is visible without any scrolling on first load (FR32)
**And** the banner has an `aria-label` attribute (UX-DR12)

---

### Story 3.3: Sidebar UX Polish (Grouping, Labels, Caption)

As a user,
I want the sidebar sliders to be clearly organized with readable labels and a confirmation that Miami defaults are loaded,
So that I can orient quickly and understand what each slider controls.

**Acceptance Criteria:**

**Given** the tool loads for the first time (no URL parameters)
**When** the sidebar renders
**Then** a subheader "Essential Inputs" appears above the 8 always-visible sliders
**And** a caption "Miami defaults loaded" appears directly below the Essential Inputs subheader (UX-DR9)
**And** an `st.expander` labeled "Advanced Inputs" contains the remaining 4 inputs (special assessment, landlord inputs, realtor commission) (UX-DR7)
**And** each slider label displays the input name left-aligned and its current value right-aligned on the same line (UX-DR8)
**And** sliders with non-obvious ranges display hint text at the track ends (e.g., "0%" … "10%" for property tax rate) (UX-DR8)
**When** URL parameters restore a non-default scenario
**Then** the "Miami defaults loaded" caption is not displayed

---

### Story 3.4: HeadlineCard Component

As a user,
I want the headline to display with prominent styling that draws my eye to the key financial verdict,
So that I immediately understand which path wins and by how much without scanning the rest of the page.

**Acceptance Criteria:**

**Given** calculations have run and a winning path is determined
**When** the HeadlineCard renders
**Then** the dollar amount displays in large text (~2.5rem, weight 700, color `#2B6CB0`) (UX-DR3)
**And** the result label reads "Renting is better by X over 5 years" or "Buying is better by X over 5 years" as appropriate (FR23)
**And** a note identifies the best-performing buying scenario (e.g., "Best buying scenario: 20% down")
**And** the renting-wins and buying-wins states use identical CSS — no color or style difference between them (UX-DR11, FR36)
**And** the component has an `aria-label` attribute (UX-DR12)
**And** the component updates in real time on any slider change

---

### Story 3.5: ScenarioColumn Component ×4

As a user,
I want each down payment scenario displayed as a distinct column with a consistent layout,
So that I can scan and compare all four scenarios at a glance without any tabs or hidden content.

**Acceptance Criteria:**

**Given** calculations have run for all four scenarios
**When** the scenario comparison section renders
**Then** four columns appear simultaneously (5%, 10%, 15%, 20% down) — never hidden, collapsed, or tabbed (UX-DR13)
**And** each column header shows the down payment percentage and total upfront cost
**And** each column displays line items in fixed order: P&I → PMI → HOA → Tax → Insurance → Total (UX-DR13)
**And** each column displays the break-even month below the line items
**And** the column with the best total monthly cost receives a `#2B6CB0` left border and `#EBF4FF` background (UX-DR4)
**And** non-best columns have no special border or background treatment
**And** each column has an `aria-label` identifying its scenario (e.g., "10% down payment scenario") (UX-DR12)

---

### Story 3.6: ExitPathsTable Component

As a user,
I want the year-5 exit path comparison displayed as a clear table with consistent row and column ordering,
So that I can evaluate all 12 outcome combinations (3 paths × 4 scenarios) without confusion.

**Acceptance Criteria:**

**Given** year-5 calculations have run for all four scenarios
**When** the ExitPathsTable renders
**Then** it displays a 3-row × 4-column table: rows are Sell → Rent Out → Continue Renting in that fixed order (UX-DR5, UX-DR13)
**And** columns correspond to 5%, 10%, 15%, 20% down in that fixed order
**And** the "Continue Renting" row label includes text indicating it represents a liquid investment portfolio (UX-DR5)
**And** distinction between Continue Renting and buying rows is conveyed via label text only — no color difference (UX-DR11)
**And** all values use standard number formatting (nearest dollar, $ prefix, comma separator, parentheses for negatives)
**And** the table has an `aria-label` attribute (UX-DR12)
**And** the table updates in real time on any slider change

---

### Story 3.7: Number Formatting & Outcome Neutrality Enforcement

As a developer,
I want a single formatting utility applied consistently across all displayed outputs,
So that every number in the tool follows the UX specification and no outcome is ever signaled by color.

**Acceptance Criteria:**

**Given** any numerical output is rendered anywhere in the tool
**When** a dollar amount is displayed
**Then** it is formatted as nearest dollar with $ prefix and comma separator (e.g., $1,234) (UX-DR10)
**When** a percentage is displayed
**Then** it is formatted to 2 decimal places with % suffix (e.g., 6.75%) (UX-DR10)
**When** a month reference is displayed
**Then** it uses the format "month N" (e.g., "month 43") (UX-DR10)
**When** a negative value is displayed
**Then** it uses parentheses, not a minus sign (e.g., ($3,200)) (UX-DR10)
**And** no output uses red or green color for any outcome anywhere in the tool (UX-DR11)
**And** every numerical output corresponds to a visible, user-adjustable input — no hidden constants or undisclosed assumptions (FR37)
**And** the "Best" badge uses `#2B6CB0` accent only — no semantic color coding (UX-DR11)

---

### Story 3.8: Accessibility Attributes

As a user relying on assistive technology,
I want all custom HTML components to have descriptive `aria-label` attributes,
So that screen readers can convey the meaning of each section.

**Acceptance Criteria:**

**Given** the page has fully rendered
**When** inspected with browser developer tools or an accessibility checker
**Then** the HeadlineCard has an `aria-label` (e.g., "Financial comparison headline") (UX-DR12)
**And** each ScenarioColumn has an `aria-label` identifying its scenario (e.g., "10% down payment scenario") (UX-DR12)
**And** the ExitPathsTable has an `aria-label` (e.g., "Year-5 exit path comparison table") (UX-DR12)
**And** the DisclaimerBanner has an `aria-label` (e.g., "Disclaimer and defaults information") (UX-DR12)
**And** all `aria-label` values are present in the rendered HTML, not just in Python source

---

### Epic 4: Budget-Based Opportunity-Cost Model & Cost Escalation

**Goal:** Replace the differential opportunity-cost model with a shared monthly-budget model, and model annual escalation of ownership costs, so the rent-vs-buy comparison reflects "same income, different housing choice" with realistic Miami cost growth.

**Source:** Sprint Change Proposal 2026-06-06 (approved by Cris). **Requirements covered:** FR17 (rewritten), FR15 (amended), FR38, FR39.

---

### Story 4.1: Budget-Based Model + Cost Escalation

As a user,
I want the tool to invest whatever's left of my income after housing each month and to grow ownership costs realistically,
So that the rent-vs-buy comparison reflects how my wealth actually evolves under each choice.

**Acceptance Criteria:**

**Given** a monthly budget (default $3,500) and the comparison horizon
**When** the rent-vs-buy calculation runs (on both the main page and `pages/scenarios.py`)
**Then** the renter portfolio is seeded with the upfront cash (down payment + closing + furniture) and each month adds `max(0, budget − rent)`, compounded monthly
**And** the buyer side-portfolio starts at $0 and each month adds `max(0, budget − total ownership cost)`, compounded monthly, added on top of home equity
**And** the budget steps up once per year at the income-growth rate, where income-growth = rent-growth + 0.25 percentage points (derived; surfaced in the UI, no separate slider)
**And** monthly contributions are floored at $0 (a shortfall month invests nothing and never draws down the portfolio)

**Given** the cost-growth slider (default 3%)
**When** monthly ownership costs are computed
**Then** HOA and HO-6 insurance escalate annually at the cost-growth rate
**And** the property-tax *rate* (millage) stays constant while the *assessed value* grows annually at the cost-growth rate, capped at 3%/yr (Save Our Homes), with the homestead exemption still applied from year 2

**Given** the sidebar
**When** it renders
**Then** a "Monthly Budget" slider appears in the neutral Comparison Settings group and an "Annual Cost Growth" slider appears in the Buy group
**And** both values round-trip through the URL (`bud`, `cg`) and fall back to defaults on missing/invalid params

**Given** the test suite
**When** `python -m pytest -q` runs
**Then** new tests cover `annual_escalate`, assessed-value growth + the 3% SOH cap, and budget-surplus floor-at-$0 behavior
**And** all previously-passing tests still pass

**References:** `sprint-change-proposal-2026-06-06.md` (§4 detailed changes, §5 handoff).
