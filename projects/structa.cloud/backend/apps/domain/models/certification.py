"""Wagtail snippet for admin-editable course certificate templates."""

import os

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from django_fusion.models.certification import AbstractCertificationTemplate


class CertificationTemplate(AbstractCertificationTemplate):
    """Admin-editable certificate template."""

    class Meta:
        app_label = "shared"
        verbose_name = _("Certification Template")
        verbose_name_plural = _("Certification Templates")
        ordering = ["-is_active", "-updated_at"]

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name}"

    def get_template_path(self):
        """Return the configured upload or the site's fallback certificate path."""
        if self.custom_template:
            return self.custom_template.path

        fallback = os.path.join(settings.BASE_DIR, "cert.html")
        if os.path.exists(fallback):
            return fallback
        return None

    def render(self, **kwargs):
        """Render the configured certificate template or the built-in fallback."""
        context = self.get_context(**kwargs)
        template_path = self.get_template_path()

        if template_path and self.custom_template:
            with open(template_path, "r") as template_file:
                from django.template import Context, Template

                return Template(template_file.read()).render(Context(context))

        return render_to_string("certification/cert_fallback.html", context)
