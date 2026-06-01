# Story 3.3: Sidebar UX Polish (Grouping, Labels, Caption)

Status: done

## Story

As a user,
I want the sidebar sliders to be clearly organized with readable labels and a confirmation that Miami defaults are loaded,
so that I can orient quickly and understand what each slider controls.

## Acceptance Criteria

1. **Given** the tool loads for the first time (no URL parameters), **When** the sidebar renders, **Then** a subheader "Essential Inputs" appears above the 8 always-visible sliders — already implemented, must remain. (UX-DR9)
2. **Given** the tool loads with no URL parameters, **When** the sidebar renders, **Then** a caption "Miami defaults loaded" appears directly below the "Essential Inputs" subheader. (UX-DR9)
3. **Given** a URL with query parameters restores a non-default scenario, **When** the sidebar renders, **Then** the "Miami defaults loaded" caption is NOT displayed.
4. **Given** the sidebar renders, **When** inspected, **Then** an `st.expander` labeled "Advanced Inputs" contains the 4 advanced inputs — already implemented, must remain. (UX-DR7)
5. **Given** the sidebar renders, **When** inspected, **Then** each slider label displays the input name left-aligned and its current formatted value right-aligned on the same line — satisfied by Streamlit's default slider rendering with the `format` parameter; no code change needed. (UX-DR8)
6. **Given** the sidebar renders, **When** sliders with non-obvious percentage ranges render, **Then** muted hint text showing the min and max values appears below the slider track at the left and right ends. Sliders requiring hints: Mortgage Rate, Property Tax Rate, Home Appreciation, Investment Return, Closing Costs. (UX-DR8)
7. **Given** the config.toml and disclaimer banner from Stories 3.1–3.2, **When** `python -m pytest tests/ -v` runs, **Then** all 94 existing tests still pass with 0 regressions.

## Tasks / Subtasks

- [x] **Task 1: Make "Miami defaults loaded" caption conditional (AC: 2, 3)**
  - [x] Add `_has_url_params = bool(st.query_params.to_dict())` immediately after the HORIZON_YEARS guard block (after line 51)
  - [x] Wrap the existing `st.caption("Miami defaults loaded")` at line 56 with `if not _has_url_params:`

- [x] **Task 2: Add range hints to non-obvious sliders (AC: 6)**
  - [x] After `mortgage_rate` slider: add 2-column range hint — left "3.00%", right "12.00%"
  - [x] After `property_tax_rate` slider: add 2-column range hint — left "0.50%", right "3.00%"
  - [x] After `appreciation_rate` slider: add 2-column range hint — left "0.00%", right "10.00%"
  - [x] After `investment_return_rate` slider: add 2-column range hint — left "0.00%", right "15.00%"
  - [x] After `closing_cost_pct` slider: add 2-column range hint — left "1.00%", right "6.00%"

- [x] **Task 3: Confirm zero regressions (AC: 7)**
  - [x] Run `python -m pytest tests/ -v` — all 94 tests pass, 0 failures
  - [x] AST parse: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`

- [x] **Task 4: Manual smoke test (AC: 2, 3, 6)**
  - [x] Run `streamlit run app.py` (already running) and reload `http://localhost:8501`
  - [x] With no URL params: confirm "Miami defaults loaded" caption appears under "Essential Inputs"
  - [x] Move any slider (params write to URL), then reload with the URL params: confirm caption is gone
  - [x] Confirm range hints visible below Mortgage Rate, Property Tax Rate, Appreciation, Investment Return, Closing Costs

## Dev Notes

### Task 1 — Exact Code Changes

**Step 1:** After the HORIZON_YEARS guard (currently lines 49–51), add one line:

```python
_initial = url_state.decode_state(st.query_params.to_dict())
if _initial['HORIZON_YEARS'] not in [5, 10, 15, 20, 25, 30]:
    _initial['HORIZON_YEARS'] = defaults.HORIZON_YEARS
_has_url_params = bool(st.query_params.to_dict())   # ← ADD THIS LINE
```

**Step 2:** In the sidebar block, change the unconditional caption (currently line 56) to conditional:

```python
# BEFORE:
st.subheader("Essential Inputs")
st.caption("Miami defaults loaded")

# AFTER:
st.subheader("Essential Inputs")
if not _has_url_params:
    st.caption("Miami defaults loaded")
```

**Why `bool(st.query_params.to_dict())` works:**
- On a clean load (no URL params): `st.query_params.to_dict()` returns `{}` → `bool({})` = `False` → caption shows
- After user interaction (URL has params): `st.query_params.to_dict()` returns a dict with 16 keys → caption hides
- On a shared link load (URL has params): same as above → caption hides
- `_has_url_params` is evaluated BEFORE `st.query_params.update()` later in the script, so it correctly reflects the incoming URL state

### Task 2 — Range Hint Pattern

