"""django-fusion — reusable Django and Wagtail helpers for Structa Cloud sites.

Package layout
--------------
django_fusion.comp           Server-side component system (slots, props, HTMX loaders).
  .cache                    Redis-backed component mapping cache with fallback.
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
django_fusion.fragments     Reusable component mixins and generic CBVs.
  .forms                    Form rendering mixins and tag generators.
  .tables                   Table rendering mixins and row generators.
  .generic                  Generic CBVs: list, create, update, delete, search.
django_fusion.config         Package-level configuration constants and conf helpers.
  .dynaconf_loader          Multi-environment YAML configuration with Dynaconf.
django_fusion.contrib        Shared admin, cache utils, debug tools, and privacy helpers.
django_fusion.core           Foundational layer — models, managers, services, utils.
  .cache                    Pluggable cache manager base classes.
  .filters                  Queryset filters: token, revision, cache-aware.
  .handlers                 View handler base classes and HTMX fragment mixins.
  .managers                 Model managers: role hierarchy, group access, tags, user.
  .middlewares              Middleware: error tracker, privacy, language, freeze.
  .models                   Base models, auth, email, interaction models.
  .services                 Service layer: CRUD base, cart, person.
  .utils                    Utilities: data, formatting, security.
django_fusion.core.health  Lightweight health-check endpoint).
django_fusion.core           Core layer — models, managers, services, utils, views, handlers, health, middlewares, templatetags.
  .cache                    Pluggable cache manager base classes.
  .filters                  Queryset filters: token, revision, cache-aware.
  .handlers                 View handler base classes and HTMX fragment mixins.
  .health                   Health-check endpoints (views, urls).
  .managers                 Model managers: role hierarchy, group access, tags, user.
  .middlewares              Request/response middleware (error tracking, language, freeze, service, site, component error).
  .models                   Base models, auth, email, interaction models.
  .services                 Service layer: CRUD base, cart, person.
  .utils                    Utilities: data, formatting, security.
  .views                    View mixins: FilterMixin, SearchMixin, AjaxResponseMixin.
django_fusion.routes         Declarative, class-based URL routing for Django projects.
django_fusion.site           Unified site layer.
  .management               Management commands and scripts.
  .interface                 Site interface layer (formerly ci) — pagination, context, auth.
    .adapters                 Site-level allauth adapter.
    .auth                     Auth forms, role/token models, allauth adapters.
    .choices                  Choice enums: cart, contact, message, styles, token.
    .context                  Context processors: auth, cookies, HTMX, languages.
    .enums                    Environment and upload enums.
    .responses                HTTP response helpers and exception schemas.
    .schemas                  Pydantic response schemas, serializers, user schemas.
    .views                    Site-level views: notifications, tag management.
django_fusion.wagtail        Wagtail integration: blocks, snippets, viewsets.
django_fusion.web            Web layer: allauth adapters (shim for core.adapters), auth backends (shim for core.backends), view mixins (shim for core.views).
  .adapters                 django-allauth account and social adapters.
  .backends                 Custom authentication backends.
  .views                    FilterMixin, SearchMixin for class-based views.

Canonical import paths
-----------------------
Routing:           from django_fusion.routes import Viewset, Site, ...
Generic CBVs:      from django_fusion.fragments.generic import ListModelView, ...
Forms/Tables:      from django_fusion.fragments.forms import FormMixin
                   from django_fusion.fragments.tables import TableMixin
Health:            from django_fusion.core.health import HealthCheckView, DatabaseHealthView
Middlewares:       from django_fusion.core.middlewares import ErrorTrackerMiddleware, DefaultLanguageMiddleware
Handlers:          from django_fusion.core.handlers import ...
Managers:          from django_fusion.core.managers import ...
Models:            from django_fusion.core.models import ...
Services:          from django_fusion.core.services import ...
Views:             from django_fusion.web.views import ...
Loaders:           from django_fusion.comp.fragment.loaders import ...
Cache:             from django_fusion.core.cache import ...
Dynaconf Config:   from django_fusion.config.dynaconf_loader import DynaconfSettings
"""

__version__ = "0.1.0"

# Default app config for Django < 3.2 compatibility and for projects that
# include "django_fusion" as a plain string in INSTALLED_APPS.
default_app_config = "django_fusion.apps.DjangoFusionConfig"
