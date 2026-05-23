# Story 1.2: Miami Defaults Module

Status: review

## Story

As a developer,
I want a single isolated `defaults.py` file containing all Miami-specific input values and a last-reviewed date,
So that Miami defaults can be updated without touching any calculation logic.

## Acceptance Criteria

1. **Given** `defaults.py` exists at the project root, **When** `import defaults` is run in Python, **Then** it succeeds without error.
2. **Given** `defaults.py` is imported, **Then** it exposes named constants for every slider input: `HOME_PRICE`, `MORTGAGE_RATE`, `HOA_MONTHLY`, `HO6_INSURANCE_ANNUAL`, `PROPERTY_TAX_RATE`, `MARKET_RENT`, `INVESTMENT_RETURN_RATE`, `APPRECIATION_RATE`, `CLOSING_COST_PCT`, `FURNITURE_BUDGET`, `SPECIAL_ASSESSMENT_AMOUNT`, `SPECIAL_ASSESSMENT_MONTH`, `RENTAL_INCOME_MONTHLY`, `VACANCY_RATE`, `PROPERTY_MGMT_FEE_PCT`, `REALTOR_COMMISSION_PCT`.
3. **Given** `defaults.py` is imported, **Then** it exposes `DEFAULTS_LAST_UPDATED` as a string in `"Month YYYY"` format (e.g., `"May 2026"`).
4. **Given** `calculations.py` is inspected after this story, **Then** it still contains zero Streamlit imports and zero references to `defaults.py` — the engine has no dependency on defaults (ARCH-3, ARCH-4).
5. **Given** any constant in `defaults.py` is changed, **Then** no changes are required in `calculations.py`, `url_state.py`, or `app.py` — isolation is total.
6. **Given** `defaults.py` is inspected, **Then** it contains no Streamlit imports, no function definitions, no calculation logic, and no control flow — constants only.

## Tasks / Subtasks

- [x] **Task 1: Replace stub docstring with all constants** (AC: 1, 2, 3, 6)
  - [x] Open `defaults.py` at project root (currently a docstring-only stub from Story 1.1)
  - [x] Keep the existing module docstring — update it to remove "Implemented in Story 1.2" now that it is being implemented
  - [x] Add all 16 slider constants + `DEFAULTS_LAST_UPDATED` — see Dev Notes for exact values and naming
  - [x] Use ALL_CAPS naming for all constants (Python module-level constant convention)
  - [x] Store percentage values as human-readable floats (e.g., `6.5` not `0.065`) — sliders display these directly to the user
  - [x] Store dollar amounts as plain integers or floats — no string formatting
  - [x] Add a short inline comment on each constant explaining the Miami source/rationale

- [x] **Task 2: Verify ARCH-4 compliance** (AC: 4, 5, 6)
  - [x] Run AST check: no imports found — PASS
  - [x] Confirm no function defs: no functions found — PASS
  - [x] Confirm `calculations.py` is unchanged and still has zero imports of any kind
  - [x] Confirm `app.py` and `url_state.py` are unchanged

- [x] **Task 3: Verify all constants are accessible** (AC: 1, 2, 3)
  - [x] `defaults.DEFAULTS_LAST_UPDATED` → "May 2026" — PASS
  - [x] `defaults.HOME_PRICE` → 300000, `defaults.MORTGAGE_RATE` → 6.5 — PASS
  - [x] All 17 constants present check — PASS

## Dev Notes

### File Location

`defaults.py` lives at the **project root** — same level as `app.py`, `calculations.py`, `url_state.py`:
```
C:\Users\criss\Documents\Home Buying\
  defaults.py          ← THIS FILE (replacing the stub)
  app.py
  calculations.py
  url_state.py
  requirements.txt
```

### Exact Content for `defaults.py`

