# 💬 Prompts — Per-Use-Case Templates & Patterns

> Ready-to-use prompt templates for AI interactions across the monorepo — from code generation to security audits.

---

## Quick Reference

| Prompt | Use Case | Temperature |
|--------|----------|:-----------:|
| Code generation | New models, views, templates | 0.0–0.3 |
| Code review | Security, performance, style audits | 0.0–0.2 |
| Translation | i18n bulk translation | 0.3–0.5 |
| Chat / Q&A | General codebase questions | 0.5–0.7 |
| Creative tasks | Design, content, announcements | 0.7–1.0 |

---

## Chat Prompts (Cypercloud, POS Sidecar)

### System Prompt

```markdown
You are an AI assistant for the Structa Cloud monorepo.
You have access to:
- Django sites: ctc-research, lms, portfolio, cypercloud
- Desktop app: POS (Tauri + React + Rust)
- Libraries: django-fusion, ceptor-ai

Answer questions about code, suggest improvements,
and generate code following project conventions.
```

### Code Generation Prompt

```markdown
Generate a Django model for [feature] following these conventions:
- Use django-fusion Viewset for CRUD
- Place in projects/<site>/www/apps/
- Add template in projects/<site>/templates/components/
- Follow BEM-style CSS naming
- Use fragment_name for HTMX fragment identifiers
```

### Wagtail Page Generation

```markdown
Create a Wagtail page model for [feature] with:
- StreamField with [blocks] for content flexibility
- django-fusion RoutableComponent for sub-pages
- HTMX fragment rendering for dynamic sections
- SEO fields (search_image, keywords)
- Panels configuration for Wagtail admin
```

---

## Agent Prompts (ceptor-ai MCP)

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

### Codebase Exploration

```markdown
Explore the [feature] implementation across the monorepo:
1. Search for relevant model definitions
2. Find template files that render this feature
3. Locate URL configurations
4. Identify test coverage
5. Summarize the full data flow

Report file paths, key classes, and any gaps or issues found.
```

---

## Task-Based Development Prompts

### New Feature Implementation

```markdown
Implement [feature] across the full stack:

**Backend:**
- Django model in projects/<site>/www/models.py
- django-fusion ModelViewset with list/detail CRUD
- Wagtail page model if CMS-managed content
- URL configuration at /<path>/

**Frontend:**
- Template in projects/<site>/templates/components/
- HTMX fragments for dynamic interactions
- BEM-style CSS classes

**Testing:**
- pytest tests for model + view logic
- Template rendering equivalence test

**Documentation:**
- Update relevant docs/ files
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

## Translation Prompts (POS i18n)

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

JSON:
{...}
```

### Translation Audit

```markdown
Audit these translation files for:
1. Missing keys (present in en.json but not in [locale].json)
2. Missing interpolation variables
3. Stale translations (no longer used in templates)
4. Inconsistent terminology

Generate a report with counts and file paths.
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
```

### POS Rust Review

```markdown
Review this Rust code for:
1. Diesel ORM best practices (connection management, migrations)
2. Tauri command registration pattern
3. Error handling (Result<T, E> convention, proper error types)
4. Database connection safety (connection pooling, transaction handling)
5. Thread safety (Mutex, Arc usage for shared state)
6. Performance (allocation patterns, cloning avoidance)
```

### React/TypeScript Review

```markdown
Review this React/TypeScript code for:
1. TypeScript strict mode compliance
2. React 19 patterns (hooks, suspense, concurrent features)
3. State management (RTK Query, Pinia patterns)
4. Component composition (reusable, testable)
5. Performance (memoization, lazy loading, code splitting)
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
```

### Theme Customization

```markdown
Customize the [project] theme:
1. Update color palette (primary, secondary, accent)
2. Modify typography (font families, sizes, weights)
3. Adjust spacing (margin, padding scale)
4. Add dark mode variant
5. Apply consistent BEM naming
6. Update CSS variables in :root block
```

---

## Related

| Resource | Path |
|----------|------|
| AI overview | [`README.md`](README.md) |
| Agents guide | [`agents.md`](agents.md) |
| MCP integration | [`mcp-integration.md`](mcp-integration.md) |
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
| Ceptor-AI prompts | [`../../libs/ceptor-ai/PROMPTS.md`](../../libs/ceptor-ai/PROMPTS.md) |
| django-fusion prompts | [`../../libs/django-fusion/PROMPTS.md`](../../libs/django-fusion/PROMPTS.md) |
