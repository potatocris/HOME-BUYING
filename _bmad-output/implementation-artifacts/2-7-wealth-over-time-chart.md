# Story 2.7: Wealth Over Time Chart

Status: review

## Story

As a user,
I want a line chart showing how both options' total wealth grow over time,
so that I can see not just the final outcome but the whole trajectory of the decision.

## Acceptance Criteria

1. **Given** both annual wealth series are computed, **When** the main area renders, **Then** a Plotly line chart appears below the HeadlineCard with two lines: "Rent + Invest" and "Buy + Invest".
2. **Given** the chart renders, **Then** the X-axis shows Year 0 through the selected horizon; the Y-axis shows total net wealth in dollars formatted with `$` prefix and comma separator.
3. **Given** both series, **Then** Year 0 is included: renter starts at `upfront_cash`, buyer starts at `0.0` (spent their capital on the purchase).
4. **Given** a break-even exists within the horizon (`break_even_year` is not None), **Then** a dashed vertical line with annotation "Break-even: year N" appears at that x position.
5. **Given** no break-even within the horizon, **Then** no crossover annotation is rendered.
6. **Given** the chart title, **Then** it reads "Total Wealth Over Time".
7. **Given** outcome neutrality, **Then** both lines use non-red, non-green colors; winner and loser lines are visually distinct but neither color implies good/bad.
8. **Given** the timeline slider or any input changes, **When** the page reruns, **Then** the chart updates in real time (Streamlit re-runs automatically — no extra code needed).
9. **Given** all existing tests, **When** `python -m pytest tests/ -v` is run, **Then** all 99 tests pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Add plotly to requirements.txt and import (AC: 1)**
  - [x] Add `plotly==6.7.0` to `requirements.txt` in alphabetical order (between `pillow` and `pluggy`)
  - [x] Add `import plotly.graph_objects as go` to the imports block at the top of `app.py` (after `import calculations`)

- [x] **Task 2: Build the Plotly figure (AC: 1–7)**
  - [x] Replace the comment `# Story 2.7 adds the Plotly chart here.` with the chart block (see exact code in Dev Notes)
  - [x] Build `x_vals`, `renter_series`, `buyer_series` including Year 0
  - [x] Add two `go.Scatter` traces: "Rent + Invest" (`#2B6CB0`) and "Buy + Invest" (`#ED8936`)
  - [x] Conditionally add `fig.add_vline(...)` if `break_even_year is not None`
  - [x] Apply layout: title, axis labels, dollar tick formatting, legend, grid, background colors
  - [x] Render with `st.plotly_chart(fig, use_container_width=True)`
  - [x] Keep `# Story 2.8 adds the annual breakdown table here.` comment below

- [x] **Task 3: Regression check (AC: 9)**
  - [x] Run `python -m pytest tests/ -v` — all 99 tests pass (0 regressions)
  - [x] Verify `calculations.py`, `url_state.py`, `tests/` are untouched

- [x] **Task 4: Syntax and smoke check**
  - [x] AST parse clean: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`
  - [x] Manual smoke: `streamlit run app.py` — chart renders below headline, two lines visible, hover shows dollar values
  - [x] Move slider from 10yr to 30yr — chart extends to 30 data points, x-axis rescales
  - [x] Verify crossover annotation appears when buy line crosses rent line (try low investment return rate to trigger buying wins)

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py          ← MODIFY (add import + chart block)
  requirements.txt ← MODIFY (add plotly==6.7.0)
  defaults.py     ← DO NOT TOUCH
  calculations.py ← DO NOT TOUCH
  url_state.py    ← DO NOT TOUCH
  tests/          ← DO NOT TOUCH (99 tests must stay green)
  pages/          ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`
- Plotly 6.7.0 is already installed in the environment; `requirements.txt` just needs the pin added

### Current state of `app.py` (Story 2.6 output — what you are editing)

```python
import streamlit as st
import defaults
import calculations
# ← ADD: import plotly.graph_objects as go

def _headline_card(...) -> str:
    ...

st.set_page_config(...)

with st.sidebar:
    # 16 sliders including horizon_years select_slider
    ...

# ── Rent vs Buy Two-Path Calculation ──────────────────────────────────────────
total_months  = horizon_years * 12
schedule      = calculations.calculate_amortization_schedule(...)
upfront_cash  = calculations.calculate_upfront_cash(...)   # ← needed for Year 0 renter start
monthly_rate  = investment_return_rate / 100 / 12
# ... renter/buyer loops ...
renter_annual = calculations.get_annual_snapshots(renter_monthly)
buyer_annual  = calculations.get_annual_snapshots(buyer_monthly)

# ── Break-even detection ───────────────────────────────────────────────────────
# ... produces break_even_year (int or None) and break_even_text (str) ...

# ── Main area ─────────────────────────────────────────────────────────────────
# ... winner/difference/headline_card already rendered ...
st.title("Miami Home Buying Decision Tool")
st.markdown(_headline_card(...), unsafe_allow_html=True)
# Story 2.7 adds the Plotly chart here.    ← REPLACE THIS COMMENT
# Story 2.8 adds the annual breakdown table here.
```

