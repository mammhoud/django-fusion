# django-fusion

`django-fusion` is a Django + Wagtail helper library that gives you a
**component system, declarative routing, a `{% comp %}` template tag,
forms/tables mixins, allauth auth, and a Wagtail integration layer** —
the toolkit Structa Cloud sites are built on.

It is the canonical `django_fusion` package. Import framework symbols from
`django_fusion.*` directly; the former standalone compatibility package is no
longer part of the supported runtime.

## What it gives you

- **`{% comp %}` template tag** with `{% prop %}`, `{% slot %}`,
  `{% var %}`, `{{ props.* }}`, `{{ attrs }}`, and `fragment_name=` for
  HTMX scoping. Comparable to django-bird / django-cotton, but pure
  Django template syntax. ([DF-004](./docs/04-component-tag.md))

- **Routing helpers** — `Site`, `Application`, `Viewset`,
  `ModelViewset` (CRUD from one class), `RoutableComponent`,
  `FragmentComponent`, `FragmentDetector`. ([DF-005](./docs/05-routing.md))

- **Forms & tables** — `FormMixin`, `TableMixin`, `FormTableMixin`
  with a template-resolution cascade. ([DF-006](./docs/06-forms-and-tables.md))

- **Component analyzer** — scan templates for `{% comp %}` usage and
  emit JSON tracking. ([DF-003](./docs/03-component-system.md))

- **Allauth auth layer** — adapters, mixins, social signup. ([:DF-002](./docs/02-architecture.md))

- **Wagtail integration** — StreamField blocks, snippets, viewsets. ([DF-010](./docs/10-wagtail-integration.md))

- **Health checks** — `/health/`, `/health/db/`, `/health/assets/`.
  ([DF-009](./docs/09-health.md))

- **Dynaconf multi-environment YAML config** + privacy/cache/middleware
  helpers in `contrib/`. ([DF-007](./docs/07-configuration.md))

## Quick start (standalone project)

```bash
pip install django-fusion
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_fusion.comp",
    "django_fusion.core",
    "django_fusion.health",          # optional
    "django_fusion.analyzer",        # optional
    "django_fusion.config",
]
```

Render your first component:

```django
{% comp "components/button.html" label="Save" variant="primary" / %}
```

The full walkthrough — including middleware ordering and template-tag
builtins — is in [**DF-001 Getting Started**](./docs/01-getting-started.md).

## Install (Structa Cloud monorepo, editable submodule)

In the Structa Cloud monorepo, `django-fusion` lives as a submodule:

```bash
git clone https://github.com/structa-cloud/structa.cloud.git
cd structa.cloud
git submodule update --init --recursive

pip install -e projects/libs/django-fusion
```

To pull the latest lib commit into the monorepo:

```bash
cd projects/libs/django-fusion && git pull origin generic && cd ../..
git add projects/libs/django-fusion
git commit -m "chore: bump django-fusion submodule"
```

## Building Component Assets (Webpack)

`django-fusion` ships a **Webpack 5 build pipeline** for its component SCSS
and JS assets. The pipeline produces a single `fusion` bundle consumed by
django-webpack-loader (`{% render_bundle 'fusion' %}`).

### Quick start

```bash
cd libs/django-fusion
make build              # Full production build (install + webpack --mode production)
```

This outputs:

```
static/bundles/fusion.<hash>.css   # Compiled component styles (~28 KB)
static/bundles/fusion.<hash>.js    # Component JS entry (empty for now)
webpack-stats.json                 # Read by django-webpack-loader
```

### Available targets (`make`)

| Target | Description |
|--------|-------------|
| `make build` | Production build (content-hashed filenames, minified) |
| `make dev` | Dev build (fast, no minification, source maps) |
| `make watch` | Dev + file watcher for live reload |
| `make clean` | Remove all generated assets |
| `make info` | Show pipeline info and file listing |
| `make reinstall` | Force reinstall npm dependencies |

### Manual (without Makefile)

```bash
npm install
npm run build       # Production
npm run dev         # Development
npm run watch       # Dev + watcher
npm run clean       # Remove generated files
```

### What gets bundled

