# Story 3.7: Number Formatting & Outcome Neutrality Enforcement

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want a single shared formatting utility applied consistently across every displayed output on both pages,
so that every number in the tool follows the UX specification (UX-DR10) and no outcome is ever signaled by color (UX-DR11).

## Acceptance Criteria

1. **Given** a new shared formatting module exists, **When** any dollar amount is rendered anywhere in the tool (`app.py` and `pages/scenarios.py`), **Then** it is produced by a single shared function formatted as nearest dollar with `$` prefix and comma separator (e.g., `$12,400`) — no inline `f"${x:,.0f}"` literals remain in either file for output values. (UX-DR10)
2. **Given** any negative dollar value is displayed, **When** it renders, **Then** it uses parentheses, not a minus sign (e.g., `($4,200)` — never `$-4,200`). This must hold on **both** pages, fixing the current `pages/scenarios.py` behavior where negative exit values render as `$-12,345`. (UX-DR10)
3. **Given** the shared module exposes a percentage formatter, **When** a percentage output is displayed, **Then** it is formatted to 2 decimal places with a `%` suffix (e.g., `6.50%`). (UX-DR10)
4. **Given** the headline's down-payment note, **When** the down payment is a fractional percentage (the slider step is 0.5, so 12.5% is reachable), **Then** the displayed value does not silently round to a misleading whole number (current `{down_pct:.0f}` renders 12.5% as "13% down"). The value must display its true magnitude. (UX-DR10 — see Decision in Dev Notes for the exact format)
5. **Given** the shared module exposes a month-reference formatter, **When** a month is referenced in any output, **Then** it uses the phrasing "month N" with a whole number (e.g., `month 31`). (UX-DR10) *(Note: the main page currently phrases break-even by year, not month — see Dev Notes; this formatter exists for correctness/reuse even if no current month output uses it.)*
6. **Given** the whole tool, **When** any outcome is displayed (renting-wins vs. buying-wins; sell vs. rent-out vs. continue-renting), **Then** no output uses red or green to signal a good/bad outcome; winning and losing states share identical visual treatment except for the literal text. The headline accent stays `#2B6CB0` regardless of winner. (UX-DR11)
7. **Given** the Story 3.5 "Better" column blue/purple coloring, **When** outcome-neutrality is enforced, **Then** that coloring is **preserved** (it is a deliberate, semantically-neutral cross-reference to the chart line colors, not an outcome signal) and explicitly documented as such — it is NOT reverted to a single color and NOT changed to red/green. (UX-DR11, see Dev Notes)
8. **Given** the new formatting module, **When** `python -m pytest tests/ -v` is run, **Then** a new `tests/test_formatting.py` covers `fmt_dollar` (positive, negative, zero, large, sub-dollar rounding), `fmt_pct`, and `fmt_month`, **and** all previously-passing tests (94 as of story 3.5) still pass with zero regressions.

## Tasks / Subtasks

- [x] **Task 1: Create `formatting.py` shared module (AC: 1, 2, 3, 5)**
  - [x] Created `formatting.py` at project root — pure Python, no Streamlit/pandas/plotly imports.
  - [x] `fmt_dollar(v)` — nearest dollar, `$` prefix, comma; negatives `($4,200)` (exact logic of the old `_fmt_dollar`).
  - [x] `fmt_pct(v)` — `f"{v:.2f}%"` → `6.50%`.
  - [x] `fmt_month(n)` — `f"month {int(round(n))}"` → `month 31`.
  - [x] Module docstring marks it the single source of truth for UX-DR10. (Also added `fmt_pct_compact` for Task 4.)

- [x] **Task 2: Wire `app.py` to the shared module (AC: 1, 2)**
  - [x] Added `import formatting`.
  - [x] Deleted local `_fmt_dollar`; the 3 table call sites now use `formatting.fmt_dollar(...)`.
  - [x] `_headline_card` now uses `formatting.fmt_dollar(difference)` (×2) at the call sites inside the f-string.

- [x] **Task 3: Wire `pages/scenarios.py` to the shared module — fixes the negative-value bug (AC: 1, 2)**
  - [x] Added `import formatting`; deleted local `_fmt`; all call sites now `formatting.fmt_dollar(...)`. Negative exit values now render `($12,345)` instead of `$-12,345`.

- [x] **Task 4: Fix the down-payment display rounding (AC: 4)**
  - [x] Headline note now uses `formatting.fmt_pct_compact(down_pct)` (Option A): `20%`, `12.5%`. No more `:.0f` mis-rounding 12.5→13.

