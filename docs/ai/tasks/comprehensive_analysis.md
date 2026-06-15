# Task: Comprehensive Django Analysis with Phased Actions

You are an expert Django architect and automation engineer. Perform a **phased** analysis of the project, following the steps below. At the end, output a report saved to `ai/reports/comprehensive_analysis_YYYYMMDD_HHMMSS.md` and **within the same file** list the recommended phases for action.

## Phase 0: Environment & Package Check
- Determine the project root directory.
- List installed packages from `requirements.txt` / `pyproject.toml` / `Pipfile`.
- Identify missing common packages: `django-extensions`, `django-debug-toolbar`, `pytest-django`, `celery`, `django-rest-framework` (if used).
- If a package is missing but would help with the tasks below, note it in the report with a suggested install command.

## Phase 1: File & Structure Mapping
- Scan the project root and all subdirectories.
- Identify all Django apps (directories containing `models.py`, `views.py`, `urls.py`).
- Map file types:
  - `*.py` – Django logic
  - `*.html` – templates
  - `*.js` – frontend (in `assets/js/` or `static/`)
  - `*.css` / `*.scss`
- Note any unusual or misplaced files.

## Phase 2: Code Quality & Pattern Analysis
- Detect design patterns used (MVC, Repository, Factory, etc.).
- Locate code duplications (same function/class across multiple files).
- Find N+1 query candidates (loops with ORM access without `select_related`).
- Identify missing type hints, docstrings, and overly complex functions.

## Phase 3: Django‑Specific Issue Detection
- Check `settings.py` for:
  - `DEBUG = True` in production‑like environment
  - `SECRET_KEY` hardcoded
  - `ALLOWED_HOSTS` misconfiguration
  - Missing `STATIC_ROOT`, `MEDIA_ROOT`
- Check `urls.py` for missing `app_name` or improper include.
- Scan for raw SQL usage (`raw()`, `execute()`).
- Find views without login required where needed.

## Phase 4: Generate Report (Markdown)
Save a markdown report in `ai/reports/comprehensive_analysis_<timestamp>.md` with the following sections:

```markdown
# Comprehensive Analysis Report for <project_name>

## Phase 0: Packages & Environment
- Installed packages (list)
- Missing suggested packages (with install commands)

## Phase 1: Structure
- Root directory tree (abbreviated)
- Apps discovered

## Phase 2: Code Quality
- Duplications (list with file:line)
- N+1 candidates
- Missing type hints / docstrings

## Phase 3: Django Issues
- Settings problems
- Raw SQL usage
- Auth/security issues

## Phase 4: Recommended Phases (Actions)
Each action must be a separate phase with a clear command or task name.

Example:
### Phase A: Fix N+1 Queries
Run `make task-run NAME=fix_n_plus_one` after reviewing the report.

### Phase B: Remove Duplications
Run `make task-run NAME=remove_duplications` with `--priority --with-docs`.

### Phase C: Add Missing Packages
Execute: `pip install django-extensions django-debug-toolbar`

### Phase D: Create Base Code (if missing)
- Add a `utils.py` with helper functions.
- Create a base template `base.html` if not present.
- Add a custom context processor for shared variables.

### Phase 5: (Optional) Generate Base Code
- If the analysis reveals missing foundational code (e.g., no utils.py, no base.html, no custom error pages), propose the content of those files in the report. - Do not write them automatically – ask the user to approve.

### Output Instructions
- After completing the analysis, save the report to ai/reports/ (create directory if needed).

- Print a summary: “Report saved to …”.

- Then ask: “Which recommended phase would you like to execute next? (Enter the phase letter, e.g., A)”

- The user can then run the corresponding make task-run command or manual steps.