Use this exact pattern after each non-obvious slider:

```python
_lo, _hi = st.columns(2)
_lo.caption("MIN_VALUE")
_hi.markdown(
    '<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">MAX_VALUE</p>',
    unsafe_allow_html=True
)
```

**The 5 sliders and their hint values:**

| Slider variable | Left hint | Right hint |
|---|---|---|
| `mortgage_rate` | `"3.00%"` | `"12.00%"` |
| `property_tax_rate` | `"0.50%"` | `"3.00%"` |
| `appreciation_rate` | `"0.00%"` | `"10.00%"` |
| `investment_return_rate` | `"0.00%"` | `"15.00%"` |
| `closing_cost_pct` | `"1.00%"` | `"6.00%"` |

**Example for mortgage_rate (lines ~75–80):**

```python
mortgage_rate = st.slider(
    "Mortgage Rate (%)",
    min_value=3.0, max_value=12.0,
    value=_initial['MORTGAGE_RATE'], step=0.125,
    format="%.3f%%",
)
_lo, _hi = st.columns(2)
_lo.caption("3.00%")
_hi.markdown(
    '<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">12.00%</p>',
    unsafe_allow_html=True
)
```

Apply the same pattern identically after each of the 5 sliders.

### AC 5 — Already Satisfied, No Code Change

Streamlit 1.57's slider widget renders the label left-aligned and the formatted current value right-aligned on the same label line (using the `format` parameter). All 12 sliders already use `format=` — this AC is satisfied by the existing implementation. Do NOT add custom label HTML or `label_visibility` changes.

### Sliders That Do NOT Need Range Hints

These sliders have obvious ranges from context (dollar format, or widely understood scale):

| Slider | Why no hint needed |
|---|---|
| `home_price` | `$100K`–`$1M` obvious from dollar format |
| `down_pct` | 3%–30% self-explanatory |
| `hoa_monthly` | `$0`–`$2,500` obvious |
| `ho6_insurance_annual` | `$500`–`$6,000` obvious |
| `market_rent` | `$500`–`$6,000` obvious |
| `furniture_budget` | `$0`–`$50,000` obvious |
| `horizon_years` | `select_slider` — options visible |
| Advanced Inputs (4 sliders) | contextual ranges, inside expander |

### Current `app.py` Sidebar Structure (exact lines after Stories 3.1 & 3.2)

```
line  49    _initial = url_state.decode_state(st.query_params.to_dict())
line  50-51 HORIZON_YEARS guard
            ← INSERT _has_url_params flag HERE (new, 1 line)
line  53    with st.sidebar:
line  55    st.subheader("Essential Inputs")
line  56    st.caption("Miami defaults loaded")  ← MAKE CONDITIONAL
line  58-63 home_price slider
line  64-69 down_pct slider
line  70-74 horizon_years select_slider
line  75-80 mortgage_rate slider              ← ADD hint after
line  81-86 hoa_monthly slider
line  87-92 ho6_insurance_annual slider
line  93-98 property_tax_rate slider          ← ADD hint after
line  99-104 market_rent slider
line 105-110 appreciation_rate slider         ← ADD hint after
line 111-116 investment_return_rate slider    ← ADD hint after
line 117-122 closing_cost_pct slider          ← ADD hint after
line 123-128 furniture_budget slider
line 130-158 st.expander("Advanced Inputs")  ← DO NOT TOUCH
```

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py             ← MODIFY (conditional caption + 5 range hints)
  defaults.py        ← DO NOT TOUCH
  calculations.py    ← DO NOT TOUCH
  url_state.py       ← DO NOT TOUCH
  pages/             ← DO NOT TOUCH
  tests/             ← DO NOT TOUCH
  .streamlit/        ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`

### No New Tests Required

Both changes are pure UI rendering (conditional caption and HTML range hints). No business logic to unit-test. The 94-test regression suite is the correctness gate.

### References

- UX-DR7 (expander), UX-DR8 (label format + range hints), UX-DR9 (caption): [Source: `_bmad-output/planning-artifacts/ux-design-specification.md` — UX Consistency Patterns / Input Patterns]
- Story 3.3 ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.3]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None.

### Completion Notes List

- Added `_has_url_params = bool(st.query_params.to_dict())` flag after HORIZON_YEARS guard.
- Made `st.caption("Miami defaults loaded")` conditional on `not _has_url_params`.
- Added 2-column range hint (`_lo.caption` + `_hi.markdown`) after 5 non-obvious % sliders: mortgage_rate (3–12%), property_tax_rate (0.5–3%), appreciation_rate (0–10%), investment_return_rate (0–15%), closing_cost_pct (1–6%).
- 94/94 tests pass, AST clean, app HTTP 200 confirmed.
- Visual verification (caption conditional behavior, hint text positioning) to be confirmed by Cris in browser.

### File List

- `app.py` (modified)
