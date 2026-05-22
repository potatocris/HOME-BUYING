---
stepsCompleted: ["step-01-document-discovery", "step-02-prd-analysis", "step-03-epic-coverage-validation", "step-04-ux-alignment", "step-05-epic-quality-review", "step-06-final-assessment"]
documentsInventoried:
  prd: "_bmad-output/planning-artifacts/prd.md"
  architecture: null
  epics: null
  ux: null
---

# Implementation Readiness Assessment Report

**Date:** 2026-05-17
**Project:** Miami Home Buying Decision Tool

## PRD Analysis

### Functional Requirements (37 total)

**Input Configuration (FR1–FR12)**
- FR1: User can set home purchase price via slider
- FR2: User can set mortgage interest rate (30-year fixed) via slider
- FR3: User can set monthly HOA fee via slider
- FR4: User can set annual homeowner's insurance cost (HO-6) via slider
- FR5: User can set property tax rate via slider
- FR6: User can set monthly market rent via slider
- FR7: User can set expected annual investment return rate via slider
- FR8: User can set expected annual home appreciation rate via slider
- FR9: User can set closing cost percentage via slider
- FR10: User can set furniture and improvements budget via slider
- FR11: User can set a one-time special assessment dollar amount and the specific month it occurs
- FR12: User can set landlord scenario inputs: expected monthly rental income, vacancy rate, and property management fee percentage

