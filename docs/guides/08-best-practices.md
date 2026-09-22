---
title: Best Practices
description: Code conventions and documentation standards for the Structa Cloud monorepo — Python, Rust, TypeScript, Django, SCSS, docs.
navigation:
  title: Best Practices
  icon: i-lucide-check
object:
  type: "guide"
  id: "guide.best-practices"
attributes:
  source_path: "guides/08-best-practices.md"
  canonical_route: "/docs/en/guides/08-best-practices"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - best-practices
  - conventions
  - python
  - rust
  - typescript
  - django
  - scss
links:
  - label: "Clone Site"
    to: "/guides/07-clone-site"
    icon: "i-lucide-package"
  - label: "Docus"
    to: "/guides/09-docus"
    icon: "i-lucide-pencil"
---

# ✅ Best Practices — Code Conventions

> Language-specific conventions and documentation standards for the Structa Cloud monorepo.

---

## Python (Django)

```python
# PEP 8, Black 88-char line length
# Type hints required for public APIs
# django-fusion canonical imports: from django_fusion import fragments, routes, comp, tables
```

- **Imports:** Group stdlib → third-party → local; use `django_fusion.*` canonical imports
- **Models:** Use `django_fusion.models.BaseModel` base; define `class Meta: ordering = ['-created']`
- **Services:** Business logic in `services.py`, not views; use `@transaction.atomic` for writes
- **Migrations:** Never edit generated — `make migrate` then `make makemigrations`
- **Tests:** `pytest` with `pytest-django`; fixtures in `tests/fixtures/`

---

## Rust (POS Backend)

```rust
// 2021 edition, rustfmt, clippy -D warnings
// Diesel for ORM; Tauri for FFI
```

- **Operations:** One file per domain (`operations/products.rs`, `operations/sales.rs`)
- **Commands:** Thin Tauri wrappers → `operations::*` functions
- **DB:** Diesel migrations in `src-tauri/migrations/`; never edit `schema.rs`
- **Error handling:** `Result<T, String>` for commands; `anyhow` for internal
- **Tests:** `cargo test -- --test-threads=1` (env var isolation)

---

## TypeScript (POS Frontend + Astro)

```typescript
// Strict mode, ESLint + Prettier
// Path aliases: @/* → src/*
```

- **Components:** Functional + hooks; `React.FC<Props>` typing
- **API:** `invoke()` for Tauri commands; typed responses via `types/`
- **State:** React Context for auth/theme/i18n; avoid global state
- **i18n:** JSON files in `src/i18n/{en,fr,ar}.json`; use `useTranslation()`

---

## Django (Wagtail + django-fusion)

- **Imports:** `django_fusion.fragments`, `django_fusion.routes`, `django_fusion.comp`, `django_fusion.tables`
- **Models:** Extend `django_fusion.models.BaseModel`; use `StreamField` for content
- **Views:** `PageHandler` for pages; `FragmentView` for HTMX fragments
- **Templates:** `{% comp "name" %}` for components; `{% include_block %}` for StreamField
- **Settings:** `configs/` cascade — base → env → site; never hardcode in `settings.py`

---

## SCSS / CSS (Fusion Design System)

```scss
// tokens: fu-* variables in assets/scss/_tokens.scss
// BEM: block__element--modifier
// No nesting > 3 levels
```

- **Tokens:** Use `fu-*` variables (colors, spacing, typography)
- **Structure:** `_tokens.scss` → `_base.scss` → `_components.scss` → `_utilities.scss`
- **Output:** `assets/static/css/fusion.css` via `make css`
- **No:** custom properties for theming (CSS vars), nesting > 3 levels

---

## TypeScript (Astro Frontend)

- **Components:** `.astro` for islands, `.tsx` for React islands
- **API:** `fetch('/apis/...')` with typed `ApiResponse<T>`
- **Content:** Markdown/MDX in `src/content/` with frontmatter schemas
- **Styling:** Tailwind v4 + fusion tokens via `@import`

---

## Rust (Sidecar)

- **Framework:** Sanic + async/await
- **DB:** Diesel async (if needed) or sync in thread pool
- **Endpoints:** REST + WebSocket; OpenAPI via `utoipa`
- **Config:** `.env` via `config` crate; validated on startup

---

## Documentation (Docus / Markdown)

- **Frontmatter:** `object`, `attributes`, `tags`, `links` required
- **Headers:** Emoji H1 + H2; `## Remarks & Notes` mandatory
- **Code blocks:** Language hints (`python`, `rust`, `bash`, `yaml`, `nginx`)
- **Diagrams:** Mermaid for architecture/ERD
- **Arabic mirror:** Add at `docs/ar-content/<same-path>.md`

---

## Git & PR Hygiene

- **Branches:** `feat/`, `fix/`, `chore/`, `docs/` prefixes
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **PRs:** Link issue; describe what/why; screenshots for UI changes
- **Reviews:** 1 approval minimum; CI must pass

---

## ## Remarks & Notes

- These conventions are living — update when tooling changes (Black, rustfmt, Prettier versions).
- Project-specific conventions override these (see project's `AGENTS.md`).
- New languages/frameworks need a convention section added here.
- Enforcement: `ruff check`, `cargo clippy`, `npx tsc --noEmit`, `npx eslint .` in CI.

---

→ [Back to Guides](README.md) | [Clone Site](07-clone-site.md) | [Docus](09-docus.md)

<!-- AI-generated: review needed -->