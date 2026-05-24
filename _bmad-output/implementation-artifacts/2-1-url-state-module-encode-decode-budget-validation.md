# Story 2.1: URL State Module (Encode/Decode + Budget Validation)

Status: review

## Story

As a developer,
I want `url_state.py` to encode all slider values into a URL query string and decode them back reliably,
So that the URL sharing feature (Stories 2.7) has a tested, validated foundation before the UI is wired up.

## Acceptance Criteria

1. **Given** a dictionary of all configurable slider values (keyed by `defaults.py` constant names), **When** `encode_state(slider_values)` is called, **Then** it returns a dict of abbreviated string key-value pairs (e.g., `{'hp': '300000.0', 'mr': '6.5', ...}`) suitable for direct assignment to `st.query_params`.
2. **Given** the encoded params dict, **When** the query string is assembled as `key=value&key=value...`, **Then** its length does not exceed 2,000 characters (NFR4).
3. **Given** the encoded length would exceed 2,000 characters, **When** `encode_state` is called, **Then** it raises a `ValueError` with a message including "exceeds" rather than silently truncating (ARCH-5).
4. **Given** a dict of abbreviated URL params (strings, as returned by `st.query_params.to_dict()`), **When** `decode_state(query_params)` is called, **Then** it returns a dict keyed by `defaults.py` constant names with values parsed to the correct Python type (float or int).
5. **Given** any key is missing from `query_params`, **When** `decode_state` is called, **Then** the missing key falls back to the Miami default value from `defaults.py` — no exception raised.
6. **Given** any value in `query_params` is non-numeric or empty, **When** `decode_state` is called, **Then** that value falls back to the Miami default — no exception raised.
7. **Given** Miami-default slider values, **When** `encode_state` then `decode_state` is called, **Then** all values round-trip with less than 0.001 absolute error.
8. **Given** `pytest` runs from the project root, **Then** all tests in `tests/test_url_state.py` pass, and all 55 existing tests in `tests/test_calculations.py` still pass (no regressions).
9. **Given** `url_state.py` after this story, **Then** `grep "import streamlit" url_state.py` returns nothing — pure Python module, independently testable.

## Tasks / Subtasks

- [x] **Task 1: Write failing tests first** (AC: 1–9)
  - [x] Create `tests/test_url_state.py` with the complete test suite from Dev Notes
  - [x] Run `python -m pytest tests/test_url_state.py -v` — confirm ALL tests FAIL (ImportError/AttributeError is expected)
  - [x] Run `python -m pytest tests/test_calculations.py -v` — confirm all 55 still PASS (regression check)

- [x] **Task 2: Implement `url_state.py`** (AC: 1–7, 9)
  - [x] Replace the docstring stub with the full implementation from Dev Notes
  - [x] Add `PARAM_MAP` constant (16 abbreviated keys ↔ defaults.py constant names)
  - [x] Add `INT_PARAMS` constant (params that decode as int, not float)
  - [x] Add `URL_MAX_QUERY_LENGTH = 2000`
  - [x] Implement `encode_state(slider_values: dict) -> dict`
  - [x] Implement `decode_state(query_params: dict) -> dict`
  - [x] Verify: `grep "import streamlit" url_state.py` returns nothing

- [x] **Task 3: Run all tests and verify** (AC: 8)
  - [x] Run `python -m pytest tests/ -v` — ALL tests must be GREEN (55 existing + new url_state tests)
  - [x] Run ARCH check: `python -c "import ast; tree = ast.parse(open('url_state.py').read()); sl = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and any('streamlit' in (getattr(n,'module','') or '') or any('streamlit' in a.name for a in getattr(n,'names',[])) for _ in [n])]; print('ARCH PASS' if not sl else 'FAIL: streamlit import found')"`

## Dev Notes

### Current State of `url_state.py`

The file currently contains only a docstring stub (created in Story 1.1):

```python
"""
URL state encoding and decoding for shareable scenario links.

Encodes all 12 slider values to st.query_params; validates total URL
length does not exceed 2,000 characters. Implemented in Story 2.1.
"""
```

**Replace the entire file contents** with the implementation below. Do NOT add Streamlit imports.

### Note on "12 sliders" vs Actual 16

