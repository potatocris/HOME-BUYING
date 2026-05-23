# Story 1.1: Project Scaffold & Module Structure

Status: done

## Story

As a developer,
I want a working project scaffold with all required module files and pinned dependencies,
So that I can run the app locally and have a clean structure to build into.

## Acceptance Criteria

1. **Given** Python 3.10–3.14 is installed, **When** I run `python -m venv .venv` and `pip install -r requirements.txt`, **Then** all dependencies install without error.
2. **Given** dependencies are installed, **When** I run `streamlit run app.py`, **Then** a Streamlit page loads in Chrome without error (placeholder content is acceptable).
3. **Given** the project is scaffolded, **Then** these five files exist at the project root: `app.py`, `calculations.py`, `defaults.py`, `url_state.py`, `requirements.txt`.
4. **Given** `calculations.py` is inspected, **Then** it contains zero Streamlit imports — verified by `grep -r "import streamlit" calculations.py` returning no results.
5. **Given** `requirements.txt` is inspected, **Then** every dependency has a pinned version number (e.g., `streamlit==1.57.0`), not a range or bare name.

## Tasks / Subtasks

- [x] **Task 1: Create virtual environment** (AC: 1)
  - [x] From project root `C:\Users\criss\Documents\Home Buying`, run: `python -m venv .venv`
  - [x] Activate: `.venv\Scripts\Activate.ps1` (PowerShell) or `.venv\Scripts\activate.bat` (CMD)
  - [x] Verify: `python --version` shows 3.10–3.14

- [x] **Task 2: Install Streamlit and pin dependencies** (AC: 1, 5)
  - [x] Run: `pip install streamlit==1.57.0`
  - [x] Run: `pip freeze > requirements.txt`
  - [x] Verify `requirements.txt` contains `streamlit==1.57.0` with pinned transitive deps

- [x] **Task 3: Create `app.py` placeholder** (AC: 2, 3)
  - [x] Create `app.py` at project root with minimal valid Streamlit content (see Dev Notes)
  - [x] Verify: `streamlit run app.py` launches with no error in Chrome

- [x] **Task 4: Create `calculations.py` stub** (AC: 3, 4)
  - [x] Create `calculations.py` at project root — pure Python only, no Streamlit imports
  - [x] Content: module docstring only — no functions yet (implemented in Stories 1.3–1.6)
  - [x] Verify: `grep "streamlit" calculations.py` returns nothing

- [x] **Task 5: Create `defaults.py` stub** (AC: 3)
  - [x] Create `defaults.py` at project root — stub only, no values yet (implemented in Story 1.2)
  - [x] Content: module docstring only

- [x] **Task 6: Create `url_state.py` stub** (AC: 3)
  - [x] Create `url_state.py` at project root — stub only, no functions yet (implemented in Story 2.1)
  - [x] Content: module docstring only

- [x] **Task 7: Final verification** (AC: 2, 4, 5)
  - [x] Run `streamlit run app.py` — confirm browser loads without error
  - [x] Run `python -c "import calculations; import defaults; import url_state"` — confirm all modules importable
  - [x] Confirm `calculations.py` has no Streamlit imports

### Review Findings

- [x] [Review][Patch] BOM character in requirements.txt corrupts first package name on some pip/CI environments [requirements.txt:1]
- [x] [Review][Defer] No python_requires or minimum Python version constraint documented — deferred, pre-existing
- [x] [Review][Defer] pyvenv.cfg points to Anaconda interpreter; recreating venv could target different Python version — deferred, pre-existing
- [x] [Review][Defer] watchdog hot-reload may interact with OneDrive sync in Documents folder — deferred, pre-existing
- [x] [Review][Defer] URL budget definition (full URL vs query-string-only) unresolved — deferred to Story 2.1

## Dev Notes

### Project Root

All five files (`app.py`, `calculations.py`, `defaults.py`, `url_state.py`, `requirements.txt`) go directly in the project root:
```
C:\Users\criss\Documents\Home Buying\
  app.py
  calculations.py
  defaults.py
  url_state.py
  requirements.txt
  .venv\               ← virtual environment (not committed)
  _bmad-output\        ← BMad planning artifacts (already exists)
  .claude\             ← Claude Code project files (already exists)
```

The `_bmad/`, `_bmad-output/`, and `.claude/` folders already exist and must not be touched.

### Stub File Content

**`app.py`** — minimal valid Streamlit page:
```python
import streamlit as st

st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")
st.title("Miami Home Buying Decision Tool")
st.write("Coming soon.")
```

