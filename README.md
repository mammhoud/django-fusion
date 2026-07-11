# django-fusion

`django-fusion` is a Django + Wagtail helper library that gives you a
**component system, declarative routing, a `{% comp %}` template tag,
forms/tables mixins, allauth auth, and a Wagtail integration layer** —
the toolkit Structa Cloud sites are built on.

It is the merged successor of the previous standalone `django_fusion`
package (shim retained for back-compat, dropped in v0.3.0).

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

pip install -e core/libs/django-fusion
```

To pull the latest lib commit into the monorepo:

```bash
cd core/libs/django-fusion && git pull origin generic && cd ../..
git add core/libs/django-fusion
git commit -m "chore: bump django-fusion submodule"
```

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

## Citation

If you reference `django-fusion` in a project, please cite it as:

> django-fusion — Reusable Django and Wagtail helpers for Structa Cloud sites.
> https://github.com/mammhoud/django-fusion

## License

[MIT](./LICENSE).

## Repository

[https://github.com/mammhoud/django-fusion](https://github.com/mammhoud/django-fusion)
