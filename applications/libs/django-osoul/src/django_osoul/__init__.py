"""django-osoul — reusable Django and Wagtail helpers for Structa Cloud sites.

Package layout
--------------
django_osoul.analyzer       Template scanner and component analyzer app.
django_osoul.comp           Server-side component system (slots, props, HTMX loaders).
  .routes                   URL route builders: model, fragment, component, site.
  .generic                  Generic CBVs: list, create, update, delete, search.
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
django_osoul.site           Site layer — pagination, context, auth.
  .adapters                 Site-level allauth adapter.
  .auth                     Auth forms, role/token models, allauth adapters.
  .choices                  Choice enums: cart, contact, message, styles, token.
  .context                  Context processors: auth, cookies, HTMX, languages.
  .enums                    Environment and upload enums.
  .responses                HTTP response helpers and exception schemas.
  .schemas                  Pydantic response schemas, serializers, user schemas.
  .views                    Site-level views: notifications, tag management.
django_osoul.comp.templatetags.include_bridge  Bridge tag: {% comp_include %} for include→comp migration.
django_osoul.wagtail        Wagtail integration: blocks, snippets, viewsets.
django_osoul.web            Web layer: allauth adapters, auth backends, view mixins.
  .adapters                 django-allauth account and social adapters.
  .backends                 Custom authentication backends.
  .views                    FilterMixin, SearchMixin for class-based views.

Canonical import paths
-----------------------
Routing:      from django_osoul.comp.routes import Viewset, Site, ...
Generic CBVs: from django_osoul.comp.generic import ListModelView, ...
Handlers:     from django_osoul.core.handlers import ...
Managers:     from django_osoul.core.managers import ...
Models:       from django_osoul.core.models import ...
Services:     from django_osoul.core.services import ...
Views:        from django_osoul.web.views import ...
Loaders:      from django_osoul.comp.loaders import ...
Middlewares:  from django_osoul.core.middlewares import ...
Cache:        from django_osoul.core.cache import ...
"""

__version__ = "0.1.0"
