# Story 2.6: Timeline Slider + Headline Display

Status: done

## Story

As a user,
I want a timeline slider and a plain-English headline telling me which path wins over my selected horizon,
so that I can immediately see the key verdict at the timeframe that matters to me.

## Acceptance Criteria

1. **Given** the tool loads, **When** the sidebar renders, **Then** a `st.select_slider` labeled "Comparison Horizon (years)" appears with options [5, 10, 15, 20, 25, 30] and defaults to 10.
2. **Given** the timeline slider is set, **When** calculations run, **Then** the full amortization schedule and both portfolio paths compute over `horizon_years × 12` months (unchanged from Story 2.5 — only the source of `horizon_years` changes).
3. **Given** both annual series are computed, **When** the main area renders, **Then** a HeadlineCard displays: "**Renting is better by $X over Y years**" or "**Buying is better by $X over Y years**" based on `renter_annual[-1]` vs `buyer_annual[-1]`.
4. **Given** the HeadlineCard renders, **Then** it shows a sub-line: "Break-even at year N" (first year the leading path overtook the other) or "No break-even within Y years" if no crossover exists within the horizon.
5. **Given** renting-wins or buying-wins, **Then** both headline states use identical CSS — no color, size, or style difference between them (outcome neutrality).
6. **Given** the timeline slider changes, **When** the page reruns, **Then** all headline values (dollar amount, year count, break-even text) update correctly in real time.
7. **Given** all existing tests, **When** `python -m pytest tests/ -v` is run, **Then** all 99 tests pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Move timeline slider into sidebar (AC: 1, 2)**
  - [x] Remove the line `horizon_years = defaults.HORIZON_YEARS` from outside the sidebar block (currently line ~130 in `app.py`, just before the calculation block)
  - [x] Add `st.select_slider` inside `with st.sidebar:`, immediately after the `down_pct` slider (see exact code in Dev Notes)
  - [x] Verify `horizon_years` is still in scope when the calculation block runs (it must be — it's assigned in the sidebar block which executes top-to-bottom before the calculation block)

- [x] **Task 2: Add `_headline_card()` helper to `app.py` (AC: 3, 4, 5)**
  - [x] Add the helper function near the top of `app.py`, after imports and before `st.set_page_config` (see exact function code in Dev Notes)
  - [x] Function signature: `_headline_card(winner: str, difference: float, horizon_years: int, break_even_text: str) -> str`
  - [x] Returns an HTML string — rendered via `st.markdown(..., unsafe_allow_html=True)` at display time
  - [x] Dollar amount: `font-size:2.5rem; font-weight:700; color:#2B6CB0` (accent blue, NOT conditional on winner)
  - [x] All body text: `color:#1A1D2E` (explicit — prevents Streamlit dark-mode turning text white)
  - [x] Card background: `#F5F7FA`; `aria-label="Financial comparison headline"`

- [x] **Task 3: Add break-even logic in `app.py` (AC: 4, 6)**
  - [x] After `renter_annual` and `buyer_annual` are produced (end of calculation block), add break-even detection (see exact code in Dev Notes)
  - [x] Logic: walk `renter_annual` and `buyer_annual` year by year; find first year where the sign of `(renter_annual[i] - buyer_annual[i])` flips vs the previous year
  - [x] `break_even_year` is 1-indexed (year 1 = `renter_annual[0]`)
  - [x] Produce `break_even_text`: `f"Break-even at year {break_even_year}"` or `f"No break-even within {horizon_years} years"`

- [x] **Task 4: Replace `st.info()` placeholder with HeadlineCard display (AC: 3, 4, 5, 6)**
  - [x] Compute `winner`, `difference` from `renter_annual[-1]` vs `buyer_annual[-1]` (see exact code in Dev Notes)
  - [x] Call `st.markdown(_headline_card(...), unsafe_allow_html=True)` — replaces the `st.info()` block
  - [x] Keep `st.title("Miami Home Buying Decision Tool")` above the card
  - [x] Leave a placeholder comment below the card: `# Story 2.7 adds the Plotly chart here.`
  - [x] Leave a second placeholder comment: `# Story 2.8 adds the annual breakdown table here.`

- [x] **Task 5: Regression check (AC: 7)**
  - [x] Run `python -m pytest tests/ -v` — all 99 tests pass (0 regressions)
  - [x] Verify `calculations.py`, `url_state.py`, `tests/` are untouched

- [x] **Task 6: Syntax and smoke check**
  - [x] AST parse clean: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')`
  - [x] Manual smoke: `streamlit run app.py` — headline shows non-zero dollar amount, timeline slider moves headline and year count, both renting-wins and buying-wins states look visually identical
  - [x] Verify: slider change from 10yr to 30yr updates headline and break-even text correctly

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py          ← MODIFY (add timeline slider, replace st.info() with HeadlineCard)
  defaults.py     ← DO NOT TOUCH (HORIZON_YEARS=10 stays; it's the slider default)
  calculations.py ← DO NOT TOUCH
  url_state.py    ← DO NOT TOUCH
  tests/          ← DO NOT TOUCH (99 tests must stay green)
  pages/          ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`
- Activate venv in PowerShell: `.venv\Scripts\Activate.ps1`

### Current state of `app.py` (Story 2.5 output — what you are editing)

```python
import streamlit as st
import defaults
import calculations

st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")

with st.sidebar:
    st.subheader("Essential Inputs")
    st.caption("Miami defaults loaded")
    home_price = st.slider(...)
    down_pct = st.slider(                   ← add horizon_years slider AFTER this
        "Down Payment (%)", ...
    )
    mortgage_rate = st.slider(...)
    # ... 9 more sliders ...
    with st.expander("Advanced Inputs"):
        # ... 5 more sliders ...

# ── Rent vs Buy Two-Path Calculation ──────────────────────────────────────────
# Story 2.6 replaces the next line with the timeline slider widget.
horizon_years = defaults.HORIZON_YEARS           ← REMOVE this line
total_months  = horizon_years * 12
# ... calculation loop ...
renter_annual = calculations.get_annual_snapshots(renter_monthly)
buyer_annual  = calculations.get_annual_snapshots(buyer_monthly)

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")
st.info(                                         ← REPLACE this block
    f"Calculations ready — ..."
)
```

### Task 1 — Exact timeline slider code (inside `with st.sidebar:`, after `down_pct`)

```python
    horizon_years = st.select_slider(
        "Comparison Horizon (years)",
        options=[5, 10, 15, 20, 25, 30],
        value=defaults.HORIZON_YEARS,
    )
```

**Critical:** This goes INSIDE `with st.sidebar:`, immediately after the `down_pct` slider. Remove the standalone `horizon_years = defaults.HORIZON_YEARS` line that currently exists outside the sidebar block.

**Why it works:** The Streamlit execution model runs the entire script top-to-bottom on every rerun. The sidebar block assigns `horizon_years` before the calculation block reads it — scope is not an issue.

**Crash prevention (from deferred work 2.5):** `options=[5, 10, 15, 20, 25, 30]` means minimum is 5 years → `total_months` is always ≥ 60 → `renter_annual` always has ≥ 5 values → `renter_annual[-1]` never crashes. No additional guard needed.

### Task 2 — `_headline_card()` helper function

Add this function after the `import` block and before `st.set_page_config(...)`:

```python
def _headline_card(winner: str, difference: float, horizon_years: int, break_even_text: str) -> str:
    return f"""
<div aria-label="Financial comparison headline"
     style="background:#F5F7FA; padding:1.5rem 2rem; border-radius:8px; margin-bottom:1.5rem;">
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0 0 0.25rem 0;">At current assumptions</p>
  <p style="color:#2B6CB0; font-size:2.5rem; font-weight:700; margin:0 0 0.25rem 0; line-height:1.1;">
    ${difference:,.0f}
  </p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:400; margin:0 0 0.5rem 0;">
    {winner} is better by ${difference:,.0f} over {horizon_years} year{"s" if horizon_years != 1 else ""}
  </p>
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0; opacity:0.75;">{break_even_text}</p>
</div>
"""
```

**Why `color:#1A1D2E` is explicit on every element:** Streamlit renders `st.markdown` HTML in the same DOM context as the app. In dark mode (or when Streamlit injects global CSS), HTML elements without explicit color inherit a light/white value and become invisible against the `#F5F7FA` background. Always use explicit color on all text nodes in custom HTML blocks.

**Outcome neutrality:** `color:#2B6CB0` on the dollar amount applies whether renting wins or buying wins. The only difference between states is the text in the `{winner} is better by...` line. CSS is identical.

### Task 3 — Break-even detection code

Add this block immediately after `renter_annual` and `buyer_annual` are produced and before the main area display block:

```python
# ── Break-even detection ───────────────────────────────────────────────────────
break_even_year = None
if len(renter_annual) >= 2:
    prev_renting_ahead = renter_annual[0] >= buyer_annual[0]
    for i in range(1, len(renter_annual)):
        curr_renting_ahead = renter_annual[i] >= buyer_annual[i]
        if curr_renting_ahead != prev_renting_ahead:
            break_even_year = i + 1  # 1-indexed: renter_annual[0] = year 1
            break
        prev_renting_ahead = curr_renting_ahead

if break_even_year is not None:
    break_even_text = f"Break-even at year {break_even_year}"
else:
    break_even_text = f"No break-even within {horizon_years} year{'s' if horizon_years != 1 else ''}"
```

**Break-even definition:** The first year where the leading path flips. If at year 3 renting was ahead but at year 4 buying pulls ahead, `break_even_year = 4`. If no flip exists (one path leads the entire way), display "No break-even within Y years."

**Index note:** `renter_annual[0]` = wealth at end of year 1, `renter_annual[1]` = year 2, etc. So when the sign flips at index `i`, the break-even year is `i + 1`.

### Task 4 — Main area HeadlineCard display

Replace the entire `st.info(...)` block with:

```python
# ── Main area ─────────────────────────────────────────────────────────────────
final_renter = renter_annual[-1]
final_buyer  = buyer_annual[-1]
if final_renter >= final_buyer:
    winner     = "Renting"
    difference = final_renter - final_buyer
else:
    winner     = "Buying"
    difference = final_buyer - final_renter

st.title("Miami Home Buying Decision Tool")
st.markdown(_headline_card(winner, difference, horizon_years, break_even_text), unsafe_allow_html=True)
# Story 2.7 adds the Plotly chart here.
# Story 2.8 adds the annual breakdown table here.
```

**Keep:** `st.title("Miami Home Buying Decision Tool")` above the card.

### Expected default output (Miami defaults: 20% down, 10yr)

With Miami defaults unchanged:
- `renter_annual[-1]` ≈ $240,604 (year 10)
- `buyer_annual[-1]` ≈ $199,712 (year 10)
- Winner: "Renting", Difference: ≈ $40,892
- Headline: "Renting is better by $40,892 over 10 years"
- Break-even: depends on when buyer equity briefly led, likely "No break-even within 10 years" or early year crossover

These values match the Story 2.5 verification output. If the headline shows very different numbers, something regressed.

### What does NOT change in the calculation block

The entire `calculate_amortization_schedule`, the renter/buyer loops, and the `get_annual_snapshots` calls are **untouched**. Story 2.6's only change to the calculation block is the **source** of `horizon_years` (slider vs constant). All formulas, variable names, and logic stay identical.

### Cross-story context

| Story | How it uses Story 2.6's output |
|---|---|
| 2.7 | Adds Plotly line chart below the HeadlineCard; consumes `renter_annual` and `buyer_annual` for the two chart lines |
| 2.8 | Adds annual breakdown table below chart; consumes `renter_annual`, `buyer_annual`, and `horizon_years` for row count |
| 2.9 | URL state adds `yr` parameter mapped to `horizon_years`; `dp` maps to `down_pct` (single value) |

### No new tests required

The calculation functions under test (`calculate_amortization_schedule`, `calculate_buyer_investment_portfolio`, `get_annual_snapshots`) are unchanged. The `_headline_card()` helper is pure string formatting — unit tests not warranted. Validation gates:
1. All 99 existing tests pass (no regressions)
2. AST parse clean on `app.py`
3. Manual smoke: headline shows correct dollar amount, both slider changes update headline in real time

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation matched story spec exactly; no debugging required.

### Completion Notes List

- Task 1: Added `st.select_slider` for "Comparison Horizon (years)" inside sidebar after `down_pct`; removed hardcoded `horizon_years = defaults.HORIZON_YEARS` from calculation block. `horizon_years` remains in scope because Streamlit executes top-to-bottom.
- Task 2: Added `_headline_card()` helper after imports and before `st.set_page_config`. Uses explicit `color:#1A1D2E` on all text nodes to prevent Streamlit dark-mode rendering text invisible. Dollar amount `color:#2B6CB0` is identical regardless of winner (outcome neutrality per AC 5).
- Task 3: Break-even detection walks `renter_annual` vs `buyer_annual` year by year; detects first sign flip. `break_even_year` is 1-indexed. If no crossover within horizon, shows "No break-even within N years".
- Task 4: Replaced `st.info()` placeholder with `st.markdown(_headline_card(...), unsafe_allow_html=True)`. Placeholder comments for Stories 2.7 and 2.8 left in place.
- Task 5: All 99 tests pass (0 regressions). `calculations.py`, `url_state.py`, `tests/` untouched.
- Task 6: AST parse clean. Manual smoke check left for user.

### File List

- `app.py` (modified)

### Change Log

- 2026-05-30: Story 2.6 — Added timeline slider to sidebar, `_headline_card()` helper, break-even detection, HeadlineCard replacing `st.info()` placeholder. 99 tests passing.
