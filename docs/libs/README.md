# Libraries — Overview

> Reusable Python packages powering every Structa Cloud project.

---

## Library Catalog

| Library | Source | Docs |
|---------|--------|------|
| **django-fusion** | `libs/django-fusion/` | [`AGENTS.md`](../../../libs/django-fusion/AGENTS.md) |
| **ceptor-ai** | `libs/ceptor-ai/` (pending) | External repo |
| **django-bolt** | `libs/django-bolt/` (pending) | External repo |

---

## django-fusion

The canonical component system and routing framework. Features:
- `{% comp %}` template tag with props, slots, HTMX scoping
- `Site`, `Application`, `Viewset`, `ModelViewset` routing
- `FormMixin`, `TableMixin`, `FormTableMixin`
- Wagtail StreamField blocks, snippets, viewsets
- Health checks (`/health/`)

📖 Full docs: [`libs/django-fusion/README.md`](../../../libs/django-fusion/README.md)
📖 Language contract: [`django-fusion-language.md`](django-fusion-language.md)

---

## ceptor-ai

AI chat client + MCP server. Powers Syntara (the AI chat customizer).

📖 External: [github.com/mammhoud/ceptor-ai](https://github.com/mammhoud/ceptor-ai)

---

## django-bolt

High-performance Rust-backed API framework. 60k+ RPS throughput.

📖 External: [github.com/dj-bolt/django-bolt](https://github.com/dj-bolt/django-bolt)

---

## Cross-References

| Topic | Link |
|-------|------|
| Precis Landing | [`../precis/precis-landing/README.md`](../precis/precis-landing/README.md) |
| Precis LMS | [`../precis/README.md`](../precis/README.md) |
| Formints POS | [`../pos/README.md`](../pos/README.md) |
| Infrastructure | [`../../infrastructure/`](../../infrastructure/) |
