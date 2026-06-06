---
stepsCompleted: ["step-01-init", "step-02-context", "step-03-starter"]
inputDocuments: ["_bmad-output/planning-artifacts/prd.md"]
workflowType: 'architecture'
project_name: 'Miami Home Buying Decision Tool'
user_name: 'Cris'
date: '2026-05-17'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
37 FRs spanning: input configuration (FR1–FR12), financial model calculations (FR13–FR21), scenario display and comparison (FR22–FR28), defaults and transparency (FR29–FR32), scenario sharing (FR33–FR35), and unbiased output (FR36–FR37).

Core functional surface: a 12-input financial calculator that computes a 60-month amortization schedule across 4 down payment scenarios, models 3 year-5 exit paths, and displays real-time comparison outputs — all within a single Streamlit page with URL-serialized state.

**Non-Functional Requirements:**
- NFR1–NFR3: Performance — ≤30s cold start load, ≤1s slider response, <100ms URL encode/decode
- NFR4: URL budget — all slider state must fit within 2,000 characters
- NFR5–NFR8: Financial correctness — amortization within $1/month of reference, PMI fires on actual balance, monthly compounding, net worth reconciliation
- NFR9–NFR10: Reliability — Chrome desktop, no silent incorrect outputs

**Scale & Complexity:**
- Primary domain: Single-page web application (Streamlit/Python)
- Complexity level: Low-medium — rich financial model, constrained deployment surface
- Estimated architectural components: 3–4 (financial engine, UI/layout layer, URL state manager, defaults/config)

### Technical Constraints & Dependencies

- Runtime: Streamlit (Python) — reactive rerun model on every user interaction
- Deployment: Streamlit Cloud (zero infrastructure cost) or local `streamlit run`
- No backend, no database, no authentication
- Browser target: Chrome desktop, ≥1,280px viewport
- URL state encoding via `st.query_params` — 2,000-character hard ceiling

### Cross-Cutting Concerns Identified

- **Financial accuracy**: All 4 scenarios share the same calculation functions; a bug in the amortization engine affects all outputs simultaneously
- **Performance vs. correctness**: Full 60-month schedule runs on every slider change across all 4 scenarios — computation must be fast enough for <1s response
- **URL parameter budget**: ~12 sliders must be serialized; abbreviating parameter keys is a design decision that affects readability vs. length constraint compliance
- **Defaults staleness**: Miami-specific defaults must be surfaced with a "last updated" date — this is a transparency requirement, not just a UX nicety

## Starter Template Evaluation

### Primary Technology Domain

Single-page web application (Python/Streamlit) — reactive browser UI with server-side Python computation. No backend API, no database, no authentication.

### Technology Stack

Technology is established by the PRD. No CLI starter exists for Streamlit; project initialization is manual.

**Setup commands:**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install streamlit
streamlit run app.py
```

**Streamlit version:** Latest stable (April 2026 release)
**Python requirement:** 3.10–3.14

### Project Structure Decision: Modular

Single-file layout (`app.py` only) was rejected because the financial calculations engine requires independent unit testing to satisfy NFR5–NFR8 (amortization within $1/month of reference, PMI fires on actual balance).

**Selected structure:**

```
app.py              ← Streamlit UI entry point: layout, sliders, display
calculations.py     ← Financial engine: amortization schedule, PMI
                       cancellation, exit path calculations, net worth
defaults.py         ← Miami-specific defaults + "last updated" date
url_state.py        ← st.query_params encode/decode + URL length validation
requirements.txt    ← Pinned dependencies
```

**Rationale:**
- `calculations.py` is pure Python (no Streamlit imports) — unit-testable against a reference spreadsheet before any UI exists
- `defaults.py` isolated so inputs can be updated without touching the engine
- `url_state.py` isolated so the 2,000-character URL budget can be validated independently

**Note:** Project initialization and module scaffolding is the first implementation story.

> **Sprint Change 2026-06-06 — Budget-based model & cost escalation.** The opportunity-cost engine moves from a differential model to a shared fixed-budget model: both the renter and buyer portfolios invest `max(0, budget − housing cost)` per month, with the budget escalating annually (income = rent-growth + 0.25%). `calculations.py` gains `annual_escalate()` and an `assessment_growth_pct` argument on `calculate_monthly_property_tax()` (HOA, insurance, and tax assessed value escalate at a shared cost-growth rate, tax capped at the 3% Save Our Homes ceiling). Two new inputs (`MONTHLY_BUDGET`, `COST_GROWTH_RATE`) are added to `defaults.py` and serialized in `url_state.py` (`bud`, `cg`). Pure-Python isolation and the 2,000-char URL budget are preserved. See `sprint-change-proposal-2026-06-06.md`.
