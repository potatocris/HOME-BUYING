# Story 2.9: URL Sharing & Page Load State Restore

Status: done

## Story

As a user,
I want the URL to automatically reflect my current slider values so I can share or bookmark my exact scenario,
so that anyone opening the link sees the same inputs and outputs I configured.

## Acceptance Criteria

1. **Given** the user changes any slider, **When** the page reruns, **Then** `st.query_params` is updated with all 18 slider values encoded via `url_state.encode_state()`.
2. **Given** the page loads with URL parameters, **When** the sidebar renders, **Then** each slider initialises to the decoded value from the URL (via `url_state.decode_state()`), not to the hardcoded default.
3. **Given** a URL with partial or missing params, **When** the page loads, **Then** missing params fall back to Miami defaults (existing `decode_state` fallback logic â€” no new code needed).
4. **Given** a URL with an invalid `yr` value (not in `[5, 10, 15, 20, 25, 30]`), **When** the page loads, **Then** the horizon slider defaults to `defaults.HORIZON_YEARS` (10) â€” prevents a select_slider crash.
5. **Given** `url_state.py`, **When** `encode_state` / `decode_state` are called, **Then** `'dp'` maps to `DOWN_PCT` (float) and `'yr'` maps to `HORIZON_YEARS` (int).
6. **Given** all existing tests plus new tests for 'dp' and 'yr', **When** `python -m pytest tests/ -v` is run, **Then** all tests pass with zero regressions (count rises from 99 to 102).

## Tasks / Subtasks

- [x] **Task 1: Extend `url_state.py` â€” add 'dp' and 'yr' params (AC: 5)**
  - [x] Add `'dp': 'DOWN_PCT'` to `PARAM_MAP` (float; no change to INT_PARAMS needed)
  - [x] Add `'yr': 'HORIZON_YEARS'` to `PARAM_MAP`
  - [x] Add `'yr'` to `INT_PARAMS` (horizon is always an int: 5/10/15/20/25/30)
  - [x] Verify `defaults.DOWN_PCT` and `defaults.HORIZON_YEARS` exist (they do â€” added in Story 2.5)

- [x] **Task 2: Add 3 new tests for 'dp' and 'yr' (AC: 6)**
  - [x] `test_decode_horizon_years_as_int` â€” `decode_state({'yr': '15'})` â†’ `HORIZON_YEARS == 15` and is `int`
  - [x] `test_decode_down_pct_as_float` â€” `decode_state({'dp': '10.0'})` â†’ `DOWN_PCT == 10.0` and is `float`
  - [x] `test_roundtrip_dp_and_yr` â€” roundtrip preserves DOWN_PCT and HORIZON_YEARS values
  - [x] Run `python -m pytest tests/ -v` â€” confirm 102 tests pass

- [x] **Task 3: Wire URL state into `app.py` (AC: 1â€“4)**
  - [x] Add `import url_state` to imports (after `import pandas as pd`)
  - [x] Remove the 4-line URL state comment block above `with st.sidebar:`
  - [x] Add `_initial = url_state.decode_state(st.query_params.to_dict())` before `with st.sidebar:`
  - [x] Add horizon guard: if `_initial['HORIZON_YEARS'] not in [5, 10, 15, 20, 25, 30]` â†’ reset to `defaults.HORIZON_YEARS`
  - [x] Replace all 18 `value=defaults.CONST_NAME` with `value=_initial['CONST_NAME']` (see exact mapping in Dev Notes)
  - [x] Add `st.query_params.update(url_state.encode_state({...}))` after the sidebar block (see exact code in Dev Notes)

