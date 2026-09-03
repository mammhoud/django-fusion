# 💬 Prompts — Templates, Skills & Patterns

> Ready-to-use prompt templates, .agents/skills inventory, and AI interaction patterns across the monorepo.

---

## Quick Reference

| Prompt Type | Use Case | Temperature |
|-------------|----------|:-----------:|
| Code generation | New models, views, templates | 0.0–0.3 |
| Code review | Security, performance, style audits | 0.0–0.2 |
| Translation | i18n bulk translation | 0.3–0.5 |
| Chat / Q&A | General codebase questions | 0.5–0.7 |
| Creative tasks | Design, content, announcements | 0.7–1.0 |

---

## .agents/skills Inventory (21 skills)

Skills are reusable, self-contained instructions loaded into Freebuff/Codex sessions. Each skill provides domain-specific expertise for a particular task.

### Design & UI Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| `design-taste-frontend` | Anti-slop frontend design for landing pages, portfolios | Building new UI, redesigning |
| `gpt-taste` | Elite UX/UI with GSAP motion, true randomization, AIDA structure | Premium landing pages, bento grids |
| `high-end-visual-design` | Premium UI standards: fonts, spacing, shadows, cards | Avoiding generic/cheap designs |
| `minimalist-ui` | Clean editorial-style interfaces | Warm monochrome, typographic contrast |
| `industrial-brutalist-ui` | Raw mechanical interfaces, Swiss typographic + military terminal | Data-heavy dashboards, portfolios |
| `shadcn` | shadcn/ui component management | Adding/fixing/styling shadcn components |
| `redesign-existing-projects` | Upgrade existing websites to premium quality | Auditing + applying premium standards |
| `stitch-design-taste` | Semantic design system (DESIGN.md generation) | Google Stitch projects |

### Image Generation Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| `imagegen-frontend-web` | Premium web design image generation | Landing pages, marketing sites, product comps |
| `imagegen-frontend-mobile` | Premium mobile app image generation | iOS, Android, cross-platform screens |
| `image-to-code` | Design-to-code conversion pipeline | Turning designs into matching implementations |
| `brandkit` | Brand system generation | Logo systems, identity decks, brand guidelines |

### Content Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| `content-strategy` | Content planning, topic clusters, calendars | "What should I write about?", content planning |
| `content-production` | Full content pipeline: blank page → published-ready | Writing blog posts, articles, guides |
| `content-creator` | Legacy routing to content-strategy or content-production | Deprecated; routes to correct specialist |

### Documentation & Data Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| `documentation` | Technical documentation writing | READMEs, runbooks, API docs, architecture docs |
| `deployment-documentation` | Deployment process documentation | CI/CD, infrastructure, deployment guides |
| `explore-data` | Dataset profiling and exploration | New tables/files, data quality checks |

### Specialized Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| `use-case-triage` | Privacy PIA/DPIA decision triage | "Does this need a PIA?", privacy checks |
| `full-output-enforcement` | Complete code generation, no placeholders | Exhaustive, unabridged output |
| `design-taste-frontend-v1` | Legacy v1 taste skill | Backward compatibility only |

### Loading Skills

Skills are loaded by the AI assistant at runtime:

```
Load skill "design-taste-frontend" to get full design instructions
Load skill "shadcn" when working with shadcn/ui components
```

See each `SKILL.md` file under `.agents/skills/<name>/SKILL.md` for full instructions. The stable machine-readable prompt packs are in [`.agents/mcp/prompts/catalog.json`](../../.agents/mcp/prompts/catalog.json), with usage and validation documented in [`PROMPT_CATALOG.md`](PROMPT_CATALOG.md).

---

## Chat Prompts (Syntara, Formint)

