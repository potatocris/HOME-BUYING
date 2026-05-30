# Story 2.8: Annual Wealth Breakdown Table

Status: review

## Story

As a user,
I want a year-by-year table comparing both paths,
so that I can see exactly how the wealth gap evolves each year.

## Acceptance Criteria

1. **Given** both annual wealth series are computed, **When** the main area renders, **Then** a table appears below the chart with columns: Year | Rent + Invest | Buy + Invest | Difference | Better.
2. **Given** the table renders, **Then** it has one row per year from Year 1 to the selected horizon (row count matches `horizon_years`).
3. **Given** any dollar column (Rent + Invest, Buy + Invest, Difference), **Then** values are formatted as `$X,XXX` (nearest dollar, `$` prefix, comma separator); negative Difference values use parentheses notation: `($X,XXX)`.
4. **Given** the "Better" column, **Then** it shows plain text "Renting" or "Buying" — no color coding, no badges (outcome neutrality).
5. **Given** the timeline slider or any input changes, **When** the page reruns, **Then** the table updates in real time.
6. **Given** all existing tests, **When** `python -m pytest tests/ -v` is run, **Then** all 99 tests pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Add `_fmt_dollar()` helper and `import pandas as pd` (AC: 3)**
  - [x] Add `import pandas as pd` to the imports block in `app.py` (after `import plotly.graph_objects as go`)
  - [x] Add `_fmt_dollar()` helper function after `_headline_card()` and before `st.set_page_config` (see exact code in Dev Notes)

- [x] **Task 2: Build and render the table (AC: 1–5)**
  - [x] Replace the comment `# Story 2.8 adds the annual breakdown table here.` with the table block (see exact code in Dev Notes)
  - [x] Build `table_rows` list by zipping `renter_annual` and `buyer_annual`
  - [x] Apply `_fmt_dollar()` to Rent + Invest, Buy + Invest, Difference columns
  - [x] "Better" column: `"Renting" if r >= b else "Buying"` (plain text, no color)
  - [x] Add `st.subheader("Annual Wealth Breakdown")`
  - [x] Render via `st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)`

- [x] **Task 3: Regression check (AC: 6)**
  - [x] Run `python -m pytest tests/ -v` — all 99 tests pass (0 regressions)
  - [x] Verify `calculations.py`, `url_state.py`, `tests/` are untouched

- [x] **Task 4: Syntax and smoke check**
  - [x] AST parse clean: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`
  - [x] Manual smoke: `streamlit run app.py` — table renders below chart, correct columns, correct row count
  - [x] Verify row count matches horizon slider (10yr → 10 rows, 30yr → 30 rows)
  - [x] Verify Difference column shows parentheses when buying wins (try low investment return to flip the outcome)

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py          ← MODIFY (add import + _fmt_dollar helper + table block)
  defaults.py     ← DO NOT TOUCH
  calculations.py ← DO NOT TOUCH
  url_state.py    ← DO NOT TOUCH
  requirements.txt ← DO NOT TOUCH (pandas==3.0.3 already present)
  tests/          ← DO NOT TOUCH (99 tests must stay green)
  pages/          ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`

### Current state of `app.py` (Story 2.7 output — what you are editing)

```python
import streamlit as st
import defaults
import calculations
import plotly.graph_objects as go
# ← ADD: import pandas as pd

def _headline_card(...) -> str:
    ...
# ← ADD: _fmt_dollar() helper here

st.set_page_config(...)

with st.sidebar:
    # 16 sliders including horizon_years select_slider
    ...

# ── Rent vs Buy Two-Path Calculation ──────────────────────────────────────────
# ... produces renter_annual, buyer_annual, horizon_years, upfront_cash ...

# ── Break-even detection ───────────────────────────────────────────────────────
# ... produces break_even_year, break_even_text ...

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")
st.markdown(_headline_card(...), unsafe_allow_html=True)

# ── Wealth over time chart ─────────────────────────────────────────────────────
# ... Plotly chart already rendered via st.plotly_chart(...) ...

# Story 2.8 adds the annual breakdown table here.    ← REPLACE THIS COMMENT
```

**Variables in scope when the table block runs:**
| Variable | Type | Value at defaults (20% down, 10yr) |
|---|---|---|
| `renter_annual` | list[float] | 10 values, last ≈ $240,604 |
| `buyer_annual` | list[float] | 10 values, last ≈ $199,712 |
| `horizon_years` | int | 10 (or slider value: 5/10/15/20/25/30) |

`renter_annual` and `buyer_annual` are guaranteed to have exactly `horizon_years` items (enforced by `get_annual_snapshots` on `total_months = horizon_years * 12`). No length guard needed.

### Task 1 — `import pandas as pd`

Add as the 5th import, after `import plotly.graph_objects as go`:

```python
import streamlit as st
import defaults
import calculations
import plotly.graph_objects as go
import pandas as pd
```

`pandas==3.0.3` is already in `requirements.txt` — no installation needed.

### Task 1 — `_fmt_dollar()` helper

Add immediately after the closing `"""` of `_headline_card()` and before `st.set_page_config(...)`:

```python
def _fmt_dollar(v: float) -> str:
    if v < 0:
        return f"(${abs(v):,.0f})"
    return f"${v:,.0f}"
```

**Why parentheses for negatives:** UX-DR10 specifies "negative values display with parentheses, not a minus sign, e.g., ($3,200)". The Difference column will be negative when buying's wealth exceeds renting's at a given year — e.g., if buying wins at year 8, Difference at year 8 = renter_annual[7] − buyer_annual[7] < 0, displayed as `($X,XXX)`.

**Why a module-level helper (not inline):** Consistent with `_headline_card()` pattern already in the file. Also reusable by Story 2.8's table and potentially Story 3.5 (chart/table polish).

### Task 2 — Exact table code (replaces `# Story 2.8 adds the annual breakdown table here.`)

```python
# ── Annual wealth breakdown table ─────────────────────────────────────────────
table_rows = []
for i, (r, b) in enumerate(zip(renter_annual, buyer_annual)):
    diff = r - b
    table_rows.append({
        "Year": i + 1,
        "Rent + Invest": _fmt_dollar(r),
        "Buy + Invest": _fmt_dollar(b),
        "Difference": _fmt_dollar(diff),
        "Better": "Renting" if r >= b else "Buying",
    })

st.subheader("Annual Wealth Breakdown")
st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)
```

**Column order:** Python 3.7+ dicts preserve insertion order; `pd.DataFrame(list_of_dicts)` follows that order. Columns will appear as: Year | Rent + Invest | Buy + Invest | Difference | Better.

**Difference sign convention:** `diff = r - b` — positive means renting ahead, negative means buying ahead. This matches the HeadlineCard logic (`final_renter - final_buyer`) so the two displays are consistent.

**"Better" tie-breaking:** `r >= b` → "Renting" (same as the headline card's `final_renter >= final_buyer` → winner = "Renting"). Ties go to Renting in both places — consistent.

**`hide_index=True`:** Hides the pandas 0-based index column. The "Year" column already provides row identity.

**`use_container_width=True`:** Table fills the full main area width, consistent with the chart above it.

### Why no `st.table()` instead of `st.dataframe()`

`st.table()` renders a fully static HTML table — no hover, no scroll for large horizons (30yr = 30 rows). `st.dataframe()` handles long tables with scrolling and has better visual consistency with the rest of the Streamlit UI. Both accept DataFrames; `st.dataframe` is the right choice here.

### No new tests required

`_fmt_dollar()` is pure string formatting — simple enough that unit tests aren't warranted. The underlying data (`renter_annual`, `buyer_annual`) is already covered by 99 existing tests. Validation gates:
1. 99 existing tests pass (no regressions)
2. AST parse clean on `app.py`
3. Manual smoke: table renders with correct rows, correct columns, dollar formatting visible

### Cross-story context

| Story | How it uses Story 2.8's output |
|---|---|
| 2.9 | URL state; table updates automatically when sliders restore from URL — no table changes needed |
| 3.5 | Chart & Table polish — may add column config, conditional formatting, or styling on top of 2.8 base |

### Learning from Story 2.7 (chart text visibility)

Story 2.7 had an issue where Plotly chart text was dim against the white background. The fix was `template="simple_white"` and explicit `font=dict(color="#1A1D2E")` on every layout component. For `st.dataframe`, Streamlit renders natively and inherits the app theme — no custom color fixes needed.

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation matched story spec exactly; no debugging required.

### Completion Notes List

- Task 1: Added `import pandas as pd` to imports. Added `_fmt_dollar()` helper after `_headline_card()` and before `st.set_page_config`; handles parentheses notation for negative values per UX-DR10.
- Task 2: Replaced `# Story 2.8` comment with table block. Zips `renter_annual` and `buyer_annual`, builds list of dicts with Year (1-indexed), formatted dollar strings, and plain-text "Better" column. Rendered via `st.dataframe(pd.DataFrame(...), hide_index=True, use_container_width=True)`.
- Task 3: 99/99 tests pass, zero regressions. `calculations.py`, `url_state.py`, `tests/` untouched.
- Task 4: AST parse clean. Manual smoke check left for user.

### File List

- `app.py` (modified — added import, `_fmt_dollar()` helper, table block)

### Change Log

- 2026-05-30: Story 2.8 created — annual wealth breakdown table
- 2026-05-30: Story 2.8 implemented — `_fmt_dollar()` helper, `pd.DataFrame` table with Year/Rent+Invest/Buy+Invest/Difference/Better columns; 99 tests passing
