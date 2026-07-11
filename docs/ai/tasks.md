# AI Task Reference

Complete reference for all AI tasks available via `make task-run NAME=<task>` and the `ai_customizer.py` CLI.

## Quick Start

```bash
# List all available tasks
make task-list

# Run a task against the whole project
make task-run NAME=analyze_project

# Run a task against a specific site
make task-run NAME=comprehensive_analysis SITE=ctc-research

# Run with verbose output
make task-run NAME=uniform_docs VERBOSE=1
```

## Task Index

### Analysis Tasks

| Task | Description | Output |
|------|-------------|--------|
| `analyze_project` | Full codebase analysis: N+1 queries, duplications, TODOs | Report in `ai/reports/` |
| `comprehensive_analysis` | Phased analysis: package check → structure map → N+1 → actions | Phased report |
| `audit_code_quality` | Ruff-style analysis: complexity, naming, unused imports | Quality report |

### Documentation Tasks

| Task | Description | Output |
|------|-------------|--------|
| `uniform_docs` | Standardise all `.md` files to consistent headings/format | In-place edits |
| `generate_docstrings` | Add missing Python docstrings to functions/classes | In-place edits |
| `update_readme` | Regenerate README from project structure and settings | `README.md` |

### Code Transformation Tasks

| Task | Description | Output |
|------|-------------|--------|
| `fix_n_plus_one` | Add `select_related`/`prefetch_related` to ORM queries | In-place edits |
| `remove_duplications` | Find and consolidate duplicate code blocks | In-place edits |
| `refactor_context` | Extract repeated view context logic into mixins | In-place edits |
| `merge_styles` | Consolidate CSS/SCSS rules across site assets | In-place edits |
| `replace_pattern` | Replace a pattern across files (config-driven) | In-place edits |
| `refactor_design_pattern` | Apply a design pattern (Factory, Repository, etc.) | In-place edits |

### Monorepo Tasks

| Task | Description | Output |
|------|-------------|--------|
| `check_imports` | Validate all import paths after library migrations | Import report |
| `validate_settings` | Check YAML settings files for missing keys | Settings report |
| `map_structure` | Generate a fresh directory structure map | `docs/architecture/project_structure.md` |

## Task File Format

Each task is a `.md` file in `docs/ai/tasks/`. The first line is the short description shown in `make task-list`.

```markdown
Analyze all Django views for N+1 query patterns.

## Instructions

1. Search all `views.py` files in the monorepo
2. For each QuerySet call, check if related objects are accessed in a loop
3. Flag any `for obj in queryset: obj.related.all()` patterns
4. Output: file path, line number, suggested fix

## Output Format

| File | Line | Pattern | Fix |
|------|------|---------|-----|
```

## Project Context Files

The AI tasks use these files as context via `@codebase` and `@folder docs`:

```
core/
├── configs/settings/     ← YAML settings for all sites
├── libs/django-fusion/    ← Language & file utilities
├── libs/ceptor-ai/    ← Email & notification tasks
├── libs/django-fusion/     ← Search indexing
└── tasks/                ← Shared Celery tasks

docs/
├── architecture/         ← System design notes
├── monorepo/PHASES.md    ← Phase tracking
└── ai/tasks/             ← Task prompt files
```

## Monorepo Phase Tracking Integration

AI tasks reference the phase system in `docs/monorepo/PHASES.md`. When running `comprehensive_analysis`, the output maps findings to the relevant phase:

```
Finding: utilities.py still imported in ctc_research/views.py
→ Phase 3 (Utilities Migration) — Task 3.4: Update imports across monorepo
→ Fix: from django_fusion.site.utils import get_file_extension
```

## Adding a New Task

1. Create `docs/ai/tasks/<task_name>.md` with the prompt
2. Run `make task-list` to verify it appears
3. Test: `make task-run NAME=<task_name> --dry-run`

## Model Recommendations

| Task Type | Recommended Model | Reason |
|-----------|------------------|--------|
| Analysis (large codebase) | `gemma3:4b` | Best context handling |
| Quick transformations | `qwen3:4b` | Faster, good at code edits |
| Docstring generation | `llama3.2:1b` | Simple, very fast |
| Full audit | `gemma3:4b` with `num_ctx: 8192` | Needs wide context |

See [config.md](config.md) for model configuration details.
