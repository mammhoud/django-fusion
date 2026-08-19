# Syntara — AI Chat Customizer

> **Related Names:** `cypercloud.localhost`, `AI chat`, `template customizer`, `ceptor-ai`, `Ollama`, `OpenAI`, `Claude`, `Gemini`
> **Tags:** #site #cypercloud #ai #chat #customizer

**Canonical path:** `projects/syntara/`  
**Domain:** localhost (default: cypercloud.localhost)  
**Port:** 5073  
**Stack:** Django 4.2+ · Webpack + SCSS · HTMX · Monaco Editor

---

## Overview

Syntara (formerly Tinker/Customizer) is an AI-powered chat and template customization tool. It provides a chat interface backed by multiple AI models (Ollama, OpenAI, Claude, Gemini) with multi-site template discovery for CTC Research, LMS, and VResume.

---

## Guide

### Development

```bash
cd projects/syntara

# Dev server
make run                    # Django dev server on :5073

# Docker
make docker-run             # Run in Docker container

# Production
make build                  # Build frontend assets
make deploy                 # Full: build → collectstatic → migrate
```

### Common Makefile Commands

| Command | Description |
|---------|-------------|
| `make run` | Run Django dev server on :5073 |
| `make check` | Django system checks |
| `make migrate` | Apply pending migrations |
| `make shell` | Django shell (shell_plus) |
| `make collectstatic` | Collect static files |
| `make build` | Build frontend assets (webpack) |
| `make docker-run` | Start Docker container |
| `make docker-down` | Stop Docker container |
| `make deploy` | Full deploy (build → collectstatic → migrate) |

---

## Code Map

### Key Files

| Path | Purpose | Customization |
|------|---------|:---:|
| `cypercloud/settings.py` | Site Django settings | ⚪ config-only |
| `cypercloud/server.py` | ASGI/WSGI application entry point | 🔴 not-customizable |
| `cypercloud/Makefile` | Site-specific commands | 🟢 customizable |
| `cypercloud/assets/static/styles/` | SCSS stylesheets (chat, editor, layout, input, navigation) | 🟢 customizable |
| `cypercloud/assets/static/scripts/` | Frontend JS (chat, editor, HTMX integration) | 🟢 customizable |
| `cypercloud/www/` | Django apps for chat, template discovery, agent config | 🟢 customizable |
| `cypercloud/templates/` | Django/Wagtail templates | 🔵 template |
| `cypercloud/plugins/` | Site plugins | 🟢 customizable |

---

## Remarks

| # | Note |
|---|------|
| ⚠️ | Copy `.env.example` to `.env` and set at minimum `CYPERCLOUD_SECRET_KEY` and `OLLAMA_BASE_URL` |
| 💡 | Supports **4 AI backends**: Ollama (local), OpenAI, Anthropic Claude, Google Gemini — configure via env vars |
| 🔌 | The **Monaco Editor** integration enables code editing with syntax highlighting and markdown rendering |
| 🔗 | Template discovery scans templates across CTC Research, LMS, and VResume sites |
| 🤖 | AI framework uses **Ceptor-AI** (MCP protocol) for tool execution and agent configuration |

---

## Customization Key

| Tag | Scope | What it means here |
|-----|-------|-------------------|
| 🟢 `customizable` | Templates & styles | Edit SCSS, frontend JS, Django templates, chat UI components |
| 🟡 `delegate` | AI backends | Add new AI model providers via Ceptor-AI agent configuration |
| 🔴 `not-customizable` | Core infra | `settings.py` structure, WSGI entry point |
| 🔵 `template` | Templates | Override Django/Wagtail templates in site `templates/` dir |
| ⚪ `config` | Settings | AI model selection, API keys, allowed hosts via env vars |

---

## Related Documentation

| Resource | Path |
|----------|------|
| Syntara strategy 🔒 | [`../startup/syntara.md`](../startup/syntara.md) |
| Full portfolio strategy 🔒 | [`../startup/STRATEGY.md`](../startup/STRATEGY.md) |
| Syntara config | [`configuration.md`](configuration.md) |
| Backend environment | [`../../back-env/`](../../back-env/) |
| Ceptor-AI library | [`../libs/README.md`](../libs/README.md) |
| AI & Agents | [`../../ai/`](../../ai/) |