The epics and story AC reference "12 slider values" (matching FR1–FR12 count). In practice, `defaults.py` has **16** configurable constants — FR11 has 2 inputs (amount + month), FR12 has 3 inputs (rental income, vacancy, mgmt fee), and `REALTOR_COMMISSION_PCT` from FR19 is also user-configurable. This implementation encodes all 16 configurable inputs. Stories 2.2 and 2.7 will pass all 16 values.

### Resolving the URL Budget Ambiguity (from deferred-work.md)

The deferred note asked whether the 2,000-char limit applies to the query string or the full URL. **Decision: validate the query string length.** The Streamlit Cloud domain adds ≤60 chars; with Miami defaults the query string is ~150 chars — well within budget regardless. Validating the query string is conservative and sufficient.

### `url_state.py` — Complete Implementation

```python
"""
URL state encoding and decoding for shareable scenario links.

Pure Python — no Streamlit imports. encode_state/decode_state work with
plain Python dicts; app.py handles st.query_params read/write.
"""

import defaults

# Bidirectional mapping: abbreviated URL key ↔ defaults.py constant name
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
}

# Keys that decode as int (not float)
INT_PARAMS = {'sam'}  # SPECIAL_ASSESSMENT_MONTH is always a whole month number

# Validate query string (the part after '?') against this limit (NFR4 / ARCH-5)
URL_MAX_QUERY_LENGTH = 2000


def encode_state(slider_values: dict) -> dict:
    """Encodes slider values to abbreviated URL query params.

    Args:
        slider_values: dict keyed by defaults.py constant names
                       (e.g., {'HOME_PRICE': 300000.0, 'MORTGAGE_RATE': 6.5, ...})

    Returns:
        dict of abbreviated string key-value pairs suitable for st.query_params
        (e.g., {'hp': '300000.0', 'mr': '6.5', ...})

    Raises:
        ValueError: if the assembled query string exceeds URL_MAX_QUERY_LENGTH chars
    """
    params = {}
    for short_key, const_name in PARAM_MAP.items():
        if const_name in slider_values:
            params[short_key] = str(slider_values[const_name])

    query_string = '&'.join(f'{k}={v}' for k, v in params.items())
    if len(query_string) > URL_MAX_QUERY_LENGTH:
        raise ValueError(
            f"Encoded URL query string ({len(query_string)} chars) exceeds "
            f"{URL_MAX_QUERY_LENGTH}-character limit (NFR4)"
        )

    return params


def decode_state(query_params: dict) -> dict:
    """Decodes URL query params back to slider values.

    Args:
        query_params: dict of string key-value pairs (e.g., from st.query_params.to_dict())
                      Keys are abbreviated (e.g., 'hp', 'mr', ...).
                      Missing keys or invalid values fall back to Miami defaults.

    Returns:
        dict keyed by defaults.py constant names with correctly typed values
        (floats for most; int for SPECIAL_ASSESSMENT_MONTH)
    """
    result = {}
    for short_key, const_name in PARAM_MAP.items():
        default_val = getattr(defaults, const_name)
        raw = query_params.get(short_key)
        if raw is None or raw == '':
            result[const_name] = default_val
        else:
            try:
                result[const_name] = int(raw) if short_key in INT_PARAMS else float(raw)
            except (ValueError, TypeError):
                result[const_name] = default_val
    return result
```

### How `app.py` Will Use This Module (for context — do NOT implement in this story)

```python
# Story 2.7 will wire this up in app.py:

import url_state

# On page load — restore state from URL:
slider_values = url_state.decode_state(st.query_params.to_dict())

# On any slider change — update URL:
st.query_params.update(url_state.encode_state(current_slider_values))
```

The slider_values dict flowing through the app always uses defaults.py constant names as keys.

### `tests/test_url_state.py` — Complete Test Suite

