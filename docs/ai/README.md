# 🤖 AI — Agents, Prompts & MCP Integration

> Covers AI agent instructions, prompt engineering, and MCP server integration across the Structa Cloud monorepo.

---

## Overview

The Structa Cloud monorepo uses AI extensively through three mechanisms:

| Mechanism | Location | Purpose |
|-----------|----------|---------|
| **AGENTS.md files** | Root + per-project dirs | AI coding assistant behavioral instructions |
| **Prompt templates** | Cypercloud, POS, ceptor-ai | Chat prompts, code generation, translation |
| **MCP Servers** | Kilo (applications/kilo), ceptor-ai | Model Context Protocol tool execution |

---

## Supported AI Backends

| Backend | Env Var | Default Model | Notes |
|---------|---------|---------------|-------|
| **Ollama** | `OLLAMA_BASE_URL` | `gemma3:4b` | Local, self-hosted, no API key |
| **OpenAI** | `OPENAI_API_KEY` | `gpt-4o` | Requires API key |
| **Anthropic** | `ANTHROPIC_API_KEY` | `claude-3-opus` | Requires API key |
| **Google Gemini** | `GEMINI_API_KEY` | `gemini-2.0-flash` | Requires API key |

---

## AGENTS.md Map

| Location | Scope |
|----------|-------|
| [Root AGENTS.md](https://github.com/mammhoud/structa.cloud/blob/generic/AGENTS.md) | Monorepo-wide conventions, template paths, Makefile delegation |
| `projects/ctc-research/AGENTS.md` | CTC Research site structure, template resolution |
| `projects/lms/AGENTS.md` | LMS site conventions, plugins, components |
| `projects/portfolio/AGENTS.md` | VResume site structure, page templates |
| `projects/cypercloud/templates/AGENTS.md` | AI chat customizer conventions |
| `projects/assets/templates/AGENTS.md` | Template organization, resolution order |
| `libs/django-fusion/AGENTS.md` | Component system, routing, canonical imports |
| `libs/ceptor-ai/AGENTS.md` | AI assistant, MCP server, chat client |
| `applications/kilo/AGENTS.md` | Kilo MCP server, tool definitions |

### AGENTS.md Structure Convention

```markdown
# [Section Name] — AI Agent Instructions
## Scope
## Conventions
## Customization Tips
```

---

## Prompt Types

| Type | Used In | Description |
|------|---------|-------------|
| **Chat Prompts** | Cypercloud, POS sidecar | Real-time streaming chat |
| **Agent Prompts** | ceptor-ai MCP | Tool-calling prompts |
| **Code Generation** | Cypercloud Monaco editor | Syntax-aware code synthesis |
| **Translation** | POS i18n audit | Bulk translation prompts |
| **System Prompts** | AGENTS.md files | Per-project behavioral instructions |

### Chat System Prompt Template

```markdown
You are an AI assistant for the Structa Cloud monorepo.
You have access to:
- Django sites: ctc-research, lms, VResume, cypercloud
- Desktop app: POS (Tauri + React + Rust)
- Libraries: django-fusion, ceptor-ai

Answer questions about code, suggest improvements,
and generate code following project conventions.
```

---

## MCP Integration

The [Kilo MCP server](../../applications/kilo/) provides Model Context Protocol tools for AI agents working on this monorepo:

| Tool | Purpose |
|------|---------|
| `search_codebase` | Search for code patterns across the monorepo |
| `read_files` | Read specific source files |
| `run_tests` | Execute test suites |
| `get_docs` | Retrieve documentation |

Ceptor-AI (`libs/ceptor-ai/`) provides the MCP client-side protocol implementation used by Cypercloud.

---

## Best Practices

### For AGENTS.md
- Be **specific** about file paths, import conventions, and naming rules
- Use **examples** of correct and incorrect code
- Reference **actual source files** the agent needs to know about
- Keep prompts **concise** — AI agents have limited context windows

### For Chat Prompts
- Use **streaming** via SSE for real-time UX
- Include **system context** about codebase structure
- Code generation: temperature 0.0–0.3 for deterministic output
- Creative tasks: temperature 0.7+

### For MCP Tools
- Define **clear tool schemas** with required/optional parameters
- Return **structured JSON** for consistent parsing
- Include **error handling** guidance

---

## Related

| Resource | Path |
|----------|------|
| Agent instructions (detail) | [`agents.md`](agents.md) |
| Prompt engineering (detail) | [`prompts.md`](prompts.md) |
| Cypercloud AI chat | [`docs/projects/cypercloud/`](../projects/cypercloud/) |
| Ceptor-AI library | [`libs/`](../libs/) |
| Best practices | [`docs/best-practices/`](../best-practices/) |
