---
stepsCompleted: ["step-01-init", "step-02-discovery", "step-02b-vision", "step-02c-executive-summary", "step-03-success", "step-04-journeys", "step-05-domain", "step-06-innovation", "step-07-project-type", "step-08-scoping", "step-09-functional", "step-10-nonfunctional", "step-11-polish"]
releaseMode: single-release
inputDocuments: ["_bmad-output/planning-artifacts/product-brief-Home-Buying.md", "_bmad-output/planning-artifacts/product-brief-Home-Buying-distillate.md"]
briefCount: 2
researchCount: 0
brainstormingCount: 0
projectDocsCount: 0
workflowType: 'prd'
classification:
  projectType: web_app
  domain: personal_fintech
  complexity: low-medium
  projectContext: greenfield
---

# Product Requirements Document — Miami Home Buying Decision Tool

**Author:** Cris
**Date:** 2026-05-17

## Executive Summary

The Miami Home Buying Decision Tool is a personal Streamlit web application giving first-time homebuyers a complete, unbiased financial picture of the rent-vs-buy decision. Built for a buyer targeting a ~$300K Miami condo, it models every cost generic calculators omit — HOA fees, PMI across four down payment tiers, Florida-specific insurance, closing costs, furnishings — alongside the opportunity cost of investing the same capital in the market. At year 5, it projects three exit paths: sell, rent out, or continue renting. No backend. No account required. No lender affiliation. The tool shows what the numbers say; the user decides.

**Primary user:** Cris — first-time buyer in Miami, FL, targeting a ~$300K condo, currently paying $1,000/month to family, planning to move out in early 2027. Financially literate, not a finance professional. Wants a data-backed decision.

**Secondary users:** Friends, family, or colleagues facing the same decision in high-cost Florida markets.

### What Makes This Special

Most rent-vs-buy calculators show one number (the mortgage payment) in one scenario. This tool shows the full financial life of the decision — upfront, ongoing, and at exit — across all meaningful scenarios simultaneously:

- **Four down payment tiers at once** (5%, 10%, 15%, 20%) — PMI, opportunity cost, and monthly burden visible side-by-side, no re-entry required
- **Three year-5 exit paths** — sell, rent out (landlord cash flow modeled), or continue renting
- **Opportunity cost as the headline** — capital not invested in the market grows alongside equity accumulation, making the trade-off explicit
- **Miami-specific defaults** — Florida HO-6 insurance, post-Surfside HOA reserve spikes, Miami-Dade property tax with homestead exemption pre-loaded
- **Every assumption is a slider** — no hidden inputs, no opaque model, no lender bias
- **Shareable via URL** — any scenario sent with a single link; no account, no backend

Core insight: tools with lender affiliations hide opportunity cost by design. This tool makes it the centerpiece. If renting wins, it shows that. If buying wins, it shows that.

## Project Classification

- **Project Type:** Web application (Streamlit, browser-based, URL-encoded state)
- **Domain:** Personal fintech — financial modeling and decision support
- **Complexity:** Low-medium (well-defined financial model, no auth, no backend, no regulatory compliance)
- **Project Context:** Greenfield

## Success Criteria

### User Success

- A user with no prior context reaches a confident, personalized output within 5 minutes — sliders adjusted to their real situation, numbers trusted
- Every major cost is visible and labeled — no hidden inputs, no opaque calculations
- The rent-vs-buy comparison is immediately legible without financial expertise
- The landlord path shows realistic net cash flow (rental income minus vacancy, property management, and carrying costs)
- Break-even month surfaced per down payment scenario in plain language

### Business Success

- Supports a confident buy/rent/wait decision before early 2027
- Any scenario shareable via URL — no account, no backend, no data loss
- Self-contained: runs locally or deploys to Streamlit Cloud at zero infrastructure cost

### Technical Success

- Initial load time ≤ 30 seconds
- No crashes or calculation errors under normal usage
- All slider interactions update outputs in real time (no page reload)
- URL state encoding captures all slider values accurately — shared links reproduce the exact scenario

### Measurable Outcomes

