# 🤖 Precis CTC — MCP + django-fusion Integration Plan

**Status:** Proposed  
**Created:** 2026-08-24  
**Product:** `projects/precis/precis-ctc/`

---

## 📋 Table of Contents

1. [Multi-language Course Switcher](#1-multi-language-course-switcher)
2. [Wagtail-First Rendering — Zero Astro Fallback](#2-wagtail-first-rendering)
3. [django-fusion Schema Analyzer & MCP Storage](#3-django-fusion-schema-analyzer--mcp-storage)
4. [Shell Design Commands](#4-shell-design-commands)
5. [MCP Integration with xyOps](#5-mcp-integration-with-xyops)
6. [Documentation & Agents](#6-documentation--agents)
7. [Implementation Order](#7-implementation-order)

---

## 1. Multi-language Course Switcher

### Current State
- Course detail pages render from Django `{% trans %}` blocks in `learning/course.html`
- Course cards in grid/list views have no language indicator
- The `language_selector.html` partial exists globally but not per-course

### Design
Two variants on course cards:

**Compact tab (mobile, small cards):**
```
┌──────────────────────────────────┐
│ 🇬🇧 EN · 🇸🇪 SV · 🇩🇪 DE · 🇫🇷 FR  │  ← horizontal tab strip
│                                  │
│ Clinical Trial Design            │
│ Biostatistics for Clinicians     │
└──────────────────────────────────┘
```

**Dropdown (desktop, large cards):**
```
┌──────────────────────────────────┐
│ 🌐 Available in 7 languages  ▾  │  ← dropdown trigger
│   ┌──────────────────────────┐   │
│   │ 🇬🇧 English              │   │
│   │ 🇸🇪 Svenska              │   │
│   │ 🇩🇪 Deutsch              │   │
│   │ 🇫🇷 Français             │   │
│   │ 🇪🇸 Español              │   │
│   │ 🇸🇦 العربية              │   │
│   │ 🇧🇷 Português (BR)      │   │
│   └──────────────────────────┘   │
└──────────────────────────────────┘
```

### Implementation

**Backend — Django component (`{% comp "courses/language_switcher.html" %}`):**
1. Reads `Course.language` + available translations from `CourseTranslation` model
2. Returns HTMX fragment or full HTML depending on `HX-Request` header
3. Registered in `django_fusion.comp` registry

**Frontend — Astro component:**
1. Reads course language field from API response
2. Renders compact tabs (≤3 languages) or dropdown (4+)
3. Links to `/ar/courses/clinical-trial-design/` etc.

**Files:**
- `assets/templates/courses/partials/language_switcher.html` (new)
- `frontend/src/components/ui/CourseLanguageSwitcher.astro` (new)
- `backend/apps/learning/models/courses.py` — add `CourseTranslation` model
- `backend/apps/learning/fixtures/` — seed translations for 8 courses × 7 locales

---

## 2. Wagtail-First Rendering (Zero Astro Fallback)

### Current State
- ✅ Pages (`index.astro`, `about.astro`, `features.astro`, etc.) already fetch via `cachedPageData(slug)` → `GET /apis/pages/<slug>/`
- ✅ `catch { /* use fallbacks */ }` exists but fallbacks are now medical-research content
- ✅ `renderModeSwitch` Alpine component handles HTML-vs-JSON road switching

### Remaining Gaps

| Page | Gap | Fix |
|---|---|---|
| `courses/[slug].astro` | No CMS-backed tagline | Add `cachedPageData('all-courses')` to pull CoursesPage.intro_text |
| `courses/index.astro` | Hardcoded description | Now uses CTC identity tagline ✅ |
| `profile.astro` | Static-only, no Wagtail | Add `SiteSettings` API call for user context |
| `privacy.astro`, `404.astro` | No API call | Add `SiteSettings` for site name/branding |
| Error pages (500, 502, 503, 504) | Static HTML blocks | Already server-rendered via Django `{% extends "plugins/errors/..." %}` ✅ |

### Plan
1. **Pass 1:** Wire every Astro page to pull its copy from Wagtail (`cachedPageData` or `cachedSiteSettings`)
2. **Pass 2:** Remove all `catch { /* use fallbacks */ }` — render `ContentError.astro` component instead
3. **Pass 3:** Add `?lang=sv` runtime locale hydration to remaining static pages (profile, privacy, 404)

---

## 3. django-fusion Schema Analyzer & MCP Storage

### Concept
A new `django_fusion.analytics` module that:
1. Accepts MCP tool call requests
2. Maps tool inputs/outputs to Django models
3. Stores analysis results for audit/replay
4. Provides CLI commands for design exploration

### Django Models

```python
# django_fusion/analytics/models.py

class MCPRequest(models.Model):
    """Every MCP tool call stored for audit."""
    site = models.ForeignKey('sites.Site', on_delete=models.CASCADE)
    tool_name = models.CharField(max_length=200)
    input_payload = models.JSONField()
    output_payload = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True)

class DesignChange(models.Model):
    """Design-system mutation recorded from MCP/shell commands."""
    site = models.ForeignKey('sites.Site', on_delete=models.CASCADE)
    target_component = models.CharField(max_length=200)  # e.g. "hero", "card", "button"
    target_file = models.CharField(max_length=500)
    change_type = models.CharField(max_length=50)  # "color", "radius", "spacing", "font"
    old_value = models.TextField()
    new_value = models.TextField()
    prompt = models.TextField()  # The full prompt that triggered this
    applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class PromptTemplate(models.Model):
    """Saved prompt templates for repeated design tasks."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)  # "design", "content", "analytics"
    template = models.TextField()  # Jinja2 template with {{ variables }}
    variables = models.JSONField(default=dict)  # Variable schema
    usage_count = models.IntegerField(default=0)
```

### CLI Commands

```bash
# Design exploration
python manage.py design explore --site ctc-research --component hero
python manage.py design prompt "make the hero section more rounded with softer shadows"
python manage.py design apply --change-id 42

# MCP replay
python manage.py mcp list --site ctc-research --tool xyops
python manage.py mcp replay --request-id 123

# Analytics
python manage.py analytics schema --app learning --output schema.json
python manage.py analytics diff --from main --to feature/branch
```

---

## 4. Shell Design Commands

### `python manage.py design`
```bash
# Apply design changes with prompt
python manage.py design prompt \
  --site ctc-research \
  --file "assets/static/styles/pages/_courses.scss" \
  --class ".course-hero__card" \
  --prompt "add 8px border-radius, soften shadow to 0 2px 8px rgba(0,0,0,0.1), add subtle 1px border in fu-line"

# This:
# 1. Reads current file
# 2. Sends prompt + context to AI (MCP or direct)
# 3. Receives SCSS patch
# 4. Stores DesignChange record
# 5. Applies if --apply flag given
# 6. Triggers webpack rebuild if --build
```

### Variation Inputs
The command accepts structured inputs for repeatable design changes:
```json
{
  "target_class": ".course-hero__card",
  "changes": {
    "border-radius": "8px",
    "box-shadow": "0 2px 8px rgba(0,0,0,0.1)",
    "border": "1px solid hsl(var(--fu-line))",
    "background": "hsl(var(--fu-card))"
  }
}
```

---

## 5. MCP Integration with xyOps

### Use Case
xyOps (`application/tools/xyops/`) is the operations automation tool. Integrate it as an MCP server that exposes tools for:

| Tool | Purpose |
|---|---|
| `analyze_schema` | Returns Django model schemas for a given app |
| `list_templates` | Lists templates with their `{% comp %}` usage |
| `audit_translations` | Finds untranslated `{% trans %}` strings across locales |
| `design_prompt` | Applies design changes via prompt |
| `build_preflight` | Runs webpack + collectstatic + checks before deploy |

### xyOps MCP Server Config
```json
{
  "mcpServers": {
    "ctc-design": {
      "command": "python",
      "args": ["-m", "xyops.mcp.server"],
      "env": {
        "XYOPS_PROJECT": "ctc-research",
        "DJANGO_SETTINGS_MODULE": "settings.site"
      }
    }
  }
}
```

### Full Workflow Example
```bash
# 1. Agent receives: "Add rounded corners to course cards"
# 2. Agent calls MCP: xyops.analyze_schema(app="learning")
# 3. Agent gets model fields + template paths
# 4. Agent calls: xyops.design_prompt(
#      target=".course-hero__card",
#      changes={"border-radius": "8px", "box-shadow": "0 2px 8px rgba(0,0,0,0.1)"}
#    )
# 5. xyOps writes SCSS, stores DesignChange record
# 6. Agent calls: xyops.build_preflight() → webpack + collectstatic
# 7. Agent verifies: curl course page, check rendered CSS
```

---

## 6. Documentation & Agents

### Files to create/update

| File | Content |
|---|---|
| `docs/guides/mcp-integration.md` | MCP server setup, tool catalog, workflow examples |
| `docs/guides/design-commands.md` | `manage.py design` usage, prompt templates, variations |
| `docs/ai/agent-instructions.md` | Agent prompts for design, content, translation tasks |
| `.agents/skills/ctc-design.json` | Skill definition for CTC-specific design work |
| `application/agents/config.json` | MCP server registration for xyOps |
| `docs/ar-content/guides/mcp-integration.md` | Arabic translation of MCP guide |

### Agent Skill
```json
{
  "name": "ctc-design",
  "description": "CTC Research design system — Swiss Industrial Print with optional rounded variants",
  "tools": ["design_prompt", "analyze_schema", "audit_translations", "build_preflight"],
  "defaults": {
    "target_project": "ctc-research",
    "scss_root": "assets/static/styles/",
    "design_tokens": "globals.css fu-* variables"
  }
}
```

---

## 7. Implementation Order

| Phase | Tasks | Effort |
|---|---|---|
| **Phase 1 — Concrete** | Course language switcher, .po translations, wire remaining Astro pages to API | 1-2 sessions |
| **Phase 2 — django-fusion** | Schema analyzer models, `manage.py design` command, MCP request storage | 2-3 sessions |
| **Phase 3 — xyOps MCP** | xyOps MCP server, tool definitions, agent instructions | 1-2 sessions |
| **Phase 4 — Docs** | MCP guide, design command docs, agent skill files, AR translations | 1 session |

---

## Remarks & Notes

- This plan documents the target architecture. Phase 1 tasks (language switcher, translations, Astro wiring) are executable immediately.
- The `django-fusion` analytics models should live in `libs/django-fusion/src/django_fusion/analytics/` as a reusable app, not in the CTC project.
- xyOps already exists at `application/tools/xyops/` — adding MCP server capability is additive.
- All design changes should record `DesignChange` records for audit. The `--apply` flag gates actual file writes.

🤖 Generated with Codebuff