- [x] **Task 5: Audit & enforce outcome neutrality (AC: 6, 7)**
  - [x] Grepped both files: only blue/purple/slate/neutral tokens; zero red/green outcome colors.
  - [x] Added comment above `_headline_card` noting accent `#2B6CB0` is winner-independent (UX-DR11).
  - [x] Added comment at `_BETTER_COLORS` documenting blue/purple are neutral chart-line cross-references, not outcome signals.
  - [x] Confirmed `pages/scenarios.py` has no "Best" badge — AC vacuously satisfied; no badge added (out of scope).

- [x] **Task 6: Add `tests/test_formatting.py` (AC: 8)**
  - [x] `fmt_dollar`: positive, negative `($4,200)`, zero, large, sub-dollar (asserts actual banker's rounding: `0.5→$0`, `1.5→$2`), tiny-negative `-0.4→($0)`.
  - [x] `fmt_pct`: `6.5→6.50%`, `0→0.00%`, `12.345→12.35%`. Plus `fmt_pct_compact`: `20.0→20%`, `12.5→12.5%`.
  - [x] `fmt_month`: `31→month 31`, `1→month 1`.

- [x] **Task 7: Regression + smoke (AC: 8)**
  - [x] `python -m pytest tests/ -q` — **109 passed** (94 prior + 15 new), zero regressions.
  - [x] AST parse clean on `app.py`, `pages/scenarios.py`, `formatting.py` — printed `AST OK`.
  - [x] Manual smoke (user, 2026-06-06): verified headline + annual table render dollars unchanged; Page 2 negatives show `($X,XXX)`; down payment 12.5% → headline reads "At 12.5% down".

## Dev Notes

### What this story is really about

There are currently **two** independent dollar formatters that have **drifted**:

| Location | Function | Negative handling | Bug? |
|---|---|---|---|
| `app.py:25` | `_fmt_dollar(v)` | `($4,200)` parentheses ✅ | correct |
| `pages/scenarios.py:183` | `_fmt(amount)` | `$-4,200` minus sign ❌ | **violates UX-DR10** |

Story 3.7 collapses both into one shared `formatting.py` so the rule is enforced in exactly one place. This is the "single formatting utility" the epic calls for. The Page 2 negative-value rendering is a real latent bug (`exit_sell` goes negative at 0% appreciation when loan balance + realtor fees exceed the flat home price — already logged in `deferred-work.md` from the 2-4 review).

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  formatting.py          ← NEW (pure Python; no streamlit/pandas/plotly)
  app.py                 ← MODIFY (import formatting; delete _fmt_dollar; fix down_pct display; comments)
  pages/scenarios.py     ← MODIFY (import formatting; delete _fmt; fixes negative bug)
  tests/test_formatting.py ← NEW
  calculations.py        ← DO NOT TOUCH
  defaults.py            ← DO NOT TOUCH
  url_state.py           ← DO NOT TOUCH
  .streamlit/            ← DO NOT TOUCH
  requirements.txt       ← DO NOT TOUCH (no new deps; pure stdlib)
```

[Source: _bmad-output/planning-artifacts/architecture.md#Selected-structure — flat modules, pure-Python engine independently unit-testable]

### Architecture fit

`architecture.md` establishes that pure-Python, no-Streamlit modules (like `calculations.py`) are isolated specifically so they are unit-testable without the UI. `formatting.py` follows that exact pattern — it must not import `streamlit`, so `tests/test_formatting.py` can import and assert on it directly the way `tests/test_calculations.py` does. [Source: architecture.md lines 74–88]

### Proposed `formatting.py`

```python
"""Single source of truth for UX-DR10 number formatting.

Pure Python (no Streamlit) so it is unit-testable in isolation, matching the
calculations.py convention. Every displayed number in app.py and
pages/scenarios.py must route through these helpers.
"""


def fmt_dollar(v: float) -> str:
    """Nearest dollar, $ prefix, comma separator; negatives in parentheses.

    fmt_dollar(12400) -> '$12,400'   fmt_dollar(-4200) -> '($4,200)'
    """
    if v < 0:
        return f"(${abs(v):,.0f})"
    return f"${v:,.0f}"


def fmt_pct(v: float) -> str:
    """Two decimal places + % suffix.  fmt_pct(6.5) -> '6.50%'."""
    return f"{v:.2f}%"


def fmt_month(n: int) -> str:
    """Whole-number 'month N'.  fmt_month(31) -> 'month 31'."""
    return f"month {int(round(n))}"
```

### Decision needed — down-payment display format (AC: 4)

The headline currently renders `At {down_pct:.0f}% down`. The down-payment slider on the main page uses `step=0.5`, so **12.5% is a real reachable value** and `:.0f` renders it as the misleading "13% down".

Three options — **recommended is Option A**:

- **Option A (recommended): compact percent that trims a trailing `.0`.** `20.0 → "20%"`, `12.5 → "12.5%"`. Reads naturally for a down-payment label and never mis-rounds. Add a helper:
  ```python
  def fmt_pct_compact(v: float) -> str:
      """Percent with up to 1 decimal, trailing .0 trimmed. 20.0->'20%', 12.5->'12.5%'."""
      s = f"{v:.1f}".rstrip("0").rstrip(".")
      return f"{s}%"
  ```
- **Option B: strict UX-DR10 two decimals.** `12.5 → "12.50% down"`, `20.0 → "20.00% down"`. Spec-literal but reads awkwardly for a down-payment label.
- **Option C: keep whole number but round-half-up honestly / change slider step to 1.0.** Changes input behavior — out of scope.

The dev should implement **Option A** unless the user directs otherwise. This is the single open product decision in the story; flagged in the Questions section below.

### Outcome neutrality — what to preserve vs. enforce (AC: 6, 7)

UX-DR11 / the UX spec "Outcome Neutrality Rules": no red/green, winning and losing states identical except text, headline accent always `#2B6CB0`. [Source: ux-design-specification.md#Outcome-Neutrality-Rules lines 410–415, 484]

Current state already largely complies:
- Headline accent is `#2B6CB0` and winner only swaps the word "Renting"/"Buying" — compliant, just add an affirming comment.
- The Story 3.5 "Better" column uses blue `#2B6CB0` (Renting) and purple `#6B46C1` (Buying). **This is a deliberate, documented deviation from strict same-color neutrality** (see story 3.5 Color Rationale): both colors are semantically neutral (no red/green), chosen to cross-reference the chart line colors. **Do NOT revert this.** Story 3.7's job is to *document* it as intentional, not undo it. Per the 3.5 review (2026-06-06) the Buy chart line was recolored to `#6B46C1` so the purple now matches the chart too.

⚠️ Common LLM mistake to avoid: "enforcing neutrality" by collapsing the blue/purple to one color or by adding green/red. Neither is wanted.

### Month references (AC: 5)

The main page expresses break-even by **year** (`break_even_text = "Break-even at year {n}"`), which is correct for the annual-horizon chart — leave it. `fmt_month` is added for spec-completeness and reuse (Page 2 computes `break_even_month` but does not currently display it). No current output needs converting; do not invent a month display just to use the helper. [Source: app.py:273–275; pages/scenarios.py:158–165]

### Out of scope (do NOT do)

- Slider widget `format=` strings (`"$%.0f"`, `"%.3f%%"`, `"%.2f%%"`, `"%.1f%%"`): these are Streamlit **input-widget** display formats whose precision intentionally matches each slider's `step` (mortgage step 0.125 needs 3 decimals). They are not "displayed outputs" and are out of scope.
- Adding a "Best" badge to Page 2 (that is Story 3.6 / Page-2 polish).
- Touching `calculations.py`, `defaults.py`, `url_state.py`.

### Testing standards

- Tests live in `tests/`, pytest, run as `python -m pytest tests/ -v` (Windows: use `python`, not `python3`). [Source: prior story Dev Notes + tests/ layout]
- `tests/test_formatting.py` imports `formatting` directly (no Streamlit needed) — mirror the structure of `tests/test_calculations.py`.
- Assert the **actual** `:,.0f` rounding behavior for half-dollar inputs (Python uses banker's rounding: `round` is not invoked here — `f"{0.5:,.0f}"` → `'0'`, `f"{1.5:,.0f}"` → `'2'`). Write the test to match real output rather than assuming half-up.

### Previous Story Intelligence (3.5, done 2026-06-06)

- Story 3.5 added `hovertemplate="%{y:$,.0f}"` and recolored the Buy line to `#6B46C1`; its code review applied 2 patches and deferred 3 items (one of which — the Page 2 `$-12,345` negative bug — **this story fixes via Task 3**). [Source: 3-5-chart-and-table-polish.md Review Findings]
- Stories 3.2–3.5 were committed together in `2088e83`. The working tree is now clean before 3.7 begins.
- Windows env: `python` not `python3`; OneDrive-synced folder (watchdog hot-reload can be noisy during `streamlit run`).

### Git Intelligence

Recent commits show each Epic 3 story modifies `app.py` plus its story/sprint files. 3.7 is the first Epic 3 story to **add a new module** (`formatting.py`) and **add a test file** — commit them together with the `app.py`/`scenarios.py` edits.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.7 — AC list, UX-DR10/DR11/FR37 mapping]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Number-Formatting-Patterns (lines 400–415), #Outcome-Neutrality-Rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#Selected-structure (lines 74–88)]
- [Source: app.py:25–28 (_fmt_dollar), :9–22 (_headline_card), :355–358 (table)]
- [Source: pages/scenarios.py:183–184 (_fmt), :145–156 (exit values that can be negative)]
- [Source: _bmad-output/implementation-artifacts/deferred-work.md — "_fmt formats negative numbers as $-X" (2-4 review)]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8

### Debug Log References

None — red-green-refactor clean. Tests written first (confirmed `ModuleNotFoundError` red), then `formatting.py` created (green, 15/15), then call sites rewired.

### Completion Notes List

- Created `formatting.py` (pure Python, no Streamlit) as the single source of truth for UX-DR10: `fmt_dollar`, `fmt_pct`, `fmt_pct_compact`, `fmt_month`.
- Consolidated the two drifted formatters: deleted `app.py:_fmt_dollar` and `pages/scenarios.py:_fmt`; all output sites now call `formatting.fmt_dollar`.
- **Bug fixed:** Page 2 negative exit values rendered `$-12,345`; now `($12,345)` (closes the 2-4-review deferred item).
- **Down-payment fix (Option A, user-approved):** headline used `{down_pct:.0f}` which mis-rounded 12.5%→"13%"; now `fmt_pct_compact` → "12.5%". Whole values stay clean ("20%").
- Outcome neutrality: verified no red/green; added affirming comments at the headline accent and `_BETTER_COLORS` so the 3.5 blue/purple cross-reference is not "neutralized" by a future edit. No "Best" badge exists on Page 2, so that AC is vacuously satisfied.
- Verification: 109/109 tests pass (94 prior + 15 new); AST clean on all three files. Manual browser smoke left for user.

### File List

- formatting.py (new)
- tests/test_formatting.py (new)
- app.py (modified)
- pages/scenarios.py (modified)

## Change Log

- 2026-06-06: Implemented Story 3.7 — new shared `formatting.py` (fmt_dollar/fmt_pct/fmt_pct_compact/fmt_month) replacing the two drifted dollar formatters in app.py and pages/scenarios.py. Fixed Page 2 `$-12,345` negative rendering and headline `{down_pct:.0f}` mis-rounding (Option A compact percent). Outcome-neutrality comments added; no red/green. Added tests/test_formatting.py (15 tests). 109/109 pass, AST clean. (claude-opus-4-8)

## Review Findings (2026-06-06)

All 8 ACs pass; 109/109 tests pass; no do-not-touch source files modified. Outcome neutrality verified (zero red/green). Consolidation is functionally complete.

- [x] [Review][Decision] RESOLVED → keep as-is. `fmt_dollar` renders `($0)` for tiny negatives [formatting.py:16]. Decision: keep current behavior (harmless, extremely rare, already test-locked). No code change.
- [x] [Review][Patch] APPLIED — `pages/scenarios.py:190,192` now route the down-payment percent (aria-label + visible "Down" label) through `formatting.fmt_pct_compact(sc['down_pct'])`, completing the consolidation. Output unchanged (5%/10%/15%/20%); 109/109 tests pass, AST clean.
- [x] [Review][Defer] `fmt_pct_compact` emits `-0%` for a small *negative* percentage [formatting.py:34] — deferred, unreachable: the only call site is `down_pct`, bounded to [3.0, 30.0]. Only matters if the helper is later reused for signed percentages.

## Questions / Clarifications for User

1. **Down-payment display format (AC 4):** Recommend **Option A** — compact percent trimming trailing `.0` (`20%`, `12.5%`). Confirm, or choose strict 2-decimal (`12.50%`) per literal UX-DR10. *(Story implements Option A by default.)*
