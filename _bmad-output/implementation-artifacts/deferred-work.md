# Deferred Work Log

## Deferred from: code review of scenarios-initial-costs-group (2026-06-06)

- **`down_payment` and `closing_fees` re-derived in the view, duplicating `calculate_upfront_cash`** (`pages/scenarios.py` scenario loop): The new Initial Costs breakdown recomputes `down_payment = price*down_pct/100` and `closing_fees = price*closing_pct/100` inline, while `calculations.calculate_upfront_cash` (`calculations.py:77`) computes the same terms to produce the total. Two sources of truth — if the upfront-cost definition ever changes (e.g. closing costs on loan amount instead of price), the card's "Cash Needed" total and its component rows silently diverge. Cleaner fix: have `calculate_upfront_cash` (or a sibling) return its components so the view consumes them. Deferred — out of scope for a display-only change.
- **New Initial Costs `<table>` has no header/scope semantics for screen readers** (`pages/scenarios.py` card HTML): Bare `<tr>/<td>` shipped via `unsafe_allow_html=True`, consistent with the adjacent monthly-cost table (house style). Belongs with the broader accessibility pass tracked in backlog story 3-8-accessibility-attributes.

## Deferred from: code review of 3-7-number-formatting-outcome-neutrality-enforcement (2026-06-06)

- **`fmt_pct_compact` emits `-0%` for a small negative percentage** (`formatting.py:34`): e.g. `fmt_pct_compact(-0.04)` → `"-0%"`. Unreachable today — the sole call site is the headline `down_pct`, bounded by the slider to [3.0, 30.0], never negative. Becomes relevant only if `fmt_pct_compact` is reused for a signed percentage. A guard (`if round(v, 1) == 0: return "0%"`) would fix it if/when needed.

## Deferred from: code review of 3-5-chart-and-table-polish (2026-06-06)

- **Styler `subset=["Better"]` would raise `KeyError` on a zero-column DataFrame** (`app.py` annual table block): `df.style.map(..., subset=["Better"])` assumes the "Better" column exists. Unreachable today — the horizon `select_slider` floor of 5 years guarantees ≥5 table rows — but latent if the minimum horizon is ever lowered below 12 months.
- **`_has_url_params` suppresses the "Miami defaults loaded" caption even when URL params are all invalid** (`app.py:~58`): `bool(st.query_params.to_dict())` is `True` for any params, including garbage/out-of-range ones that fall back to Miami defaults. The caption is then hidden even though defaults were effectively applied. Cosmetic, 3.3 carryover.
- **`__pycache__/*.pyc` bytecode is tracked in git** and appears in every diff. Should be added to `.gitignore` and untracked. Repo hygiene.

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

## Deferred from: code review of 2-2-sidebar-input-sliders-with-miami-defaults (2026-05-24)

- **`decode_state` no range-clamping against slider bounds** (`url_state.py`): Out-of-range URL values (e.g. `?hp=50000`) parse as valid finite floats but cause `StreamlitAPIException` when fed as `value=` to `st.slider`. Slider min/max are defined in `app.py`; `url_state.py` has no knowledge of them. Fix: clamp decoded values to slider bounds before passing as `value=` in Story 2.7. Related to the existing 2-1 deferred entry for "No range/domain validation in `decode_state`".
- **`SPECIAL_ASSESSMENT_MONTH` int-type fragility**: The slider uses all-`int` args (`min_value=1, max_value=60, step=1, value=defaults.SPECIAL_ASSESSMENT_MONTH`). If `defaults.SPECIAL_ASSESSMENT_MONTH` is ever changed to `1.0`, Streamlit raises `StreamlitAPIException` (mixed int/float). The int-ness is load-bearing for `url_state.INT_PARAMS = {'sam'}`. Consider adding a guard or comment in `defaults.py` noting `SPECIAL_ASSESSMENT_MONTH` must remain int.
- **No test asserting `slider_values` keys == `PARAM_MAP` values**: A key typo in `app.py`'s `slider_values` dict silently causes `encode_state` to skip that parameter (line 36: `if const_name in slider_values`), producing a URL that drops one input silently. Worth a small test: `assert set(slider_values) == set(url_state.PARAM_MAP.values())`.
- **Slider range caps below real Miami extremes**: `home_price` capped at $1M (luxury condos exceed this), `special_assessment_amount` capped at $100K (post-Surfside assessments have exceeded this per unit). Both are spec-defined defaults; revisit range maxima if the tool is shared publicly.
- **`SPECIAL_ASSESSMENT_MONTH` max=60 off-by-one risk for Story 2.3**: Slider allows months 1–60 inclusive. Story 2.3's calculation wiring must ensure month 60 is treated as within the 5-year horizon (not dropped or double-counted depending on whether the calc model uses 0-indexed or 1-indexed months).

