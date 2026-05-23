# Deferred Work Log

## Deferred from: code review of 1-1-project-scaffold-module-structure (2026-05-22)

- **No python_requires or minimum Python version constraint documented.** No setup.cfg, pyproject.toml, or .python-version file exists. Compiled wheels (numpy, pyarrow, pillow) are Python-minor-version specific — a developer on a different minor version will get cryptic errors.
- **pyvenv.cfg points to Anaconda base interpreter.** If the venv is ever recreated, story instructions must specify the exact interpreter path (C:\Users\criss\anaconda3\python.exe) to preserve Python 3.12.7 and avoid wheel compatibility issues.
- **watchdog 6.0.0 + OneDrive sync interaction.** Project lives in Documents\ which OneDrive syncs by default. watchdog's ReadDirectoryChangesW may fire spuriously on OneDrive .tmp files, causing unexpected Streamlit hot-reloads or PermissionErrors during active development.
- **URL state budget definition unresolved.** url_state.py docstring states a 2,000-character cap on "total URL length." Story 2.1 must clarify whether this is measured from the full URL (including Streamlit Cloud domain ~40-60 chars) or the query string only — the distinction affects whether the validation logic is correct in production.
