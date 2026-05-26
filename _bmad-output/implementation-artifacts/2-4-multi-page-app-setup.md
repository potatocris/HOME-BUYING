# Story 2.4: Multi-Page App Setup

Status: in-progress

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

- [ ] **Task 1: Create `pages/scenarios.py` (AC: 1, 2, 3)**
  - [ ] Create `pages/` directory in project root
  - [ ] Create `pages/scenarios.py` with full sidebar (all 16 sliders + `slider_values` dict, copied from `app.py`)
  - [ ] Add `st.set_page_config` at top of `pages/scenarios.py` (required for multipage pages that set a title)
  - [ ] Copy 4-scenario calculation loop from `app.py` into `pages/scenarios.py`
  - [ ] Copy `_fmt` helper and 4-column card display from `app.py` into `pages/scenarios.py`
  - [ ] Add page title: `st.title("Scenario Comparison — 4 Down Payment Options")`
  - [ ] Verify `pages/scenarios.py` is self-contained: imports `streamlit`, `defaults`, `calculations` independently

- [ ] **Task 2: Clear `app.py` main area (AC: 4)**
  - [ ] Remove the `_fmt` helper function from `app.py`
  - [ ] Remove the 4-column card display loop from `app.py`
  - [ ] Remove the 4-scenario calculation loop (lines 144–229) from `app.py`
  - [ ] Remove the `slider_values` dict from `app.py` (no longer needed on main page for now)
  - [ ] Replace cleared main area with: `st.title("Miami Home Buying Decision Tool")` + `st.info("Rent vs Buy comparison coming in Stories 2.5–2.8.")`
  - [ ] Keep the full sidebar block unchanged

- [ ] **Task 3: Regression check (AC: 6)**
  - [ ] Run `python -m pytest tests/ -v` — all tests must pass
  - [ ] Verify only `app.py` modified + `pages/scenarios.py` created (no changes to `calculations.py`, `defaults.py`, `url_state.py`, `tests/`)

- [ ] **Task 4: Manual smoke test (AC: 2, 3, 5)**
  - [ ] Run `streamlit run app.py` (venv active)
  - [ ] Confirm sidebar nav shows both pages
  - [ ] Navigate to Scenario Comparison — confirm 4 cards render correctly
  - [ ] Drag a slider on Scenario Comparison page — confirm cards update
  - [ ] Navigate to Home — confirm placeholder message visible, sidebar still present
  - [ ] Confirm no Python traceback in app or terminal

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

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

### Change Log