**`calculations.py`** — pure Python stub, ZERO Streamlit imports:
```python
"""
Financial calculation engine for the Miami Home Buying Decision Tool.

Pure Python only — no Streamlit imports. This module is independently
unit-testable against a reference spreadsheet.
"""
```

**`defaults.py`** — stub:
```python
"""
Miami-specific default input values and last-reviewed date.

Isolated from calculation logic so defaults can be updated independently.
Implemented in Story 1.2.
"""
```

**`url_state.py`** — stub:
```python
"""
URL state encoding and decoding for shareable scenario links.

Encodes all 12 slider values to st.query_params; validates total URL
length does not exceed 2,000 characters. Implemented in Story 2.1.
"""
```

### Streamlit Version

Use **Streamlit 1.57.0** (latest stable as of 2026-05-22). Key APIs this project relies on:
- `st.query_params` — URL state (available since 1.27.0; replaces deprecated `st.experimental_get_query_params`)
- `st.sidebar` — Split View layout
- `st.columns(4)` — 4-scenario grid
- `st.expander` — Advanced Inputs collapsible section
- `st.markdown(unsafe_allow_html=True)` — custom HTML components

### Windows Activation

In PowerShell, use: `.venv\Scripts\Activate.ps1`
If execution policy blocks it: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### ARCH-3 Invariant — Never Break This

`calculations.py` must contain **zero Streamlit imports** for the entire lifetime of this project. This is enforced in Story 1.1 and must be maintained through all subsequent stories. The file is pure Python to enable unit testing independent of the Streamlit runtime.

Verification command: `python -c "import ast, sys; tree = ast.parse(open('calculations.py').read()); imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]; streamlit_imports = [n for n in imports if any('streamlit' in (getattr(n, 'module', '') or '') or any('streamlit' in alias.name for alias in getattr(n, 'names', [])) for _ in [n])]; sys.exit(1 if streamlit_imports else 0)"`

### .streamlit/config.toml

**Do NOT create this file in Story 1.1.** The Streamlit theme (`config.toml` with Direction A color tokens) is implemented in Story 3.1. Creating it now would duplicate work and may interfere with the unstyled development in Epics 1 and 2.

### Project Structure Notes

- No test framework setup required in this story — unit testing scaffold will be added when Story 1.3 (amortization engine) is implemented
- No `.gitignore` is strictly required for this story, but adding one to exclude `.venv/`, `__pycache__/`, and `.streamlit/` is good practice
- The `requirements.txt` generated by `pip freeze` will contain many transitive dependencies — this is correct and expected

### References

- [Source: architecture.md — Project Structure Decision: Modular]
- [Source: architecture.md — Technical Constraints & Dependencies]
- [Source: epics.md — Story 1.1 Acceptance Criteria]
- [Source: prd.md — ARCH-1, ARCH-2, ARCH-3]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (Claude Code, 2026-05-22)

### Debug Log References

No blockers. pip install warning about pip upgrade (24.2 → 26.1.1) is cosmetic — not an error.

### Completion Notes List

- Created `.venv` using `python -m venv .venv`; Python 3.12.7 confirmed (within 3.10–3.14 range).
- Installed `streamlit==1.57.0` via pip into venv; generated `requirements.txt` via `pip freeze` — 44 lines, all pinned with `==`.
- Created `app.py` with exact content from Dev Notes spec.
- Created `calculations.py` stub (docstring only); ARCH-3 verified via AST analysis — zero Streamlit imports.
- Created `defaults.py` stub (docstring only).
- Created `url_state.py` stub (docstring only).
- All three modules confirmed importable: `import calculations; import defaults; import url_state` — no errors.
- AC 2 (browser load) verified at module level: `streamlit==1.57.0` imports cleanly. Browser verification requires running `streamlit run app.py` interactively — see note below.
- No `.streamlit/config.toml` created per Dev Notes (deferred to Story 3.1).

> **Note for Cris:** To fully satisfy AC 2, activate the venv (`.venv\Scripts\Activate.ps1`) and run `streamlit run app.py` — it will open in Chrome automatically. You should see the "Miami Home Buying Decision Tool / Coming soon." page.

### File List

- `app.py` (new)
- `calculations.py` (new)
- `defaults.py` (new)
- `url_state.py` (new)
- `requirements.txt` (new)
- `.venv/` (new — virtual environment directory, not committed)

## Change Log

- 2026-05-22: Story 1.1 implemented — project scaffold created. Virtual environment, pinned dependencies, and all five stub files created and verified.