```python
"""
Miami-specific default input values and last-reviewed date.

Isolated from calculation logic so defaults can be updated independently.
All percentage values stored as human-readable floats (6.5 = 6.5%, not 0.065)
so they feed directly into Streamlit sliders without conversion.
"""

# ── Property ──────────────────────────────────────────────────────────────
HOME_PRICE = 300_000          # Miami condo target price (dollars)
APPRECIATION_RATE = 3.0       # Conservative Miami appreciation (% per year)
PROPERTY_TAX_RATE = 1.0       # Miami-Dade effective rate with homestead (% of value)
HOA_MONTHLY = 500             # Post-Surfside reserve spike estimate ($/month)
HO6_INSURANCE_ANNUAL = 1_200  # Florida HO-6 condo unit policy ($/year)

# ── Mortgage ──────────────────────────────────────────────────────────────
MORTGAGE_RATE = 6.5           # 30-year fixed (% per year)
CLOSING_COST_PCT = 3.5        # FL avg: title, recording, lender fees (% of price)

# ── Renting / Opportunity Cost ────────────────────────────────────────────
MARKET_RENT = 2_000           # Comparable Miami unit monthly rent ($/month)
INVESTMENT_RETURN_RATE = 7.0  # Long-run stock market return assumption (% per year)

# ── Upfront Costs ─────────────────────────────────────────────────────────
FURNITURE_BUDGET = 15_000     # Furniture and improvements estimate (dollars)

# ── Special Assessment ────────────────────────────────────────────────────
SPECIAL_ASSESSMENT_AMOUNT = 0  # Default: no assessment (dollars)
SPECIAL_ASSESSMENT_MONTH = 1   # Month the assessment lands (1–60)

# ── Landlord Scenario ─────────────────────────────────────────────────────
RENTAL_INCOME_MONTHLY = 2_000  # Expected gross rent if unit rented out ($/month)
VACANCY_RATE = 5.0             # Assumed vacancy (% of months)
PROPERTY_MGMT_FEE_PCT = 10.0   # Property manager cut of gross rent (%)

# ── Exit Costs ────────────────────────────────────────────────────────────
REALTOR_COMMISSION_PCT = 5.5   # Seller's agent + buyer's agent total (%)

# ── Metadata ──────────────────────────────────────────────────────────────
DEFAULTS_LAST_UPDATED = "May 2026"  # Displayed in DisclaimerBanner (Story 3.2)
```

### ARCH-4 Invariant — Never Break This

`defaults.py` must contain **zero imports, zero functions, zero calculation logic** for the entire project lifetime. It is a pure data file. This is enforced by Task 2 and must be maintained through all subsequent stories.

If `app.py` needs to pass defaults into a calculation function, it does so like:
```python
import defaults
import calculations
result = calculations.some_function(defaults.HOME_PRICE, defaults.MORTGAGE_RATE)
```
`calculations.py` never imports `defaults` — the dependency flows through `app.py` only.

### Percentage Convention

All rates are stored as **display percentages** (e.g., `6.5` means 6.5%), not decimals. This is intentional so `app.py` can pass them directly to `st.slider(value=defaults.MORTGAGE_RATE)` without conversion. `calculations.py` will divide by 100 where needed — that is the calculation layer's responsibility, not the defaults layer's.

### Story 1.1 Learnings — Critical for This Story

- **Python command:** Use `python` not `python3` on this Windows machine
- **Virtual environment:** `.venv\Scripts\Activate.ps1` — activate before running verification commands
- **BOM issue:** If writing `defaults.py` via PowerShell redirect (`>`), use `[System.IO.File]::WriteAllLines()` with UTF-8 no-BOM encoding. Writing via Claude's Write tool is safe and BOM-free.
- **File already exists** as a stub — overwrite it entirely; do not append
- **No test framework yet** — unit testing scaffold added in Story 1.3; verification here is via `python -c` one-liners only

### What Story 1.2 Does NOT Do

- Does NOT add any import statements to `defaults.py`
- Does NOT add functions or classes
- Does NOT change `calculations.py`, `app.py`, or `url_state.py`
- Does NOT install new packages
- Does NOT create `.streamlit/config.toml` (deferred to Story 3.1)
- Does NOT wire defaults into sliders (deferred to Story 2.2)
- Does NOT add `DEFAULTS_LAST_UPDATED` to the UI (deferred to Story 3.2 DisclaimerBanner)

### Cross-Story Context

| Story | Dependency on `defaults.py` |
|---|---|
| 1.3–1.6 | `calculations.py` gets values via `app.py` — never imports defaults directly |
| 2.2 | `app.py` uses all constants as `st.slider(value=defaults.X)` initial values |
| 2.7 | URL decode falls back to `defaults.X` for missing/invalid params |
| 3.2 | `DEFAULTS_LAST_UPDATED` displayed in DisclaimerBanner |

### References

- [Source: epics.md — Story 1.2 Acceptance Criteria]
- [Source: architecture.md — ARCH-4: defaults.py isolation]
- [Source: prd.md — FR29, FR30: defaults pre-population and last-updated date]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (Claude Code, 2026-05-22)

### Debug Log References

PowerShell parallel tool calls hit internal errors — switched to Bash tool for all verification. No functional issues.

### Completion Notes List

- Replaced `defaults.py` stub (docstring only) with 16 slider constants + `DEFAULTS_LAST_UPDATED`.
- All constants use ALL_CAPS naming; percentages stored as human-readable floats (6.5 not 0.065).
- AST verified: zero imports, zero function definitions — ARCH-4 compliant.
- All 17 constants confirmed accessible via `import defaults` — PASS.
- `calculations.py`, `app.py`, `url_state.py` untouched — isolation total.

### File List

- `defaults.py` (modified — stub replaced with 16 constants + DEFAULTS_LAST_UPDATED)

## Change Log

- 2026-05-22: Story 1.2 implemented — defaults.py populated with all Miami-specific constants. ARCH-4 compliance verified via AST.