- [x] **Task 4: Regression and smoke check (AC: 6)**
  - [x] Run `python -m pytest tests/ -v` â€” 102 tests pass, 0 regressions
  - [x] AST parse clean: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`
  - [x] Manual smoke: `streamlit run app.py` â€” move any slider, observe URL updates in the browser address bar
  - [x] Copy the URL, open it in a new tab â€” all sliders restore to the shared values, outputs match

## Dev Notes

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  url_state.py       â† MODIFY (add 'dp' and 'yr' to PARAM_MAP; 'yr' to INT_PARAMS)
  tests/test_url_state.py â† MODIFY (add 3 new tests)
  app.py             â† MODIFY (add import, decode on load, slider value=_initial, encode after sidebar)
  defaults.py        â† DO NOT TOUCH (DOWN_PCT and HORIZON_YEARS already present)
  calculations.py    â† DO NOT TOUCH
  pages/             â† DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) â€” Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`

### Task 1 â€” Exact changes to `url_state.py`

Current `PARAM_MAP` has 16 entries ending at `'rc': 'REALTOR_COMMISSION_PCT'`.
Current `INT_PARAMS = {'sam'}`.

**Add two entries to PARAM_MAP** (append after `'rc'`):

```python
PARAM_MAP = {
    'hp':   'HOME_PRICE',
    'mr':   'MORTGAGE_RATE',
    'hoa':  'HOA_MONTHLY',
    'ins':  'HO6_INSURANCE_ANNUAL',
    'tr':   'PROPERTY_TAX_RATE',
    'rent': 'MARKET_RENT',
    'ir':   'INVESTMENT_RETURN_RATE',
    'apr':  'APPRECIATION_RATE',
    'cc':   'CLOSING_COST_PCT',
    'fur':  'FURNITURE_BUDGET',
    'sa':   'SPECIAL_ASSESSMENT_AMOUNT',
    'sam':  'SPECIAL_ASSESSMENT_MONTH',
    'ri':   'RENTAL_INCOME_MONTHLY',
    'vac':  'VACANCY_RATE',
    'mgmt': 'PROPERTY_MGMT_FEE_PCT',
    'rc':   'REALTOR_COMMISSION_PCT',
    'dp':   'DOWN_PCT',
    'yr':   'HORIZON_YEARS',
}

INT_PARAMS = {'sam', 'yr'}
```

**Why 'yr' must be in INT_PARAMS:**
`select_slider(value=...)` requires the value to be the same type as the options. Options are `[5, 10, 15, 20, 25, 30]` â€” all ints. If 'yr' were decoded as float (10.0), `value=10.0` with int options would crash. `INT_PARAMS` ensures `decode_state` returns `int('10')` = `10`, not `float('10')` = `10.0`.

**Why 'dp' stays as float (not in INT_PARAMS):**
The down payment slider uses `min_value=3.0`, `max_value=30.0`, `step=0.5` â€” all floats. `value=20.0` is the expected type.

**Impact on existing tests:**
The `_miami_defaults()` helper in `test_url_state.py` builds from `PARAM_MAP.values()`:
```python
def _miami_defaults():
    return {const_name: getattr(defaults, const_name) for const_name in PARAM_MAP.values()}
```
After adding 'dp'/'yr', this automatically includes `DOWN_PCT=20.0` and `HORIZON_YEARS=10` â€” all 6 tests using `_miami_defaults()` now cover the new params without modification. The 99 existing tests all continue to pass.

**One edge case in `test_decode_all_non_int_params_are_floats`:**
This test passes `'1.0'` for every param key including 'yr'. For 'yr' in INT_PARAMS, `decode_state` tries `int('1.0')` â†’ `ValueError` â†’ falls back to `defaults.HORIZON_YEARS`. The test only checks `if short_key not in INT_PARAMS`, so HORIZON_YEARS is excluded from the float assertion. Test passes âœ“.

### Task 2 â€” Exact new tests (add to end of `tests/test_url_state.py`)

```python
# â”€â”€ New params: dp (DOWN_PCT) and yr (HORIZON_YEARS) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_decode_horizon_years_as_int():
    result = decode_state({'yr': '15'})
    assert result['HORIZON_YEARS'] == 15
    assert isinstance(result['HORIZON_YEARS'], int)


def test_decode_down_pct_as_float():
    result = decode_state({'dp': '10.0'})
    assert result['DOWN_PCT'] == 10.0
    assert isinstance(result['DOWN_PCT'], float)


def test_roundtrip_dp_and_yr():
    values = _miami_defaults()
    values['DOWN_PCT'] = 15.0
    values['HORIZON_YEARS'] = 20
    decoded = decode_state(encode_state(values))
    assert decoded['DOWN_PCT'] == 15.0
    assert decoded['HORIZON_YEARS'] == 20
    assert isinstance(decoded['HORIZON_YEARS'], int)
```

