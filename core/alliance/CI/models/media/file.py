from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from django_grep.contrib.enums import FileUploadStorage
from django_grep.contrib.utils import file_generate_upload_path
from django_grep.pipelines.models import ContentBase


class File(ContentBase):
    """
    Represents a file uploaded to the system with metadata, uploader linkage,
    storage handling, and Wagtail admin integration.
    """

    file = models.FileField(
        upload_to=file_generate_upload_path,
        blank=True,
        null=True,
        verbose_name=_("File"),
    )

    original_file_name = models.TextField(verbose_name=_("Original File Name"))
    file_name = models.CharField(max_length=255, unique=True, verbose_name=_("File Name"))
    file_type = models.CharField(max_length=255, verbose_name=_("File Type"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Description"))

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Related Content Type"),
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Uploaded By"),
    )

    upload_finished_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Upload Finished At"))
    download_count = models.PositiveIntegerField(default=0, verbose_name=_("Download Count"))

    class Meta:
        db_table = "Files"
        verbose_name = _("File")
        verbose_name_plural = _("Files")
        ordering = ["-uploaded_at", "file_name"]

    def __str__(self):
        return f"{self.file_name} ({self.file_type})"

    @property
    def is_valid(self):
        return bool(self.upload_finished_at)

    @property
    def url(self):
        if not self.file:
            return None
        if settings.FILE_UPLOAD_STORAGE == FileUploadStorage.S3:
            return self.file.url
        return f"{settings.APP_DOMAIN}{self.file.url}"

    def get_file_size_mb(self):
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0

    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=["download_count"])

    @classmethod
    def get_user_storage_usage(cls, user):
        user_files = cls.objects.filter(uploaded_by=user)
        total_size = sum(file.get_file_size_mb() for file in user_files if file.file)
        return round(total_size, 2)

    @classmethod
    def get_files_by_type(cls, file_type):
        return cls.objects.filter(file_type__icontains=file_type)

    def move_to_storage(self, storage_name):
        if not self.file:
            return False

        original_path = self.file.path
        new_storage = default_storage._get_alternate_storage(storage_name)

        with open(original_path, "rb") as file_content:
            new_path = new_storage.save(self.file.name, file_content)
            self.file.name = new_path
            self.save()

        default_storage.delete(original_path)
        return True

    def create_backup(self):
        if not self.file:
            return None
        backup_name = f"backup_{self.file_name}"
        backup_path = default_storage.save(f"backups/{backup_name}", self.file)
        return backup_path

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("file"),
                FieldPanel("description"),
                FieldPanel("file_type"),
                FieldPanel("uploaded_by"),
                FieldPanel("upload_finished_at"),
            ],
            heading=_("File Details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_published"),
                FieldPanel("order"),
                FieldPanel("notes"),
            ],
            heading=_("Content Settings"),
        ),
    ]