## Deferred from: code review of stories 1-3 through 1-6 (2026-05-23)

- **No input validation for out-of-range inputs in calculation engine** (`calculations.py`): `down_pct >= 100` produces a zero/negative loan; negative `down_pct` or negative `price` produce nonsensical schedules; `months` outside 1–60 range in `calculate_monthly_property_tax` silently returns values; `vacancy_rate_pct` or `mgmt_fee_pct > 100` produce negative income. Epic 2 UI sliders will enforce all valid ranges — no fix needed at calculation layer.
- **pytest and dev dependencies in production `requirements.txt`**: `pytest==9.0.3`, `pluggy==1.6.0`, `iniconfig==2.3.0`, `Pygments==2.20.0` are dev-only and inflate the Streamlit Cloud deploy image. Low impact for a personal tool but worth separating into `requirements-dev.txt` before any public sharing.
- **Negative `monthly_contribution` in `calculate_investment_portfolio`**: Passing a withdrawal amount exceeding the balance produces a nonsensical compounding negative portfolio. Not applicable for this tool's slider-driven UI but worth noting for any future reuse of this engine.

## Deferred from: code review of 2-3-four-scenario-real-time-calculation-wiring (2026-05-24)

- **Break-even ignores selling costs from home equity** (`app.py:271–275`): `home_equity = appreciated_value - balance` with no deduction for realtor commission or transaction costs. The Sell exit path already computes net proceeds correctly; the break-even comparison uses the grosser home equity figure. Acceptable for a "how long until equity is worth it" metric; deferred as a design choice for now.
- **`monthly_contribution` fixed at month-1 costs for all 60 months** (`app.py:241`): PMI cancels around month ~36 for 5% down (~month 6 for 15% down, never for 20% down). Homestead exemption reduces property tax starting month 13. Using month-1 as representative overstates the buyer's monthly cost for later months, slightly disadvantaging buying. Documented as a known simplification in story Dev Notes.
- **Market rent held constant over 60-month horizon** (`app.py:241`): `market_rent` slider value is used as a fixed monthly figure for the full 5-year renter portfolio calculation. Real rent inflates annually. Acceptable simplification for v1; revisit if tool is shared publicly.
- **`monthly_contribution` clamped at 0 when buying cheaper than renting** (`app.py:241`): `max(0.0, total_m1 - market_rent)` — when buying costs less than market rent (possible for 20% down in high-rent markets), the buyer's monthly surplus is not modeled anywhere. Renter's portfolio gets no new contributions even though buying would be freeing up cash. Modeling limitation; would require redesigning the surplus tracking for both sides.

## Deferred from: code review of 2-5-rent-vs-buy-two-option-calculation-wiring (2026-05-29)

- **`renter_annual[-1]` / `buyer_annual[-1]` IndexError if annual list is empty** (`app.py` display block): `get_annual_snapshots` returns `[]` if monthly list has fewer than 12 entries. Can't crash today (HORIZON_YEARS=10 → 120 months), but Story 2.6 must set timeline slider minimum ≥ 1 year (5 years in practice) to prevent crash. Guard needed before `st.info(... renter_annual[-1] ...)`.
- **`calculate_monthly_property_tax` docstring says "(1-60)" but now called for months 1–360** (`calculations.py`): Stale docstring — function logic is correct for any month (homestead exemption applies from month 13 onward, indefinitely). Update docstring to remove the "(1-60)" range hint in a future cleanup story.
- **Furniture budget included in renter's opportunity cost portfolio** (`app.py`): `upfront_cash` includes `furniture_budget` ($15K default), which inflates the renter's investment starting capital by $15K. A renter would also buy furniture, so this isn't truly "opportunity cost." At 7% return over 10 years, this overstates renter wealth by ~$29K. Pre-existing design assumption from Story 2.3; revisit if tool is shared publicly.

