# 🤖 Agents — Per-File Use Cases

> Every AGENTS.md file in the monorepo — what it covers and when to use it.

---

## AGENTS.md File Map

### Root

| File | Scope | When to Read |
|------|-------|-------------|
| [AGENTS.md](https://github.com/mammhoud/structa.cloud/blob/generic/AGENTS.md) | Monorepo-wide conventions, template paths, Makefile delegation | Always — first file any AI agent should read |

### Django Sites

| File | Scope | Use Case |
|------|-------|----------|
| `projects/lms/AGENTS.md` | LMS site conventions, plugins, components | Working on structa.cloud code |
| `projects/portfolio/AGENTS.md` | VResume site structure, page templates | Working on vresume.structa.cloud |
| `projects/cypercloud/templates/AGENTS.md` | AI chat customizer conventions | Working on Cypercloud templates |

### Libraries

| File | Scope | Use Case |
|------|-------|----------|
| `libs/django-fusion/AGENTS.md` | Component system, routing, canonical imports | Working on django-fusion or using components |
| `libs/ceptor-ai/AGENTS.md` | AI assistant, MCP server, chat client | Working on AI features or MCP tools |

### Infrastructure

| File | Scope | Use Case |
|------|-------|----------|
| `applications/kilo/AGENTS.md` | Kilo MCP server, tool definitions | Working on MCP server configuration |

### Templates

| File | Scope | Use Case |
|------|-------|----------|
| `projects/assets/templates/AGENTS.md` | Template organization, resolution order | Adding/modifying shared templates |
| `projects/assets/templates/components/AGENTS.md` | Component template conventions | Creating reusable components |
| `projects/assets/templates/plugins/AGENTS.md` | Plugin template conventions | Adding plugin templates |

---

## AGENTS.md Structure Convention

Every AGENTS.md follows this pattern:

```markdown
# [Section Name] — AI Agent Instructions

## Scope
What this directory covers

## Conventions
- Code style, imports, naming, template rules

## Customization Tips
- What's safe to change
- Where to find related code
```

## When to Add a New AGENTS.md

- Creating a new project or plugin directory
- Adding complex template directories
- Introducing non-obvious constraints AI agents need to know

---

## Related

| Resource | Path |
|----------|------|
| AI overview | [`README.md`](README.md) |
| Prompts guide | [`prompts.md`](prompts.md) |
| Best practices | [`../best-practices/`](../best-practices/) |
