# Libs — Local Reusable Libraries

> **Related Names:** `django-fusion`, `ceptor-ai`, `component system`, `AI assistant`, `MCP server`, `routing framework`
> **Tags:** #project #libs #django-fusion #ceptor-ai #libraries #components

**Canonical path:** `libs/`

---

## Overview

The `libs/` directory contains two local reusable Python libraries developed alongside the Structa Cloud monorepo. They are installed as editable packages via Git submodules and are consumed by all Django sites.

| Library | Path | Purpose |
|---------|------|---------|
| **django-fusion** | `libs/django-fusion/` | Component system, routing framework, viewset infrastructure |
| **ceptor-ai** | `libs/ceptor-ai/` | AI assistant core, MCP server protocol, multi-model chat |

---

## Guide

### Installation

```bash
# Initialize submodules (required after clone)
git submodule update --init --recursive

# Install as editable packages
uv pip install -e libs/django-fusion/
uv pip install -e libs/ceptor-ai/
```

### Updating

```bash
git submodule update --remote libs/django-fusion
git submodule update --remote libs/ceptor-ai
```

### Testing

```bash
# django-fusion test suite
cd libs/django-fusion
pytest tests/

# ceptor-ai test suite
cd libs/ceptor-ai
pytest tests/
```

---

## Code Map

### django-fusion

| Path | Purpose | Customization |
|------|---------|:---:|
| `django-fusion/src/django_fusion/comp/routes.py` | Route definitions, Viewset, Site, Application, Fragment components | 🟡 delegate |
| `django-fusion/src/django_fusion/comp/generic.py` | Generic CBVs: Create, Read, Update, Delete, List views | 🟡 delegate |
| `django-fusion/src/django_fusion/comp/loaders.py` | Template loaders and component resolution | 🔴 not-customizable |
| `django-fusion/src/django_fusion/comp/registry.py` | Component registry, include-path registration | 🔴 not-customizable |
| `django-fusion/src/django_fusion/core/handlers.py` | Page handler base classes | 🟡 delegate |
| `django-fusion/src/django_fusion/core/managers.py` | Model managers | 🔴 not-customizable |
| `django-fusion/src/django_fusion/core/models.py` | Core mixins and abstract models | 🟡 delegate |
| `django-fusion/src/django_fusion/core/services.py` | Business logic service layer | 🟡 delegate |
| `django-fusion/src/django_fusion/web/views.py` | FilterMixin, SearchMixin | 🟡 delegate |
| `django-fusion/src/django_fusion/core/cache.py` | Cache utilities | 🔴 not-customizable |

### ceptor-ai

| Path | Purpose | Customization |
|------|---------|:---:|
| `ceptor-ai/src/ceptor_ai/chat/client.py` | Chat client (multi-model: Ollama, OpenAI, Anthropic, Gemini) | 🟢 customizable |
| `ceptor-ai/src/ceptor_ai/chat/bubble.py` | Chat bubble UI component (rendered via `ChatBubble`) | 🟢 customizable |
| `ceptor-ai/src/ceptor_ai/mcp/` | MCP (Model Context Protocol) server implementation | 🔴 not-customizable |
| `ceptor-ai/configs/` | Agent configuration presets | 🟢 customizable |
| `ceptor-ai/kilo.jsonc` | Kilo MCP server configuration | 🟢 customizable |

---

## Remarks

| # | Note |
|---|------|
| ⚠️ | Both libraries are **Git submodules**. If you get `ImportError` after cloning, you forgot `git submodule update --init --recursive`. |
| 💡 | Use **canonical import paths** — no re-export shims remain. Import from `django_fusion.comp.routes` directly, not from compatibility wrappers. |
| 🔌 | The `django-fusion` component system uses dot notation: `{% comp "contact.sections.form" %}` |
| 📦 | Optional dependencies: `django-fusion[dev]` for testing, `ceptor-ai[mcp]` for MCP protocol support, `ceptor-ai[test]` for test utilities |

---

## Customization Key

| Tag | Scope | What it means here |
|-----|-------|-------------------|
| 🟢 `customizable` | Consumer code | Add new components, extend viewsets, configure AI agents — use the public API |
| 🟡 `delegate` | Extension hooks | Subclass `ModelViewset`, implement custom `PageHandler`, add new chat client providers |
| 🔴 `not-customizable` | Framework core | Registry, loaders, MCP protocol — modify through public API only |
| ⚪ `config` | Environment | AI model selection, agent configs, Kilo MCP settings |

---

## Related Documentation

| Resource | Path |
|----------|------|
| django-fusion docs | [`django-fusion.md`](django-fusion.md) |
| django-fusion README | [GitHub](https://github.com/mammhoud/django-fusion) |
| ceptor-ai README | [GitHub](https://github.com/mammhoud/ceptor-ai) |
| Component system guides | [`django-tags.md`](django-tags.md) |
| Configuration | [`configuration.md`](configuration.md) |
