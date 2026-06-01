# Story 3.4: HeadlineCard Component

Status: done

## Story

As a user,
I want the headline to display with prominent styling that draws my eye to the key financial verdict,
so that I immediately understand which path wins and by how much without scanning the rest of the page.

## Acceptance Criteria

1. **Given** calculations have run, **When** the HeadlineCard renders, **Then** the dollar amount displays in large text (~2.5rem, weight 700, color `#2B6CB0`) — **already implemented**, must remain. (UX-DR3)
2. **Given** calculations have run, **When** the HeadlineCard renders, **Then** the result label reads "Renting is better by $X over Y years" or "Buying is better by $X over Y years" as appropriate — **already implemented**, must remain. (FR23)
3. **Given** calculations have run, **When** the HeadlineCard renders, **Then** the note line displays the current down payment percentage and break-even info, e.g. "At 20% down · Break-even at year 5" or "At 20% down · No break-even within 10 years". (UX-DR3)
4. **Given** renting wins or buying wins, **When** the HeadlineCard renders, **Then** both states use identical CSS — no color or style difference — **already implemented**, must remain. (UX-DR11, FR36)
5. **Given** the HeadlineCard renders, **When** inspected, **Then** it has `aria-label="Financial comparison headline"` — **already implemented**, must remain. (UX-DR12)
6. **Given** any slider changes, **When** the page reruns, **Then** the HeadlineCard reflects the updated values — **already implemented** via Streamlit reactive reruns, must remain.
7. **Given** the change is applied, **When** `python -m pytest tests/ -v` runs, **Then** all 94 existing tests still pass with 0 regressions.

## Tasks / Subtasks

- [x] **Task 1: Add `down_pct` parameter to `_headline_card()` and update note line (AC: 3)**
  - [x] Update function signature: add `down_pct: float` as 4th parameter (before `break_even_text`)
  - [x] Update the note `<p>` at the bottom of the HTML: replace bare `{break_even_text}` with `At {down_pct:.0f}% down · {break_even_text}`
  - [x] Update the call site at line 281 to pass `down_pct` as the new 4th argument

- [x] **Task 2: Confirm zero regressions (AC: 7)**
  - [x] Run `python -m pytest tests/ -v` — all 94 tests pass, 0 failures
  - [x] AST parse: `python -c "import ast; ast.parse(open('app.py').read()); print('OK')"`

- [x] **Task 3: Manual smoke test (AC: 3)**
  - [x] Playwright/Chromium: note line shows "At 20% down · No break-even within 10 years" at defaults
  - [x] URL param probes (dp=5, dp=30) confirmed note line updates with correct down_pct

## Dev Notes

### What's Already Done — Do Not Change

The `_headline_card()` function at lines 9–22 already satisfies ACs 1, 2, 4, 5, 6:

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

### The Exact Changes (Task 1)

**Function signature** — add `down_pct: float` as the 4th parameter:

```python
# BEFORE:
def _headline_card(winner: str, difference: float, horizon_years: int, break_even_text: str) -> str:

# AFTER:
def _headline_card(winner: str, difference: float, horizon_years: int, down_pct: float, break_even_text: str) -> str:
```

**Note line** — combine down_pct and break_even_text:

```python
# BEFORE:
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0; opacity:0.75;">{break_even_text}</p>

# AFTER:
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0; opacity:0.75;">At {down_pct:.0f}% down · {break_even_text}</p>
```

**Call site at line 281** — add `down_pct` as 4th argument:

```python
# BEFORE:
    st.markdown(_headline_card(winner, difference, horizon_years, break_even_text), unsafe_allow_html=True)

# AFTER:
    st.markdown(_headline_card(winner, difference, horizon_years, down_pct, break_even_text), unsafe_allow_html=True)
```

### Why `down_pct:.0f` (no decimal)

The note line is small secondary text (0.875rem, opacity 0.75). "At 20% down" is more readable than "At 20.0% down" in this context. Use `:.0f` (no decimal places).

### Context: Single-Scenario Main Page

The main page uses ONE `down_pct` slider. The original UX spec said "Best buying scenario: 20% down" — that was written when there were 4 scenarios. After the sprint-change pivot, the main page is single-scenario, so "At X% down" accurately describes the current scenario without implying comparison.

### `down_pct` Is Already In Scope

`down_pct` is the sidebar slider variable, available throughout the main area rendering block. The call site at line 281 is inside the `else:` branch of the `if _calc_error` block — `down_pct` is always in scope there (set by the sidebar slider before the calculation block).

### File Locations

```
C:\Users\criss\Documents\Home Buying\
  app.py             ← MODIFY (function signature + HTML note line + call site)
  defaults.py        ← DO NOT TOUCH
  calculations.py    ← DO NOT TOUCH
  url_state.py       ← DO NOT TOUCH
  pages/             ← DO NOT TOUCH
  tests/             ← DO NOT TOUCH
  .streamlit/        ← DO NOT TOUCH
```

### Windows / Environment Reminders

- Use `python` (NOT `python3`) — Anaconda on Windows
- Run pytest as: `python -m pytest tests/ -v`

### No New Tests Required

The change is 3 lines modifying a string-rendering helper. No business logic. The 94-test regression suite is the correctness gate.

### References

- HeadlineCard spec: [Source: `_bmad-output/planning-artifacts/ux-design-specification.md` — Component Strategy / HeadlineCard]
- FR23 (verdict label), FR36 (outcome neutrality): [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.4]
- UX-DR3 (large dollar), UX-DR11 (neutral colors), UX-DR12 (aria-label): [Source: `_bmad-output/planning-artifacts/ux-design-specification.md`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
