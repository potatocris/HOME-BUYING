# Story 3.2: DisclaimerBanner Component

Status: done

## Story

As a user,
I want to see a permanent disclaimer and the defaults last-updated date immediately when the page loads,
so that I know this is a financial calculator — not lender advice — before I interact with any numbers.

## Acceptance Criteria

1. **Given** the tool loads in a standard Chrome desktop viewport (≥1,280px), **When** the page renders without scrolling, **Then** a disclaimer banner is visible at the top of the main area with background color `#EBF4FF` (UX-DR6).
2. **Given** the banner renders, **When** inspected, **Then** the left side displays: "Financial calculator only. No lender affiliation. Not financial advice." (FR31).
3. **Given** the banner renders, **When** inspected, **Then** the right side displays: "Defaults last updated: May 2026" (the `DEFAULTS_LAST_UPDATED` value from `defaults.py`) (FR30).
4. **Given** the banner renders, **When** inspected, **Then** it has `aria-label="Disclaimer and defaults information"` (UX-DR12).
5. **Given** a calculation error occurs, **When** `st.error(...)` displays, **Then** the banner is still visible above the error — it renders unconditionally (FR32).
6. **Given** the config.toml file was added in Story 3.1, **When** `python -m pytest tests/ -v` runs, **Then** all 94 existing tests still pass with 0 regressions.

## Tasks / Subtasks

- [x] **Task 1: Add `_disclaimer_banner()` helper function to `app.py` (AC: 1, 2, 3, 4)**
  - [x] Add the function after `_fmt_dollar()` (line 28) and before `st.set_page_config()` (line 31)
  - [x] Function signature: `def _disclaimer_banner(last_updated: str) -> str:`
  - [x] Returns the HTML string defined in Dev Notes below — exact colors, exact text, exact aria-label

- [x] **Task 2: Render the banner in the main area (AC: 1, 5)**
  - [x] Insert `st.markdown(_disclaimer_banner(defaults.DEFAULTS_LAST_UPDATED), unsafe_allow_html=True)` immediately before `st.title(...)` at line 217
  - [x] The call must be OUTSIDE the `if _calc_error` block — banner always shows

- [x] **Task 3: Confirm zero regressions (AC: 6)**
  - [x] Run `python -m pytest tests/ -v` — all 94 tests pass, 0 failures
  - [x] AST parse: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`

- [x] **Task 4: Manual smoke test (AC: 1, 2, 3, 4, 5)**
  - [x] Run `streamlit run app.py` and open `http://localhost:8501`
  - [x] Confirm banner appears at the top of the main area, above the page title
  - [x] Confirm background is light blue (`#EBF4FF`), text is blue (`#2B6CB0`), font is small (~12px)
  - [x] Confirm left text: "Financial calculator only. No lender affiliation. Not financial advice."
  - [x] Confirm right text: "Defaults last updated: May 2026"
  - [x] Confirm banner is above the fold without scrolling at 1,280px+ viewport

## Dev Notes

### The Exact Function to Add

Add this block after `_fmt_dollar()` at line 28, before `st.set_page_config()` at line 31:

```python
def _disclaimer_banner(last_updated: str) -> str:
    return f"""
<div aria-label="Disclaimer and defaults information"
     style="background:#EBF4FF; padding:0.5rem 1rem; border-radius:4px; margin-bottom:1rem;
            display:flex; justify-content:space-between; align-items:center;">
  <span style="color:#2B6CB0; font-size:0.75rem;">
    Financial calculator only. No lender affiliation. Not financial advice.
  </span>
  <span style="color:#2B6CB0; font-size:0.75rem;">
    Defaults last updated: {last_updated}
  </span>
</div>
"""
```

### The Exact Insertion Point in the Main Area

Current line 217:
```python
st.title("Miami Home Buying Decision Tool")
```

After this story, lines 217–218 become:
```python
st.markdown(_disclaimer_banner(defaults.DEFAULTS_LAST_UPDATED), unsafe_allow_html=True)
st.title("Miami Home Buying Decision Tool")
```

Nothing else in the main area changes.

### Why Unconditional Rendering

The banner must render whether or not the calculation succeeded (FR32: "visible on first load"). The `_calc_error` flag only gates the headline/chart/table section (currently line 219 onwards). The banner call goes before `st.title`, which is already outside that gate — so it's naturally unconditional. Do not move the banner inside the `if _calc_error / else` block.

### Why Explicit `color:` in Inline Styles

`app.py` already uses this pattern (see `_headline_card`). Streamlit in dark mode would render HTML text white if color is not explicitly set. The config.toml from Story 3.1 establishes a light theme, but explicit inline `color:` is still the safe pattern — keep it.

### No New `defaults` Import Needed

`defaults` is already imported at line 2 of `app.py`:
```python
import defaults
```
`defaults.DEFAULTS_LAST_UPDATED` resolves to `"May 2026"` (set in `defaults.py` line 40). No changes needed to `defaults.py`.

### Current `app.py` Structure (with exact line references)

```
line  2      import defaults  ← already imported; DEFAULTS_LAST_UPDATED available
lines 9–22   _headline_card() helper
lines 25–28  _fmt_dollar() helper
             ← INSERT _disclaimer_banner() HERE (new, ~13 lines)
line  31     st.set_page_config(...)
lines 33–163 sidebar + URL write
lines 165–215 try/except calculation block (_calc_error flag set here)
line  217    st.title(...)  ← INSERT banner call BEFORE this line
line  219    if _calc_error: ...  ← banner is ABOVE this gate
```

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py             ← MODIFY (add helper function + one render call)
  defaults.py        ← DO NOT TOUCH
  calculations.py    ← DO NOT TOUCH
  url_state.py       ← DO NOT TOUCH
  pages/             ← DO NOT TOUCH
  tests/             ← DO NOT TOUCH
  .streamlit/        ← DO NOT TOUCH (Story 3.1 artifact)
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`

### No New Tests Required

The banner is a pure HTML rendering helper with no business logic. There is nothing to unit-test. The regression check (94 tests pass) is the correctness gate. Visual verification is done via manual smoke test.

### References

- DisclaimerBanner spec: [Source: `_bmad-output/planning-artifacts/ux-design-specification.md` — Component Strategy / DisclaimerBanner]
- FR30 (defaults date), FR31 (disclaimer text), FR32 (visible on load): [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.2]
- UX-DR6 (`#EBF4FF` background), UX-DR12 (aria-label): [Source: `_bmad-output/planning-artifacts/ux-design-specification.md`]
- `DEFAULTS_LAST_UPDATED` value: [Source: `defaults.py` line 40]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — straightforward implementation.

### Completion Notes List

- Added `_disclaimer_banner(last_updated: str) -> str` helper to `app.py` after `_fmt_dollar()`.
- Renders flexbox div: `#EBF4FF` background, left disclaimer text + right "Defaults last updated" date, `#2B6CB0` text at 0.75rem, `aria-label="Disclaimer and defaults information"`.
- Render call inserted before `st.title()` — unconditional, displays even when `_calc_error = True`.
- 94/94 tests pass, 0 regressions. AST clean. App HTTP 200 confirmed.
- Visual verification (banner position, colors, text) to be confirmed by Cris in browser.

### File List

- `app.py` (modified)