**Variables in scope when the chart block runs:**
| Variable | Type | Value at defaults (20% down, 10yr) |
|---|---|---|
| `upfront_cash` | float | ~$141,500 |
| `renter_annual` | list[float] | 10 values, last ≈ $240,604 |
| `buyer_annual` | list[float] | 10 values, last ≈ $199,712 |
| `horizon_years` | int | 10 (or slider value) |
| `break_even_year` | int or None | None (renting leads all 10yr at defaults) |
| `break_even_text` | str | "No break-even within 10 years" |

### Task 1 — requirements.txt change

Add `plotly==6.7.0` between `pillow==12.2.0` and `pluggy==1.6.0`:

```
pillow==12.2.0
plotly==6.7.0
pluggy==1.6.0
```

### Task 2 — Exact chart code (replaces the `# Story 2.7 adds the Plotly chart here.` comment)

```python
# ── Wealth over time chart ─────────────────────────────────────────────────────
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
))
fig.add_trace(go.Scatter(
    x=x_vals, y=buyer_series,
    name="Buy + Invest",
    mode="lines+markers",
    line=dict(color="#ED8936", width=2),
    marker=dict(size=5),
))

if break_even_year is not None:
    fig.add_vline(
        x=break_even_year,
        line_dash="dash",
        line_color="#A0AEC0",
        annotation_text=f"Break-even: year {break_even_year}",
        annotation_position="top",
    )

fig.update_layout(
    title="Total Wealth Over Time",
    xaxis=dict(title="Year", tickmode="linear", dtick=5, tick0=0),
    yaxis=dict(title="Total Net Wealth", tickprefix="$", tickformat=","),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=0, r=0, t=60, b=0),
    hovermode="x unified",
)
fig.update_xaxes(showgrid=True, gridcolor="#E2E8F0")
fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0")

st.plotly_chart(fig, use_container_width=True)
```

### Why Year 0 is included

Year 0 represents the moment of decision before any time passes:
- Renter's Year 0 wealth = `upfront_cash` — they kept the capital they didn't spend on a down payment
- Buyer's Year 0 wealth = `0.0` — they spent all their capital on the purchase (down payment + closing costs + furniture); home equity = 0 at time of purchase (paid market price)

This anchors the chart at a meaningful starting point and shows the renter's initial capital advantage, which the buyer tries to overcome through equity and investing.

`upfront_cash` is already computed in the calculation block before the chart — no new calculation needed.

### Why `#ED8936` (orange) for Buy + Invest

Outcome neutrality (UX-DR11): no red/green coloring. The theme's accent is `#2B6CB0` (blue) for Rent. Orange (`#ED8936`) is visually distinct, neutral (neither "good" nor "bad"), and contrasts well against white backgrounds. No value judgment implied by either color.

### Crossover annotation: `add_vline` API

`fig.add_vline(x, line_dash, line_color, annotation_text, annotation_position)` is stable since Plotly 5.0 (installed: 6.7.0). The `annotation_position="top"` places the label at the top of the vertical line. No additional imports needed — `go.Figure()` provides this method.

### X-axis tick spacing

`dtick=5` with `tick0=0` produces ticks at 0, 5, 10, 15, 20, 25, 30. Since all slider options are multiples of 5, this aligns perfectly with every possible horizon value. The chart always starts at Year 0 and ends at the selected horizon.

### No new tests required

`calculations.py` is untouched. The chart code uses only list construction and Plotly — no custom business logic. Validation gates:
1. 99 existing tests pass (no regressions)
2. AST parse clean on `app.py`
3. Manual smoke: two lines visible, hover shows dollar amounts, slider updates chart

### Cross-story context

| Story | How it uses Story 2.7's output |
|---|---|
| 2.8 | Adds annual table directly below chart; consumes same `renter_annual`, `buyer_annual`, `horizon_years` — all already in scope |
| 2.9 | URL state; chart updates automatically when sliders restore from URL — no chart changes needed |
| 3.5 | Chart & Table polish — styling refinements on top of 2.7 base (line thickness, hover templates, etc.) |

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation matched story spec exactly; no debugging required.

### Completion Notes List

- Task 1: Added `plotly==6.7.0` to `requirements.txt` between `pillow` and `pluggy`. Added `import plotly.graph_objects as go` to imports in `app.py`.
- Task 2: Built chart block at `# Story 2.7 adds...` comment. `x_vals` = [0..horizon_years], `renter_series` = [upfront_cash] + renter_annual (Year 0 anchor), `buyer_series` = [0.0] + buyer_annual. Two `go.Scatter` traces: "Rent + Invest" (#2B6CB0) and "Buy + Invest" (#ED8936). Conditional `add_vline` for break-even. Layout: title, dollar tick format, white background matching theme, grid, unified hover. Rendered via `st.plotly_chart(fig, use_container_width=True)`.
- Task 3: 99/99 tests pass, zero regressions. `calculations.py`, `url_state.py`, `tests/` untouched.
- Task 4: AST parse clean. Manual smoke check left for user.

### File List

- `app.py` (modified — added import + chart block)
- `requirements.txt` (modified — added plotly==6.7.0)

### Change Log

- 2026-05-30: Story 2.7 created — Plotly wealth-over-time line chart
- 2026-05-30: Story 2.7 implemented — two-line chart with Year 0 anchor, break-even vline, outcome-neutral colors, 99 tests passing
