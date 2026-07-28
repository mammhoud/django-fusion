# Per-App Documentation Standards

Standards for `AGENTS.md`, `PROMPTS.md`, and `README.md` files across all apps and shared directories in the Structa Cloud monorepo.

## File Types

### `README.md` — Human-readable overview

| Section | Contents |
|---------|----------|
| **Purpose** | What this app/directory does and why it exists |
| **Tech Stack** | Key dependencies (Django, Wagtail, HTMX, etc.) |
| **Entry Points** | URL routes, management commands, API endpoints |
| **Key Files** | Most important source files with one-line descriptions |
| **Runbook** | Common dev commands: check, test, migrate, build |

### `AGENTS.md` — AI agent context

| Section | Contents |
|---------|----------|
| **Canonical Paths** | Import paths and template resolution order |
| **Template Resolution Order** | Django TEMPLATES_DIRS priority chain |
| **Component Conventions** | How `{% comp %}` and fragments are used here |
| **Key Imports** | Most-used imports with canonical paths |
| **Site-Specific Deviations** | Differences from shared `AGENTS.md` |

### `PROMPTS.md` — Prompt reference for AI-driven development

| Section | Contents |
|---------|----------|
| **Prompt Text** | Exact prompt to give the AI |
| **Expected Input** | What context/files the AI needs |
| **Expected Output** | What the AI should produce |
| **Doc References** | Links to relevant docs |

## Coverage Inventory

| Directory | `README.md` | `AGENTS.md` | `PROMPTS.md` |
|-----------|-------------|-------------|--------------|
| `applications/ctc-research/` | ✅ present | ✅ present | ✅ present |
| `applications/lms-demo/` | ✅ present | ✅ present | ✅ present |
| `applications/VResume/` | ✅ present | ✅ present | ✅ present |
| `applications/crm/` | ✅ present | ❌ missing | ❌ missing |
| `applications/configs/` | ✅ present | ❌ missing | ❌ missing |
| `applications/assets/` | ✅ present | ❌ missing | ❌ missing |
| `applications/libs/django-fusion/` | ✅ present | ✅ present | ✅ present |
| `applications/libs/ceptor-ai/` | ✅ present | ✅ present | ✅ present |

## README.md Template

```markdown
# <App Name>

## Purpose
One-paragraph description of what this app does.

## Tech Stack
- Django 4.2+ / Wagtail
- HTMX for dynamic fragments
- django-fusion component system

## Entry Points
- `/app/url/` — main listing
- `/app/url/<slug>/` — detail view

## Key Files
- `models.py` — data models
- `views.py` — view handlers
- `urls.py` — URL configuration
- `templates/` — Django templates

## Runbook
make -C applications check WEBSITE=<site>
make -C applications test WEBSITE=<site>
```

## AGENTS.md Template

```markdown
# <App Name> — AI Agent Instructions

## Canonical Paths
Site root: `applications/<site>/`
App path: `applications/<site>/www/<app>/`

## Template Resolution Order
1. Site templates (highest)
2. Plugin templates
3. Shared assets/templates/ (lowest)

## Component Conventions
- Use `{% comp "components/..." / %}` for all includes
- Fragment namespace: `<site>.fragments.<app>.<name>`

## Key Imports
from django_fusion.comp.routes import Site, Application
from django_fusion.comp.generic import ListModelView

## Site-Specific Deviations
- Describe differences from shared AGENTS.md
```

## PROMPTS.md Template

```markdown
# <App Name> — AI Prompt Reference

## Adding a field to <Model>

**Prompt:** Add a `description` field to the <Model> model, include it in Wagtail panels, migrate, and update the template.

**Expected Input:** Current `models.py`, template file

**Expected Output:** Updated model, migration, template

**Doc References:**
- `applications/<site>/AGENTS.md`
- `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md`
```
