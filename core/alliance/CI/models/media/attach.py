from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_grep.pipelines.models import ContentBase

from .file import File


class Attachment(ContentBase):
    files = models.ManyToManyField(File, verbose_name=_("File"))
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    description = models.CharField(max_length=255, blank=True, verbose_name=_("Description"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type"))
    object_id = models.PositiveIntegerField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    file_name = models.CharField(max_length=255)

    class Meta:
        db_table = "Attachments"
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.description or _("Attachment %(id)s") % {"id": self.id}  # type: ignore

    def delete(self, *args, **kwargs):
        self.files.delete(save=False)  # Ensure the file is deleted from the filesystem # type: ignore
        super(Attachment, self).delete(*args, **kwargs)  # type: ignore  # noqa: UP008
