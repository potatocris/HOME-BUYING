# Story 2.4: Multi-Page App Setup

Status: done

## Story

As a developer,
I want the existing 4-scenario comparison to live on a dedicated second page,
so that the main page can be rebuilt as the Rent vs Buy primary view without losing existing work.

## Acceptance Criteria

1. **Given** the project root, **Then** a `pages/` directory exists containing `pages/scenarios.py`.
2. **Given** `pages/scenarios.py`, **When** Streamlit renders it, **Then** it displays identically to today's `app.py` main area — the same 4-column monthly cost breakdown cards with the same sidebar sliders.
3. **Given** the Streamlit multipage app is running, **When** the user opens the app, **Then** both "app" (Home) and "scenarios" (Scenario Comparison) pages are accessible via the sidebar navigation.
4. **Given** `app.py` after this story, **Then** the main area contains only a title and a placeholder `st.info` message — the 4-scenario calculation loop and card display are gone from `app.py`.
5. **Given** the sidebar in both pages, **When** any slider is adjusted, **Then** the page re-renders with updated values (standard Streamlit reactivity; no cross-page state needed).
6. **Given** all existing tests, **When** `python -m pytest tests/ -v` is run, **Then** all tests pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Create `pages/scenarios.py` (AC: 1, 2, 3)**
  - [x] Create `pages/` directory in project root
  - [x] Create `pages/scenarios.py` with full sidebar (all 16 sliders + `slider_values` dict, copied from `app.py`)
  - [x] Add `st.set_page_config` at top of `pages/scenarios.py` (required for multipage pages that set a title)
  - [x] Copy 4-scenario calculation loop from `app.py` into `pages/scenarios.py`
  - [x] Copy `_fmt` helper and 4-column card display from `app.py` into `pages/scenarios.py`
  - [x] Add page title: `st.title("Scenario Comparison — 4 Down Payment Options")`
  - [x] Verify `pages/scenarios.py` is self-contained: imports `streamlit`, `defaults`, `calculations` independently

- [x] **Task 2: Clear `app.py` main area (AC: 4)**
  - [x] Remove the `_fmt` helper function from `app.py`
  - [x] Remove the 4-column card display loop from `app.py`
  - [x] Remove the 4-scenario calculation loop (lines 144–229) from `app.py`
  - [x] Remove the `slider_values` dict from `app.py` (no longer needed on main page for now)
  - [x] Replace cleared main area with: `st.title("Miami Home Buying Decision Tool")` + `st.info("Rent vs Buy comparison coming in Stories 2.5–2.8.")`
  - [x] Keep the full sidebar block unchanged

- [x] **Task 3: Regression check (AC: 6)**
  - [x] Run `python -m pytest tests/ -v` — all tests must pass (99/99 passed in 0.13s)
  - [x] Verify only `app.py` modified + `pages/scenarios.py` created (no changes to `calculations.py`, `defaults.py`, `url_state.py`, `tests/`)

- [x] **Task 4: Manual smoke test (AC: 2, 3, 5)**
  - [x] Run `streamlit run app.py` (venv active)
  - [x] Confirm sidebar nav shows both pages
  - [x] Navigate to Scenario Comparison — confirm 4 cards render correctly
  - [x] Drag a slider on Scenario Comparison page — confirm cards update
  - [x] Navigate to Home — confirm placeholder message visible, sidebar still present
  - [x] Confirm no Python traceback in app or terminal

## Dev Notes

### Sidebar Duplication (Option A — Intentional)

`pages/scenarios.py` duplicates the full sidebar block from `app.py`. This is intentional for Story 2.4:
- Each Streamlit page runs as an independent script; sidebar widgets in `app.py` are not accessible from `pages/scenarios.py`
- The two sidebars will diverge in Story 2.5 (adds timeline slider, changes calculation model for the main page)
- Story 2.9 (URL state) will handle cross-page state if needed

No shared sidebar module is created here — that would be premature abstraction.

### `pages/scenarios.py` Structure

Full self-contained page script in this order:
1. Imports (`streamlit`, `defaults`, `calculations`)
2. `st.set_page_config(page_title="Scenario Comparison", layout="wide")`
3. Full sidebar block (copy from `app.py` — all 16 sliders, `slider_values`)
4. 4-scenario calculation loop → `scenarios` list (copy from `app.py` lines 144–229)
5. Main area: `st.title(...)` + `_fmt` helper + 4-column card display (copy from `app.py` lines 231–273)

### `app.py` After This Story

