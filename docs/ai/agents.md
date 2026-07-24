# 🤖 Agents — Per-File Use Cases & Best Practices

> Every AGENTS.md file in the monorepo — what it covers, when to use it, and how AGENTS.md files form a hierarchical instruction system for AI coding assistants.

---

## How AGENTS.md Works

AGENTS.md files act as **behavioral instructions** for AI coding assistants (Claude, Codebuff, Cursor, etc.). They form a hierarchy:

```
Root AGENTS.md — Monorepo-wide conventions
  ├── docs/ AGENTS.md — Documentation standards
  ├── projects/<site>/AGENTS.md — Site-specific conventions
  │     ├── plugins/<name>/AGENTS.md — Plugin conventions
  │     └── templates/AGENTS.md — Template conventions
  └── libs/<name>/AGENTS.md — Library conventions
  └── applications/<name>/AGENTS.md — Infrastructure conventions
```

When an AI agent works on a file, it loads all AGENTS.md files from the root down to the file's directory — later files override/refine earlier ones.

---

## AGENTS.md File Map

### Root

| File | Scope | When to Read |
|------|-------|-------------|
| [AGENTS.md](../AGENTS.md) | Monorepo-wide conventions, template paths, Makefile delegation | **Always** — first file any AI agent should read |

### Django Sites

| File | Scope | Use Case |
|------|-------|----------|
| `projects/lms/AGENTS.md` | LMS site conventions, plugins, components | Working on structa.cloud code |
| `projects/portfolio/AGENTS.md` | Portfolio/VResume site structure, page templates | Working on vresume.structa.cloud |
| `projects/cypercloud/AGENTS.md` | Cypercloud AI chat, customizer conventions | Working on Cypercloud templates |
| `projects/ctc-research/AGENTS.md` | CTC Research site structure | Working on ctc-research.com |

### Shared Assets

| File | Scope | Use Case |
|------|-------|----------|
| `projects/assets/templates/AGENTS.md` | Template organization, resolution order | Adding/modifying shared templates |
| `projects/assets/templates/components/AGENTS.md` | Component template conventions | Creating reusable components |
| `projects/assets/templates/plugins/AGENTS.md` | Plugin template conventions | Adding plugin templates |

### Libraries

| File | Scope | Use Case |
|------|-------|----------|
| `libs/django-fusion/AGENTS.md` | Component system, routing, canonical imports | Working on django-fusion or using components |
| `libs/ceptor-ai/AGENTS.md` | AI assistant, MCP server, chat client | Working on AI features or MCP tools |
| `libs/django-fusion/.../templates/components/AGENTS.md` | Built-in component inventory | When using django-fusion components |

### Infrastructure

| File | Scope | Use Case |
|------|-------|----------|
| `applications/kilo/AGENTS.md` | Kilo MCP server, tool definitions | Working on MCP server configuration |

---

## AGENTS.md Structure Convention

Every AGENTS.md follows this pattern:

```markdown
# [Section Name] — AI Agent Instructions

## Scope
What this directory covers

## Conventions
- Code style, imports, naming, template rules
- Structural constraints the agent must follow

## Key Files
- Path → Purpose mapping for important files

## Customization Tips
- What's safe to change
- Where to find related code
- Red flags / things NOT to do

## Related Docs
- Cross-links to relevant documentation
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

- Creating a new project or plugin directory
- Adding complex template directories with non-obvious conventions
- Introducing constraints AI agents need to know about
- Adding a library with specific import patterns or API surfaces
- Adding infrastructure components with specific configuration patterns

---

## Known AGENTS.md Shortcomings

- **Overlapping scope**: Some AGENTS.md files duplicate conventions from the root file. Prefer deduplication via cross-references.
- **Stale paths**: Some files still reference the old `core/` layout or legacy plugin locations. When editing, update paths.
- **Missing `@tested` annotations**: Not all AGENTS.md files declare they've been tested against the actual codebase. Add `# @tested <category>` at the end when verified.

---

## Related

| Resource | Path |
|----------|------|
| AI overview | [`README.md`](README.md) |
| Prompts guide | [`prompts.md`](prompts.md) |
| MCP integration | [`mcp-integration.md`](mcp-integration.md) |
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
