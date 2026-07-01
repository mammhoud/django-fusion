"""django-osoul — reusable Django and Wagtail helpers for Structa Cloud sites.

Package layout
--------------
django_osoul.analyzer       Template scanner and component analyzer app.
django_osoul.comp           Server-side component system (slots, props, HTMX loaders).
  .configuration            Component manifest, options, and config schema.
  .core                     Component bootstrap and lifecycle.
  .forms                    Form layout helpers for component rendering.
  .loaders                  Lazy/HTMX-safe ``component_loader`` decorator.
  .payloads                 JSON payload service for HTMX component responses.
  .plugins                  Pluggy-based hook system for extending components.
  .static                   Static file discovery and asset manifest helpers.
  .templates                Template discovery, URL routing, and rendering engine.
  .templatetags             ``comp``, ``slot``, ``prop``, ``var``, ``css``, ``js``,
                            plus UI tags: card, field, menu, modal, table.
django_osoul.config         Package-level configuration constants and conf helpers.
django_osoul.contrib        Shared admin, cache utils, debug tools, and privacy helpers.
  .admin                    Custom admin site and Wagtail admin hooks.
  .cache                    Cache utility functions for views and managers.
  .debug_tools              Dev-only tools: autoreload, monitoring, Sentry, Prometheus.
  .email_config             Email configuration helpers.
  .privacy                  Privacy middleware and consent helpers.
django_osoul.core           Foundational layer — models, managers, services, utils.
  .cache                    Pluggable cache manager base classes.
  .filters                  Queryset filters: token, revision, cache-aware.
  .handlers                 View handler base classes and HTMX fragment mixins.
  .managers                 Model managers: role hierarchy, group access, tags, user.
  .middlewares              Middleware: error tracker, privacy, language, freeze.
  .models                   Base models, auth, email, interaction models.
  .services                 Service layer: CRUD base, cart, person.
  .utils                    Utilities: data, formatting, security.
django_osoul.health         Lightweight health-check endpoint.
django_osoul.infrastructure Locale, management command base, scripts, template tags.
django_osoul.middlewares    → compat shim for django_osoul.core.middlewares
django_osoul.routes         Route builder helpers (also at site.routes).
django_osoul.site           Site layer — pagination, context, auth, generic views.
  .adapters                 Site-level allauth adapter.
  .auth                     Auth forms, role/token models, allauth adapters.
  .choices                  Choice enums: cart, contact, message, styles, token.
  .context                  Context processors: auth, cookies, HTMX, languages.
  .enums                    Environment and upload enums.
  .generic                  Generic CBVs: list, create, update, delete, search.
  .responses                HTTP response helpers and exception schemas.
  .routes                   URL route builders: model, fragment, component, site.
  .schemas                  Pydantic response schemas, serializers, user schemas.
  .views                    Site-level views: notifications, tag management.
django_osoul.smart_loader   → compat shim for django_osoul.comp.loaders
django_osoul.wagtail        Wagtail integration: blocks, snippets, viewsets.
django_osoul.web            Web layer: allauth adapters, auth backends, view mixins.
  .adapters                 django-allauth account and social adapters.
  .backends                 Custom authentication backends.
  .views                    FilterMixin, SearchMixin for class-based views.

Deprecated paths (compat shims kept for backward compatibility)
---------------------------------------------------------------
django_osoul.cache          -> django_osoul.core.cache
django_osoul.middlewares    -> django_osoul.core.middlewares
django_osoul.smart_loader   -> django_osoul.comp.loaders
django_osoul.handlers       -> django_osoul.core.handlers  (compat re-export)
django_osoul.managers       -> django_osoul.core.managers  (compat re-export)
django_osoul.models         -> django_osoul.core.models    (compat re-export)
django_osoul.services       -> django_osoul.core.services  (compat re-export)
django_osoul.views          -> django_osoul.web.views      (compat re-export)
"""

__version__ = "0.1.0"
