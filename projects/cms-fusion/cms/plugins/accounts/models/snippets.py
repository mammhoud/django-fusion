from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.fields import RichTextField


class AuthEmailTemplate(models.Model):
    class TemplateType(models.TextChoices):
        REGISTRATION_CONFIRMATION = "registration_confirmation", _("Registration Confirmation")
        SIGNIN_SUCCESS = "signin_success", _("Sign-In Success")

    template_type = models.CharField(
        max_length=50,
        choices=TemplateType.choices,
        verbose_name=_("Template Type"),
    )
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    body_html = RichTextField(verbose_name=_("Body (HTML)"))
    body_text = models.TextField(
        verbose_name=_("Body (Plain Text)"),
        help_text=_("Used as fallback for email clients that do not render HTML."),
    )
    is_active = models.BooleanField(default=False, verbose_name=_("Active"))

    class Meta:
        app_label = "accounts"
        db_table = "accounts_registration_authemailtemplate"
        verbose_name = _("Auth Email Template")
        verbose_name_plural = _("Auth Email Templates")

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.get_template_type_display()} ({status})"

    def save(self, *args, **kwargs):
        if self.is_active:
            AuthEmailTemplate.objects.filter(
                template_type=self.template_type,
                is_active=True,
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
