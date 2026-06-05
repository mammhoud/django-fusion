"""
Fake module manager for django_osoul.

This module creates stub/fake implementations of django_osoul modules
that are not available in the environment (e.g., due to Twilio dependency constraints).

This is imported and initialized in application settings before any
real imports of django_osoul occur.
"""
import sys
import types


def setup_django_osoul_stub():
    """Setup all fake django_osoul modules in sys.modules."""

    # Create module hierarchy using types.ModuleType
    django_osoul = types.ModuleType('django_osoul')
    django_osoul.__file__ = '/fake/django_osoul/__init__.py'

    django_osoul_models = types.ModuleType('django_osoul.models')
    django_osoul_models.__file__ = '/fake/django_osoul/models/__init__.py'

    django_osoul_site = types.ModuleType('django_osoul.site')
    django_osoul_site.__file__ = '/fake/django_osoul/site/__init__.py'

    django_osoul_context_mixins = types.ModuleType('django_osoul.site._context_mixins')
    django_osoul_context_mixins.__file__ = '/fake/django_osoul/site/_context_mixins.py'

    # Add dynamic __getattr__ to site module to handle missing submodules
    def site_getattr(name):
        """Return a fake module for any requested attribute"""
        fake_mod = types.ModuleType(f'django_osoul.site.{name}')
        fake_mod.__file__ = f'/fake/django_osoul/site/{name}.py'
        # Add to sys.modules
        sys.modules[f'django_osoul.site.{name}'] = fake_mod
        return fake_mod

    django_osoul_site.__getattr__ = site_getattr

    # Also create common classes that might be needed from _context_mixins
    class WagtailPageMixin:
        pass

    django_osoul_context_mixins.WagtailPageMixin = WagtailPageMixin

    django_osoul_enums = types.ModuleType('django_osoul.site.enums')
    django_osoul_enums.__file__ = '/fake/django_osoul/site/enums/__init__.py'

    django_osoul_env = types.ModuleType('django_osoul.site.enums.env')
    django_osoul_env.__file__ = '/fake/django_osoul/site/enums/env.py'

    django_osoul_upload = types.ModuleType('django_osoul.site.enums.upload')
    django_osoul_upload.__file__ = '/fake/django_osoul/site/enums/upload.py'

    django_osoul_managers = types.ModuleType('django_osoul.managers')
    django_osoul_managers.__file__ = '/fake/django_osoul/managers/__init__.py'

    django_osoul_core = types.ModuleType('django_osoul.core')
    django_osoul_core.__file__ = '/fake/django_osoul/core/__init__.py'

    django_osoul_core_models = types.ModuleType('django_osoul.core.models')
    django_osoul_core_models.__file__ = '/fake/django_osoul/core/models/__init__.py'

    # Create fake classes for commonly used attributes
    class FakeEnvironment:
        pass

    class FakeRuntime:
        pass

    class FakeModule:
        pass

    class FakeDirection:
        pass

    class FakeFileUploadStorage:
        pass

    class FakeFileUploadStrategy:
        pass

    class FakeBaseModel:
        pass

    # Add __getattr__ to handle any missing attributes
    def env_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    # Monkey patch __getattr__ onto the module
    django_osoul_env.__getattr__ = env_getattr

    # Add attributes to env module
    django_osoul_env.Environment = FakeEnvironment
    django_osoul_env.Runtime = FakeRuntime
    django_osoul_env.Module = FakeModule
    django_osoul_env.Direction = FakeDirection

    # Add __getattr__ to upload module too
    def upload_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_upload.__getattr__ = upload_getattr

    # Add attributes to upload module
    django_osoul_upload.FileUploadStorage = FakeFileUploadStorage
    django_osoul_upload.FileUploadStrategy = FakeFileUploadStrategy

    # Add __getattr__ to managers module too
    def managers_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_managers.__getattr__ = managers_getattr

    # Add BaseModel to core.models
    class FakeBaseModel:
        pass

    django_osoul_core_models.BaseModel = FakeBaseModel

    # Add __getattr__ to core.models
    def core_models_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_core_models.__getattr__ = core_models_getattr

    # Add core.models to core module
    django_osoul_core.models = django_osoul_core_models

    # Add __getattr__ to core module
    def core_getattr(name):
        """Return a fake module for any requested attribute"""
        fake_mod = types.ModuleType(f'django_osoul.core.{name}')
        fake_mod.__file__ = f'/fake/django_osoul/core/{name}.py'
        sys.modules[f'django_osoul.core.{name}'] = fake_mod
        return fake_mod

    django_osoul_core.__getattr__ = core_getattr

    # Add core.managers module
    django_osoul_core_managers = types.ModuleType('django_osoul.core.managers')
    django_osoul_core_managers.__file__ = '/fake/django_osoul/core/managers/__init__.py'

    class FakeCachedManager:
        pass

    class FakeBaseManager:
        pass

    class FakeGroupAccessControl:
        pass

    class FakeRoleHierarchyManager:
        pass

    def fake_cached_method(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    django_osoul_core_managers.CachedManager = FakeCachedManager
    django_osoul_core_managers.BaseManager = FakeBaseManager
    django_osoul_core_managers.GroupAccessControl = FakeGroupAccessControl
    django_osoul_core_managers.RoleHierarchyManager = FakeRoleHierarchyManager
    django_osoul_core_managers.cached_method = fake_cached_method

    def core_managers_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_core_managers.__getattr__ = core_managers_getattr
    django_osoul_core.managers = django_osoul_core_managers

    # Add core.handlers module
    django_osoul_core_handlers = types.ModuleType('django_osoul.core.handlers')
    django_osoul_core_handlers.__file__ = '/fake/django_osoul/core/handlers/__init__.py'

    class FakeErrorTrackerMiddleware:
        pass

    django_osoul_core_handlers.ErrorTrackerMiddleware = FakeErrorTrackerMiddleware

    # Add core.handlers.core module
    django_osoul_core_handlers_core = types.ModuleType('django_osoul.core.handlers.core')
    django_osoul_core_handlers_core.__file__ = '/fake/django_osoul/core/handlers/core.py'

    class FakeDynamicComponentRenderer:
        pass

    class FakeEmailTemplateRegistry:
        pass

    class FakeEmailTemplate:
        pass

    django_osoul_core_handlers_core.DynamicComponentRenderer = FakeDynamicComponentRenderer
    django_osoul_core_handlers_core.EmailTemplateRegistry = FakeEmailTemplateRegistry
    django_osoul_core_handlers_core.EmailTemplate = FakeEmailTemplate

    def core_handlers_getattr(name):
        """Return a fake module for any requested attribute"""
        fake_mod = types.ModuleType(f'django_osoul.core.handlers.{name}')
        fake_mod.__file__ = f'/fake/django_osoul/core/handlers/{name}.py'
        sys.modules[f'django_osoul.core.handlers.{name}'] = fake_mod
        return fake_mod

    django_osoul_core_handlers.__getattr__ = core_handlers_getattr
    django_osoul_core_handlers.core = django_osoul_core_handlers_core
    django_osoul_core.handlers = django_osoul_core_handlers

    # Add core.services module
    django_osoul_core_services = types.ModuleType('django_osoul.core.services')
    django_osoul_core_services.__file__ = '/fake/django_osoul/core/services/__init__.py'

    class FakeCartServiceBase:
        pass

    class FakePostFilterServiceBase:
        pass

    class FakeTagServiceBase:
        pass

    django_osoul_core_services.CartServiceBase = FakeCartServiceBase
    django_osoul_core_services.PostFilterServiceBase = FakePostFilterServiceBase
    django_osoul_core_services.TagServiceBase = FakeTagServiceBase

    def core_services_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_core_services.__getattr__ = core_services_getattr
    django_osoul_core.services = django_osoul_core_services

    # Add web.routes module
    django_osoul_web = types.ModuleType('django_osoul.web')
    django_osoul_web.__file__ = '/fake/django_osoul/web/__init__.py'

    django_osoul_web_routes = types.ModuleType('django_osoul.web.routes')
    django_osoul_web_routes.__file__ = '/fake/django_osoul/web/routes.py'

    class FakeApplication:
        pass

    class FakeSite:
        pass

    class FakeViewprop:
        pass

    class FakeFragmentComponent:
        pass

    class FakeRoutableComponent:
        pass

    class FakeModelViewset:
        pass

    class FakeReadonlyModelViewset:
        pass

    django_osoul_web_routes.Application = FakeApplication
    django_osoul_web_routes.Site = FakeSite
    django_osoul_web_routes.viewprop = FakeViewprop
    django_osoul_web_routes.FragmentComponent = FakeFragmentComponent
    django_osoul_web_routes.RoutableComponent = FakeRoutableComponent
    django_osoul_web_routes.ModelViewset = FakeModelViewset
    django_osoul_web_routes.ReadonlyModelViewset = FakeReadonlyModelViewset

    def web_routes_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_web_routes.__getattr__ = web_routes_getattr
    django_osoul_web.routes = django_osoul_web_routes

    # Add web.views module
    django_osoul_web_views = types.ModuleType('django_osoul.web.views')
    django_osoul_web_views.__file__ = '/fake/django_osoul/web/views.py'

    class FakeFilterMixin:
        pass

    class FakeSearchMixin:
        pass

    django_osoul_web_views.FilterMixin = FakeFilterMixin
    django_osoul_web_views.SearchMixin = FakeSearchMixin

    def web_views_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_web_views.__getattr__ = web_views_getattr
    django_osoul_web.views = django_osoul_web_views

    def web_getattr(name):
        """Return a fake module for any requested attribute"""
        fake_mod = types.ModuleType(f'django_osoul.web.{name}')
        fake_mod.__file__ = f'/fake/django_osoul/web/{name}.py'
        sys.modules[f'django_osoul.web.{name}'] = fake_mod
        return fake_mod

    django_osoul_web.__getattr__ = web_getattr

    # Add comp.site module
    django_osoul_comp = types.ModuleType('django_osoul.comp')
    django_osoul_comp.__file__ = '/fake/django_osoul/comp/__init__.py'

    django_osoul_comp_site = types.ModuleType('django_osoul.comp.site')
    django_osoul_comp_site.__file__ = '/fake/django_osoul/comp/site.py'

    class FakeNotificationMixin:
        pass

    class FakePageHandler:
        pass

    django_osoul_comp_site.NotificationMixin = FakeNotificationMixin
    django_osoul_comp_site.PageHandler = FakePageHandler

    def comp_site_getattr(name):
        """Return a fake class for any requested attribute"""
        class FakeAttr:
            pass
        return FakeAttr

    django_osoul_comp_site.__getattr__ = comp_site_getattr
    django_osoul_comp.site = django_osoul_comp_site

    def comp_getattr(name):
        """Return a fake module for any requested attribute"""
        fake_mod = types.ModuleType(f'django_osoul.comp.{name}')
        fake_mod.__file__ = f'/fake/django_osoul/comp/{name}.py'
        sys.modules[f'django_osoul.comp.{name}'] = fake_mod
        return fake_mod

    django_osoul_comp.__getattr__ = comp_getattr

    # Add attributes to models module
    django_osoul_models.BaseModel = FakeBaseModel

    # Build module hierarchy
    django_osoul_site.enums = django_osoul_enums
    django_osoul_enums.env = django_osoul_env
    django_osoul_enums.upload = django_osoul_upload
    django_osoul_models.interaction = types.ModuleType('django_osoul.models.interaction')
    django_osoul_models.interaction.__file__ = '/fake/django_osoul/models/interaction/__init__.py'
    django_osoul_models.interaction.call = types.ModuleType('django_osoul.models.interaction.call')
    django_osoul_models.interaction.call.__file__ = '/fake/django_osoul/models/interaction/call.py'

    class FakeTwilioClient:
        pass

    django_osoul_models.interaction.call.Client = FakeTwilioClient

    # Add submodules to main django_osoul module
    django_osoul.models = django_osoul_models
    django_osoul.site = django_osoul_site
    django_osoul.managers = django_osoul_managers
    django_osoul.core = django_osoul_core
    django_osoul.web = django_osoul_web
    django_osoul.comp = django_osoul_comp

    # Register all modules in sys.modules BEFORE importing configs.settings
    sys.modules['django_osoul'] = django_osoul
    sys.modules['django_osoul.models'] = django_osoul_models
    sys.modules['django_osoul.site'] = django_osoul_site
    sys.modules['django_osoul.site._context_mixins'] = django_osoul_context_mixins
    sys.modules['django_osoul.site.enums'] = django_osoul_enums
    sys.modules['django_osoul.site.enums.env'] = django_osoul_env
    sys.modules['django_osoul.site.enums.upload'] = django_osoul_upload
    sys.modules['django_osoul.managers'] = django_osoul_managers
    sys.modules['django_osoul.core'] = django_osoul_core
    sys.modules['django_osoul.core.models'] = django_osoul_core_models
    sys.modules['django_osoul.core.managers'] = django_osoul_core_managers
    sys.modules['django_osoul.core.handlers'] = django_osoul_core_handlers
    sys.modules['django_osoul.core.handlers.core'] = django_osoul_core_handlers_core
    sys.modules['django_osoul.core.services'] = django_osoul_core_services
    sys.modules['django_osoul.web'] = django_osoul_web
    sys.modules['django_osoul.web.routes'] = django_osoul_web_routes
    sys.modules['django_osoul.web.views'] = django_osoul_web_views
    sys.modules['django_osoul.comp'] = django_osoul_comp
    sys.modules['django_osoul.comp.site'] = django_osoul_comp_site
    sys.modules['django_osoul.models.interaction'] = django_osoul_models.interaction
    sys.modules['django_osoul.models.interaction.call'] = django_osoul_models.interaction.call