- Net worth comparison at year 5 for all 3 exit paths across all 4 down payment scenarios
- All cost lines modeled: mortgage (P&I), PMI (auto-cancels at 78% LTV), HOA, property tax (with homestead exemption), insurance (HO-6), closing costs, furniture/improvements, seller costs
- Investment portfolio growth modeled as the alternative to down payment, compounding monthly at user-set rate
- Special assessment risk: one-time dollar amount at a user-specified month

## Product Scope

### MVP — Minimum Viable Product

- 4 down payment scenarios (5%, 10%, 15%, 20%) shown side-by-side
- Plain-language headline: "Buying/Renting is better by $X over 5 years" — updates on every slider change
- Full monthly cost breakdown per scenario (mortgage, PMI, HOA, property tax, insurance)
- Upfront cost modeling (down payment + closing costs + furniture/improvements)
- 5-year projection with configurable appreciation and investment return rates
- 3 year-5 exit paths: sell (minus seller costs + Florida documentary stamp tax), rent out (rental income minus vacancy and management fee), continue renting
- Investment portfolio growth as alternative to down payment, compounded monthly
- Net worth comparison at year 5 — liquid (portfolio) vs. illiquid (equity) distinguished
- PMI tracked via amortization schedule; cancels at 78% LTV per federal law
- Florida homestead exemption applied from year 2 onward
- Special assessment slider: one-time lump-sum at a user-specified month
- Break-even month per down payment scenario
- URL-encoded state via `st.query_params`
- Miami-specific defaults with "defaults last updated" date
- Permanent "no lender affiliation" disclaimer visible on first load

**Nice-to-have for v1** (include if straightforward, defer if complexity spikes):
- Amortization schedule visualization (loan balance curve over 5 years)
- Callout explaining counterintuitive results (e.g., why 5% down sometimes beats 20% down)

### Growth Features (Post-MVP)

- Tax optimization — mortgage interest deduction, capital gains exemption on primary residence sale, depreciation on rental income
- Amortization schedule visualization (if deferred from MVP)
- ARM scenario support — adjustable-rate mortgage comparison
- Mobile-optimized UI

### Vision (Future)

- Multi-city support (Orlando, Tampa, Fort Lauderdale)
- Live market data feeds (mortgage rates, rental comps, insurance quotes)
- "When to buy" timeline view factoring in rate trends
- Multi-property comparison

## Development Strategy

**Approach:** Single developer, problem-solving build — ship when the financial model is correct, not when a deadline hits. No infrastructure overhead, no scope creep.

**Resources:** Solo developer (Cris), Python/Streamlit. The financial math (amortization schedule, PMI cancellation, compound interest) is the highest-skill component; AI pair programming can assist with formula implementation and validation.

**Technical risks:**
- *Financial model accuracy:* Amortization schedule and PMI cancellation logic are the most failure-prone components. Validate output against a verified reference (spreadsheet or established online calculator) before treating the model as correct.
- *URL state length:* With many sliders, query parameter strings can grow long. Estimate total URL length at design time; abbreviate parameter names if approaching the 2,000-character cross-platform limit.

**Personal/market risk:** None — personal tool with no external users.

## User Journeys

### Journey 1: First Use — Reaching a Confident Decision

*The happy path.*

**Opening scene.** It's a Sunday afternoon. Cris has spent the last hour on Bankrate, Zillow, and a Reddit thread about Miami condos. Three browser tabs, three mortgage payment estimates, and not one mentions HOA. The question isn't "can I afford a mortgage?" — it's "what does this decision actually cost me, compared to investing my savings and staying a renter?" No tool has answered that.

**Rising action.** Cris opens the tool. Miami-specific defaults are already populated — $300K home price, 6.5% mortgage rate, $500/month HOA, $1,200/year HO-6 insurance, 1.0% property tax. A headline is visible immediately: *"At these assumptions, renting is better by $12,400 over 5 years."* Cris adjusts HOA to $750, closing costs to 3.8%, furniture/improvements to $12,000. The headline updates in real time.