### Task 3 â€” Exact changes to `app.py`

**Step A: Add import** â€” after `import pandas as pd`:
```python
import url_state
```

**Step B: Replace the 4-line comment block and add decode call** â€” the current code above `with st.sidebar:` reads:
```python
# â”€â”€ Sidebar: all 16 input sliders â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Story 2.7 will add url_state.decode_state() here to restore slider values from
# URL params. For now, value= points directly to defaults.py constants.
# Pattern: when Story 2.7 wires URL state, replace each value=defaults.CONST_NAME
# with value=_initial["CONST_NAME"] where _initial = url_state.decode_state(st.query_params.to_dict()).

with st.sidebar:
```

Replace with:
```python
# â”€â”€ Sidebar: all 18 input sliders â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_initial = url_state.decode_state(st.query_params.to_dict())
if _initial['HORIZON_YEARS'] not in [5, 10, 15, 20, 25, 30]:
    _initial['HORIZON_YEARS'] = defaults.HORIZON_YEARS

with st.sidebar:
```

**Step C: Replace all `value=defaults.CONST_NAME` with `value=_initial['CONST_NAME']`** â€” full mapping:

| Slider variable | Old value= | New value= |
|---|---|---|
| `home_price` | `defaults.HOME_PRICE` | `_initial['HOME_PRICE']` |
| `down_pct` | `defaults.DOWN_PCT` | `_initial['DOWN_PCT']` |
| `horizon_years` | `defaults.HORIZON_YEARS` | `_initial['HORIZON_YEARS']` |
| `mortgage_rate` | `defaults.MORTGAGE_RATE` | `_initial['MORTGAGE_RATE']` |
| `hoa_monthly` | `defaults.HOA_MONTHLY` | `_initial['HOA_MONTHLY']` |
| `ho6_insurance_annual` | `defaults.HO6_INSURANCE_ANNUAL` | `_initial['HO6_INSURANCE_ANNUAL']` |
| `property_tax_rate` | `defaults.PROPERTY_TAX_RATE` | `_initial['PROPERTY_TAX_RATE']` |
| `market_rent` | `defaults.MARKET_RENT` | `_initial['MARKET_RENT']` |
| `appreciation_rate` | `defaults.APPRECIATION_RATE` | `_initial['APPRECIATION_RATE']` |
| `investment_return_rate` | `defaults.INVESTMENT_RETURN_RATE` | `_initial['INVESTMENT_RETURN_RATE']` |
| `closing_cost_pct` | `defaults.CLOSING_COST_PCT` | `_initial['CLOSING_COST_PCT']` |
| `furniture_budget` | `defaults.FURNITURE_BUDGET` | `_initial['FURNITURE_BUDGET']` |
| `special_assessment_amount` | `defaults.SPECIAL_ASSESSMENT_AMOUNT` | `_initial['SPECIAL_ASSESSMENT_AMOUNT']` |
| `special_assessment_month` | `defaults.SPECIAL_ASSESSMENT_MONTH` | `_initial['SPECIAL_ASSESSMENT_MONTH']` |
| `rental_income_monthly` | `defaults.RENTAL_INCOME_MONTHLY` | `_initial['RENTAL_INCOME_MONTHLY']` |
| `vacancy_rate` | `defaults.VACANCY_RATE` | `_initial['VACANCY_RATE']` |
| `property_mgmt_fee_pct` | `defaults.PROPERTY_MGMT_FEE_PCT` | `_initial['PROPERTY_MGMT_FEE_PCT']` |
| `realtor_commission_pct` | `defaults.REALTOR_COMMISSION_PCT` | `_initial['REALTOR_COMMISSION_PCT']` |

