# Catalog & Django Fusion — landing-fusion

> **Status:** current as of the 2026-08 catalog seed
> **Scope:** the product catalog and its editions, what depends on django-fusion,
> and the Django Fusion guides/references to reach for.

The public structa.cloud site is one catalog document (per
[ADR-0001](./adr/0001-merge-projects-into-products.md), `/projects/` permanently
redirects to `/products/`). Everything below is seeded Wagtail content —
`ProductPage` records with their `Edition` blocks — rendered on both render
roads (see `Render mode` in [CONTEXT.md](../CONTEXT.md)). Glossary terms
(`Product`, `Edition`, `Category`, `Flagship`, `Catalog`) are defined there.

---

## 1 · The product catalog at a glance

| Product (slug) | Category | Editions | Free entry | Paid range | Featured tier |
|---|---|---|---|---|---|
| **Formints** (`formint-pos`) — flagship | application | Community · Standard · Pro · Custom | Community $0 | $119 – $129 | Pro |
| **Precis LMS** (`lms`) | platform | Solo · Standard · Custom | — | $29 – $299 | Standard |
| **Loop** (`cms`) | platform | Community · Standard · Custom | Community $0 | $99 / Custom | Standard |
| **Syntara** (`cypercloud`) | platform | Community · Business | hidden — in development | — | — |
| **vResume** (`vresume`) | platform | Community · Business | Community $0 | $9 | Business |
| **ceptor-ai** (`ceptor-ai`) | library | Open Source | Open Source $0 | — | — |

Rules of the catalog: the **Flagship** (Formints) gets the featured position at
the top; an **Edition** is a priced tier with its own name, price, and feature
set; a product's `featured` edition is the one the pricing section highlights.
ceptor-ai is a **library** (consumed by Syntara's chat client and vResume's
Syntara AI summaries), not a sold product — it ships one Open Source edition.

### Edition detail

**Formints — offline-first POS for one terminal → multi-terminal cloud sync**
(Tauri 2 + Rust core, SQLite, i18n en/fr/ar)

| Edition | Price | Tier | Distinguishing features |
|---|---|---|---|
| Community | $0 | outline | Offline-first single terminal; sales, receipting + inventory; cash/card/split payments; refunds & returns |
| Standard | $119 | default | Everything in Community; F&B menu support, kitchen display + payroll; REST API; inventory + sales analytics; invoice PDFs; loyalty & rewards; multi-currency & tax profiles; custom roles; CSV/JSON export (50% off · launch, was $238) |
| Pro | $129 | featured | Everything in Standard; multi-terminal sync via a cloud master; WebSocket streaming; high-throughput Rust API (50% off · launch, was $258) |
| Custom | Custom | managed | Everything in Pro; hosted cloud CRM master; unlimited terminals; automatic backups + monitoring; dedicated onboarding |

**Precis LMS — learning platform for creators and organizations**

| Edition | Price | Tier | Distinguishing features |
|---|---|---|---|
| Solo | $29 | default | Unlimited courses; certificates; offline downloads; advanced analytics; SSO & role management; dedicated success manager; high-end learning experience design |
| Standard | $299 | featured | Everything in Solo; custom branding; API access; bulk enrollments + cohorts; priority support; advanced analytics (50% off · launch, was $598) |
| Custom | Custom | managed | Everything in Standard; dedicated success manager; managed hosting + backups; custom integrations; SLA + onboarding |

**Loop — Wagtail CMS landing sites, self-hosted or managed**

| Edition | Price | Tier | Distinguishing features |
|---|---|---|---|
| Community | $0 | outline | Wagtail StreamField blocks; django-fusion rendering; HTMX fragments; MIT license |
| Standard | $99 | featured | Everything in Community; custom StreamField blocks; blog + FAQ sections; analytics + SEO; HTMX forms; full GSAP animations |
| Custom | Custom | managed | Everything in Standard; multi-site + roles; dedicated support; managed hosting; custom animations + design |

**Syntara — managed chat client over ceptor-ai (hidden: in development)**

| Edition | Price | Tier | Distinguishing features |
|---|---|---|---|
| Community | $0 | outline | ceptor-ai chat client; MCP server; multi-model support |
| Business | $39 | featured | Everything in Community; branded widget; behavior rules; analytics |

> Syntara is `hidden=True` in the catalog seed: excluded from `/products/`,
> `/pricing/`, the homepage grid, the nav dropdown and `/brand/` boards while
> under development. Its detail page (`/products/cypercloud/`) stays reachable
> by direct link.

**vResume — resume builder**

| Edition | Price | Tier | Distinguishing features |
|---|---|---|---|
| Community | $0 | outline | Modern resume templates; live preview; PDF export |
| Business | $9 | featured | Everything in Community; custom domain; multiple resumes; Syntara AI summaries; analytics |

**ceptor-ai — MCP server + chat client (library)**

| Edition | Price | Tier | Distinguishing features |
|---|---|---|---|
| Open Source | $0 | default | Full MCP server; chat client; BEM converter; agent generation |

---

## 2 · What depends on django-fusion

The dependency is a monorepo submodule: `libs/django-fusion` @ `008bdd8`
(pinned by gitlink — `git add libs/django-fusion` updates it). Both halves of
this project consume it: the backend imports the `django_fusion` Python
package, and the frontend imports the `fusion-js` TypeScript modules behind
the `@fusion` alias.

### Backend — `django_fusion` package

