# 🤖 AI — Agents, Prompts & MCP Integration

> Covers AI agent instructions, prompt engineering, and MCP server integration across the Structa Cloud monorepo.

---

## Overview

The Structa Cloud monorepo uses AI extensively through three mechanisms:

| Mechanism | Location | Purpose |
|-----------|----------|---------|
| **AGENTS.md files** | Root + per-project dirs | AI coding assistant behavioral instructions |
| **Prompt templates** | Cypercloud, POS, ceptor-ai, `docs/ai/` | Chat prompts, code generation, translation |
| **MCP Servers** | Kilo (`applications/kilo`), ceptor-ai (`libs/ceptor-ai`) | Model Context Protocol tool execution |

### How They Work Together

```
AGENTS.md files
  └─ Tell AI assistants HOW to work in this codebase
     └─ Conventions, paths, rules, constraints

Prompt templates
  └─ Tell AI assistants WHAT to generate or review
     └─ Reusable prompts for common tasks

MCP Servers
  └─ Give AI assistants TOOLS to execute
     └─ Code search, file reading, test running, doc retrieval
```

---

## Supported AI Backends

| Backend | Env Var | Default Model | Notes |
|---------|---------|---------------|-------|
| **Ollama** | `OLLAMA_BASE_URL` | `gemma3:4b` | Local, self-hosted, no API key required |
| **OpenAI** | `OPENAI_API_KEY` | `gpt-4o` | Requires API key, best for complex tasks |
| **Anthropic** | `ANTHROPIC_API_KEY` | `claude-3.5-sonnet` | Requires API key, strong code understanding |
| **Google Gemini** | `GEMINI_API_KEY` | `gemini-2.0-flash` | Requires API key, fast inference |

---

## AGENTS.md Hierarchy

AGENTS.md files form a hierarchical instruction system:

```
Root AGENTS.md ─── Monorepo-wide conventions
  ├── projects/<site>/AGENTS.md ─── Site-specific rules
  ├── libs/<lib>/AGENTS.md ─── Library conventions
  ├── projects/assets/templates/AGENTS.md ─── Template rules
  └── applications/<tool>/AGENTS.md ─── Infrastructure rules
```

AI agents load ALL AGENTS.md files from root to leaf — later files override earlier ones.

### Complete AGENTS.md Map

| Location | Scope |
|----------|-------|
| [Root AGENTS.md](../AGENTS.md) | Monorepo-wide conventions, template paths, Makefile delegation |
| `projects/lms/AGENTS.md` | LMS site conventions, plugins, components |
| `projects/portfolio/AGENTS.md` | Portfolio/VResume site structure, page templates |
| `projects/cypercloud/templates/AGENTS.md` | AI chat customizer conventions |
| `projects/assets/templates/AGENTS.md` | Template organization, resolution order |
| `projects/assets/templates/components/AGENTS.md` | Shared component inventory |
| `projects/assets/templates/plugins/AGENTS.md` | Plugin template conventions |
| `libs/django-fusion/AGENTS.md` | Component system, routing, canonical imports |
| `libs/ceptor-ai/AGENTS.md` | AI assistant, MCP server, chat client |
| `applications/kilo/AGENTS.md` | Kilo MCP server, tool definitions |

### AGENTS.md Structure Convention

```markdown
# [Section Name] — AI Agent Instructions
## Scope
## Conventions
## Key Files
## Customization Tips
## Related Docs
```

---

## Prompt Types & Use Cases

| Type | Used In | Description | Temperature |
|------|---------|-------------|:-----------:|
| **Chat Prompts** | Cypercloud, POS sidecar | Real-time streaming chat | 0.5–0.7 |
| **Code Generation** | All projects | New models, views, templates | 0.0–0.3 |
| **Code Review** | All projects | Security, performance, style audits | 0.0–0.2 |
| **Translation** | POS i18n audit | Bulk translation prompts | 0.3–0.5 |
| **System Prompts** | AGENTS.md files | Per-project behavioral instructions | — |
| **MCP Tool Prompts** | Kilo, ceptor-ai | Tool-calling prompts | 0.0–0.2 |

See [prompts.md](prompts.md) for the full template library.

---

## MCP Integration

Two MCP servers provide tool access to AI assistants:

### Kilo MCP Server (`applications/kilo/`)

| Tool | Purpose | Parameters |
|------|---------|------------|
| `search_codebase` | Search for code patterns | `pattern`, `file_types`, `directory` |
| `read_files` | Read source files | `paths`, `max_lines` |
| `run_tests` | Execute test suites | `project`, `test_path`, `verbose` |
| `get_docs` | Retrieve documentation | `path`, `section` |

### Ceptor-AI MCP Server (`libs/ceptor-ai/`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health status |
| `/features` | GET | List registered MCP tools |
| `/tools` | GET | Tool schema definitions |
| `/file-structure` | GET | Repository file tree |

See [mcp-integration.md](mcp-integration.md) for full details.

---

## AI Workflow Best Practices

### For Code Generation

1. **Read** the relevant AGENTS.md files first
2. **Search** the codebase for existing patterns
3. **Generate** code following conventions
4. **Review** output against AGENTS.md rules
5. **Test** generated code with project test suite

### For Code Review

1. **Load** the file's context (imports, dependencies)
2. **Check** against AGENTS.md conventions
3. **Verify** canonical import paths
4. **Test** for common issues (N+1, XSS, CSRF)
5. **Report** findings with file:line references

### For AI Chat

- Include **system context** about codebase structure
- Reference **actual source files** for precision
- Use **streaming** via SSE for real-time UX
- Code generation: temperature 0.0–0.3
- Creative tasks: temperature 0.7+

---

## Related

| Resource | Path |
|----------|------|
| Agent instructions (detail) | [`agents.md`](agents.md) |
| Prompt engineering (detail) | [`prompts.md`](prompts.md) |
| MCP integration (detail) | [`mcp-integration.md`](mcp-integration.md) |
| Cypercloud AI chat | [`../projects/cypercloud/`](../projects/cypercloud/) |
| Ceptor-AI library | [`libs/ceptor-ai/`](../../libs/ceptor-ai/) |
| django-fusion library | [`libs/django-fusion/`](../../libs/django-fusion/) |
| Kilo MCP server | [`../../applications/kilo/`](../../applications/kilo/) |
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
