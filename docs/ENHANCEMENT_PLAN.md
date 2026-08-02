# Django-Fusion staged enhancement plan

## Current canonical boundaries

| Area | Canonical ownership | Rule |
|---|---|---|
| Route infrastructure | `django_fusion.routes.core.base` | `Viewset`, `Route`, decorators, descriptors |
| Site/application tree | `django_fusion.routes.core.sites` | `Site`, `Application`, menus |
| Routed components | `django_fusion.routes.components.routable` and `routes.fragments` | `RoutableComponent`, `FragmentComponent` |
| Page views | `django_fusion.routes.pages.views` | Wagtail page-backed views |
| View pipeline | `django_fusion.routes.pages.handler` | `ComponentViews`, `PageHandler`, pagination views |
| Request strategy | `django_fusion.routes.http.detection` | HTMX/fragment strategy detection |
| Context pipeline | `django_fusion.core.context._context_mixins` | Comprehensive `FragmentHandlerMixin` implementation |
| Public context path | `django_fusion.core.context.context` | Direct import of the canonical `FragmentHandlerMixin` |
| HTMX plugin | `django_fusion.plugins.htmx.core` | `is_htmx_request`, fragment predicate, request details |
| Asset configuration | `django_fusion.config.staticfiles` and `config.manifest` | Asset types, collection, normalized manifests |
| Component props | `django_fusion.config.params` | Per-render `Params`, `Param`, and `Value` resolution |
| Component registry | `django_fusion.comp._init` | One canonical component instance per identity |
| Include-path registration | `django_fusion.comp.registry` | Full path identity plus collision-safe optional bare alias |

All runtime imports use these direct canonical modules. No deleted `comp.fragment`
package or legacy redirect module is used. `core/context/context.py` is the
intentional public façade requested for the canonical context API; it is not a
legacy compatibility shim.

## Implemented deduplication contract

1. `Component.identity` is the shared identity used by the registry, render
   metadata, prop resolution, and asset collection.
2. `ComponentRegistry.register()` returns the existing instance for an already
   registered key; repeated renders do not create component nodes.
3. `BoundComponent` receives fresh `Params` for every template node. Prop and
   attribute rendering never mutates the bound parameter lists.
4. `ComponentRenderMetadata` is a frozen, shallowly immutable value object
   that records page path, metadata, resolved props, and component assets for
   the render. Arbitrary `source` and `requested_by` values are retained as
   supplied; callers needing deep immutability should pass stable scalars.
5. Include-path registration shares one instance between the literal path and a
   bare stem only while that stem is unique.
6. When two paths share a stem, the bare alias is removed, invalidated from the
   cache, marked ambiguous, and rejected. Callers must use the full path.
7. Lazy include templates defer template loading until render while preserving
   Django's backend-template interface (`template`, `nodelist`, `origin`, and
   `render`).

## Asset and page/component linkage

The component registry owns component identity. `Component.assets` is collected
once from the canonical template path, while `ComponentRenderMetadata.assets`
provides the per-render link consumed by diagnostics and asset tags. The asset
tag resolves components from the page/template usage map and deduplicates
assets by the immutable `Asset` value.

Page discovery remains in `routes.page_catalog`; it reports included component
paths and sections without constructing duplicate component instances. Future
customizer work should pass page props into the component tag rather than
re-registering components.

## Route organization migration (remaining phase)

The route package is intentionally file-stable in the current dirty submodule.
No physical moves are included in this phase. The next isolated migration
should introduce these subdirectories and update all direct imports in one
commit:

```text
routes/
  core/       base, detection, converters, session, response, renderers
  views/      page_handler, paginators, notifications, generic view mixins
  components/ routed components and fragment components
  pages/      Wagtail page views and page catalog
  sites/      Site/Application viewsets
  models/     model viewsets and CRUD mixins
```

Before moving files, add import-graph tests for every public symbol and verify
that no parent project imports a private module. Do not add re-export shims;
update callers to the new canonical paths and remove the old modules only after
the import graph is green.

## Validation completed for this phase

- Component registry, component tag, and include-path equivalence tests pass.
- Fragment, context, and page-catalog tests pass.
- Python compilation and `git diff --check` pass.
- Remaining import-test failures target pre-existing deleted modules
  (`core.middlewares.error_tracker`, `models.tasks`) or require a full Wagtail
  app configuration; they are tracked separately and are not masked with
  compatibility shims.

## Next priorities

1. Repair stale middleware/service/model imports as a separate cleanup slice.
2. Add the route subdirectory migration with direct-import updates.
3. Add page customizer prop schemas and component asset manifests on top of the
   canonical identity contract.
4. Consolidate plugin diagnostics and add integration tests for HTMX/UnPoly
   response behavior.
