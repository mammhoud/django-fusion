"""
django_fusion.contrib.context.settings
======================================

Django context processor that provides empty context for site settings.

This is a base context processor that provides empty dictionaries for
``brand_settings``, ``social_settings``, and ``announcement_banner``.

Projects that use ``ceptor_ai`` should override this context processor
with their own implementation that populates these values from the database.

Usage
-----
Add to ``TEMPLATES[0]["OPTIONS"]["context_processors"]`` in ``settings.py``::

    "django_fusion.contrib.context.settings.SETTINGS",

Or override in your project's context processor::

    from django_fusion.contrib.context.settings import SETTINGS as base_settings

    def SETTINGS(request=None):
        context = base_settings(request)
        # Add project-specific settings here
        return context

Template usage::

    {{ brand_settings.site_name }}
    {{ social_settings.phone_number }}
    {% if announcement_banner %}…{% endif %}
"""


def SETTINGS(request=None) -> dict:  # noqa: N802  (uppercase matches Django convention)
    """
    Context processor — provides empty context for site settings.

    This base implementation returns empty dictionaries. Projects that use
    ``ceptor_ai`` should override this in their own context processor
    to populate these values from the database.

    Args:
        request: The current :class:`~django.http.HttpRequest` (may be
            ``None`` when called outside a request cycle).

    Returns:
        dict with keys:

        - ``brand_settings`` — empty dict (override in project)
        - ``social_settings`` — empty dict (override in project)
        - ``announcement_banner`` — None (override in project)
    """
    return {
        "brand_settings": {},
        "social_settings": {},
        "announcement_banner": None,
    }
