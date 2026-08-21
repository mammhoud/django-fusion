# 🤖 Agents — AGENTS.md File Inventory & Hierarchy

> Complete inventory of every `AGENTS.md` file in the monorepo — what it covers, when to use it, and how the hierarchical instruction system works for AI coding assistants.

---

## How AGENTS.md Works

AGENTS.md files act as **behavioral instructions** for AI coding assistants (Claude, Codebuff, Cursor, Freebuff, etc.). They form a cumulative hierarchy:

```
Root /AGENTS.md — Monorepo-wide conventions, safety rules, ownership
  ├── projects/AGENTS.md — Project-level conventions
  │   ├── projects/precis/precis-main/AGENTS.md — Precis LMS project
  │   └── projects/precis/precis-main/backend/AGENTS.md — Precis LMS backend
  │   │   ├── projects/precis/precis-main/backend/apps/pages/blog/templates/AGENTS.md
  │   │   ├── projects/precis/precis-main/backend/apps/pages/profile/templates/AGENTS.md
  │   │   ├── projects/precis/precis-main/backend/apps/pages/accounts/templates/AGENTS.md
  │   │   ├── projects/precis/precis-main/backend/apps/learning/templates/AGENTS.md
  │   │   ├── projects/precis/precis-main/backend/apps/templates/AGENTS.md
  │   │   └── projects/precis/precis-main/backend/templates/AGENTS.md
  │   ├── projects/precis/precis-main/assets/templates/AGENTS.md
  │   │   ├── projects/precis/precis-main/assets/templates/blog/AGENTS.md
  │   │   ├── projects/precis/precis-main/assets/templates/pages/AGENTS.md
  │   │   ├── projects/precis/precis-main/assets/templates/lms/AGENTS.md
  │   │   ├── projects/precis/precis-main/assets/templates/components/AGENTS.md
  │   │   ├── projects/precis/precis-main/assets/templates/profile/AGENTS.md
  │   │   └── projects/precis/precis-main/assets/templates/plugins/AGENTS.md
  │   ├── projects/precis/precis-landing/AGENTS.md
  │   ├── projects/syntara/AGENTS.md
  │   │   └── projects/syntara/templates/AGENTS.md
  │   └── projects/formints/AGENTS.md
  │       ├── projects/formints/formint-pro/AGENTS.md
  │       ├── projects/formints/formint-community/AGENTS.md
  │       ├── projects/formints/formint-cloud/frontend/AGENTS.md
  │       ├── projects/formints/formint-standard/AGENTS.md
  │       ├── projects/formints/formint-client/AGENTS.md
  │       └── projects/formints/tests/pos-e2e/AGENTS.md
  ├── libs/django-fusion/AGENTS.md
  ├── application/AGENTS.md
  │   └── application/agents/AGENTS.md (Kilo MCP)
  └── tests/AGENTS.md
```

When an AI agent works on a file, it loads all AGENTS.md files from the root down to the file's directory — later files override/refine earlier ones.

---

## Complete AGENTS.md Inventory

### Root Level

| File | Scope | Key Rules |
|------|-------|-----------|
| [`/AGENTS.md`](../../AGENTS.md) | Monorepo-wide conventions, safety rules, ownership, dispatcher | **Always read first** — authoritative on product boundaries, name migrations, safety |

### Project Level

| File | Scope | Key Rules |
|------|-------|-----------|
| `projects/AGENTS.md` | Project-level dispatcher conventions | Makefile delegation, WEBSITE= selection |
| `projects/precis/precis-main/AGENTS.md` | Precis LMS project | Full product surface — backend, frontend, assets, templates, deployment |
| `projects/precis/precis-main/backend/AGENTS.md` | Precis LMS backend | App ownership, URL flow, template resolution order |
| `projects/precis/precis-landing/AGENTS.md` | Precis Landing project | Astro/Django dual rendering, content contracts, testing |
| `projects/syntara/AGENTS.md` | Syntara / Cypercloud | AI streaming, template catalog, provider boundaries |
| `projects/formints/AGENTS.md` | Formint multi-edition POS | Edition map, cloud rules, community rules, cross-cutting |
| `projects/formints/formint-pro/AGENTS.md` | Formint Professional | Django + Ninja + Astro + Tauri; fusion render-mode |

### Template & Asset Level

| File | Scope | Key Rules |
|------|-------|-----------|
| `projects/precis/precis-main/backend/apps/pages/blog/templates/AGENTS.md` | Blog templates | Blog-specific component and fragment conventions |
| `projects/precis/precis-main/backend/apps/pages/profile/templates/AGENTS.md` | Profile templates | Profile page structure and template rules |
| `projects/precis/precis-main/backend/apps/pages/accounts/templates/AGENTS.md` | Auth/account templates | Allauth integration, verification templates |
| `projects/precis/precis-main/backend/apps/learning/templates/AGENTS.md` | Learning templates | Course catalog, enrollment, progress templates |
| `projects/precis/precis-main/backend/apps/templates/AGENTS.md` | App-level shared templates | Shared component overrides and conventions |
| `projects/precis/precis-main/backend/templates/AGENTS.md` | Backend root templates | Site-root shells, error pages, admin overrides |
| `projects/precis/precis-main/assets/templates/AGENTS.md` | Asset templates root | Template organization and resolution order |
| `projects/precis/precis-main/assets/templates/blog/AGENTS.md` | Asset blog templates | Blog asset template conventions |
| `projects/precis/precis-main/assets/templates/pages/AGENTS.md` | Asset page templates | Page template conventions |
| `projects/precis/precis-main/assets/templates/lms/AGENTS.md` | Asset LMS templates | LMS-specific template conventions |
| `projects/precis/precis-main/assets/templates/components/AGENTS.md` | Asset components | Reusable component conventions |
| `projects/precis/precis-main/assets/templates/profile/AGENTS.md` | Asset profile templates | Profile template conventions |
| `projects/precis/precis-main/assets/templates/plugins/AGENTS.md` | Asset plugin templates | Plugin template conventions |
| `projects/syntara/templates/AGENTS.md` | Syntara templates | AI chat/editor component templates |