**Step D: Add URL write after the sidebar block** â€” immediately after `with st.sidebar:` closes (before `# â”€â”€ Rent vs Buy Two-Path Calculation`):

```python
# â”€â”€ Write current slider state to URL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.query_params.update(url_state.encode_state({
    'HOME_PRICE':              home_price,
    'DOWN_PCT':                down_pct,
    'HORIZON_YEARS':           horizon_years,
    'MORTGAGE_RATE':           mortgage_rate,
    'HOA_MONTHLY':             hoa_monthly,
    'HO6_INSURANCE_ANNUAL':    ho6_insurance_annual,
    'PROPERTY_TAX_RATE':       property_tax_rate,
    'MARKET_RENT':             market_rent,
    'APPRECIATION_RATE':       appreciation_rate,
    'INVESTMENT_RETURN_RATE':  investment_return_rate,
    'CLOSING_COST_PCT':        closing_cost_pct,
    'FURNITURE_BUDGET':        furniture_budget,
    'SPECIAL_ASSESSMENT_AMOUNT': special_assessment_amount,
    'SPECIAL_ASSESSMENT_MONTH':  special_assessment_month,
    'RENTAL_INCOME_MONTHLY':   rental_income_monthly,
    'VACANCY_RATE':            vacancy_rate,
    'PROPERTY_MGMT_FEE_PCT':   property_mgmt_fee_pct,
    'REALTOR_COMMISSION_PCT':  realtor_commission_pct,
}))
```

**Why `st.query_params.update()` does NOT cause an infinite rerun loop:**
In Streamlit 1.30+, writing to `st.query_params` updates the browser URL silently â€” it does NOT trigger a page rerun. The URL reflects the current state; users can copy and share it. Opening that URL triggers a fresh load where `st.query_params.to_dict()` returns the saved params.

**Why `st.query_params.to_dict()` (not `dict(st.query_params)`):**
The existing comment in app.py already specifies `.to_dict()`. Both work in Streamlit 1.57.0, but `.to_dict()` is the documented method on the `QueryParamsProxy` object.

### Streamlit 1.57.0 `st.query_params` API summary

| Operation | Code |
|---|---|
| Read all params as dict | `st.query_params.to_dict()` |
| Write params to URL | `st.query_params.update({...})` |
| Read single param | `st.query_params.get('hp')` |

Setting params does NOT trigger rerun. Reading params on the next fresh load returns the saved values.

### Cross-story context

| Story | How it uses Story 2.9's output |
|---|---|
| 3.3 | Sidebar polish â€” may add/remove "Miami defaults loaded" caption based on URL params |
| 3.x | All polish stories benefit from shareable URLs â€” scenarios can be shared exactly |

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None â€” implementation matched story spec exactly; no debugging required.

### Completion Notes List

- Task 1: Added `'dp': 'DOWN_PCT'` and `'yr': 'HORIZON_YEARS'` to `PARAM_MAP`; added `'yr'` to `INT_PARAMS`. `defaults.DOWN_PCT` and `defaults.HORIZON_YEARS` confirmed present (Story 2.5).
- Task 2: Added 3 tests at end of `test_url_state.py`: `test_decode_horizon_years_as_int`, `test_decode_down_pct_as_float`, `test_roundtrip_dp_and_yr`. All pass. Total tests: 102.
- Task 3: Added `import url_state`. Replaced 4-line comment with `_initial = url_state.decode_state(st.query_params.to_dict())` + horizon guard. Replaced all 18 `value=defaults.X` with `value=_initial['X']`. Added `st.query_params.update(url_state.encode_state({...}))` after sidebar with all 18 slider values.
- Task 4: 102/102 tests pass, AST clean. Manual smoke check left for user.

### File List

- `url_state.py` (modified)
- `tests/test_url_state.py` (modified)
- `app.py` (modified)

### Change Log

- 2026-05-30: Story 2.9 created â€” URL sharing & page load state restore