**Financial Model — Calculations (FR13–FR21)**
- FR13: System calculates full 60-month amortization schedule per scenario (principal, interest, loan balance monthly)
- FR14: System automatically cancels PMI when loan balance reaches 78% of original purchase price
- FR15: System applies Florida homestead exemption ($50K deduction) from year 2; year-1 taxes on full assessed value
- FR16: System calculates total upfront cash (down payment + closing costs + furniture/improvements)
- FR17: System models renter's investment portfolio (down payment capital + monthly savings) compounded monthly at user-set rate over 60 months
- FR18: System applies special assessment as one-time lump-sum cash outflow at user-specified month
- FR19: System calculates year-5 sell exit (gross sale price minus realtor commission + FL documentary stamp tax ~0.7%)
- FR20: System calculates year-5 rent-out exit (cumulative net cash flow minus vacancy/mgmt fee/carrying costs + equity)
- FR21: System calculates year-5 continue-renting exit (renter's accumulated investment portfolio value)

**Scenario Display & Comparison (FR22–FR28)**
- FR22: System displays all 4 down payment scenarios simultaneously without re-entry
- FR23: System displays plain-language headline (e.g., "Renting is better by $12,400 over 5 years")
- FR24: System displays monthly cost breakdown per scenario (mortgage P&I, PMI, HOA, property tax, insurance, total)
- FR25: System displays year-5 net worth for all 3 exit paths across all 4 scenarios
- FR26: System distinguishes liquid assets (portfolio) from illiquid assets (equity) in net worth comparisons
- FR27: System displays break-even month per scenario in plain language
- FR28: All outputs update in real time on any slider change, without page reload

**Defaults & Transparency (FR29–FR32)**
- FR29: System pre-populates all sliders with Miami-specific defaults on first load
- FR30: System displays date Miami-specific defaults were last reviewed
- FR31: System displays permanent disclaimer (financial calculator, no lender affiliation, not financial advice)
- FR32: Disclaimer visible without scrolling on first load

**Scenario Sharing (FR33–FR35)**
- FR33: System encodes all current slider values into page URL on any input change
- FR34: System decodes slider values from URL on page load, restoring exact scenario
- FR35: Any person opening a shared URL can interact with all sliders without account or login

**Unbiased Output (FR36–FR37)**
- FR36: Headline correctly identifies financially superior path regardless of direction
- FR37: Every numerical output traceable to a visible, user-adjustable input — no hidden constants

### Non-Functional Requirements (10 total)

**Performance**
- NFR1: Initial page load ≤ 30 seconds on Streamlit Cloud (including cold start)
- NFR2: Any slider interaction produces updated outputs within 1 second
- NFR3: URL state encoding/decoding completes in under 100ms
- NFR4: Total URL length ≤ 2,000 characters

**Financial Correctness**
- NFR5: Amortization schedule output matches verified reference within $1 per month
- NFR6: PMI cancellation fires in first month loan balance falls at or below 78% of original purchase price
- NFR7: Year-5 net worth figures reconcile — cash flows + terminal asset values = displayed net worth
- NFR8: Renter's investment portfolio compounds monthly, not annually

**Reliability**
- NFR9: Functions correctly in current stable Google Chrome on desktop
- NFR10: No calculation error produces visible incorrect output — failures show error message or fall back to default

### Additional Requirements (Domain & Platform)

**Financial Model Accuracy (domain):** Mathematical precision required for amortization, PMI, compounding; specific FL rules for homestead exemption and documentary stamp tax; seller costs modeled explicitly.

**Assumption Transparency (domain):** All outputs traceable to visible inputs; "defaults last updated" date displayed; no hidden constants.

**Calculation Precision (domain):** Dollar outputs rounded to nearest dollar; percentages to 2 decimal places; amortization to the cent internally; break-even to exact month.

**Platform:** Chrome only, desktop, 1280px+ viewport; Streamlit/Python; `st.query_params` for URL state; no backend/auth.

### PRD Completeness Assessment

The PRD is thorough for a personal fintech tool at this stage. 37 FRs and 10 NFRs are well-specified and implementation-agnostic. Domain requirements are precise. The main gap expected at this stage: no architecture or UX documents yet, and no epics/stories to validate coverage against.

## Epic Coverage Validation

### Coverage Matrix

No epics or stories document found — this is expected at the current workflow stage (PRD just completed; architecture and epics not yet created).

| Status | Count |
|---|---|
| Total PRD FRs | 37 |
| FRs covered in epics | 0 (no epics exist yet) |
| Coverage percentage | N/A — pre-epic stage |

### Missing Requirements

All 37 FRs and 10 NFRs require epics and stories to be created. This is the next workflow step, not a deficiency.

**Recommended epic groupings (based on FR capability areas):**
- Epic 1: Input Configuration (FR1–FR12) — all slider inputs
- Epic 2: Financial Model (FR13–FR21) — amortization, PMI, exit calculations
- Epic 3: Scenario Display (FR22–FR28) — side-by-side comparison, headline, break-even
- Epic 4: Defaults, Transparency & Disclaimers (FR29–FR32)
- Epic 5: URL Sharing (FR33–FR35)
- Epic 6: Unbiased Output & Correctness (FR36–FR37 + NFR5–NFR8)

## UX Alignment Assessment

### UX Document Status

Not found — no UX design document exists yet.

### UX Implication Assessment

This is a user-facing Streamlit web application. UI is heavily implied by the PRD:
- FR22–FR28 require a side-by-side 4-scenario dashboard layout
- FR23 requires a prominent plain-language headline component
- FR24 requires a tabular monthly cost breakdown view
- FR25–FR26 require a net worth comparison visualization (liquid vs. illiquid)
- FR27 requires break-even month display per scenario
- FR29–FR32 require defaults display and a persistent disclaimer component
- FR33–FR35 require URL state management (no visible UI component, but implicit)

### Warnings

⚠️ **UX documentation is missing for a UI-heavy application.** The PRD defines 15+ display-facing FRs that will require deliberate layout decisions. Key unresolved UX questions:
- How are 4 scenarios laid out side-by-side? (columns, tabs, cards?)
- Where does the headline live relative to the input sliders?
- How are the 3 exit paths presented within each scenario?
- How is liquid vs. illiquid equity visually distinguished?
- Where does the disclaimer appear (header, footer, sidebar)?

**Recommendation:** Run `[CU] Create UX` (bmad-create-ux-design) before or alongside architecture to resolve these layout questions before implementation begins. The Streamlit layout model (columns, expanders, sidebars) constrains UX options and should be decided explicitly.

## Summary and Recommendations

### Overall Readiness Status

**NEEDS WORK** — PRD is complete and well-specified. Architecture, UX design, and Epics/Stories must be created before implementation can begin. This is the expected state at end of Phase 2 (Planning); it is not a deficiency in the PRD.

### Critical Issues Requiring Immediate Action

1. **No Architecture Document** — Technical decisions (Streamlit layout strategy, state management pattern, Python module structure, amortization engine design) are unresolved. The architecture must be defined before epics can be properly scoped and sequenced.

2. **No UX Design Document** — 15 of 37 FRs (FR22–FR37) are display-facing and require explicit layout decisions. Key open questions: column vs. tab layout for 4 scenarios, placement of the plain-language headline, visualization of liquid vs. illiquid equity, break-even display format. Without UX decisions, implementation will produce an inconsistent interface.

3. **No Epics or Stories** — Zero implementation units exist. The 37 FRs and 10 NFRs are undecomposed. No sprint plan is possible until epics are created and prioritized.

### Recommended Next Steps

1. **`[CA] Create Architecture`** (`bmad-create-architecture`) — Define the Streamlit application structure, financial model module design, URL state encoding approach, and Python package layout. This is required before epics can be properly decomposed.

2. **`[CU] Create UX`** (`bmad-create-ux-design`) — Design the dashboard layout for the 4-scenario side-by-side view, net worth comparison visualization, and persistent disclaimer placement. Can run in parallel with or immediately after architecture.

3. **`[CE] Create Epics and Stories`** (`bmad-create-epics-and-stories`) — Decompose all 37 FRs into implementation-ready epics and stories. Use the 6 recommended groupings as a starting framework. Requires architecture and UX to be complete first.

4. **`[SP] Sprint Planning`** — Once epics and stories exist, run sprint planning to sequence implementation work and begin Phase 4.

### Recommended Epic Groupings (for Step 3 above)

| Epic | Scope | FRs |
|---|---|---|
| Epic 1 | Input Configuration | FR1–FR12 |
| Epic 2 | Financial Model (Calculations) | FR13–FR21 |
| Epic 3 | Scenario Display & Comparison | FR22–FR28 |
| Epic 4 | Defaults, Transparency & Disclaimers | FR29–FR32 |
| Epic 5 | URL State Sharing | FR33–FR35 |
| Epic 6 | Unbiased Output & Financial Correctness | FR36–FR37 + NFR5–NFR8 |

### Final Note

This assessment identified **3 structural gaps** across **3 categories** (architecture, UX, epics). None of these gaps are deficiencies in the PRD — the PRD is thorough and implementation-ready as a specification. All gaps are the normal pre-implementation artifacts that must be created in Phase 3 (Solutioning) before development begins. The PRD's 37 FRs and 10 NFRs are well-specified and provide a strong foundation for all downstream artifacts.

---

*Assessment completed: 2026-05-17 | Assessor: BMad Implementation Readiness Check*