**Climax.** The headline flips: *"Buying at 15% down is better by $8,200 over 5 years."* Cris scrolls to the year-5 net worth comparison — all 4 down payment scenarios side-by-side. The 10% down scenario breaks even at month 41; the 20% scenario at month 29, but requires $60K upfront. Adjusting investment return to 9% flips the headline back to renting. At 6%, buying at 15% or 20% wins clearly.

**Resolution.** Cris has a clear map of which assumptions drive the decision. Saves the URL and schedules a call with parents.

*Capabilities required: Miami defaults, headline summary, real-time updates, side-by-side display, year-5 net worth, break-even month, URL encoding.*

---

### Journey 1B: The Tool Says "Rent"

*The emotionally hardest path.*

**Opening scene.** Cris has toured three condos. One felt right. She's 80% bought in emotionally. She opens the tool to confirm what she already believes.

**Rising action.** She enters her real numbers — the HOA the building disclosed ($920/month), her insurance quote ($1,850/year), asking price ($335K). The headline reads: *"Renting is better by $31,400 over 5 years."* Break-even is past month 60 across all four scenarios.

**Climax.** Cris drags appreciation from 3% to 5%. The headline shifts: *"Buying at 20% down is better by $4,100 over 5 years."* She leaves it there for a moment. Then drags it back to 3%. She knows 5% is optimistic. The tool holds its ground.

**Resolution.** Cris saves the honest URL — 3% appreciation — and sits with it. The tool didn't tell her not to buy. It told her what the math says. She schedules time with a financial advisor before making an offer.

*Capabilities required: headline stating renting wins when it does, no bias toward either outcome, honest real-time updates in any direction.*

---

### Journey 2: Worst-Case Scenario Exploration

*The "what if things go sideways?" path.*

**Opening scene.** Cris has been reading about Florida's condo reserve funding law (post-Surfside). The building she's looking at is from 1987. No special assessment notice yet — but she wants to know what the math looks like if one lands in year 2.

**Rising action.** Cris loads her saved URL. She sets the special assessment to $18,000 as a one-time amount at month 18. The headline shifts: *"Renting is better by $22,600 over 5 years."* Break-even for the 10% down scenario moves from month 41 to 58; for 5% down, past the 5-year window entirely. She nudges HOA to $950 and insurance to $1,800.

**Climax.** Under worst-case assumptions, only the 20% down scenario breaks even before year 5 — by only 4 months. Toggling back to baseline makes the contrast stark: a $600/month HOA swing changes the entire calculus.

**Resolution.** Cris saves a worst-case URL separately. She now has a specific agenda for the HOA conversation: reserve fund balance, pending assessments, litigation status.

*Capabilities required: special assessment as one-time lump-sum at a specified month, URL encoding for multiple saved scenarios, real-time headline updates.*

---

### Journey 3: Trusted Third Party — Shared URL

*A realtor, parent, or partner trying to understand the decision.*

**Opening scene.** Cris's mother has been pushing for the purchase — "renting is throwing money away." Abstract percentages don't land. Cris sends the numbers instead.

**Rising action.** Mom clicks the link. The tool loads in under 10 seconds with no account prompt. Headline: *"Buying at 15% down is better by $8,200 over 5 years."* Mom sees the monthly breakdown for the first time — mortgage, HOA, insurance, property tax. She adjusts appreciation from 3% to 5%. Headline: *"Buying at 15% down is better by $21,500 over 5 years."*

**Climax.** Cris, on a video call, adjusts it back to 3% and explains the conservative stance. First time they've had a shared reference point instead of competing intuitions.

**Resolution.** Complex financial conversation becomes concrete. Cris's realtor gets the same link before the next property tour.

*Note on adversarial use:* A party with an incentive (e.g., realtor) could edit slider values before resharing. The URL does not currently signal when values differ from Miami defaults. Flagged for future consideration.

*Capabilities required: zero-friction URL load, load time ≤30s, all sliders interactive for any URL recipient, headline visible immediately on load.*

---

### Journey Requirements Summary