```python
import pytest
import defaults
from url_state import encode_state, decode_state, PARAM_MAP, INT_PARAMS, URL_MAX_QUERY_LENGTH


def _miami_defaults():
    """Build a full slider_values dict from Miami defaults."""
    return {const_name: getattr(defaults, const_name) for const_name in PARAM_MAP.values()}


# ── encode_state ──────────────────────────────────────────────────────────────

def test_encode_returns_abbreviated_keys():
    params = encode_state(_miami_defaults())
    assert 'hp' in params
    assert 'HOME_PRICE' not in params


def test_encode_covers_all_params():
    params = encode_state(_miami_defaults())
    assert set(params.keys()) == set(PARAM_MAP.keys())


def test_encode_home_price_as_string():
    params = encode_state(_miami_defaults())
    assert params['hp'] == str(defaults.HOME_PRICE)


def test_encode_query_string_within_budget():
    params = encode_state(_miami_defaults())
    query = '&'.join(f'{k}={v}' for k, v in params.items())
    assert len(query) <= URL_MAX_QUERY_LENGTH


def test_encode_raises_on_budget_overflow():
    # Fabricate a value long enough to overflow 2000 chars
    oversize = {const: 'x' * 200 for const in PARAM_MAP.values()}
    with pytest.raises(ValueError, match="exceeds"):
        encode_state(oversize)


def test_encode_ignores_unknown_keys():
    # Extra keys not in PARAM_MAP are silently dropped
    values = _miami_defaults()
    values['UNKNOWN_KEY'] = 99999
    params = encode_state(values)
    assert set(params.keys()) == set(PARAM_MAP.keys())


def test_encode_partial_dict_only_encodes_present_keys():
    params = encode_state({'HOME_PRICE': 350_000.0})
    assert 'hp' in params
    assert len(params) == 1


# ── decode_state ──────────────────────────────────────────────────────────────

def test_decode_home_price_as_float():
    result = decode_state({'hp': '350000.0'})
    assert result['HOME_PRICE'] == 350_000.0
    assert isinstance(result['HOME_PRICE'], float)


def test_decode_special_assessment_month_as_int():
    result = decode_state({'sam': '12'})
    assert result['SPECIAL_ASSESSMENT_MONTH'] == 12
    assert isinstance(result['SPECIAL_ASSESSMENT_MONTH'], int)


def test_decode_all_non_int_params_are_floats():
    result = decode_state({k: '1.0' for k in PARAM_MAP.keys()})
    for short_key, const_name in PARAM_MAP.items():
        if short_key not in INT_PARAMS:
            assert isinstance(result[const_name], float), f"{const_name} should be float"


def test_decode_empty_params_falls_back_to_all_defaults():
    result = decode_state({})
    for const_name in PARAM_MAP.values():
        assert result[const_name] == getattr(defaults, const_name)


def test_decode_missing_single_key_falls_back_to_default():
    result = decode_state({'hp': '400000.0'})  # only home price provided
    assert result['HOME_PRICE'] == 400_000.0
    assert result['MORTGAGE_RATE'] == defaults.MORTGAGE_RATE  # fallback


def test_decode_invalid_value_falls_back_to_default():
    result = decode_state({'hp': 'not-a-number'})
    assert result['HOME_PRICE'] == defaults.HOME_PRICE


def test_decode_empty_string_falls_back_to_default():
    result = decode_state({'mr': ''})
    assert result['MORTGAGE_RATE'] == defaults.MORTGAGE_RATE


def test_decode_unrecognized_key_is_ignored():
    result = decode_state({'unknown_key': '999'})
    # Should still return all defaults without error
    assert result['HOME_PRICE'] == defaults.HOME_PRICE


# ── Round-trip ────────────────────────────────────────────────────────────────

def test_roundtrip_miami_defaults():
    original = _miami_defaults()
    decoded = decode_state(encode_state(original))
    for const_name, val in original.items():
        assert abs(decoded[const_name] - val) < 0.001, \
            f"Round-trip mismatch for {const_name}: {val} → {decoded[const_name]}"


def test_roundtrip_non_default_values():
    values = _miami_defaults()
    values['HOME_PRICE'] = 450_000.0
    values['MORTGAGE_RATE'] = 7.25
    values['SPECIAL_ASSESSMENT_MONTH'] = 36
    decoded = decode_state(encode_state(values))
    assert abs(decoded['HOME_PRICE'] - 450_000.0) < 0.001
    assert abs(decoded['MORTGAGE_RATE'] - 7.25) < 0.001
    assert decoded['SPECIAL_ASSESSMENT_MONTH'] == 36


def test_roundtrip_zero_special_assessment():
    values = _miami_defaults()
    values['SPECIAL_ASSESSMENT_AMOUNT'] = 0.0
    decoded = decode_state(encode_state(values))
    assert decoded['SPECIAL_ASSESSMENT_AMOUNT'] == 0.0


# ── NFR3: Performance < 100ms ─────────────────────────────────────────────────

def test_encode_is_fast_nfr3():
    import time
    values = _miami_defaults()
    start = time.perf_counter()
    for _ in range(1000):
        encode_state(values)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    assert elapsed_ms < 100, f"encode_state took {elapsed_ms:.2f}ms avg (NFR3 limit: 100ms)"


def test_decode_is_fast_nfr3():
    import time
    params = encode_state(_miami_defaults())
    start = time.perf_counter()
    for _ in range(1000):
        decode_state(params)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    assert elapsed_ms < 100, f"decode_state took {elapsed_ms:.2f}ms avg (NFR3 limit: 100ms)"
```

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  url_state.py              ← REPLACE entire contents (currently docstring stub)
  tests/
    test_url_state.py       ← NEW file
    test_calculations.py    ← DO NOT TOUCH (55 tests must stay green)
    __init__.py             ← DO NOT TOUCH