### Library Level

| File | Scope | Key Rules |
|------|-------|-----------|
| `libs/django-fusion/AGENTS.md` | Shared framework | Canonical imports, components, routing, fragments, assets |

### Infrastructure Level

| File | Scope | Key Rules |
|------|-------|-----------|
| `application/AGENTS.md` | Infrastructure | Docker, proxy, databases, deployment boundaries |
| `application/agents/AGENTS.md` | Kilo MCP server | Read-only introspection, endpoint groups, skills |

### Testing Level

| File | Scope | Key Rules |
|------|-------|-----------|
| `tests/AGENTS.md` | Workspace tests | Integration, browser, E2E testing conventions |

### Formint Edition Level

| File | Scope | Key Rules |
|------|-------|-----------|
| `projects/formints/formint-community/AGENTS.md` | Community (Tauri + React) | Offline-first, no Python, Rust/Diesel patterns |
| `projects/formints/formint-cloud/frontend/AGENTS.md` | Cloud frontend | Django templates, Unfold admin, Channels |
| `projects/formints/formint-standard/AGENTS.md` | Standard edition | Astro + Tauri conventions |
| `projects/formints/formint-client/AGENTS.md` | POS Client | Vue 3 + Tauri + Django backend |
| `projects/formints/tests/pos-e2e/AGENTS.md` | POS E2E tests | Playwright flows, API contracts |

---

## AGENTS.md Structure Convention

Every AGENTS.md follows this pattern:

```markdown
# [Section Name] — AI Agent Instructions

## Path
Absolute or repo-relative path to the owning directory.

## Layout
Directory structure and key files.

## Conventions / Rules
- Code style, imports, naming, template rules
- Structural constraints the agent must follow
- Safety rules and boundaries

## Commands
Relevant development, test, build, and deployment commands.

## Testing
Test expectations and affected suites.

## Do Not / Red Flags
Things to avoid when working in this scope.

## Related
Cross-links to other AGENTS.md files and documentation.
```

### Best Practices

| Practice | Why |
|----------|-----|
| Be **specific** about file paths and naming rules | Avoids hallucinated file locations |
| Include **examples** of correct and incorrect code | Reduces ambiguity |
| Reference **actual source files** the agent needs to know | Precise context = better output |
| Keep prompts **concise** | AI agents have limited context windows |
| Avoid **contradictions** between nested AGENTS.md files | Later files override earlier ones |
| Use **absolute or repo-relative paths** for cross-references | Paths stay valid across tools |

---

## When to Add a New AGENTS.md

- Creating a new project or product directory
- Adding a complex template directory with non-obvious conventions
- Introducing constraints AI agents need to know about
- Adding a library with specific import patterns or API surfaces
- Adding infrastructure components with specific configuration patterns

---

## Associated Agent Configuration

Beyond AGENTS.md files, the project includes:

### `.agents/` Directory

```
.agents/
├── skills/                              # 21 reusable AI skills
│   ├── design-taste-frontend/SKILL.md   # Anti-slop frontend design
│   ├── gpt-taste/SKILL.md               # Elite UX/UI with GSAP
│   ├── high-end-visual-design/SKILL.md  # Premium UI standards
│   ├── shadcn/SKILL.md                  # shadcn/ui component management
│   ├── brandkit/SKILL.md                # Brand system generation
│   ├── imagegen-frontend-web/SKILL.md   # Web design image generation
│   ├── imagegen-frontend-mobile/SKILL.md # Mobile design image generation
│   ├── image-to-code/SKILL.md           # Design-to-code conversion
│   ├── documentation/SKILL.md           # Technical documentation
│   ├── deployment-documentation/SKILL.md # Deployment docs
│   ├── content-strategy/SKILL.md        # Content planning
│   ├── content-production/SKILL.md      # Content creation pipeline
│   ├── content-creator/SKILL.md         # Legacy content routing
│   ├── explore-data/SKILL.md            # Dataset profiling
│   ├── use-case-triage/SKILL.md         # Privacy PIA/DPIA triage
│   ├── minimalist-ui/SKILL.md           # Clean editorial interfaces
│   ├── industrial-brutalist-ui/SKILL.md # Raw mechanical interfaces
│   ├── stitch-design-taste/SKILL.md     # Semantic design system
│   ├── redesign-existing-projects/SKILL.md # Project redesign
│   ├── design-taste-frontend-v1/SKILL.md  # Legacy v1 skill
│   └── full-output-enforcement/SKILL.md   # Complete code generation
└── kiro/
    └── settings/
        └── mcp.json                    # MCP server configuration
```

### Kilo MCP Server (`application/agents/`)

The Kilo MCP server provides programmatic introspection for:
- Health/readiness checks
- django-fusion framework inventory
- Site endpoint discovery
- Docker service status
- Auth configuration

Commands and skills in `application/agents/commands/` and `application/agents/skills/`.

---

## Related

| Resource | Path |
|----------|------|
| AI overview | [`README.md`](README.md) |
| Prompts guide | [`prompts.md`](prompts.md) |
| MCP integration | [`mcp-integration.md`](mcp-integration.md) |
| Root AGENTS.md | [`../../AGENTS.md`](../../AGENTS.md) |
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