| Capability | Revealed By |
|---|---|
| Plain-language headline: "Buying/Renting is better by $X" | All journeys |
| Miami-specific defaults, pre-populated on load | Journey 1 |
| Real-time output updates on every slider interaction | Journeys 1, 1B, 2 |
| Side-by-side 4-scenario display | Journey 1 |
| Year-5 net worth comparison (liquid vs. illiquid) | Journey 1 |
| Break-even month per scenario, plain language | Journeys 1, 2 |
| Unbiased headline — states renting wins when it does | Journey 1B |
| Explicit "no lender affiliation" UI signal | Trust requirement (all journeys) |
| Special assessment: one-time amount at a specified month | Journey 2 |
| URL-encoded state: full scenario in shareable link | Journeys 1, 2, 3 |
| Zero-friction URL load (no account, no setup) | Journey 3 |
| Load time ≤ 30 seconds | Journey 3 |
| All sliders interactive for any URL recipient | Journey 3 |

## Domain-Specific Requirements

### Financial Model Accuracy

- All financial calculations must be mathematically precise — no approximations for mortgage amortization, PMI cancellation, or investment compounding
- PMI cancellation triggered by actual loan balance (via amortization schedule) reaching 78% of original purchase price per the Homeowners Protection Act — not estimated by time elapsed
- Florida homestead exemption ($50,000 assessed value deduction) applies from year 2 onward; year-1 taxes calculated on full assessed value
- Special assessment modeled as a one-time lump-sum cash outflow at the user-specified month — not amortized
- Seller costs at year-5 exit: realtor commission (user-configurable, default 5.5%) + Florida documentary stamp tax (~0.7% of sale price) deducted from gross sale proceeds

### Assumption Transparency

- Every output traceable to a visible, user-adjustable input — no hidden constants or embedded assumptions
- All Miami-specific defaults documented with source and last-reviewed date
- Tool displays "defaults last updated" date so users know whether inputs reflect current market conditions

### Calculation Precision

- Dollar outputs: rounded to nearest dollar
- Percentage inputs: accepted and displayed to 2 decimal places
- Amortization schedule: calculated to the cent internally to ensure accurate PMI cancellation month
- Break-even month: calculated to the exact month, displayed as a whole number

### Positioning and Disclaimers

- Permanent disclaimer displayed: financial calculator only, not personalized financial advice, no lender or real estate affiliation
- Disclaimer visible without scrolling on first load

### Known Risks

- **Default staleness:** Miami market inputs reflect conditions at time of development. "Defaults last updated" date surfaces this prominently; review before major sharing.
- **Adversarial URL sharing:** A third party could adjust sliders and reshare. The tool does not signal drift from Miami defaults. Flagged for future consideration.

## Web Application Requirements

### Browser & Platform

- Target browser: Google Chrome (current stable version), desktop only
- No cross-browser compatibility or mobile optimization required for v1
- Minimum recommended viewport: 1,280px width (required for side-by-side 4-scenario layout)

### Performance Targets

- Initial page load: ≤ 30 seconds including Streamlit Cloud cold start
- Slider interaction → output update: ≤ 1 second
- URL state encoding/decoding: < 100ms
- Total URL length (all slider values as query parameters): ≤ 2,000 characters

### Accessibility & SEO

- Visually clear and functional in Chrome on desktop; sufficient color contrast
- No WCAG compliance required for v1
- SEO not applicable — personal tool, not publicly indexed

### Implementation Notes

- Built with Streamlit (Python); reactivity model handles real-time slider updates via `st.session_state`
- URL state: all slider values serialized to query parameters via `st.query_params`
- Deployable to Streamlit Cloud at zero infrastructure cost; runnable locally with `streamlit run app.py`
- No backend, no database, no authentication layer

## Functional Requirements

### Input Configuration

- **FR1:** User can set home purchase price via slider
- **FR2:** User can set mortgage interest rate (30-year fixed) via slider
- **FR3:** User can set monthly HOA fee via slider
- **FR4:** User can set annual homeowner's insurance cost (HO-6) via slider
- **FR5:** User can set property tax rate via slider
- **FR6:** User can set monthly market rent via slider
- **FR7:** User can set expected annual investment return rate via slider
- **FR8:** User can set expected annual home appreciation rate via slider
- **FR9:** User can set closing cost percentage via slider
- **FR10:** User can set furniture and improvements budget via slider
- **FR11:** User can set a one-time special assessment dollar amount and the specific month it occurs
- **FR12:** User can set landlord scenario inputs: expected monthly rental income, vacancy rate, and property management fee percentage

