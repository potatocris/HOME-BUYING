# Story 2.4: Monthly Cost Breakdown Display

Status: review

## Story

As a user,
I want to see a detailed monthly cost breakdown for each down payment scenario,
so that I understand exactly what I would pay each month and how costs differ by scenario.

## Acceptance Criteria

1. **Given** calculations have run for all four scenarios, **When** the main area renders, **Then** each scenario column displays monthly line items in fixed order: P&I → PMI → HOA → Property Tax → Insurance → Total (FR24).
2. **Given** the 20% down scenario, **When** the monthly breakdown renders, **Then** PMI shows as $0 (no PMI at 80% LTV) — this happens automatically from the amortization engine, no special-case code needed.
3. **Given** any dollar amount is displayed, **When** it appears in the monthly breakdown, **Then** it is formatted as nearest dollar with $ prefix and comma separator (e.g., $1,234) (UX-DR10).
4. **Given** all four scenarios are displayed, **When** any slider changes, **Then** all four columns update within a single Streamlit rerun (FR28, NFR2).
5. **Given** a special assessment amount > 0, **When** the breakdown renders, **Then** the special assessment is shown as a separate one-time note below the recurring total — NOT as a line item in the Total row (because it is a lump-sum cost, not a monthly recurring cost).
6. **Given** `app.py` after this story, **Then** `calculations.py`, `defaults.py`, `url_state.py`, and all files under `tests/` remain byte-for-byte unchanged.

## Tasks / Subtasks

- [x] **Task 1: Replace interim 4-column display with monthly cost breakdown (AC: 1–5)**
  - [x] Add `_fmt` helper function at the start of the main area section (before the columns loop)
  - [x] Replace the `cols`/loop/`st.info` interim block (lines 232–243 in current `app.py`) with the new implementation per Dev Notes
  - [x] Verify: each column shows header (X% Down, Upfront: $X,XXX), recurring monthly total, five line items in correct order, Total row, optional special assessment note
  - [x] Verify: 20% Down column shows PMI = $0

- [x] **Task 2: Manual smoke test (AC: 3–4)**
  - [x] Run `streamlit run app.py` (venv active)
  - [x] Open `http://localhost:8501` in Chrome
  - [x] Confirm 4 columns appear with correct formatting ($ prefix, commas, no decimals)
  - [x] Confirm 20% Down column shows PMI = $0
  - [x] Drag any slider — confirm all 4 columns update within 1 second
  - [x] Set Special Assessment > $0 — confirm the one-time note appears below the Total row
  - [x] Confirm no Python traceback visible in app or terminal

- [x] **Task 3: Regression check (AC: 6)**
  - [x] Run `python -m pytest tests/ -v` — all 77 tests must still pass
  - [x] Confirm only `app.py` was modified (no changes to `calculations.py`, `defaults.py`, `url_state.py`, `tests/`)

## Dev Notes

### Current State of `app.py` Main Area (lines 231–244)

The current interim block that this story replaces:

```python
# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")

# Interim 4-column display confirming calculations ran (Stories 2.4–2.6 replace this block).
cols = st.columns(4)
for col, sc in zip(cols, scenarios):
    col.subheader(f"{sc['down_pct']}% Down")
    col.write(f"Upfront: ${sc['upfront_cash']:,.0f}")
    col.write(f"Month 1 total: ${sc['monthly_cost_m1']['total']:,.0f}")
    be = sc["break_even_month"]
    col.write(f"Break-even: {'Month ' + str(be) if be else 'None in 5 yrs'}")

st.info("Monthly breakdown, headline & net worth display coming in Stories 2.4–2.6.")
```

**Replace those 12 lines (232–244) with the implementation below.** Line 231 (`st.title(...)`) stays.

### Complete Replacement Block for `app.py` Main Area

