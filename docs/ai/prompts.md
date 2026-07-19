# 💬 Prompts — Per-Use-Case Templates

> Ready-to-use prompt templates for AI interactions across the monorepo.

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
```

---

## Agent Prompts (ceptor-ai MCP)

### Tool-Calling Prompt

```markdown
You have access to these MCP tools:
- search_codebase: Search for code patterns
- read_files: Read source files
- run_tests: Execute test suites

Use these tools to answer questions about the codebase.
Always return structured JSON responses.
```

---

## Translation Prompts (POS i18n)

### Bulk Translation

```markdown
Translate the following English JSON keys to French (fr) and Arabic (ar).
Preserve interpolation variables {count}, {name}, etc.
Use Modern Standard Arabic (فصحى) for Arabic translations.

JSON:
{...}
```

---

## Code Review Prompts

### Django Review

```markdown
Review this Django code for:
1. PEP 8 compliance
2. django-fusion conventions (canonical import paths)
3. Template naming (BEM-style classes, fragment_name convention)
4. Security (CSRF, SQL injection, XSS)
```

### POS Rust Review

```markdown
Review this Rust code for:
1. Diesel ORM best practices
2. Tauri command registration pattern
3. Error handling (Result<T, String> convention)
4. Database connection safety
```

---

## Related

| Resource | Path |
|----------|------|
| AI overview | [`README.md`](README.md) |
| Agents guide | [`agents.md`](agents.md) |
| Best practices | [`../best-practices/`](../best-practices/) |
