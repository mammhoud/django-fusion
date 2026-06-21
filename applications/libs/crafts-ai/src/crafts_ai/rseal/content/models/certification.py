"""
CertificationTemplate — Wagtail Snippet for course certificates.

Provides admin-modifiable certificate options:
- Organization name, footer text
- Logo and signature images
- Border color, accent color
- Custom CSS overrides
- Fallback to default cert.html if no template uploaded

Used by both Structa and CTC-Research via shared django-grep.
"""
import os

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from colorfield.fields import ColorField
from wagtail.fields import RichTextField


class CertificationTemplate(models.Model):
    """
    Admin-editable certificate template.
    Each course can reference one CertificationTemplate.
    """

    # === Identity ===
    name = models.CharField(
        max_length=255,
        verbose_name=_("Template Name"),
        help_text=_("Internal name for this certificate template."),
    )

    # === Modifiable Text ===
    organization_name = models.CharField(
        max_length=255,
        default="STRUCTA RESEARCH HUB",
        verbose_name=_("Organization Name"),
        help_text=_("Displayed at the top of the certificate."),
    )
    certificate_title = models.CharField(
        max_length=255,
        default="CERTIFICATE OF ATTENDANCE",
        verbose_name=_("Certificate Title"),
    )
    footer_text = models.CharField(
        max_length=255,
        default="STRUCTA CENTER TEAM",
        verbose_name=_("Footer Text"),
        help_text=_("Text displayed at the bottom of the certificate."),
    )
    body_text = models.CharField(
        max_length=500,
        default="has successfully attended and completed the training course titled:",
        verbose_name=_("Body Text"),
        help_text=_("Text between recipient name and course title."),
    )
    certifies_text = models.CharField(
        max_length=255,
        default="This certifies that:",
        verbose_name=_("Certifies Text"),
    )

    # === Modifiable Colors ===
    border_color = ColorField(
        default="#2c3e50",
        verbose_name=_("Border Color"),
        help_text=_("Main border and header/footer line color."),
    )
    accent_color = ColorField(
        default="#3498db",
        verbose_name=_("Accent Color"),
        help_text=_("Organization name and corner decoration color."),
    )
    text_color = ColorField(
        default="#333333",
        verbose_name=_("Text Color"),
        help_text=_("Default text color in the certificate body."),
    )

    # === Modifiable Images ===
    logo_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo Image"),
        help_text=_("Optional logo displayed in the header."),
    )
    signature_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Signature Image"),
        help_text=_("Optional signature image in the footer area."),
    )

    # === Custom Template ===
    custom_template = models.FileField(
        upload_to="certifications/templates/",
        blank=True,
        null=True,
        verbose_name=_("Custom HTML Template"),
        help_text=_(
            "Upload a custom HTML template. If blank, uses the default "
            "cert.html fallback at BASE_DIR."
        ),
    )
    custom_css = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Custom CSS"),
        help_text=_("Additional CSS injected into the certificate."),
    )

    # === State ===
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    notes = RichTextField(
        blank=True,
        default="",
        verbose_name=_("Notes"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Certification Template")
        verbose_name_plural = _("Certification Templates")
        ordering = ["-is_active", "-updated_at"]

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name}"

    def get_template_path(self):
        """
        Return the template to use for rendering.
        Priority: custom_template > cert.html at BASE_DIR > built-in fallback
        """
        if self.custom_template:
            return self.custom_template.path

        # Fallback to cert.html in BASE_DIR
        fallback = os.path.join(settings.BASE_DIR, "cert.html")
        if os.path.exists(fallback):
            return fallback

        # Built-in fallback template in django-grep
        return None

    def get_context(self, recipient_name="", course_title="", presenter_name="",
                    presenter_title="", course_date="", **extra):
        """Build the context dict for certificate rendering."""
        ctx = {
            "organization_name": self.organization_name,
            "certificate_title": self.certificate_title,
            "footer_text": self.footer_text,
            "body_text": self.body_text,
            "certifies_text": self.certifies_text,
            "border_color": self.border_color,
            "accent_color": self.accent_color,
            "text_color": self.text_color,
            "logo_image": self.logo_image,
            "signature_image": self.signature_image,
            "custom_css": self.custom_css,
            "recipient_name": recipient_name,
            "course_title": course_title,
            "presenter_name": presenter_name,
            "presenter_title": presenter_title,
            "course_date": course_date,
        }
        ctx.update(extra)
        return ctx

    def render(self, **kwargs):
        """
        Render the certificate HTML with the given context.
        Uses Django template engine for the built-in fallback,
        or reads custom template file directly.
        """
        context = self.get_context(**kwargs)
        template_path = self.get_template_path()

        if template_path and self.custom_template:
            # Custom uploaded template — read and render manually
            with open(template_path, "r") as f:
                from django.template import Template, Context
                tpl = Template(f.read())
                return tpl.render(Context(context))

        # Use Django template system for cert_fallback.html
        return render_to_string(
            "certification/cert_fallback.html",
            context,
        )
