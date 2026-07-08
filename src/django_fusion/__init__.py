"""django-fusion — reusable Django and Wagtail helpers for Structa Cloud sites.

Package layout
--------------
django_fusion.analyzer       Template scanner and component analyzer app.
django_fusion.comp           Server-side component system (slots, props, HTMX loaders).
  .cache                    Redis-backed component mapping cache with fallback.
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
django_fusion.config         Package-level configuration constants and conf helpers.
  .dynaconf_loader          Multi-environment YAML configuration with Dynaconf.
django_fusion.contrib        Shared admin, cache utils, debug tools, and privacy helpers.
  .admin                    Custom admin site and Wagtail admin hooks.
  .cache                    Cache utility functions for views and managers.
  .debug_tools              Dev-only tools: autoreload, monitoring, Sentry, Prometheus.
  .email_config             Email configuration helpers.
  .privacy                  Privacy middleware and consent helpers.
django_fusion.core           Foundational layer — models, managers, services, utils.
  .cache                    Pluggable cache manager base classes.
  .filters                  Queryset filters: token, revision, cache-aware.
  .handlers                 View handler base classes and HTMX fragment mixins.
  .managers                 Model managers: role hierarchy, group access, tags, user.
  .middlewares              Middleware: error tracker, privacy, language, freeze.
  .models                   Base models, auth, email, interaction models.
  .services                 Service layer: CRUD base, cart, person.
  .utils                    Utilities: data, formatting, security.
django_fusion.health         Lightweight health-check endpoint.
django_fusion.infrastructure Locale, management command base, scripts, template tags.
django_fusion.site           Site layer — pagination, context, auth.
  .adapters                 Site-level allauth adapter.
  .auth                     Auth forms, role/token models, allauth adapters.
  .choices                  Choice enums: cart, contact, message, styles, token.
  .context                  Context processors: auth, cookies, HTMX, languages.
  .enums                    Environment and upload enums.
  .responses                HTTP response helpers and exception schemas.
  .schemas                  Pydantic response schemas, serializers, user schemas.
  .views                    Site-level views: notifications, tag management.
django_fusion.wagtail        Wagtail integration: blocks, snippets, viewsets.
django_fusion.web            Web layer: allauth adapters, auth backends, view mixins.
  .adapters                 django-allauth account and social adapters.
  .backends                 Custom authentication backends.
  .views                    FilterMixin, SearchMixin for class-based views.

Canonical import paths
-----------------------
Routing:           from django_fusion.comp.routes import Viewset, Site, ...
Generic CBVs:      from django_fusion.comp.generic import ListModelView, ...
Component Cache:   from django_fusion.comp.cache import get_component_map_cache
Handlers:          from django_fusion.core.handlers import ...
Managers:          from django_fusion.core.managers import ...
Models:            from django_fusion.core.models import ...
Services:          from django_fusion.core.services import ...
Views:             from django_fusion.web.views import ...
Loaders:           from django_fusion.comp.loaders import ...
Middlewares:       from django_fusion.core.middlewares import ...
Cache:             from django_fusion.core.cache import ...
Dynaconf Config:   from django_fusion.config.dynaconf_loader import DynaconfSettings
"""

__version__ = "0.1.0"
