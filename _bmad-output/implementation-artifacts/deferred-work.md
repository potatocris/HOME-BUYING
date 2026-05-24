# Deferred Work Log

## Deferred from: code review of 1-1-project-scaffold-module-structure (2026-05-22)

- **No python_requires or minimum Python version constraint documented.** No setup.cfg, pyproject.toml, or .python-version file exists. Compiled wheels (numpy, pyarrow, pillow) are Python-minor-version specific — a developer on a different minor version will get cryptic errors.
- **pyvenv.cfg points to Anaconda base interpreter.** If the venv is ever recreated, story instructions must specify the exact interpreter path (C:\Users\criss\anaconda3\python.exe) to preserve Python 3.12.7 and avoid wheel compatibility issues.
- **watchdog 6.0.0 + OneDrive sync interaction.** Project lives in Documents\ which OneDrive syncs by default. watchdog's ReadDirectoryChangesW may fire spuriously on OneDrive .tmp files, causing unexpected Streamlit hot-reloads or PermissionErrors during active development.
- **URL state budget definition unresolved.** url_state.py docstring states a 2,000-character cap on "total URL length." Story 2.1 must clarify whether this is measured from the full URL (including Streamlit Cloud domain ~40-60 chars) or the query string only — the distinction affects whether the validation logic is correct in production.

## Deferred from: code review of 2-1-url-state-module-encode-decode-budget-validation (2026-05-23)

- **URL length check uses raw (unencoded) key=value pairs** (`url_state.py:38`): The 2000-char budget is measured against `str()` output without percent-encoding. All current values are numeric, so no special characters exist today — but if a string-valued param were ever added to PARAM_MAP, the check would undercount real URL length.
- **No range/domain validation in `decode_state`** (`url_state.py:47`): Any `math.isfinite` float passes through verbatim (e.g., `hp=999999999999.0`, `vac=100`). Story 2.8 handles error display; Epic 2 UI sliders enforce valid ranges. Not actionable here.
- **Performance test threshold very lenient** (`tests/test_url_state.py:150,160`): `elapsed_ms < 100` asserts an average per-call time under 100ms, which will never fail on any modern machine for a pure-Python dict lookup. Consider tightening to `< 1` ms in a future test quality pass.
- **`calculate_exit_continue_renting` returns 0.0 for empty portfolio** (`calculations.py:110`): Defensive guard silently masks upstream logic errors. Acceptable as a safety net; upstream empty-portfolio would be caught by other scenario tests.
- **`pmi_cancelled` no guard for `price == 0`** (`calculations.py:24`): Division by zero if price is zero. Pre-existing issue; slider enforces a minimum home price at the UI layer.
- **`test_exit_rent_out_reconciles_cashflow_plus_equity_ac5` tautological**: Test manually recomputes the same formula as the implementation. Passes even if both share an incorrect formula. Low risk for a personal tool; a future refactor should test against a fixed known-correct value.

## Deferred from: code review of stories 1-3 through 1-6 (2026-05-23)

- **No input validation for out-of-range inputs in calculation engine** (`calculations.py`): `down_pct >= 100` produces a zero/negative loan; negative `down_pct` or negative `price` produce nonsensical schedules; `months` outside 1–60 range in `calculate_monthly_property_tax` silently returns values; `vacancy_rate_pct` or `mgmt_fee_pct > 100` produce negative income. Epic 2 UI sliders will enforce all valid ranges — no fix needed at calculation layer.
- **pytest and dev dependencies in production `requirements.txt`**: `pytest==9.0.3`, `pluggy==1.6.0`, `iniconfig==2.3.0`, `Pygments==2.20.0` are dev-only and inflate the Streamlit Cloud deploy image. Low impact for a personal tool but worth separating into `requirements-dev.txt` before any public sharing.
- **Negative `monthly_contribution` in `calculate_investment_portfolio`**: Passing a withdrawal amount exceeding the balance produces a nonsensical compounding negative portfolio. Not applicable for this tool's slider-driven UI but worth noting for any future reuse of this engine.