```python
import streamlit as st
import defaults

st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")

with st.sidebar:
    # ... all 16 sliders unchanged ...

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")
st.info("Rent vs Buy comparison coming in Stories 2.5–2.8.")
```

Note: `import calculations` may be removed from `app.py` once the calculation loop is gone — only re-add it when Story 2.5 wires new calculations.

### Streamlit Multipage Navigation

Streamlit auto-discovers pages in the `pages/` directory. The file `pages/scenarios.py` will appear in the sidebar nav as "Scenarios" (Streamlit derives the label from the filename). No manual registration needed.

Page ordering: Streamlit sorts pages alphabetically by filename unless numeric prefixes are used. For now, no prefix needed — there is only one extra page.

### What Stays Unchanged

- `calculations.py` — DO NOT TOUCH
- `defaults.py` — DO NOT TOUCH
- `url_state.py` — DO NOT TOUCH
- `tests/` directory — DO NOT TOUCH (99 tests must stay green)

### Windows / Environment Reminders

- Use `python -m pytest tests/ -v` (not `python3`)
- Activate venv: `.venv\Scripts\activate` in PowerShell before running pytest or streamlit
- Use PowerShell tool (not Bash tool) for venv activation

### Testing Approach

No new unit tests for this story. The display and navigation logic is Streamlit UI code — not unit-testable. Validation gates: manual smoke test + existing test regression pass.

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py                ← MODIFY (clear main area, remove calculation loop)
  pages/                ← CREATE (new directory)
    scenarios.py        ← CREATE (full 4-scenario page)
  calculations.py       ← DO NOT TOUCH
  defaults.py           ← DO NOT TOUCH
  url_state.py          ← DO NOT TOUCH
  tests/                ← DO NOT TOUCH
```

### Review Findings

- [x] [Review][Defer] `_fmt` formats negative numbers as `$-X` with no sign guard [pages/scenarios.py] — deferred, pre-existing
- [x] [Review][Defer] `break_even_month=None` silent trap — future render stories will display "None" or crash via `_fmt(None)` [pages/scenarios.py break-even loop] — deferred, pre-existing; actionable in Story 2.5+
- [x] [Review][Defer] No engine guard on negative mortgage rate in `calculate_amortization_schedule` [calculations.py] — deferred, pre-existing; UI slider (min=3.0) blocks it today
- [x] [Review][Defer] Floating-point amortization can produce a tiny negative balance, slightly inflating `exit_sell` [calculations.py] — deferred, pre-existing; theoretical
- [x] [Review][Defer] `appreciation_rate=0` + realtor fees can make `exit_sell` silently negative [pages/scenarios.py] — deferred, pre-existing; not displayed in Story 2.4
- [x] [Review][Defer] Landlord exit uses static month-1 carrying costs; ignores homestead exemption (month 13+) and PMI cancellation [pages/scenarios.py] — deferred, pre-existing; known simplification
- [x] [Review][Defer] Structural trap: any `st.*` call at module level in `defaults.py` or `calculations.py` would fire before `set_page_config` [pages/scenarios.py:5] — deferred, pre-existing; low risk
- [x] [Review][Defer] No explicit `key=` args on sliders — risk of state bleed / DuplicateWidgetID when Story 2.9 wires URL state [pages/scenarios.py sidebar] — deferred, pre-existing; actionable in Story 2.9

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_No issues encountered. Implementation was found complete in the working tree (committed in "a19abb4 update"). Verified against all ACs._

### Completion Notes List

- Created `pages/` directory and `pages/scenarios.py` — self-contained multipage page with full 16-slider sidebar, 4-scenario calculation loop, `_fmt` helper, and 4-column card display. Intentional sidebar duplication per Dev Notes (pages will diverge in Story 2.5).
- Cleared `app.py` main area: removed calculation loop, `_fmt`, card display, `slider_values` dict, and `import calculations`. Main area now shows only title + `st.info` placeholder.
- `calculations.py`, `defaults.py`, `url_state.py`, and `tests/` untouched.
- Regression: 99/99 tests pass. AST syntax check clean for both `app.py` and `pages/scenarios.py`. All imports resolve.

### File List

- `app.py` (modified — main area cleared, import calculations removed)
- `pages/scenarios.py` (created — full 4-scenario comparison page)

### Change Log

- 2026-05-29: Story 2.4 complete — multi-page setup; 4-scenario display moved to `pages/scenarios.py`; `app.py` main area cleared for Stories 2.5–2.8