```python
# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Miami Home Buying Decision Tool")

def _fmt(amount: float) -> str:
    return f"${amount:,.0f}"

cols = st.columns(4)
for col, sc in zip(cols, scenarios):
    mc = sc["monthly_cost_m1"]
    recurring_total = mc["p_and_i"] + mc["pmi"] + mc["hoa"] + mc["property_tax"] + mc["insurance"]

    special_note = ""
    if mc["special_assessment"] > 0:
        special_note = (
            f"<div style='font-size:0.8rem;color:#555;margin-top:6px'>"
            f"+ {_fmt(mc['special_assessment'])} one-time assessment"
            f" (month&nbsp;{special_assessment_month})"
            f"</div>"
        )

    card_html = f"""
<div aria-label="{sc['down_pct']}% down payment scenario"
     style="background:#F5F7FA;border:1px solid #D1D9E6;border-radius:8px;padding:16px">
  <div style="font-weight:600;font-size:1.05rem">{sc['down_pct']}% Down</div>
  <div style="font-size:0.82rem;color:#555;margin-bottom:10px">Upfront: {_fmt(sc['upfront_cash'])}</div>
  <div style="font-size:1.4rem;font-weight:700;margin-bottom:10px">{_fmt(recurring_total)}<span style="font-size:0.82rem;font-weight:400">&thinsp;/mo</span></div>
  <table style="width:100%;font-size:0.82rem;border-collapse:collapse">
    <tr><td>P&amp;I</td><td style="text-align:right">{_fmt(mc['p_and_i'])}</td></tr>
    <tr><td>PMI</td><td style="text-align:right">{_fmt(mc['pmi'])}</td></tr>
    <tr><td>HOA</td><td style="text-align:right">{_fmt(mc['hoa'])}</td></tr>
    <tr><td>Property Tax</td><td style="text-align:right">{_fmt(mc['property_tax'])}</td></tr>
    <tr><td>Insurance</td><td style="text-align:right">{_fmt(mc['insurance'])}</td></tr>
    <tr style="border-top:1px solid #D1D9E6;font-weight:600">
      <td>Total</td><td style="text-align:right">{_fmt(recurring_total)}</td>
    </tr>
  </table>
  {special_note}
</div>
"""
    col.markdown(card_html, unsafe_allow_html=True)

st.info("Headline & year-5 net worth display coming in Stories 2.5–2.6.")
```

### Critical Design Decisions

**1. Recurring Total vs. `monthly_cost_m1["total"]`**

`monthly_cost_m1["total"]` (from Story 2.3) includes `special_assessment`, which is a one-time lump sum — not a monthly recurring cost. Displaying it as the "Total" monthly cost would mislead users (e.g., a $30,000 assessment in month 1 would show as the "monthly" payment).

The fix: compute `recurring_total = p_and_i + pmi + hoa + property_tax + insurance` and use that for the Total row. Show `special_assessment` separately as a footnote if non-zero. This matches FR24's fixed list exactly: P&I → PMI → HOA → Property Tax → Insurance → Total.

**2. `special_assessment_month` variable scope**

`special_assessment_month` is a module-level variable in `app.py` defined by the slider (line 90). It is in scope inside the `for col, sc in zip(cols, scenarios)` loop — no need to re-read it from the `sc` dict. Use it directly in the `special_note` f-string.

**3. PMI = $0 for 20% Down**

`mc["pmi"]` comes from `schedule[0]["pmi"]` which is set by `calculate_amortization_schedule()`. At 20% down the LTV is exactly 80%, so the engine returns `pmi = 0.0` already. No conditional logic needed in the display code.

**4. `_fmt` function placement**

Define `_fmt` as a module-level function (inside the main script, before the loop). It is a simple helper — no class, no module extraction. Story 3.7 will implement a full number formatting utility; this `_fmt` is a temporary local helper for 2.4–2.6 only. (Story 3.7 will replace all inline formatting calls.)

**5. "Best" badge**

NOT implemented in this story. Epic 3 (Story 3.5) adds the "Best" column badge with `#2B6CB0` border and `#EBF4FF` background. Story 2.4 uses `#F5F7FA` / `#D1D9E6` for all columns (standard state) — no conditional styling.

**6. Break-even month**

NOT displayed in this story. Story 2.5 adds break-even to the column cards. Do not add it here to avoid conflicting with 2.5's layout.

### `scenarios` Data Contract (from Story 2.3 — DO NOT CHANGE)

Each `sc` in `scenarios` provides for this story:

| Key | Type | Used |
|-----|------|------|
| `down_pct` | `int` | Column header (5, 10, 15, or 20) |
| `upfront_cash` | `float` | Column header subline |
| `monthly_cost_m1` | `dict` | All line items + totals |

`monthly_cost_m1` keys:

