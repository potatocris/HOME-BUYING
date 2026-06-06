---
title: 'Sidebar rent/buy grouped & color-coded inputs'
type: 'feature'
created: '2026-06-06'
status: 'done'
context: []
baseline_commit: '3fde2f2a85231efc1b921840b21bb2c1d08b2ed9'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** All 18 sidebar inputs sit under one flat "Essential Inputs" header, so users can't tell which inputs drive the rent side vs the buy side. The chart and table already use blue=renting (`#2B6CB0`) and purple=buying (`#6B46C1`), but the sidebar doesn't reflect that convention.

**Approach:** Regroup the sidebar into three labeled sections — a neutral group for shared inputs on top, then a blue Rental group, then a purple Buy group — and color each group's header AND its slider labels to match the established chart/table palette.

## Boundaries & Constraints

**Always:** Keep all 18 input variable names and their current values/ranges/steps unchanged. Preserve the URL round-trip — every key in the `st.query_params.update(url_state.encode_state({...}))` block stays present and unchanged. Keep each slider's min/max caption row directly beneath its own slider. Use exactly `#2B6CB0` (rental) and `#6B46C1` (buy). Group mapping is fixed: Rental = Market Rent, Rent Increase. Neutral = Comparison Horizon, Investment Return. Buy = everything else (Home Price, Down Payment, Mortgage Rate, HOA, HO-6 Insurance, Property Tax Rate, Home Appreciation, Closing Costs, Furniture & Improvements, plus the Advanced Inputs expander).

**Ask First:** Any change to the fixed group mapping above. Applying color to the neutral group's labels.

**Never:** Touch `calculations.py`, `defaults.py`, `url_state.py`, `formatting.py`, or `pages/scenarios.py`. Change slider ranges, steps, or default values. Rename URL keys. Alter the main-area cards, chart, or table. Recolor the neutral inputs.

</frozen-after-approval>

## Code Map

- `app.py:89-222` — the `with st.sidebar:` block; the ONLY code changed. Reorder sliders into 3 groups, add `key=` prefixes to colored sliders, inject scoped CSS, add colored group headers.
- `app.py:224-243` — `encode_state` block; must remain valid (all variable assignments still execute before it). Read-only reference — do not edit.

## Tasks & Acceptance

**Execution:**
- [x] `app.py` — At the top of the `with st.sidebar:` block, inject one `st.markdown("<style>...</style>", unsafe_allow_html=True)` that colors `section[data-testid="stSidebar"] div[class*="st-key-rent_"] label` blue (`#2B6CB0`) and `...div[class*="st-key-buy_"] label` purple (`#6B46C1`), with `!important`. Scope selectors to the sidebar so nothing leaks to the main area.
- [x] `app.py` — Replace the single "Essential Inputs" subheader with three colored group headers (HTML markdown): a neutral header (default text color), a blue "Rental" header, a purple "Buy" header. Keep the "Miami defaults loaded" caption near the top.
- [x] `app.py` — Reorder the 18 sliders into the fixed groups. Neutral first (Comparison Horizon, Investment Return), then Rental (Market Rent, Rent Increase), then Buy (the 9 sliders + Advanced Inputs expander). Assign `key="rent_*"` to Rental sliders and `key="buy_*"` to Buy sliders; leave neutral sliders unkeyed (or `key="nx_*"`). Keep each existing min/max caption row attached to its slider.

**Acceptance Criteria:**
- Given the app loads, when the sidebar renders, then inputs appear top-to-bottom as: neutral group (Comparison Horizon, Investment Return), Rental group (Market Rent, Rent Increase), Buy group (Home Price → Furniture, then Advanced Inputs expander).
- Given the sidebar renders, when viewing slider labels, then Rental labels are `#2B6CB0`, Buy labels are `#6B46C1`, and neutral labels keep the default color.
- Given a slider that had a min/max caption row, when the sidebar is reordered, then that caption row stays directly beneath its slider.
- Given the injected CSS, when inspecting the main area and the neutral sliders, then no blue/purple label coloring leaks outside the Rental/Buy groups.
- Given encoded URL state, when the page loads and a slider is changed, then the app runs without error and all 17 `encode_state` keys remain present with unchanged values.

## Design Notes

Streamlit 1.57 adds a `st-key-<key>` CSS class to each keyed widget's container `div`. Color slider labels by matching that class prefix — no nth-child fragility:

```python
st.markdown("""<style>
section[data-testid="stSidebar"] div[class*="st-key-rent_"] label { color:#2B6CB0 !important; }
section[data-testid="stSidebar"] div[class*="st-key-buy_"]  label { color:#6B46C1 !important; }
</style>""", unsafe_allow_html=True)
```

Group headers use explicit `color:` HTML (Streamlit can render markdown text white in dark mode), matching the existing card pattern, e.g. `st.markdown('<p style="color:#2B6CB0;font-weight:700;font-size:1.05rem;margin:1rem 0 0.25rem 0;">Rental</p>', unsafe_allow_html=True)`. Key prefixes are the contract the CSS depends on — `rent_` and `buy_` must stay in sync with the selectors.

## Verification

**Commands:**
- `python -m py_compile app.py` — expected: no output (syntax OK).
- `python -m pytest -q` — expected: 113 passed (no test touches the sidebar; suite stays green).

**Manual checks:**
- `streamlit run app.py` — sidebar shows three groups in the specified order; Rental labels blue, Buy labels purple, neutral labels default; min/max captions sit under their sliders; changing a slider updates the URL; main-area cards/chart/table unchanged.

## Suggested Review Order

**Color mechanism (entry point)**

- Sidebar-scoped CSS keys off `st-key-*` classes — the contract every slider key depends on.
  [`app.py:101`](../../app.py#L101)

**Group headers & ordering**

- Neutral group header + the two shared inputs (Horizon, Investment Return) on top.
  [`app.py:108`](../../app.py#L108)
- Blue Rental header, then Market Rent + Rent Increase.
  [`app.py:131`](../../app.py#L131)
- Purple Buy header, then all buy inputs + the Advanced expander.
  [`app.py:148`](../../app.py#L148)

**Regression surface**

- Consumer of every slider variable — confirms reorder/keying didn't break the URL round-trip.
  [`app.py:260`](../../app.py#L260)
