import logging

from django.apps import AppConfig

logger = logging.getLogger("apps.domain")


class DomainConfig(AppConfig):
    name = "apps.domain"
    label = "shared"
    verbose_name = "Domain Models"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """
        Patch Wagtail's Page.get_indexed_instance() to return None when
        self.specific resolves to a model that is not registered with
        modelsearch's search index (e.g. django.contrib.sites.models.Site
        for the Root page). This prevents AttributeError warnings during
        fixture loading and page save operations.
        """
        self._patch_page_get_indexed_instance()

    def _patch_page_get_indexed_instance(self):
        """
        Monkey-patch wagtail.models.Page.get_indexed_instance() to guard
        against returning non-Indexed model instances.

        Root cause: Wagtail's Page.get_indexed_instance() calls self.specific,
        which follows multi-table inheritance to the most specific subclass.
        For the Root page (depth=1), self.specific resolves to
        django.contrib.sites.models.Site — a model that does NOT inherit from
        modelsearch.index.Indexed. modelsearch then tries calling
        get_indexed_objects() on Site, which fails with AttributeError.

        The fix: after calling the original method, check if the returned
        instance's class is registered with modelsearch (i.e. is a subclass
        of modelsearch.index.Indexed with non-empty search_fields). If not,
        return None so modelsearch's indexing pipeline skips it gracefully.
        """
        from wagtail.models import Page

        # Sentinel: prevent double-patching if ready() is called more than once
        if getattr(Page, '_search_patched', False):
            return

        try:
            from modelsearch.index import class_is_indexed

            original_method = Page.get_indexed_instance

            def _safe_page_get_indexed_instance(page_self):
                instance = original_method(page_self)
                if instance is None:
                    return None
                if not class_is_indexed(type(instance)):
                    logger.debug(
                        "Skipping indexing for %s (pk=%s) — not a modelsearch.Indexed subclass",
                        type(instance).__qualname__,
                        instance.pk,
                    )
                    return None
                return instance

            Page.get_indexed_instance = _safe_page_get_indexed_instance
            Page._search_patched = True
            logger.debug(
                "Patched wagtail.models.Page.get_indexed_instance() to guard against non-Indexed models"
            )
        except ImportError:
            logger.warning(
                "Could not patch Page.get_indexed_instance() — modelsearch not installed"
            )