> Tags: `#structa-cloud` `#formints` `#pos` `#syntara` `#cypercloud`
> `#chat` `#ai`
>
> Formint edition status (21 Aug 2026): Community/Standard/Pro ✅ done ·
> Cloud 🟡 staging · pos-client 🔵 dev. Remaining promotion steps:
> [`docs/plans/editions/09-completion-plan.md`](../plans/editions/09-completion-plan.md).

### System Prompt

```markdown
You are an AI assistant for the Structa Cloud monorepo.
You have access to:
- Precis LMS (Django + Wagtail learning platform)
- Precis Landing (Astro + Django marketing site)
- Syntara/Cypercloud (AI chat + code customization)
- Formint POS (multi-edition restaurant POS)
- django-fusion (shared Django/Wagtail components)

Answer questions about code, suggest improvements,
and generate code following project conventions.
```

### Code Generation Prompt

```markdown
Generate a Django model for [feature] following these conventions:
- Use django-fusion Viewset for CRUD
- Place in projects/<product>/backend/apps/<app>/
- Add template in the appropriate templates directory
- Follow BEM-style CSS naming
- Use fragment_name for HTMX fragment identifiers
- Check the nearest AGENTS.md for product-specific rules
```

### Wagtail Page Generation

```markdown
Create a Wagtail page model for [feature] with:
- StreamField with [blocks] for content flexibility
- django-fusion RoutableComponent for sub-pages
- HTMX fragment rendering for dynamic sections
- SEO fields (search_image, keywords)
- Panels configuration for Wagtail admin
- Place in projects/<product>/backend/apps/pages/
```

---

## Stable Skills-as-Prompts Catalog

Use the catalog when an agent needs a reusable task prompt rather than only a
role description:

| Catalog group | IDs | Includes |
|---|---|---|
| Skill packs | `skill.*` | Task prompt, primary/supporting agents, installed skills, inputs, output contract, safety |
| Project packs | `project.*` | Stack, paths, boundaries, agent sequence, project prompt, checks |
| Workflows | `workflow.*` | Multi-agent orchestration sequence and handoff stages |

Recommended selection:

1. Load the nearest `AGENTS.md` files.
2. Select one `project.*` pack.
3. Select one primary `skill.*` pack and only the supporting skills needed.
4. Delegate independent architecture, UI/security, and test review to the listed agents.
5. Implement only after the plan is understood; validate with project-owned commands.

The catalog is served read-only by the local Kilo helper at `/prompts` and
`/prompts/{id}`. It never executes prompts or grants mutation permissions.

See [`PROMPT_CATALOG.md`](PROMPT_CATALOG.md) for the complete descriptions,
project boundaries, safety contract, and examples.

---

## Agent Prompts (Kilo MCP)

### Tool-Calling System Prompt

```markdown
You have access to these MCP tools:
- search_codebase: Search for code patterns using ripgrep
- read_files: Read source files with line numbers
- run_tests: Execute test suites for specific projects
- get_docs: Retrieve documentation for a project or component

Use these tools to answer questions about the codebase.
Always return structured JSON responses.
Confirm before making any file modifications.
```

---

## Task-Based Development Prompts

### New Feature Implementation

```markdown
Implement [feature] across the full stack for [product]:

**Backend:**
- Django model in the appropriate backend/apps/ directory
- django-fusion ModelViewset with list/detail CRUD
- Wagtail page model if CMS-managed content
- URL configuration

**Frontend:**
- Template in the product's template directory
- HTMX fragments for dynamic interactions
- BEM-style CSS classes

**Testing:**
- pytest tests for model + view logic
- Template rendering test

**Documentation:**
- Update relevant docs/ files
- Follow AGENTS.md hierarchy conventions
```

### Security Audit Prompt

```markdown
Audit this code for security vulnerabilities:

1. **CSRF** — Are all mutation endpoints CSRF-protected?
2. **SQL Injection** — Are raw queries parameterized?
3. **XSS** — Is user input escaped in templates?
4. **Auth** — Are views properly permission-gated?
5. **Secrets** — Are any secrets hardcoded?
6. **Rate limiting** — Are sensitive endpoints rate-limited?
7. **HTTPS** — Is SSL enforced for all pages?

Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW).
```