| Key | Content |
|-----|---------|
| `p_and_i` | Month-1 principal + interest |
| `pmi` | Month-1 PMI (0.0 for 20% down) |
| `hoa` | HOA monthly (same across all scenarios) |
| `property_tax` | Month-1 property tax (no homestead exemption yet) |
| `insurance` | HO-6 annual ÷ 12 |
| `special_assessment` | Lump-sum if `special_assessment_month == 1`, else 0.0 |
| `total` | Sum of all 6 above — **do NOT use as the displayed Total** |

**DO NOT rename or restructure `monthly_cost_m1`** — Stories 2.5 and 2.6 reference these keys.

### What Stays Completely Unchanged

- Lines 1–230 of `app.py` (imports, sidebar, `slider_values`, computation block) — **byte-for-byte unchanged**
- `calculations.py` — DO NOT TOUCH
- `defaults.py` — DO NOT TOUCH
- `url_state.py` — DO NOT TOUCH
- `tests/` directory — DO NOT TOUCH

### Testing Approach

No new unit tests for this story. Rationale:
- The `monthly_cost_m1` dict is built and tested indirectly through the 55 calculation tests.
- The display loop is Streamlit UI code — not unit-testable.
- Validation gates: manual smoke test + existing 77-test regression pass.

### Windows / Environment Reminders (from Story 2.3)

- Use `python -m pytest tests/ -v` (not `python3`)
- Activate venv: `.venv\Scripts\activate` in PowerShell before running pytest or streamlit
- Use PowerShell tool (not Bash tool) for venv activation

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py              ← MODIFY (replace interim display with monthly cost breakdown)
  calculations.py     ← DO NOT TOUCH
  defaults.py         ← DO NOT TOUCH
  url_state.py        ← DO NOT TOUCH
  tests/              ← DO NOT TOUCH (77 tests must stay green)
```

### Forward Compatibility Note

Story 3.5 (ScenarioColumn component) will replace the HTML cards written here with a full styled component using `#2B6CB0` border on the "best" column and a "Best" badge. Story 2.5 will add break-even month text inside each column. Write the 2.4 card HTML cleanly — no hidden state, no extra divs — so 2.5 and 3.5 can extend it without surgery.

### References

- [Source: epics.md — Story 2.4 ACs, FR24, FR26, FR28, UX-DR10]
- [Source: ux-design-specification.md — ScenarioColumn anatomy, standard/best states, color tokens]
- [Source: story 2-3 — `scenarios` data contract, `monthly_cost_m1` dict structure with `special_assessment` key patch]
- [Source: story 2-3 — Windows Python quirks: `python -m pytest`, `.venv\Scripts\activate`]
- [Source: architecture.md — ARCH-3: only `app.py` is modified; `calculations.py` zero Streamlit imports]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — clean implementation on first attempt. Code matched the story spec exactly; no deviations or debug iterations required.

### Completion Notes List

- Replaced the 12-line interim `app.py` main area block (lines 232–244) with the monthly cost breakdown display.
- Added `_fmt(amount)` helper at module level in the main area section; formats floats as `$X,XXX` (nearest dollar, comma separator, $ prefix).
- `recurring_total` computed as `p_and_i + pmi + hoa + property_tax + insurance` — intentionally excludes `special_assessment` from the Total row (it is a one-time lump sum, not a monthly recurring cost).
- 20% Down PMI = $0 confirmed — `calculate_amortization_schedule` returns `pmi = 0.0` at 20% down with no special-case display logic needed.
- Special assessment footnote renders conditionally when `mc["special_assessment"] > 0`; references `special_assessment_month` slider variable (module-level scope, no lookup needed).
- Each card uses `aria-label` on the outer `<div>` identifying the scenario (UX-DR12, low-effort accessibility).
- `st.info` banner updated: "Headline & year-5 net worth display coming in Stories 2.5–2.6."
- Regression: 77/77 tests pass. Only `app.py` modified.

### File List

- `app.py` — MODIFIED (replaced interim 4-column display with monthly cost breakdown cards)

### Change Log

- 2026-05-24: Story 2-4 implemented — monthly cost breakdown cards with `_fmt` helper, recurring total (excludes lump-sum special assessment), line items in fixed order P&I→PMI→HOA→Tax→Insurance→Total, special assessment one-time footnote, aria-labels. 77/77 tests green.