The entry point (`src/django_fusion/assets/entry.js`) imports
`fusion.scss`, which in turn imports:

```
assets/variables/    → Design tokens (colors, typography, spacing)
assets/base/         → Component reset + print styles
comp/*/              → Per-component SCSS (button, card, modal, form, table, nav)
assets/utilities/    → Spacing & typography utility classes
templates/fusion/    → Layout grid for base.html / base_fragment.html
```

### Django integration

Install with webpack support:

```bash
pip install django-fusion[webpack]
```

Then in your Django template:

```django
{% load render_bundle from webpack_loader %}
{% render_bundle 'fusion' 'css' %}
{% render_bundle 'fusion' 'js' %}
```

For Next.js projects, use the `FUSION_ASSETS` endpoint instead:

```tsx
// FusionAssets component calls /api/fusion/assets/manifest/
<FusionAssets />
```

### Pipeline files

| File | Purpose |
|------|---------|
| `webpack.config.js` | Webpack 5 config (137 lines) |
| `package.json` | Dependencies & scripts |
| `Makefile` | Build targets |
| `src/django_fusion/assets/entry.js` | JS entry point |
| `src/django_fusion/assets/fusion.scss` | SCSS entry point |
| `src/django_fusion/assets/variables/` | Design token SCSS partials |
| `src/django_fusion/assets/base/` | Reset & print SCSS partials |
| `src/django_fusion/assets/utilities/` | Utility class SCSS partials |
| `src/django_fusion/comp/*/_*.scss` | Per-component SCSS partials |
| `src/django_fusion/templates/fusion/_layout.scss` | Layout styles |

---

## Documentation

The complete library documentation lives under [`docs/`](./docs/INDEX.md) and
is numbered with stable `DF-0NN` IDs.

| ID | Topic | File |
|----|-------|------|
| [DF-001](./docs/01-getting-started.md) | Getting started | `docs/01-getting-started.md` |
| [DF-002](./docs/02-architecture.md) | Architecture overview | `docs/02-architecture.md` |
| [DF-003](./docs/03-component-system.md) | Component system (Python) | `docs/03-component-system.md` |
| [DF-004](./docs/04-component-tag.md) | `{% comp %}` template tag | `docs/04-component-tag.md` |
| [DF-005](./docs/05-routing.md) | Routing & viewsets | `docs/05-routing.md` |
| [DF-006](./docs/06-forms-and-tables.md) | Forms & tables | `docs/06-forms-and-tables.md` |
| [DF-007](./docs/07-configuration.md) | Settings & configuration | `docs/07-configuration.md` |
| [DF-008](./docs/08-api-reference.md) | API reference | `docs/08-api-reference.md` |
| [DF-009](./docs/09-health.md) | Health checks | `docs/09-health.md` |
| [DF-010](./docs/10-wagtail-integration.md) | Wagtail integration | `docs/10-wagtail-integration.md` |
| [DF-011](./docs/11-best-practices.md) | Best practices | `docs/11-best-practices.md` |
| [DF-012](./docs/12-integration-examples.md) | Integration examples | `docs/12-integration-examples.md` |
| [DF-013](./docs/13-troubleshooting.md) | Troubleshooting | `docs/13-troubleshooting.md` |
| [DF-014](./docs/14-faq.md) | FAQ | `docs/14-faq.md` |
| [DF-015](./docs/15-viewflow-mapping.md) | Viewflow / django-material mapping | `docs/15-viewflow-mapping.md` |
| [DF-016](./docs/16-assets.md) | Asset pipeline & webpack | `docs/16-assets.md` |
| [DF-017](./docs/17-integration-modes.md) | Integration modes and project organization | `docs/17-integration-modes.md` |

## Citation

If you reference `django-fusion` in a project, please cite it as:

> django-fusion — Reusable Django and Wagtail helpers for Structa Cloud sites.
> https://github.com/mammhoud/django-fusion

## License

[MIT](./LICENSE).

## Repository

[https://github.com/mammhoud/django-fusion](https://github.com/mammhoud/django-fusion)
# @tested django-fusion v0.2.0 - Built and tested with pytest (63+ tests), hypothesis property-based testing, Django 4.2/5.0 on Python 3.11/3.12