### Performance Audit Prompt

```markdown
Review this code for performance issues:

1. **N+1 queries** — Are prefetch_related / select_related used?
2. **Caching** — Are expensive queries cached?
3. **Template rendering** — Are {% comp %} tags used over {% include %}?
4. **Database** — Are there missing indexes?
5. **Static files** — Are CSS/JS bundles optimized?
6. **Async** — Can any sync operations be made async?

Report with estimated impact and fix suggestions.
```

---

## Translation Prompts (Formint i18n)

> Tags: `#formints` `#pos` `#i18n` `#translation` `#arabic` `#french`
> `#l10n`

### Bulk Translation

```markdown
Translate the following English JSON keys to French (fr) and Arabic (ar).
Preserve interpolation variables {count}, {name}, etc.
Use Modern Standard Arabic (فصحى) for Arabic translations.

Rules:
- Keep all interpolation variables intact: {count}, {name}, {amount}
- French: Use formal "vous" form
- Arabic: Use Modern Standard Arabic, not dialectal
- Preserve HTML tags if present

JSON: {...}
```

---

## Code Review Prompts

### Django Review

```markdown
Review this Django code for:
1. PEP 8 compliance and type hints
2. django-fusion conventions (canonical import paths)
3. Template naming (BEM-style classes, fragment_name convention)
4. Security (CSRF, SQL injection, XSS)
5. Database query efficiency (N+1, indexes)
6. Error handling (try/except blocks, logging)
7. Test coverage (unit tests for new code)
8. AGENTS.md compliance (check nearest AGENTS.md)
```

### Rust Review (Formint)

> Tags: `#formints` `#pos` `#rust` `#tauri` `#diesel` `#sqlite`

```markdown
Review this Rust code for:
1. Diesel ORM best practices (connection management, migrations)
2. Tauri command registration pattern
3. Error handling (Result<T, E> convention, proper error types)
4. Database connection safety (connection pooling, transaction handling)
5. Thread safety (Mutex, Arc usage for shared state)
6. Performance (allocation patterns, cloning avoidance)
```

### Astro/TypeScript Review

```markdown
Review this Astro/TypeScript code for:
1. TypeScript strict mode compliance
2. Astro 5 patterns (islands, View Transitions, content collections)
3. State management (Alpine.js stores, Nanostores)
4. Component composition (reusable, testable)
5. Performance (partial hydration, lazy loading)
6. Accessibility (aria attributes, keyboard navigation)
7. i18n (translation key usage, RTL support)
```

---

## Design & Customization Prompts

### New Component Design

```markdown
Design a reusable [component-name] component:

Requirements:
- Uses django-fusion {% comp %} tag
- BEM-style CSS classes
- HTMX for interactivity
- Supports dark/light theme
- Accessible (WCAG AA)
- Responsive (mobile-first)
- Documented with context variables and usage examples
- Follow the nearest templates/AGENTS.md conventions
```

### Theme Customization

```markdown
Customize the [product] theme:
1. Update color palette (primary, secondary, accent)
2. Modify typography (font families, sizes, weights)
3. Adjust spacing (margin, padding scale)
4. Add dark mode variant
5. Apply consistent BEM naming
6. Update CSS variables in :root block
7. Build with the product's asset pipeline
```

---

## Related

| Resource | Path |
|----------|------|
| AI overview | [`README.md`](README.md) |
| Agents guide | [`agents.md`](agents.md) |
| MCP integration | [`mcp-integration.md`](mcp-integration.md) |
| Best practices | [`../guides/08-best-practices.md`](../guides/08-best-practices.md) |
| .agents/skills | [`.agents/skills/`](../../.agents/skills/) |
| Project structure | [`../project-structure.md`](../project-structure.md) |
