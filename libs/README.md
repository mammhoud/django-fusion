# Structa Cloud — Libraries

> Reusable Python packages that power every Structa Cloud project. Each is a
> git submodule with its own CI, tests, and documentation.

---

## Library Catalog

| Library | Submodule | Description | Key Docs |
|---------|-----------|-------------|----------|
| **django-fusion** | [`django-fusion`](./django-fusion/) | Component system, routing, forms/tables, auth, Wagtail blocks | [`AGENTS.md`](./django-fusion/AGENTS.md) |
| **ceptor-ai** | `ceptor-ai` (pending) | AI chat client, MCP server, BEM converter, agent generation | `ceptor-ai/AGENTS.md` |
| **django-bolt** | `django-bolt` (pending) | High-performance Rust-backed API framework (BoltAPI) | `django-bolt/README.md` |

> **Note:** `ceptor-ai` and `django-bolt` are referenced throughout the codebase but
> are managed as separate repositories. Initialize them when needed:
> ```bash
> git submodule add https://github.com/mammhoud/ceptor-ai.git libs/ceptor-ai
> git submodule add https://github.com/mammhoud/django-bolt.git libs/django-bolt
> git submodule update --init --recursive
> ```

---

## django-fusion

The canonical component system and routing framework. Every Structa Cloud
Django site uses it for:

- **`{% comp %}` template tag** — component rendering with props, slots, and HTMX scoping
- **Routing** — `Site`, `Application`, `Viewset`, `ModelViewset` (CRUD from one class)
- **Forms & Tables** — `FormMixin`, `TableMixin`, `FormTableMixin` with template resolution
- **Wagtail integration** — StreamField blocks, snippets, admin viewsets
- **Health checks** — `/health/`, `/health/db/`, `/health/assets/`

### Quick Reference

```python
# Install
pip install django-fusion

# Import (canonical paths)
from django_fusion.routes.core.base import Viewset
from django_fusion.routes.models.crud import ModelViewset
from django_fusion.routes.core.sites import Module, Application
from django_fusion.comp.generic import ListModelView, CreateModelView

# Template
{% comp "components/button.html" label="Save" / %}
```

📖 Full docs: [`django-fusion/README.md`](./django-fusion/README.md) |
[DF-001 Getting Started](./django-fusion/docs/01-getting-started.md)

---

## ceptor-ai

AI chat client + MCP (Model Context Protocol) server. Powers the Syntara chat
customizer platform and agent tooling across the monorepo.

- **MCP Server** — agent communication protocol for LLM tool integration
- **Chat Client** — multi-model support with streaming
- **BEM Converter** — prompt-to-component CSS generation
- **Agent Generation** — scaffold AI agents from templates

📖 External: [github.com/mammhoud/ceptor-ai](https://github.com/mammhoud/ceptor-ai)

---

## django-bolt

High-performance Rust-backed API framework (`BoltAPI`). Provides a
lightning-fast REST layer for Django applications.

- **Rust core** — 60k+ RPS throughput
- **Django integration** — auto-generated API endpoints from models
- **Type-safe** — Pydantic schema generation

📖 External: [github.com/dj-bolt/django-bolt](https://github.com/dj-bolt/django-bolt)

---

## Working with Submodules

```bash
# Init all submodules
git submodule update --init --recursive

# Update to latest
cd libs/django-fusion && git pull origin generic

# Push a lib change
make push-lib LIB=django-fusion

# Add a new submodule
git submodule add <url> libs/<name>
```

---

## Cross-References

| Topic | Link |
|-------|------|
| Monorepo AGENTS.md | [`../AGENTS.md`](../AGENTS.md) |
| docs/ README | [`../docs/README.md`](../docs/README.md) |
| Landing-Fusion | [`../projects/precis/precis-landing/README.md`](../projects/precis/precis-landing/README.md) |
| Precis LMS | [`../projects/precis/precis-lms/README.md`](../projects/precis/precis-lms/README.md) |
