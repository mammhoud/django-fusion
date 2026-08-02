import logging
import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
if "wagtail" in settings.INSTALLED_APPS:
    from wagtail.admin.panels import FieldPanel, MultiFieldPanel
else:
    FieldPanel = MultiFieldPanel = None

logger = logging.getLogger(__name__)

PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
)


class DefaultBase(models.Model):
    """
    Enhanced abstract base model with UUID, timestamps, audit fields,
    and Wagtail admin integration.
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name=_("Created By"),
        help_text=_("User who created this record"),
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name=_("Updated By"),
        help_text=_("User who last updated this record"),
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Indicates whether this record is active"),
    )

    # Publication fields
    live = models.BooleanField(
        default=True,
        verbose_name=_("Live"),
        help_text=_("Whether this record is publicly accessible"),
    )

    first_published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("First Published At"),
    )
    
    last_published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Published At"),
    )

    # SEO/Social fields
    search_description = models.TextField(
        blank=True,
        verbose_name=_("Search description"),
        help_text=_("Description for search engines and social sharing"),
    )

    # Wagtail admin panels are only built when the Wagtail app is installed.
    promote_panels = (
        [
            MultiFieldPanel(
                [FieldPanel("search_description")],
                heading=_("For search engines"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("live"),
                    FieldPanel("first_published_at"),
                    FieldPanel("last_published_at"),
                ],
                heading=_("Publishing"),
            ),
        ]
        if FieldPanel is not None
        else []
    )
    settings_panels = (
        [
            MultiFieldPanel(
                [
                    FieldPanel("is_active"),
                    FieldPanel("created_by"),
                    FieldPanel("updated_by"),
                ],
                heading=_("Settings"),
            )
        ]
        if FieldPanel is not None
        else []
    )

    class Meta:
        app_label = "shared"
        abstract = True
        ordering = ["-created_at"]
        get_latest_by = "created_at"

    def save(self, *args, **kwargs):
        """
        Automatically handles audit fields and publication dates.
        """
        # Set publication dates
        if self.live and not self.first_published_at:
            self.first_published_at = timezone.now()
        
        if self.live:
            self.last_published_at = timezone.now()

        # Set updated_by if available
        if (
            hasattr(self, "_current_user")
            and self._current_user
            and self._current_user.is_authenticated
        ):
            if not self.created_by and self._state.adding:
                self.created_by = self._current_user
            self.updated_by = self._current_user

        super().save(*args, **kwargs)

    @classmethod
    def set_current_user(cls, user):
        """
        Class method to set current user for audit fields.
        Usage: Model.set_current_user(request.user)
        """
        cls._current_user = user

    @property
    def display_name(self):
        """Default display name for the object."""
        if hasattr(self, "name"):
            return self.name
        elif hasattr(self, "title"):
            return self.title
        elif hasattr(self, "first_name") and hasattr(self, "last_name"):
            return f"{self.first_name} {self.last_name}"
        elif hasattr(self, "email"):
            return self.email
        elif hasattr(self, "code"):
            return self.code
        else:
            return str(self.pk)

    def __str__(self):
        return self.display_name

    def soft_delete(self):
        """Soft delete by setting is_active to False."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])

    def publish(self):
        """Publish the record."""
        self.live = True
        self.last_published_at = timezone.now()
        if not self.first_published_at:
            self.first_published_at = timezone.now()
        self.save(update_fields=["live", "last_published_at", "first_published_at"])

    def unpublish(self):
        """Unpublish the record."""
        self.live = False
        self.save(update_fields=["live"])

    @property
    def status_string(self):
        """Get human-readable status string."""
        if not self.live:
            return _("Draft")
        elif not self.is_active:
            return _("Inactive")
        else:
            return _("Published")

    @property
    def admin_url(self):
        """Get admin edit URL for this object."""
        from django.urls import reverse

        try:
            app_label = self._meta.app_label
            model_name = self._meta.model_name
            return reverse(f"admin:{app_label}_{model_name}_change", args=[self.id])
        except:
            return None

    def get_absolute_url(self):
        """Get public URL for this object."""
        # This should be overridden in child models
        return None


