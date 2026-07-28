# VResume — Portfolio Deep Dive

> **Related Code**
> * **Domain:** Site (Portfolio Application)
> * **Paths:**
>   * `applications/VResume/www/pages/routable_components.py` (`PortfolioApp`, `ProjectList`, `ProjectDetail`)
>   * `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` (referenced by this doc; now mirrored at [`../../libs/django-fusion/ROUTING_SYSTEM.md`](../../libs/django-fusion/ROUTING_SYSTEM.md))
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/components.py`
> * **Classes:** `RoutableComponent`, `ProjectList`, `ProjectDetail`, `Application(name="portfolio", components=[ProjectList, ProjectDetail])`

The Portfolio Application demonstrates the canonical "list + detail" pattern using `RoutableComponent`. It treats projects as a virtual model not bridged to a Django model class — the route handlers return SimpleNamespace-shaped data so the templates render identically to a Wagtail Page-derived surface.

## Routes

| URL                        | Component       | Method          | Template                              |
|----------------------------|-----------------|-----------------|---------------------------------------|
| `/portfolio/`              | `ProjectList`   | `RoutableComponent.render_list`  | `portfolio/sections/projects.html` |
| `/portfolio/<int:id>/`     | `ProjectDetail` | `RoutableComponent.render_detail`| `portfolio/sections/project_detail.html` |

## Patterns applied

* **Class-as-object-arg:** `PortfolioApp(self.ProjectList(), self.ProjectDetail())` registers children idiomatically.
* **Auto app_name derivation:** `PortfolioApp` derives `app_name = "portfolio"` from the class name (no explicit override needed).
* **`@viewprop` for viewsets:** projects are pre-computed viewset list (since they're static + not tied to a model manager).
* **fragment_name:** `ProjectList.fragment_name = "portfolio.fragments.projects_grid"` so HTMX swaps land the right partial.

## Worked example — project detail

```python
class ProjectDetail(RoutableComponent):
    route_name = "portfolio-detail"
    route_path = "<int:id>/"
    fragment_name = "portfolio.fragments.project_detail"

    def get_context_data(self, **kwargs):
        project = next((p for p in PROJECTS if p["id"] == kwargs["id"]), None)
        if not project:
            raise Http404
        return {"project": project, "block": self}
```

The detail view returns a flat dict; the canonical `applications/assets/templates/components/portfolio/sections/project_detail.html` template then renders it without needing Wagtail Page plumbing.

## Best practices

1. **Don't duplicate CMS state** — if a project needs editor-driven content, prefer a Wagtail Page model under `applications/VResume/<project>/models.py` instead. Reserve this Application for read-only, hardcoded portfolio entries.
2. **Use `RoutableComponent.fragment_name`** for HTMX fragments so Unpoly / HTMX swap targets land correctly.
3. **Always run the analyzer** (`docs/development/analyzer.md`) on a portfolio.html change to verify expected `sections` are emitted.

## See also

* [`index.md`](index.md) — VResume site overview.
* [`../shared_lms.md`](../shared_lms.md) — comparison with LMS Application patterns.
* [`../../architecture/routable_applications.md`](../../reference/architecture/routable_applications.md) — Application-level conventions.
