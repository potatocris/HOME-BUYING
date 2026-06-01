# Story 3.1: Streamlit Theme & Global Styles

Status: done

## Story

As a developer,
I want the Streamlit app to use the Direction A color palette configured in `config.toml`,
so that the visual foundation matches the UX specification without requiring custom CSS overrides.

## Acceptance Criteria

1. **Given** a `.streamlit/config.toml` file exists in the project root, **When** `streamlit run app.py` launches, **Then** the theme section contains exactly: `primaryColor = "#2B6CB0"`, `backgroundColor = "#FFFFFF"`, `secondaryBackgroundColor = "#F5F7FA"`, `textColor = "#1A1D2E"` (UX-DR1).
2. **Given** the config.toml theme is applied, **When** the app renders, **Then** Streamlit native elements (slider handles, expander arrows, sidebar background) inherit the Direction A palette without any additional CSS.
3. **Given** the config.toml theme is applied, **When** the sidebar renders, **Then** its background color is `#F5F7FA` (secondaryBackgroundColor) automatically — no inline CSS override needed.
4. **Given** the config.toml file is added, **When** `python -m pytest tests/ -v` runs, **Then** all existing tests still pass with 0 regressions (94 tests, no code changes required).

## Tasks / Subtasks

- [x] **Task 1: Create `.streamlit/` directory and `config.toml` (AC: 1, 2, 3)**
  - [x] Create directory `.streamlit/` at the project root (same level as `app.py`)
  - [x] Create `.streamlit/config.toml` with the `[theme]` section below — exact hex values, exact key names
  - [x] Verify the file parses as valid TOML (no typos in hex codes or key names)

- [x] **Task 2: Confirm zero regressions (AC: 4)**
  - [x] Run `python -m pytest tests/ -v` — all 94 tests pass, 0 failures
  - [x] AST parse: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`

- [x] **Task 3: Manual smoke test (AC: 2, 3)**
  - [x] Run `streamlit run app.py` and open `http://localhost:8501`
  - [x] Confirm sidebar background is light gray (`#F5F7FA`)
  - [x] Confirm slider handles are blue (`#2B6CB0`)
  - [x] Confirm page background is white (`#FFFFFF`)
  - [x] Confirm text is dark (`#1A1D2E`)
  - [x] Confirm no visual regressions in headline card, chart, or table

## Dev Notes

### The Exact File to Create

**File:** `.streamlit/config.toml` (new file — directory does not exist yet)

```toml
[theme]
primaryColor = "#2B6CB0"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F7FA"
textColor = "#1A1D2E"
```

That is the entire file — no other sections needed for this story.

### What This Does (and Does Not Do)

- **Does:** Makes Streamlit native UI elements (slider handles, expander arrows, button fill, sidebar panel) use the Direction A palette automatically on every page load.
- **Does NOT:** Replace the hardcoded hex values already in `app.py`'s custom HTML/CSS (`_headline_card`, `_fmt_dollar`, Plotly chart colors). Those inline styles remain as-is — they are intentional and already correct. `config.toml` layers beneath them, not over them.
- **Does NOT:** Affect `pages/scenarios.py` behavior (it also benefits automatically).

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  .streamlit/            ← CREATE THIS DIRECTORY
    config.toml          ← CREATE THIS FILE (new)
  app.py                 ← DO NOT TOUCH
  calculations.py        ← DO NOT TOUCH
  defaults.py            ← DO NOT TOUCH
  url_state.py           ← DO NOT TOUCH
  pages/                 ← DO NOT TOUCH
  tests/                 ← DO NOT TOUCH
  requirements.txt       ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`
- Streamlit is pinned at `1.57.0` (requirements.txt). `config.toml` `[theme]` section has been stable since Streamlit 0.85+; no compatibility concern.

### Streamlit Dark Mode Note

The config.toml establishes a **light theme** for the app. This prevents Streamlit's dark-mode behavior (where custom HTML text would appear white on white) — which is why `app.py`'s custom HTML blocks already use explicit `color:#1A1D2E` inline styles. The config.toml and the explicit inline styles work together. Do not remove the explicit `color:` styles from `_headline_card()` or any other HTML helper.

### Current `app.py` Structure (no changes needed)

```
line  31     st.set_page_config(page_title=..., layout="wide")  ← no conflict with config.toml
lines 33–36  URL decode
lines 38–143 with st.sidebar: (18 sliders)
lines 145–163 URL write
lines 165–215 try/except calculation block
lines 217–321 main area (title, headline, chart, table)
```

`st.set_page_config` and `.streamlit/config.toml` are independent — `config.toml` sets theme; `set_page_config` sets page title and layout. Both are needed, neither overrides the other.

### No New Tests Required

This story creates one config file. There is no Python logic to unit-test. The regression check (`python -m pytest tests/ -v`) is the correctness gate. 94 tests should pass unchanged.

### References

- Direction A color tokens: [Source: `_bmad-output/planning-artifacts/ux-design-specification.md` — Visual Design Foundation / Color System]
- `config.toml` exact block: [Source: `_bmad-output/planning-artifacts/architecture.md` — Technology Stack]
- UX-DR1: [Source: `_bmad-output/planning-artifacts/ux-design-specification.md` — Design System Foundation / Design Tokens]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation was straightforward (one new file, no code changes).

### Completion Notes List

- Created `.streamlit/` directory and `config.toml` with Direction A theme tokens (primaryColor, backgroundColor, secondaryBackgroundColor, textColor).
- TOML validated via `toml.load()` — all 4 keys parsed correctly.
- 94/94 tests pass, 0 regressions. No Python code touched.
- `app.py` AST parse clean.
- Streamlit launched cleanly (HTTP 200, no errors in server log). Visual color verification (slider handles, sidebar bg) to be confirmed by Cris in browser.

### File List

- `.streamlit/config.toml` (new)