| Surface | Where | What it provides |
|---|---|---|
| Installed app | `backend/settings.py` `INSTALLED_APPS` | The `django_fusion` package + its templates/static |
| Component template tags | `settings.py` `TEMPLATES` → `django_fusion.comp.templatetags.components` | `{% comp %}` / `{% slot %}` / `{% prop %}` / `{% var %}` in every page template |
| Page handlers | `apps/handlers/views.py` — every view subclasses `django_fusion.routes.pages.handler.PageHandler` | The unified fragment/full render pipeline (`FragmentHandlerMixin`): HTMX requests get `pages/fragments/page.html`, plain loads get the full document |
| Routing | `apps/handlers/fusion.py` + `apps/learning/fusion.py` — `Application` + `menu_path` from `django_fusion.routes.core` | The route tables with menu metadata (name/icon/title) that drive the fusion menu system |
| Render mode | `settings.py` `FUSION_RENDER_FIRST_DEFAULT` (+ per-request `X-Fusion-Render-First` header) | The dual-mode contract: `fusion-render` (server HTML) vs `data-api` (JSON for the Astro build) |
| Assets pipeline | `apps/pages/api.py` → `django_fusion.config.assets.get_asset_pipeline_options`; compiled `fusion.css` + components manifest | The design-system stylesheet (`--fu-*` tokens, `.btn-primary`, `.tag-marker`) every template styles against |
| Component registry | `apps/pages/apps.py` → `django_fusion.comp.registry.register_include_paths` | Registers shared component include paths for the `{% comp %}` resolver |
| Introspection | `backend/urls.py` → `django_fusion.plugins.debug_tools.introspection` | The fusion introspection dashboard (plugin map, component usage, render tracker) |

### Frontend — `fusion-js` TS modules

| Surface | Where | What it provides |
|---|---|---|
| `@fusion` alias | `frontend/tsconfig.json` + `astro.config.mjs` → `../../../libs/django-fusion/js/fusion-js/src` | The shared modular TS bundles (htmx wrapper, fragments, SSE, scroll, theme) |
| Project bindings | `frontend/src/fusion/*` (`htmx.ts`, `fragments.ts`, `sse.ts`, `scroll.ts`, `theme.ts`, `index.ts`) | Thin typed re-exports that adapt fusion-js to this Astro app |
| Image build | `frontend/Dockerfile` `COPY libs/django-fusion/js/fusion-js …` | The alias target must exist in the image — this was the build-blocking dependency fixed by pinning the submodule |
| Design tokens | `frontend/src/styles/globals.css` | Mirrors the fusion theme (`--fu-*` custom properties) so both roads share one design language |

**Deleting either half is not optional**: remove the backend `PageHandler`
base and every page route loses its fragment/full dual-mode rendering; remove
the `@fusion` alias and the frontend loses HTMX/SSE/scroll/theme runtime. The
two halves are adapters over one library — the seam is the submodule itself.

---

## 3 · Django Fusion guides & references

The source of truth is the submodule's own doc index (`libs/django-fusion/docs/INDEX.md`,
DF-000), which carries stable `DF-NNN` IDs. The guides most relevant to
landing-fusion:

| Guide | Why this project reaches for it |
|---|---|
| [Getting started (DF-001)](../../../libs/django-fusion/docs/01-getting-started.md) | Install + first `{% comp %}` |
| [Architecture (DF-002)](../../../libs/django-fusion/docs/02-architecture.md) | The dual-mode render pipeline this site is built on |
| [Component system (DF-003)](../../../libs/django-fusion/docs/03-component-system.md) | Python-side component registry, `register_include_paths` |
| [`{% comp %}` tag (DF-004)](../../../libs/django-fusion/docs/04-component-tag.md) | The template tag every page template uses |
| [Routing (DF-005)](../../../libs/django-fusion/docs/05-routing.md) | `Application` / `PageHandler` / `menu_path` — the route tables in `apps/handlers/fusion.py` |
| [Configuration (DF-007)](../../../libs/django-fusion/docs/07-configuration.md) | `FUSION_RENDER_FIRST_DEFAULT` and friends |
| [API reference (DF-008)](../../../libs/django-fusion/docs/08-api-reference.md) | Docstring-generated reference for `django_fusion.*` |
| [Wagtail integration (DF-010)](../../../libs/django-fusion/docs/10-wagtail-integration.md) | StreamField blocks + snippets — how content becomes pages |
| [Best practices (DF-011)](../../../libs/django-fusion/docs/11-best-practices.md) | Patterns mined from the component case studies |
| [Integration examples (DF-012)](../../../libs/django-fusion/docs/12-integration-examples.md) | End-to-end walkthroughs of real integration shapes |
| [Troubleshooting (DF-013)](../../../libs/django-fusion/docs/13-troubleshooting.md) | Symptom → cause → fix entries |
| [FAQ (DF-014)](../../../libs/django-fusion/docs/14-faq.md) | Answers mined from real edge cases |
| [Assets (DF-016)](../../../libs/django-fusion/docs/16-assets.md) | The assets pipeline behind `fusion.css` + the components manifest |
| [Integration modes (DF-017)](../../../libs/django-fusion/docs/17-integration-modes.md) | Webpack/template/API modes — the render-mode contract |
| [Component case studies](../../../libs/django-fusion/docs/COMPONENT_CASE_STUDIES.md) | Long-form per-component references |

Also: [QUICKSTART.md](../../../libs/django-fusion/QUICKSTART.md) for the
fastest path to a working site, and
[CHANGELOG.md](../../../libs/django-fusion/CHANGELOG.md) before bumping the
submodule pointer. When something behaves unexpectedly on either road, start
at DF-013 (troubleshooting) with the DF-ID of the surface you touched —
routing (DF-005), comp tag (DF-004), or assets (DF-016).
