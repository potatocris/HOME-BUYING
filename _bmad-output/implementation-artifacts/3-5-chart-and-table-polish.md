# Story 3.5: Chart & Table Polish

Status: ready-for-dev

## Story

As a user,
I want the wealth chart to show formatted dollar values on hover and the annual table to display the "Better" column with a clear visual accent,
so that the main-page outputs feel polished, readable, and consistent with the UX design system.

## Acceptance Criteria

1. **Given** the wealth chart renders, **When** the user hovers over any data point, **Then** the tooltip shows the dollar value formatted as `$X,XXX` (nearest dollar, comma separator, `$` prefix) — not a raw float like `240604.23`.
2. **Given** a break-even year exists within the selected horizon, **When** the vertical break-even annotation renders on the chart, **Then** the annotation text uses color `#1A1D2E` and font size 12 — consistent with the app's text color token.
3. **Given** the annual table renders, **When** the user inspects the "Better" column, **Then** "Renting" is displayed in `#2B6CB0` (blue, matching the chart's Rent + Invest line) and "Buying" is displayed in `#6B46C1` (purple), both with font-weight 600 — colors match their respective chart lines so the table and chart are visually consistent; neither color implies good or bad.
4. **Given** the annual table renders, **When** the "Year" column is displayed, **Then** it shows as a whole integer with no decimal places (e.g., `1`, `2`, `10`) and uses a narrow column width.
5. **Given** all existing tests, **When** `python -m pytest tests/ -v` is run, **Then** all 94 tests pass with zero regressions.

## Tasks / Subtasks

- [ ] **Task 1: Add hovertemplate to both chart traces (AC: 1)**
  - [ ] In the `fig.add_trace(go.Scatter(...))` call for "Rent + Invest" (line ~289): add `hovertemplate="$%{y:,.0f}<extra></extra>"`
  - [ ] In the `fig.add_trace(go.Scatter(...))` call for "Buy + Invest" (line ~296): add `hovertemplate="$%{y:,.0f}<extra></extra>"`

- [ ] **Task 2: Style the break-even annotation (AC: 2)**
  - [ ] In the `fig.add_vline(...)` call (line ~304): add `annotation_font=dict(color="#1A1D2E", size=12)` as a new keyword argument

- [ ] **Task 3: Apply pandas Styler to the "Better" column (AC: 3)**
  - [ ] Before `st.subheader("Annual Wealth Breakdown")`, build `df = pd.DataFrame(table_rows)`
  - [ ] Apply Styler: map "Renting" → `color: #2B6CB0; font-weight: 600` and "Buying" → `color: #6B46C1; font-weight: 600` on the "Better" subset (see exact code in Dev Notes)
  - [ ] Pass `styled` (not `df`) to `st.dataframe`

- [ ] **Task 4: Add column_config for "Year" column (AC: 4)**
  - [ ] Add `column_config={"Year": st.column_config.NumberColumn("Year", format="%d", width="small")}` to the `st.dataframe` call

- [ ] **Task 5: Regression check (AC: 5)**
  - [ ] Run `python -m pytest tests/ -v` — all 94 tests pass (0 regressions)
  - [ ] Verify `calculations.py`, `url_state.py`, `tests/`, `defaults.py` are untouched

- [ ] **Task 6: Syntax and smoke check**
  - [ ] AST parse clean: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`
  - [ ] Manual smoke: `streamlit run app.py` — hover over chart shows `$X,XXX` format; "Better" column shows "Renting" in blue and "Buying" in purple; Year column shows integers
  - [ ] Hover check: drag horizon to 30yr; hover any year-end point — confirm formatted dollar value
  - [ ] Annotation check: set investment return to 0% (forces buying to win eventually) — confirm break-even annotation appears with dark text

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py             ← MODIFY (chart traces + add_vline + table rendering)
  defaults.py        ← DO NOT TOUCH
  calculations.py    ← DO NOT TOUCH
  url_state.py       ← DO NOT TOUCH
  pages/             ← DO NOT TOUCH
  tests/             ← DO NOT TOUCH
  .streamlit/        ← DO NOT TOUCH
  requirements.txt   ← DO NOT TOUCH (plotly==6.7.0, pandas==3.0.3 already present)
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`
- 94 tests pass as of story 3.4 (not 99 — special assessment tests were removed in story 2.10)

### Current State of app.py (Story 3.4 output — what you are editing)

The relevant sections are at approximately these line ranges:

```python
# ── imports (lines 1-6) ────────────────────────────────────────────────────────
import streamlit as st
import defaults
import calculations
import plotly.graph_objects as go
import pandas as pd
import url_state

# ── helpers (lines 8-43) ───────────────────────────────────────────────────────
def _headline_card(winner, difference, horizon_years, down_pct, break_even_text) -> str: ...
def _fmt_dollar(v: float) -> str: ...
def _disclaimer_banner(last_updated: str) -> str: ...

# ── Wealth over time chart (lines 283-339) ────────────────────────────────────
# MODIFY THIS BLOCK (Task 1 + Task 2)
x_vals        = list(range(horizon_years + 1))
renter_series = [upfront_cash] + renter_annual
buyer_series  = [0.0] + buyer_annual

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x_vals, y=renter_series,
    name="Rent + Invest",
    mode="lines+markers",
    line=dict(color="#2B6CB0", width=2),
    marker=dict(size=5),
    # ← ADD: hovertemplate="$%{y:,.0f}<extra></extra>"
))
fig.add_trace(go.Scatter(
    x=x_vals, y=buyer_series,
    name="Buy + Invest",
    mode="lines+markers",
    line=dict(color="#ED8936", width=2),
    marker=dict(size=5),
    # ← ADD: hovertemplate="$%{y:,.0f}<extra></extra>"
))

if break_even_year is not None:
    fig.add_vline(
        x=break_even_year,
        line_dash="dash",
        line_color="#A0AEC0",
        annotation_text=f"Break-even: year {break_even_year}",
        annotation_position="top",
        # ← ADD: annotation_font=dict(color="#1A1D2E", size=12)
    )

fig.update_layout(...)  # DO NOT TOUCH — already correct
st.plotly_chart(fig, use_container_width=True)

# ── Annual wealth breakdown table (lines 341-354) ─────────────────────────────
# MODIFY THIS BLOCK (Task 3 + Task 4)
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
# BEFORE: st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)
# AFTER: see Task 3 + Task 4 below
```

### Task 1 — Exact Chart Trace Changes

Only the `hovertemplate` argument is added. Everything else stays exactly the same.

```python
fig.add_trace(go.Scatter(
    x=x_vals, y=renter_series,
    name="Rent + Invest",
    mode="lines+markers",
    line=dict(color="#2B6CB0", width=2),
    marker=dict(size=5),
    hovertemplate="$%{y:,.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=x_vals, y=buyer_series,
    name="Buy + Invest",
    mode="lines+markers",
    line=dict(color="#ED8936", width=2),
    marker=dict(size=5),
    hovertemplate="$%{y:,.0f}<extra></extra>",
))
```

**Why `<extra></extra>`:** In Plotly, the `<extra>` tag controls the secondary hover box that shows the trace name. Without it, both a formatted value AND a separate "Rent + Invest" label box appear. `<extra></extra>` suppresses that redundant box — the trace name is already visible in the legend.

**Why `$%{y:,.0f}`:** `%{y:,.0f}` uses d3-format syntax: `,` for thousands separator, `.0f` for 0 decimal places. The `$` prefix is literal. Result: `$240,604`.

### Task 2 — Exact add_vline Change

```python
if break_even_year is not None:
    fig.add_vline(
        x=break_even_year,
        line_dash="dash",
        line_color="#A0AEC0",
        annotation_text=f"Break-even: year {break_even_year}",
        annotation_position="top",
        annotation_font=dict(color="#1A1D2E", size=12),
    )
```

`annotation_font` is a Plotly API parameter supported since Plotly 5.0 (installed: 6.7.0). No import changes needed.

### Task 3 + Task 4 — Exact Table Rendering Change

Replace the current `st.dataframe` call with:

```python
_BETTER_COLORS = {"Renting": "color: #2B6CB0; font-weight: 600", "Buying": "color: #6B46C1; font-weight: 600"}

st.subheader("Annual Wealth Breakdown")
df = pd.DataFrame(table_rows)
styled = df.style.map(
    lambda v: _BETTER_COLORS.get(v, ""),
    subset=["Better"]
)
st.dataframe(
    styled,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Year": st.column_config.NumberColumn("Year", format="%d", width="small"),
    },
)
```

**`_BETTER_COLORS` dict:** Define as a module-level constant near the other helpers (after `_fmt_dollar`). Keeps the lambda clean and the color values easy to find.

**`df.style.map` (not `applymap`):** `applymap` is deprecated in pandas 2.1+ and removed in pandas 3.x. Always use `df.style.map` on pandas 3.0.3.

**`subset=["Better"]`:** Applies styling only to the "Better" column cells. The `lambda v` receives each cell value ("Renting" or "Buying") and returns the matching CSS from the dict.

**`column_config` with Styler:** Streamlit supports passing both a Styler object AND `column_config` to `st.dataframe`. The Styler controls cell-level CSS; `column_config` controls column metadata (type, format, width). They are independent and compose correctly.

**Why `format="%d"` for Year:** The Year column contains Python `int` values (1, 2, ... N). Without `format="%d"`, Streamlit may render them with a decimal point or trailing zero on some display widths. `%d` ensures clean integer display.

**Dollar columns stay as pre-formatted strings:** The `_fmt_dollar()` strings (`$1,234,567`, `($3,200)`) are left as-is. Using `TextColumn` for them is not needed — Streamlit renders string columns as text by default. Switching to `NumberColumn` would break the parentheses-for-negatives convention (UX-DR10).

### Color Rationale for "Better" Column

"Renting" → `#2B6CB0` (blue) — matches the "Rent + Invest" chart line color.
"Buying" → `#6B46C1` (purple) — a distinct, non-red/non-green color that has no "good" or "bad" connotation.

The color difference aids quick identification (table value matches chart line) without implying either outcome is better. Neither color is used elsewhere in the app with a positive/negative meaning. This is a deliberate deviation from strict same-color neutrality — the trade-off favors readability while keeping both colors semantically neutral.

### No New Tests Required

All changes are in `app.py` UI rendering only:
- `hovertemplate` is a Plotly display hint — no business logic
- `annotation_font` is a display-only attribute
- `df.style.map` is a display-only style applied in Streamlit rendering
- `column_config` is metadata only

Validation gates:
1. 94 existing tests pass (no regressions)
2. AST parse clean on `app.py`
3. Manual smoke: hover, annotation, table styling

### Variables in Scope at Chart/Table Blocks

| Variable | Type | Notes |
|---|---|---|
| `x_vals` | list[int] | [0, 1, ..., horizon_years] |
| `renter_series` | list[float] | [upfront_cash] + renter_annual |
| `buyer_series` | list[float] | [0.0] + buyer_annual |
| `break_even_year` | int or None | None if lines don't cross |
| `renter_annual` | list[float] | horizon_years items |
| `buyer_annual` | list[float] | horizon_years items |
| `horizon_years` | int | 5/10/15/20/25/30 |

### Learning from Previous Stories

- **Story 2.7 (chart text color issue):** Fixed by `template="simple_white"` + explicit `font=dict(color="#1A1D2E")` in `update_layout`. That fix is already in place — do NOT touch `update_layout`.
- **Story 2.8 (table):** `_fmt_dollar()` handles negatives as `($X,XXX)`. Do not change this helper — it's used by both the table and potentially other outputs.
- **Story 3.4 (headline):** `down_pct` was threaded as a new parameter. That call site is at line ~281; don't accidentally revert it.
- **Windows environment:** Use `python` not `python3`; run pytest as `python -m pytest tests/ -v`.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