### Financial Model — Calculations

- **FR13:** The system calculates a full 60-month amortization schedule for each down payment scenario, tracking principal, interest, and remaining loan balance month by month
- **FR14:** The system automatically cancels PMI when the loan balance reaches 78% of the original purchase price
- **FR15:** The system applies the Florida homestead exemption ($50,000 assessed value deduction) to property tax starting in year 2; year-1 taxes calculated on full assessed value
- **FR16:** The system calculates total upfront cash as the sum of down payment, closing costs, and furniture/improvements
- **FR17:** The system models the renter's investment portfolio as down payment capital plus monthly savings (when renting costs less than buying), compounded at the user-set return rate over 60 months
- **FR18:** The system applies the special assessment as a single lump-sum cash outflow at the user-specified month
- **FR19:** The system calculates year-5 sell exit value as gross sale price minus realtor commission (user-configurable, default 5.5%) and Florida documentary stamp tax (~0.7%)
- **FR20:** The system calculates year-5 rent-out exit as cumulative net cash flow (rental income minus vacancy, management fee, and carrying costs) plus remaining equity
- **FR21:** The system calculates year-5 continue-renting exit as the renter's accumulated investment portfolio value

### Scenario Display & Comparison

- **FR22:** The system displays all four down payment scenarios (5%, 10%, 15%, 20%) simultaneously without requiring re-entry of inputs
- **FR23:** The system displays a plain-language headline identifying which path is financially better and by how much (e.g., "Renting is better by $12,400 over 5 years")
- **FR24:** The system displays a monthly cost breakdown per down payment scenario: mortgage (P&I), PMI, HOA, property tax, insurance, and total
- **FR25:** The system displays net worth at year 5 for all three exit paths across all four down payment scenarios
- **FR26:** The system distinguishes liquid assets (investment portfolio) from illiquid assets (home equity) in all net worth comparisons
- **FR27:** The system displays break-even month per down payment scenario in plain language
- **FR28:** All outputs update in real time on any slider change, without page reload

### Defaults & Transparency

- **FR29:** The system pre-populates all sliders with Miami-specific defaults on first load
- **FR30:** The system displays the date Miami-specific defaults were last reviewed
- **FR31:** The system displays a permanent disclaimer: financial calculator, no lender affiliation, not financial advice
- **FR32:** The disclaimer is visible without scrolling on first load

### Scenario Sharing

- **FR33:** The system encodes all current slider values into the page URL on any input change
- **FR34:** The system decodes slider values from the URL on page load, restoring the exact scenario
- **FR35:** Any person opening a shared URL can interact with all sliders without an account or login

### Unbiased Output

- **FR36:** The headline correctly identifies the financially superior path regardless of direction — renting wins are stated as renting wins
- **FR37:** Every numerical output is traceable to a visible, user-adjustable input — no hidden constants or undisclosed assumptions

## Non-Functional Requirements

### Performance

- **NFR1:** Initial page load completes within 30 seconds on Streamlit Cloud, including cold start
- **NFR2:** Any slider interaction produces updated outputs within 1 second
- **NFR3:** URL state encoding and decoding completes in under 100ms
- **NFR4:** Total URL length (all slider values as query parameters) must not exceed 2,000 characters

### Financial Correctness

- **NFR5:** Amortization schedule output must match a verified reference implementation within $1 per month
- **NFR6:** PMI cancellation fires in the first month the loan balance falls at or below 78% of original purchase price
- **NFR7:** Year-5 net worth figures must reconcile — sum of all monthly cash flows plus terminal asset values equals the displayed net worth
- **NFR8:** Renter's investment portfolio compounds monthly, not annually

### Reliability

- **NFR9:** The tool functions correctly in the current stable version of Google Chrome on desktop
- **NFR10:** No calculation error or unhandled exception produces a visible incorrect output — failures display a clear error message or fall back to default state
