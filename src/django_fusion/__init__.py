"""django-fusion - reusable Django and Wagtail helpers.

A component system, declarative routing, fragment rendering, forms/tables
mixins, and health/asset plumbing for Django + Wagtail sites.

Package layout
--------------
django_fusion.comp           Server-side component system (slots, props, HTMX).
  .registry                Component registry, include-path registration, cache.
  .cache                   Component mapping cache with graceful fallback.
  .loader                  Lazy / HTMX-safe ``component_loader``.
  .tags                    ``{% comp %}``, ``{% prop %}``, ``{% slot %}``, ``{% var %}``.
django_fusion.routes         Declarative, class-based URL routing.
  .core.base               ``Viewset``, ``Route``, ``route``, descriptors.
  .core.sites              ``Module`` and ``Application``.
  .core.landing            ``Landing``.
  .components.routable     ``RoutableComponent``.
  .components.fragments    ``FragmentComponent``.
  .components.dual_mode    Render-first / data-API component bridge.
  .http.detection          ``FragmentDetector`` (HTMX / Unpoly / SSE).
  .rendering.decorators    ``fusion_view`` dual-mode function view.
  .rendering.render_mode   ``resolve_render_mode`` chain.
  .pages.handler           Page handler base classes.
django_fusion.fragments      URL-driven fragment rendering.
  .forms                   ``FormMixin`` and form tag generators.
  .tables                  ``TableMixin`` and row generators.
  .generic                 Generic CBVs: list, create, update, delete, detail, search.
  .viewsets                Wagtail-aware viewsets.
  .analyzer                Template scanner over ``{% comp %}`` usage.
django_fusion.core           Foundation: middleware, context, rendering, assets, health.
  .middlewares             Error tracking, language, privacy, freeze, service.
  .context                 Context processors (auth, cookies, HTMX, languages).
  .assets                  Asset manifest API and template tags.
  .health                  Health-check endpoints (``/health/``, ``db``, ``assets``).
  .rendering               Shared render helpers.
  .encoder                 Response encoding utilities.
django_fusion.config         Configuration.
  .conf                    Typed settings objects (``FUSION_*``).
  .loader                  Multi-environment YAML config (Dynaconf).
  .manifest                Asset manifest generation.
django_fusion.models         Base models, mixins, and shared domain models.
  .base / .mixins          ``BaseModel``, ``TimeStampedModel``, ``SoftDeleteModel``, ....
  .auth                    ``Role``, ``UserRole``.
  .email                   ``EmailLog``, ``EmailTemplate``, ``UserGroup``.
  .interaction             ``Call``, ``Notification`` (migrated, concrete models).
  .datatoken               Sync/tagging token models and managers.
  .cache_storage           ``CachingStorage``, ``ModelCacheMixin``.
django_fusion.services       Reusable service layer.
  .base                    ``BaseService``, ``ModelService``, ``ServiceRegistry``.
  .jobs                    Logged background-job dispatch.
  .token                   ``TokenService``, ``TokenProtectedService``.
  .crud                    Functional and class-based CRUD helpers.
django_fusion.management     Management commands, handlers, filters, managers, utils.
  .commands                ``generate_asset_manifest``, ``verify_content``, ....
django_fusion.tasks          Broker-agnostic background tasks (Dramatiq, in-process).
django_fusion.site           Site-level authentication mixins.
django_fusion.plugins        Optional integrations (loaded on demand).
  .apis                    django-bolt API bridge (extra: ``bolt``).
  .designer                Interactive UI designer tools and MCP router.
  .htmx / .unpoly          Fragment-detection integration hooks.
  .webpack                 django-webpack-loader glue (extra: ``webpack``).
  .debug_tools             Development diagnostics.
django_fusion.builder        Landing builder: Wagtail page assembly and themes.
django_fusion.template_fields Sandboxed dynamic template field engine.
django_fusion.mcp            Reusable FastAPI/MCP routers for Fusion servers.
                             Requires the optional ``bolt`` extra.
django_fusion.contrib        Admin, cache, privacy, and utility extensions.

Canonical import paths
----------------------
Routing:      from django_fusion.routes.core.base import Viewset, Route, route
              from django_fusion.routes.core.sites import Module, Application
Components:   from django_fusion.routes.components.routable import RoutableComponent
              from django_fusion.routes.components.fragments import FragmentComponent
Fragments:    from django_fusion.routes.http.detection import FragmentDetector
Forms/Tables: from django_fusion.fragments.forms import FormMixin
              from django_fusion.fragments.tables import TableMixin
Registry:     from django_fusion.comp._init import components
              from django_fusion.comp.registry import register_include_paths
Health:       from django_fusion.core.health import HealthCheckView
Assets:       from django_fusion.core.assets import urls as assets_urls
Services:     from django_fusion.services import BaseService, TokenService, dispatch_job
Settings:     from django_fusion.config.conf import resolve_render_mode_setting
Render mode:  from django_fusion.routes.rendering.render_mode import resolve_render_mode

Optional integrations (install the matching extra first):
  ``django_fusion.plugins.apis`` and ``django_fusion.mcp`` -> ``django-fusion[bolt]``
  ``django_fusion.plugins.webpack``                        -> ``django-fusion[webpack]``
  ``django_fusion.contrib.auth`` allauth integration       -> ``django-fusion[auth]``
  django-tables2 adapter                                   -> ``django-fusion[tables]``

Full documentation: ``docs/INDEX.md`` in the source distribution, or
https://github.com/mammhoud/django-fusion/tree/generic/docs
"""

__version__ = "2.0.2"

# Default app config for Django < 3.2 compatibility and for projects that
# include "django_fusion" as a plain string in INSTALLED_APPS.
default_app_config = "django_fusion.apps.DjangoFusionConfig"
