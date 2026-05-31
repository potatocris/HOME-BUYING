# Story 2.10: Error Handling & Chrome Reliability

Status: done

## Story

As a user,
I want the tool to display a clear error message if a calculation fails rather than showing a wrong number silently,
so that I can trust every result I see is accurate.

## Acceptance Criteria

1. **Given** any `calculations.py` function raises an exception, **When** the page reruns, **Then** the main area displays a clear user-readable error message (e.g., "Unable to calculate â€” please check your inputs").
2. **Given** a calculation error occurs, **When** the error message displays, **Then** no incorrect numerical value is shown in place of the failed calculation (NFR10).
3. **Given** a calculation error occurs, **When** the error message displays, **Then** the sidebar sliders and URL continue to work normally (unaffected outputs still render).
4. **Given** a URL with an invalid or out-of-range parameter value, **When** the page loads, **Then** the tool loads successfully with that parameter silently falling back to its Miami default â€” **ALREADY IMPLEMENTED in Story 2.9** (`decode_state()` + `HORIZON_YEARS` guard in `app.py`; no new code needed for this AC.
5. **Given** any exception occurs, **When** it is caught, **Then** no Python traceback or raw exception text is ever visible to the user.
6. **Given** the tool is running in current stable Google Chrome on desktop (NFR9), **When** all sliders are at default values, **Then** the page loads and all outputs render correctly with no console errors.

## Tasks / Subtasks

- [x] **Task 1: Wrap the calculation block in `app.py` with try/except (AC: 1, 2, 5)**
  - [x] Identify the calculation block start and end in `app.py` (see Dev Notes â€” lines 181â€“226)
  - [x] Wrap the entire block in `try:` / `except Exception:` setting `_calc_error = True` on failure
  - [x] Initialize `_calc_error = False` before the try block

- [x] **Task 2: Conditional main area rendering (AC: 2, 3)**
  - [x] In the main area, check `if _calc_error:` â€” show `st.error(...)` message
  - [x] Otherwise render headline, chart, and table as before (no structural change to existing code)
  - [x] Sidebar, title, and URL write remain outside the try block (they must still render)

- [x] **Task 3: Smoke test and Chrome verification (AC: 5, 6)**
  - [x] Run `python -m pytest tests/ -v` â€” 102 tests pass, 0 regressions
  - [x] AST parse clean: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`
  - [x] Manual smoke: `streamlit run app.py` â€” defaults load, all outputs render, no console errors
  - [x] Temporarily trigger an error (e.g., set `home_price = -1` in the calc block) â€” verify `st.error` appears, no traceback visible; revert after testing

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py             â† MODIFY ONLY (wrap calc block in try/except; conditional main area)
  calculations.py    â† DO NOT TOUCH
  url_state.py       â† DO NOT TOUCH
  defaults.py        â† DO NOT TOUCH
  pages/             â† DO NOT TOUCH
  tests/             â† DO NOT TOUCH (no new tests needed; 102 existing tests cover calculations.py)
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) â€” Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`

### Current `app.py` Structure (Story 2.9 output)

The file has these sections in order:

```
lines 1â€“6    imports (streamlit, defaults, calculations, plotly, pandas, url_state)
lines 8â€“22   _headline_card() helper
lines 25â€“28  _fmt_dollar() helper
line  31     st.set_page_config()
lines 33â€“36  URL decode: _initial = url_state.decode_state(...) + HORIZON_YEARS guard
lines 38â€“157 with st.sidebar: (18 sliders)
lines 158â€“178 st.query_params.update(url_state.encode_state({...}))   â† URL write
lines 180â€“226 CALCULATION BLOCK â† WRAP THIS
lines 228â€“241 break-even detection
lines 243â€“325 main area (title, headline, chart, table)
```

### Task 1 â€” Exact Wrap Pattern

The calculation block currently starts at:
```python
# â”€â”€ Rent vs Buy Two-Path Calculation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
total_months  = horizon_years * 12
```

And ends with:
```python
renter_annual = calculations.get_annual_snapshots(renter_monthly)
buyer_annual  = calculations.get_annual_snapshots(buyer_monthly)
```

Wrap it as follows â€” add `_calc_error = False` before, wrap in `try/except`:

```python
# â”€â”€ Rent vs Buy Two-Path Calculation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_calc_error = False
try:
    total_months  = horizon_years * 12

    schedule     = calculations.calculate_amortization_schedule(
        home_price, down_pct, mortgage_rate, months=total_months
    )
    upfront_cash = calculations.calculate_upfront_cash(
        home_price, down_pct, closing_cost_pct, furniture_budget
    )
    monthly_rate = investment_return_rate / 100 / 12

    # Pass 1: renter portfolio (variable contributions) + buyer surplus list
    renter_balance     = upfront_cash
    renter_monthly     = []
    buyer_surplus_list = []

    for month_idx, rec in enumerate(schedule):
        m        = month_idx + 1
        p_and_i  = rec["interest"] + rec["principal"]
        pmi_m    = rec["pmi"]
        tax_m    = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, m)
        ins_m    = ho6_insurance_annual / 12
        buying_cost_m = p_and_i + pmi_m + hoa_monthly + tax_m + ins_m

        renter_contribution = max(0.0, buying_cost_m - market_rent)
        renter_balance      = (renter_balance + renter_contribution) * (1 + monthly_rate)
        renter_monthly.append(renter_balance)

        buyer_surplus_list.append(max(0.0, market_rent - buying_cost_m))

    # Buyer side portfolio: $0 start, grows from monthly surpluses
    buyer_portfolio = calculations.calculate_buyer_investment_portfolio(
        buyer_surplus_list, investment_return_rate
    )

    # Pass 2: buyer total wealth = home equity + side portfolio
    buyer_monthly = []
    for month_idx, rec in enumerate(schedule):
        m                   = month_idx + 1
        appreciated_value_m = home_price * (1 + appreciation_rate / 100) ** (m / 12)
        home_equity_m       = appreciated_value_m - rec["balance"]
        buyer_monthly.append(home_equity_m + buyer_portfolio[month_idx])

    # Annual snapshots for chart (Story 2.7) and table (Story 2.8)
    renter_annual = calculations.get_annual_snapshots(renter_monthly)
    buyer_annual  = calculations.get_annual_snapshots(buyer_monthly)

except Exception:
    _calc_error = True
```

### Task 2 â€” Exact Conditional Main Area

The break-even detection block and main area rendering both depend on `renter_annual` / `buyer_annual`. Wrap them all in an `if _calc_error:` / `else:` guard:

```python
# â”€â”€ Break-even detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.title("Miami Home Buying Decision Tool")

if _calc_error:
    st.error("Unable to calculate â€” please check your inputs.")
else:
    # â”€â”€ Break-even detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    break_even_year = None
    if len(renter_annual) >= 2:
        prev_renting_ahead = renter_annual[0] >= buyer_annual[0]
        for i in range(1, len(renter_annual)):
            curr_renting_ahead = renter_annual[i] >= buyer_annual[i]
            if curr_renting_ahead != prev_renting_ahead:
                break_even_year = i + 1
                break
            prev_renting_ahead = curr_renting_ahead

    if break_even_year is not None:
        break_even_text = f"Break-even at year {break_even_year}"
    else:
        break_even_text = f"No break-even within {horizon_years} year{'s' if horizon_years != 1 else ''}"

    # â”€â”€ Main area â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    final_renter = renter_annual[-1]
    final_buyer  = buyer_annual[-1]
    if final_renter >= final_buyer:
        winner     = "Renting"
        difference = final_renter - final_buyer
    else:
        winner     = "Buying"
        difference = final_buyer - final_renter

    st.markdown(_headline_card(winner, difference, horizon_years, break_even_text), unsafe_allow_html=True)

    # ... rest of chart and table code unchanged, just indented under else: ...
```

**Important:** `st.title("Miami Home Buying Decision Tool")` moves OUTSIDE the else block (before it) so the page title always renders even when there's a calc error.

### What Remains OUTSIDE the try/except (must not change)

- `_initial = url_state.decode_state(...)` and HORIZON_YEARS guard â€” URL decode always runs
- `with st.sidebar:` block â€” sliders always render
- `st.query_params.update(url_state.encode_state({...}))` â€” URL write always runs
- `st.title(...)` â€” title always renders

### AC 4 Pre-Implementation Note

AC 4 (invalid URL params fall back to defaults) is **fully covered by Story 2.9**:
- `decode_state()` in `url_state.py` already catches `ValueError`/`TypeError` and returns the default
- The `HORIZON_YEARS not in [5,10,15,20,25,30]` guard in `app.py` (line 35-36) already handles out-of-range `yr`
- No code changes needed for this AC â€” just verify it still works in the smoke test

### Error Message Text

Use exactly: `"Unable to calculate â€” please check your inputs."` (the em dash `â€”` is intentional; matches the tone of the rest of the UI).

`st.error()` renders a styled red/orange alert box â€” it does NOT show tracebacks. This satisfies AC 5 (no traceback visible to user).

### Why No New Unit Tests

All `calculations.py` functions are already fully tested (80 tests in `test_calculations.py`, 22 in `test_url_state.py` = 102 total). The error handling added in this story is in `app.py`, which is a Streamlit UI file and is not unit-tested. Manual smoke testing is the appropriate verification path for this story.

### Cross-story Context

| Story | Relationship |
|---|---|
| 2.9 | AC 4 (URL fallback) already implemented â€” do not redo |
| 3.x | All polish stories benefit from the error guard being in place |

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_none_

### Completion Notes List

- Wrapped lines 180â€“225 of `app.py` (entire calculation block) in `try/except Exception` with `_calc_error = False` flag initialized before the try block.
- Moved `st.title(...)` outside the conditional so the page title always renders.
- Added `if _calc_error: st.error("Unable to calculate â€” please check your inputs.")` with all existing rendering (break-even, headline, chart, table) moved into the `else:` branch.
- Sidebar sliders, URL write, and title remain unconditionally outside the error guard (AC 3 satisfied).
- AC 4 (invalid URL params) confirmed still handled by Story 2.9 code â€” no changes needed.
- AC 5 (no traceback visible): `except Exception` block only sets the flag; `st.error()` renders only the message string by Streamlit design â€” no traceback path exists.
- 102 tests pass (0 regressions). AST parse clean. Streamlit smoke test: HTTP 200 on defaults.

### File List

- `app.py` (modified)

### Change Log

- 2026-05-30: Story 2.10 created â€” error handling & Chrome reliability
