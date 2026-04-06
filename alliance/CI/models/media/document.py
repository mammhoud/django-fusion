from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel


# from alliance.CI.utils.enums import FileUploadStorage
class DocumentVersion(models.Model):
    """
    Tracks individual versions of a Document with changelogs and author history.
    """

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Document"),
    )

    file = models.FileField(upload_to="document_versions/", verbose_name=_("Version File"))
    version_number = models.CharField(max_length=50, verbose_name=_("Version Number"))
    changelog = models.TextField(blank=True, verbose_name=_("Changelog"))
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["document", "version_number"]
        verbose_name = _("Document Version")
        verbose_name_plural = _("Document Versions")

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"

    @property
    def file_url(self):
        return self.file.url if self.file else None

    @property
    def created_on(self):
        return timezone.localtime(self.created_at).strftime("%Y-%m-%d %H:%M:%S")

    panels = [
        FieldPanel("version_number"),
        FieldPanel("file"),
        FieldPanel("changelog"),
        FieldPanel("created_by"),
    ]