```

### Key Constraints

- **No Streamlit imports** in `url_state.py` — pure Python only. `st.query_params` integration lives in `app.py` (Story 2.7). This keeps url_state.py independently testable.
- **`defaults` is the only import** beyond stdlib.
- **Do NOT modify** `calculations.py`, `defaults.py`, `app.py`, or any existing test file.
- **Use `python`** not `python3` on this Windows machine.
- **Run pytest** as `python -m pytest tests/ -v` with the venv active.

### Story Learnings from Epic 1

- `python -m pytest tests/ -v` works reliably (not `.venv\Scripts\pytest.exe` which fails in Bash)
- Bash tool works better than PowerShell for Python verification one-liners
- BOM-free requirements.txt: use `[System.IO.File]::WriteAllLines` if pip install is needed (none required here — no new dependencies)
- TDD red-green sequence: always confirm tests FAIL before implementing
- The existing test suite is 55 tests in `tests/test_calculations.py` — run it before and after to confirm zero regressions

### Cross-Story Context

| Story | Uses url_state.py output |
|---|---|
| 2.7 | `encode_state` called on every slider change to update `st.query_params`; `decode_state` called on page load to restore slider values from URL |
| 2.2 | Slider defaults on first load — if `decode_state({})` is called with empty params, all values fall back to Miami defaults. This is the "first load" behavior. |
| 2.8 | If `encode_state` raises `ValueError` (URL budget overflow), Story 2.8's error handling must catch it and display a user-readable message instead of a traceback |

### References

- [Source: epics.md — Story 2.1 Acceptance Criteria, FR33, FR34, FR35]
- [Source: prd.md — NFR3 (encode/decode < 100ms), NFR4 (URL ≤ 2,000 chars)]
- [Source: architecture.md — ARCH-5 (url_state.py validates URL budget), modular structure]
- [Source: deferred-work.md — URL budget measurement decision resolved: query string only]
- [Source: defaults.py — all 16 configurable constants + their default values]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- RED phase confirmed: `python -m pytest tests/test_url_state.py` → ImportError (20 collected, 0 passed)
- 55 existing tests confirmed passing before implementation
- GREEN phase: 20/20 url_state tests pass after implementation
- Full suite: 75/75 passing, 0.08s
- ARCH-3 check: `url_state.py` has zero Streamlit imports (pure Python)

### Completion Notes List

- Implemented `url_state.py` from docstring stub: PARAM_MAP (16 keys), INT_PARAMS ({'sam'}), URL_MAX_QUERY_LENGTH=2000, encode_state(), decode_state()
- TDD cycle complete: RED (ImportError) → GREEN (20/20) → no refactor needed
- All 9 ACs satisfied: encode abbreviation, budget validation, ValueError on overflow, decode type coercion, default fallback (missing/invalid/empty), round-trip accuracy, regression-free, ARCH-3 pure Python
- 75/75 total tests passing (55 calculations + 20 url_state)
- Note on "12 vs 16 sliders": implemented all 16 configurable constants from defaults.py (AC says "12" matching FR count, but defaults.py has 16 — encoded all 16 as documented in Dev Notes)

### File List

- `url_state.py` — MODIFIED (docstring stub → full implementation)
- `tests/test_url_state.py` — NEW (20 tests: encode, decode, round-trip, NFR3 performance)

### Change Log

- 2026-05-23: Story 2.1 implemented and all tasks complete. url_state.py implemented with full PARAM_MAP (16 params), encode_state, decode_state. 75/75 tests green.