class TemplateRenderMixin:
    """
    Mixin to add template rendering capabilities to models.
    """

    def render_template(self, template_name, context=None, use_template_object=True):
        """
        Render an email template for this object.

        Args:
            template_name: Template name or EmailTemplate object
            context: Additional context for template rendering
            use_template_object: Whether to use EmailTemplate model or Django templates

        Returns:
            dict with rendered email content
        """
        if context is None:
            context = {}

        # Add object to context
        context.update(
            {
                "object": self,
                "model_name": self._meta.model_name,
                "app_label": self._meta.app_label,
            }
        )

        if use_template_object:
            # Try to get EmailTemplate from database
            from .models import EmailTemplate

            if isinstance(template_name, EmailTemplate):
                template = template_name
            else:
                # Try to get template by name or path
                template = EmailTemplate.objects.filter(
                    Q(name=template_name) | Q(template_path=template_name), is_active=True
                ).first()

            if template:
                return template.render_for_email(context)

        # Fallback to Django template rendering
        from django.template.loader import render_to_string

        # Determine template paths
        html_template = f"emails/{template_name}.html"
        text_template = f"emails/{template_name}.txt"

        try:
            html_content = render_to_string(html_template, context)
            text_content = render_to_string(text_template, context)

            # Extract subject from template or context
            subject = context.get("subject", template_name)

            return {
                "subject": subject,
                "html": html_content,
                "text": text_content,
                "preview_text": context.get("preview_text", ""),
            }
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")

            # Return minimal fallback
            return {
                "subject": str(self),
                "html": f"<h1>{self.display_name}</h1>",
                "text": str(self),
                "preview_text": "",
            }

    def send_template_email(
        self, template_name, recipients, context=None, use_template_object=True, **email_kwargs
    ):
        """
        Send email using a template.

        Args:
            template_name: Template name or EmailTemplate object
            recipients: List of recipient emails
            context: Template context
            use_template_object: Whether to use EmailTemplate model
            **email_kwargs: Additional email parameters

        Returns:
            bool: Success status
        """
        from .email_utils import InvitationEmailHandler

        # Render template
        email_content = self.render_template(template_name, context, use_template_object)

        if not email_content:
            return False

        # Send email
        email_handler = InvitationEmailHandler()

        return email_handler.send_email(
            subject=email_content["subject"],
            recipients=recipients,
            html_content=email_content["html"],
            text_content=email_content["text"],
            **email_kwargs,
        )

    def get_email_context(self):
        """
        Get default email context for this object.
        Should be overridden in child models.
        """
        from django.conf import settings
        from wagtail.models import Site

        current_site = Site.find_for_request(None)

        return {
            "object": self,
            "site_name": current_site.site_name
            if current_site
            else getattr(settings, "SITE_NAME", ""),
            "site_url": current_site.root_url
            if current_site
            else getattr(settings, "SITE_URL", ""),
            "current_year": timezone.now().year,
            "model_name": self._meta.model_name,
            "app_label": self._meta.app_label,
        }


class EnhancedBase(DefaultBase, TemplateRenderMixin):
    """
    Enhanced base model combining DefaultBase and TemplateRenderMixin
    with additional utility methods.
    """
    
    # History tracking
    version = models.PositiveIntegerField(default=1, verbose_name=_("Version"))
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Increment version on save"""
        if not self._state.adding:
            self.version += 1
        super().save(*args, **kwargs)
    
    def create_revision(self):
        """Create a revision/snapshot of the object"""
        from .revision import Revision
        return Revision.objects.create(
            content_object=self,
            content=self._serialize(),
            version=self.version,
            created_by=self.updated_by,
        )
    
    def _serialize(self):
        """Serialize object data for revision"""
        # Override in child models for custom serialization
        return {
            'id': str(self.id),
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class ContentBase(EnhancedBase):
    """
    Abstract base class for all content types with publishing capabilities.
    """

    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        help_text=_("The title of the content."),
    )

    subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Subtitle"),
        help_text=_("Optional subtitle for the content."),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of the content."),
    )

    excerpt = models.TextField(
        blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("Short excerpt for previews and listings."),
    )

    order = models.IntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("The display order of the content (lower numbers first)."),
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Is Published"),
        help_text=_("Indicates whether the content is published and visible to the public."),
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published At"),
        help_text=_("When this content was published."),
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("Internal Notes"),
        help_text=_("Additional internal notes about the content."),
    )
    
    # Content panels for Wagtail admin, when Wagtail is installed.
    content_panels = (
        [
            FieldPanel("title"),
            FieldPanel("subtitle"),
            FieldPanel("description"),
            FieldPanel("excerpt"),
            FieldPanel("order"),
            FieldPanel("is_published"),
            FieldPanel("published_at"),
            FieldPanel("notes"),
        ]
        if FieldPanel is not None
        else []
    )

    class Meta:
        abstract = True
        ordering = ["order", "-created_at"]
        verbose_name = _("Content")
        verbose_name_plural = _("Contents")

    def save(self, *args, **kwargs):
        """
        Auto-set published_at when content is published.
        """
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        elif not self.is_published and self.published_at:
            self.published_at = None

        super().save(*args, **kwargs)

    def publish(self):
        """Publish the content."""
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=["is_published", "published_at", "updated_at"])

    def unpublish(self):
        """Unpublish the content."""
        self.is_published = False
        self.published_at = None
        self.save(update_fields=["is_published", "published_at", "updated_at"])

    @property
    def status(self):
        """Get human-readable status."""
        if self.is_published:
            return _("Published")
        return _("Draft")

    @property
    def is_draft(self):
        """Check if content is in draft state."""
        return not self.is_published

    def __str__(self):
        return self.title


class TaggableBase(EnhancedBase):
    """
    Abstract base model that enables tag relationships via ClusterTaggableManager.
    """

    tags = ClusterTaggableManager(
        through="TaggedPerson",
        blank=True,
        verbose_name=_("Tags"),
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["is_active"])]

    # ---------------------- Tag Helpers ----------------------

    @property
    def tag_list(self) -> str:
        """Comma-separated list of tag names."""
        return ", ".join(self.tags.names())

    def add_tag(self, tag_name: str, **kwargs):
        """Add tag to object."""
        self.tags.add(tag_name, **kwargs)

    def remove_tag(self, tag_name: str):
        """Remove tag from object."""
        self.tags.remove(tag_name)

    def has_tag(self, tag_name: str) -> bool:
        """Check if tag exists."""
        return self.tags.filter(name__iexact=tag_name).exists()

    def get_tags_by_category(self, category_name: str):
        """Return tags by category name."""
        return self.tags.filter(category__name__iexact=category_name)