## Deferred from: code review of 2-4-multi-page-app-setup (2026-05-29)

- **`_fmt` formats negative numbers as `$-X` with no sign guard** (`pages/scenarios.py`): Negative `exit_sell` or negative `home_equity` renders as `$-12,345` — not a valid currency display. Pre-existing; cosmetic until a future story displays these values.
- **`break_even_month=None` silent trap + `_fmt(None)` crash** (`pages/scenarios.py`): When no break-even month is found in 60 months, `break_even_month` stays `None`. Not displayed in Story 2.4, but a future story rendering it will either show "None" or raise `ValueError: Unknown format code 'f' for NoneType`. Guard needed before Story 2.5+ renders break-even.
- **No engine guard on negative mortgage rate** (`calculations.py`): `calculate_amortization_schedule` has no assertion against negative rates. UI slider (min=3.0%) blocks this today. Pre-existing.
- **Floating-point amortization can produce a tiny negative balance** (`calculations.py`): Rounding error over 60 iterations can cause the terminal balance to go a few cents below zero, slightly inflating `exit_sell` net proceeds. Pre-existing, theoretical.
- **`appreciation_rate=0` + realtor fees can make `exit_sell` silently negative** (`pages/scenarios.py`): At 0% appreciation the undiscounted loan balance + fees can exceed the flat home price, producing a negative exit value with no warning. Not displayed in Story 2.4. Pre-existing.
- **Landlord exit uses static month-1 carrying costs** (`pages/scenarios.py`): Homestead exemption reduces property tax from month 13 (overstating landlord costs) and PMI is excluded (understating costs for <20% down). Known simplification, pre-existing.
- **No explicit `key=` args on sliders in `pages/scenarios.py`** (`pages/scenarios.py` sidebar): Streamlit auto-generates keys from label strings. Both pages use identical labels. In the current multi-page setup this is fine, but when Story 2.9 wires `st.query_params` URL state, the lack of explicit keys can cause state bleed between pages. Add `key=` args before Story 2.9.

## Deferred from: code review of 1-8-variable-horizon-engine-extension (2026-05-25)

- **`months > 360` in `calculate_amortization_schedule` produces negative balances** (`calculations.py`): After month 360 the loan is fully amortized; continuing the loop causes principal to keep subtracting from a ~$0 balance, yielding negative values. Per the established project policy, engine-layer input validation is deferred to the UI; Story 2.6's timeline slider caps the horizon at 30 years (360 months).
- **`months=0` or negative passed to `calculate_amortization_schedule` returns empty list silently** (`calculations.py`): `range(1, months+1)` with non-positive `months` yields an empty range. Consistent with project policy; no UI slider can produce 0 or negative months.
- **Negative surplus values in `calculate_buyer_investment_portfolio` not guarded** (`calculations.py`): The function accepts any numeric value in `monthly_surplus_list`; a negative surplus drives the balance negative. Caller responsibility per docstring (`max(0, …)`); Story 2.5 enforces this before calling.
- **`get_annual_snapshots` with list shorter than 12 months returns empty list silently** (`calculations.py`): `range(11, N, 12)` with `N < 12` is empty. Documented behavior (`len(result) == len(monthly_values) // 12`); practical callers always pass ≥ 60 months.
- **`calculate_exit_continue_renting` docstring references "month 60" — stale with variable horizon** (`calculations.py:108`): Docstring says "portfolio value at month 60" but the function returns `portfolio_values[-1]`, which may be any horizon length. Pre-existing; update when the 5-year horizon is fully retired in a future story.
