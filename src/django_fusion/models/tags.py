"""Enhanced Tagging System for Django/Wagtail Applications"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.aggregates import Avg
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from taggit.models import ItemBase, TagBase
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index

from django_fusion.core.managers import (
    PersonTagCategoryManager,
    PersonTagManager,
    TaggedPersonManager,
)


# ---------------------------------------------------------------------
# Constants & Choices
# ---------------------------------------------------------------------
class TagVisibilityChoices(models.IntegerChoices):
    """Visibility levels for tags"""

    PRIVATE = 0, _("Private")  # Only visible to admins
    PROTECTED = 1, _("Protected")  # Visible to authenticated users
    PUBLIC = 2, _("Public")  # Visible to everyone


class TagImportanceChoices(models.IntegerChoices):
    """Importance levels for tags"""

    LOW = 1, _("Low")
    MEDIUM = 2, _("Medium")
    HIGH = 3, _("High")
    CRITICAL = 4, _("Critical")


# ---------------------------------------------------------------------
# Base Tag Category Model (Enhanced)
# ---------------------------------------------------------------------
class BaseTagCategory(ClusterableModel):
    """
    Abstract base model for tag categories with enhanced features
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Category Name"),
        help_text=_("Display name for the category"),
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the name"),
    )
    description = RichTextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of the category purpose"),
    )
    short_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Short Description"),
        help_text=_("Brief summary for listings"),
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        default="#6B7280",
        verbose_name=_("Color"),
        help_text=_("Category color in hex format (e.g., #3B82F6)"),
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Icon"),
        help_text=_("Icon class or SVG name for this category"),
    )
    visibility = models.IntegerField(
        choices=TagVisibilityChoices.choices,
        default=TagVisibilityChoices.PUBLIC,
        verbose_name=_("Visibility Level"),
        help_text=_("Who can see this category"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Order in which categories appear (lower numbers first)"),
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Category"),
        help_text=_("Highlight this category in listings"),
    )
    max_tags_per_item = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Max Tags Per Item"),
        help_text=_(
            "Maximum number of tags from this category that can be assigned to an item (leave blank for unlimited)"
        ),
    )
    require_approval = models.BooleanField(
        default=False,
        verbose_name=_("Require Approval"),
        help_text=_("New tags in this category require administrator approval"),
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(class)s",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    last_used = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("Last Used")
    )

    class Meta:
        app_label = "shared"
        abstract = True
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["display_order", "name"]),
            models.Index(fields=["visibility", "is_featured"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["last_used"]),
        ]

    search_fields = [
        index.SearchField("name", boost=3),
        index.SearchField("description", boost=2),
        index.SearchField("short_description"),
        index.FilterField("visibility"),
        index.FilterField("is_featured"),
        # index.FilterField("live"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("color"),
                        FieldPanel("icon"),
                    ]
                ),
                FieldPanel("short_description"),
                FieldPanel("description"),
            ],
            heading=_("Appearance & Description"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("visibility"),
                FieldPanel("is_featured"),
                FieldPanel("display_order"),
                FieldPanel("max_tags_per_item"),
                FieldPanel("require_approval"),
            ],
            heading=_("Settings"),
        ),
    ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # Validate color format
        if self.color and not self.color.startswith("#"):
            raise ValidationError({"color": _("Color must start with #")})
        # Validate slug is lowercase
        if self.slug != self.slug.lower():
            raise ValidationError({"slug": _("Slug must be lowercase")})
        # Validate display order uniqueness within visibility
        if self.display_order < 0:
            raise ValidationError({"display_order": _("Display order must be positive")})

    @property
    def tag_count(self):
        """Total number of tags in this category"""
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def published_tag_count(self):
        """Number of published tags in this category"""
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def is_public(self):
        """Check if category is public"""
        return self.visibility == TagVisibilityChoices.PUBLIC

    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = timezone.now()
        self.save(update_fields=["last_used"])

    def get_absolute_url(self):
        raise NotImplementedError("Subclasses must implement this method")

    def get_statistics(self):
        """Get comprehensive statistics for this category"""
        raise NotImplementedError("Subclasses must implement this method")


# ---------------------------------------------------------------------
# Base Tag Model (Enhanced)
# ---------------------------------------------------------------------
class BaseTag(TagBase, ClusterableModel):
    """
    Abstract base model for enhanced tags with rich features
    """

    description = RichTextField(
        blank=True, verbose_name=_("Description"), help_text=_("Detailed description of the tag")
    )
    short_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Short Description"),
        help_text=_("Brief summary for tooltips and listings"),
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        default="#6B7280",
        verbose_name=_("Color"),
        help_text=_("Tag color in hex format"),
    )
    icon = models.CharField(
        max_length=100, blank=True, verbose_name=_("Icon"), help_text=_("Icon class or SVG name")
    )
    importance = models.IntegerField(
        choices=TagImportanceChoices.choices,
        default=TagImportanceChoices.MEDIUM,
        verbose_name=_("Importance Level"),
        help_text=_("How important is this tag"),
    )
    visibility = models.IntegerField(
        choices=TagVisibilityChoices.choices,
        default=TagVisibilityChoices.PUBLIC,
        verbose_name=_("Visibility Level"),
        help_text=_("Who can see this tag"),
    )

    # SEO fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Meta Title"),
        help_text=_("Title for SEO (leave blank to use tag name)"),
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name=_("Meta Description"),
        help_text=_("Description for SEO (leave blank to use tag description)"),
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Meta Keywords"),
        help_text=_("Comma-separated keywords for SEO"),
    )

    # Statistics
    usage_count = models.PositiveIntegerField(
        default=0, editable=False, verbose_name=_("Usage Count")
    )
    view_count = models.PositiveIntegerField(
        default=0, editable=False, verbose_name=_("View Count")
    )
    click_count = models.PositiveIntegerField(
        default=0, editable=False, verbose_name=_("Click Count")
    )
    last_used = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("Last Used")
    )

    # Relationships
    synonyms = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=True,
        verbose_name=_("Synonyms"),
        help_text=_("Tags with similar meaning"),
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(class)s_tags",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    # Analytics
    average_rating = models.FloatField(
        default=0.0, editable=False, verbose_name=_("Average Rating")
    )
    relevance_score = models.FloatField(
        default=0.0, editable=False, verbose_name=_("Relevance Score")
    )

    class Meta:
        abstract = True
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["usage_count"]),
            models.Index(fields=["importance", "usage_count"]),
            # models.Index(fields=["visibility", "live"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["last_used"]),
            models.Index(fields=["relevance_score"]),
        ]

    search_fields = [
        index.SearchField("name", boost=3),
        index.SearchField("description", boost=2),
        index.SearchField("short_description", boost=1.5),
        index.SearchField("meta_title"),
        index.SearchField("meta_description"),
        index.SearchField("meta_keywords"),
        index.FilterField("visibility"),
        index.FilterField("importance"),
        # index.FilterField("live"),
        index.AutocompleteField("name"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("color"),
                        FieldPanel("icon"),
                    ]
                ),
                FieldPanel("short_description"),
                FieldPanel("description"),
            ],
            heading=_("Appearance & Description"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("importance"),
                FieldPanel("visibility"),
            ],
            heading=_("Settings"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("meta_title"),
                FieldPanel("meta_description"),
                FieldPanel("meta_keywords"),
            ],
            heading=_("SEO"),
        ),
        InlinePanel("synonyms", label=_("Synonyms")),
    ]

    def clean(self):
        super().clean()
        # Validate color format
        if self.color and not self.color.startswith("#"):
            raise ValidationError({"color": _("Color must start with #")})
        # Validate slug
        if self.slug != self.slug.lower():
            raise ValidationError({"slug": _("Slug must be lowercase")})
        # Auto-generate meta fields if empty
        if not self.meta_title:
            self.meta_title = self.name
        if not self.meta_description and self.short_description:
            self.meta_description = self.short_description[:160]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def update_usage_stats(self):
        """Update usage statistics for this tag"""
        raise NotImplementedError("Subclasses must implement this method")

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=["view_count"])

    def increment_click_count(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=["click_count"])

    @property
    def published_items_count(self):
        """Count of published items using this tag"""
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def effective_meta_title(self):
        """Get effective meta title (falls back to name)"""
        return self.meta_title or self.name

    @property
    def effective_meta_description(self):
        """Get effective meta description (falls back to short description or description)"""
        return self.meta_description or self.short_description or str(self.description)[:160]

    @property
    def is_popular(self):
        """Check if tag is popular based on usage"""
        return self.usage_count > 100  # Adjust threshold as needed

    @property
    def trending_score(self):
        """Calculate trending score based on recent usage"""
        # Implement logic based on usage in last 7 days
        return min(self.usage_count / 100, 1.0)

    def get_tag_cloud_data(self, min_size=12, max_size=36):
        """Get data for tag cloud visualization"""
        size = min_size + (self.usage_count * (max_size - min_size)) / 1000
        return {
            "tag": self,
            "size": min(max_size, max(min_size, size)),
            "color": self.color,
            "importance": self.get_importance_display(),
        }

    def merge_into(self, target_tag, user=None):
        """Merge this tag into another tag"""
        raise NotImplementedError("Subclasses must implement this method")

    def get_timeline_events(self):
        """Get timeline of events for this tag"""
        raise NotImplementedError("Subclasses must implement this method")


# ---------------------------------------------------------------------
# Tag Relationship Model
# ---------------------------------------------------------------------
class TagRelationship(models.Model):
    """Model for defining relationships between tags"""

    RELATIONSHIP_TYPES = (
        ("related", _("Related")),
        ("parent", _("Parent")),
        ("child", _("Child")),
        ("requires", _("Requires")),
        ("conflicts", _("Conflicts")),
        ("similar", _("Similar")),
    )

    relationship_type = models.CharField(
        max_length=20, choices=RELATIONSHIP_TYPES, default="related"
    )
    strength = models.FloatField(default=1.0, help_text=_("Strength of relationship (0.0 to 1.0)"))
    description = models.TextField(blank=True, help_text=_("Description of the relationship"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            (
                "relationship_type",
            )
        ]
        ordering = ["-strength", "relationship_type"]

    def __str__(self):
        return f"{self.target_tag} ({self.relationship_type})"


# ---------------------------------------------------------------------
# Tag History Model
# ---------------------------------------------------------------------
class TagHistory(models.Model):
    """Model for tracking changes to tags"""

    ACTION_TYPES = (
        ("create", _("Created")),
        ("update", _("Updated")),
        ("delete", _("Deleted")),
        ("merge", _("Merged")),
        ("publish", _("Published")),
        ("unpublish", _("Unpublished")),
        ("approve", _("Approved")),
        ("reject", _("Rejected")),
    )

    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    changes = models.JSONField(default=dict, help_text=_("JSON object containing changed fields"))
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Tag History")
        verbose_name_plural = _("Tag Histories")

    def __str__(self):
        return f"{self.tag.name} - {self.action} at {self.created_at}"


# ---------------------------------------------------------------------
# Concrete Implementation: Tag (for general content)
# ---------------------------------------------------------------------
class Tag(BaseTag):
    """Tag for categorizing notes and other content."""

    class Meta:
        ordering = ["name"]
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        indexes = BaseTag.Meta.indexes + [
            models.Index(fields=["content_type"]),
        ]

    # For generic tagging across different content types
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Content type this tag is primarily associated with"),
    )

    def __str__(self):
        return self.name

    def update_usage_stats(self):
        """Update usage statistics for this tag."""
        # Implementation depends on your tagging through model

    @property
    def published_items_count(self):
        """Count published items using this tag."""
        # Implementation depends on your through model
        return 0


# ---------------------------------------------------------------------
# Person Tag Category (Enhanced)
# ---------------------------------------------------------------------
class PersonTagCategory(BaseTagCategory):
    """Category for organizing person tags"""

    objects = PersonTagCategoryManager()

    # Additional fields specific to person tags
    applies_to_user_type = models.ManyToManyField(
        "auth.Group",
        blank=True,
        verbose_name=_("Applies to User Types"),
        help_text=_("User types/groups this category applies to"),
    )
    allow_multiple = models.BooleanField(
        default=True,
        verbose_name=_("Allow Multiple Tags"),
        help_text=_("Allow multiple tags from this category on a single person"),
    )

    class Meta:
        verbose_name = _("Person Tag Category")
        verbose_name_plural = _("Person Tag Categories")
        db_table = "person_tag_categories"

    panels = BaseTagCategory.panels + [
        FieldPanel("applies_to_user_type"),
        FieldPanel("allow_multiple"),
    ]

    @property
    def tag_count(self):
        return self.tags.count()

    def get_absolute_url(self):
        return reverse("person-tag-category-detail", kwargs={"slug": self.slug})

    def get_tags_with_stats(self):
        """Get tags in this category with statistics."""
        return self.tags.get_tags_with_stats(category=self)

    def get_usage_statistics(self):
        """Get usage statistics for this category."""
        from django.db.models import Avg, Count, Q

        stats = self.tags.aggregate(
            total_usage=Count(
                "tagged_persons", filter=Q(tagged_persons__content_object__is_active=True)
            ),
            unique_persons=Count(
                "tagged_persons__content_object",
                filter=Q(tagged_persons__content_object__is_active=True),
                distinct=True,
            ),
            average_tags_per_person=Avg(
                models.Subquery(
                    PersonTag.objects.filter(
                        category=self, tagged_persons__content_object=models.OuterRef("pk")
                    )
                    .values("tagged_persons__content_object")
                    .annotate(count=Count("id"))
                    .values("count")[:1]
                )
            ),
            most_used_tag=models.Subquery(
                self.tags.annotate(
                    usage=Count(
                        "tagged_persons", filter=Q(tagged_persons__content_object__is_active=True)
                    )
                )
                .order_by("-usage")
                .values("name")[:1]
            ),
        )

        return stats

    def get_statistics(self):
        """Get comprehensive statistics for this category."""
        stats = self.get_usage_statistics()
        stats.update(
            {
                "total_tags": self.tag_count,
                "published_tags": self.published_tag_count,
                "draft_tags": self.tag_count - self.published_tag_count,
                "avg_importance": self.tags.aggregate(avg=Avg("importance"))["avg"] or 0,
            }
        )
        return stats

    def can_apply_to_user(self, user):
        """Check if this category can be applied to a user."""
        if not self.applies_to_user_type.exists():
            return True
        return user.groups.filter(
            id__in=self.applies_to_user_type.values_list("id", flat=True)
        ).exists()


# ---------------------------------------------------------------------
# Person Tag (Enhanced)
# ---------------------------------------------------------------------
class PersonTag(BaseTag):
    """Enhanced Tag model for persons"""

    category = models.ForeignKey(
        PersonTagCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tags",
        verbose_name=_("Category"),
        help_text=_("Category this tag belongs to"),
    )

    # Additional fields for person tags
    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expiration Date"),
        help_text=_("Date when this tag automatically expires"),
    )
    requires_verification = models.BooleanField(
        default=False,
        verbose_name=_("Requires Verification"),
        help_text=_("This tag requires manual verification"),
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_tags",
        verbose_name=_("Verified By"),
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Verified At"))

    objects = PersonTagManager()

    class Meta:
        verbose_name = _("Person Tag")
        verbose_name_plural = _("Person Tags")
        db_table = "person_tags"
        indexes = BaseTag.Meta.indexes + [
            models.Index(fields=["category", "importance"]),
            models.Index(fields=["expiration_date"]),
            models.Index(fields=["requires_verification", "verified_at"]),
        ]

    panels = BaseTag.panels + [
        FieldPanel("category"),
        MultiFieldPanel(
            [
                FieldPanel("expiration_date"),
                FieldPanel("requires_verification"),
            ],
            heading=_("Verification & Expiration"),
        ),
    ]

    def clean(self):
        super().clean()
        # Validate expiration date
        if self.expiration_date and self.expiration_date < timezone.now():
            raise ValidationError({"expiration_date": _("Expiration date cannot be in the past")})
        # Validate verification
        if self.verified_at and not self.verified_by:
            raise ValidationError(
                {"verified_by": _("Verifier is required if verification date is set")}
            )

    @property
    def is_expired(self):
        """Check if tag has expired"""
        if not self.expiration_date:
            return False
        return self.expiration_date < timezone.now()

    @property
    def is_verified(self):
        """Check if tag is verified"""
        return bool(self.verified_at and self.verified_by)

    def verify(self, user):
        """Verify this tag"""
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save(update_fields=["verified_by", "verified_at"])

    def get_absolute_url(self):
        return reverse("person-tag-detail", kwargs={"slug": self.slug})

    @property
    def published_items_count(self):
        return self.tagged_persons.filter(
            content_object__is_active=True, created_at__lte=timezone.now()
        ).count()

    def get_tagged_persons(self, active_only=True):
        """Get persons tagged with this tag."""
        return self.tagged_persons.get_persons_by_tag(self, active_only)

    def merge_into(self, target_tag, user=None):
        """Merge this tag into another tag."""
        return PersonTag.objects.merge_tags(self, target_tag, user)

    def get_timeline_events(self):
        """Get timeline of events for this tag."""
        events = []

        # Creation event
        events.append(
            {
                "date": self.created_at,
                "type": "created",
                "user": self.created_by,
                "description": _("Tag created"),
            }
        )

        # Verification event
        if self.verified_at:
            events.append(
                {
                    "date": self.verified_at,
                    "type": "verified",
                    "user": self.verified_by,
                    "description": _("Tag verified"),
                }
            )

        # History events
        events.extend(
            [
                {
                    "date": history.created_at,
                    "type": history.action,
                    "user": history.user,
                    "description": history.notes or history.get_action_display(),
                    "changes": history.changes,
                }
                for history in self.history.all().order_by("created_at")
            ]
        )

        # Usage milestones
        if self.usage_count >= 100:
            events.append(
                {
                    "date": self.last_used or self.created_at,
                    "type": "milestone",
                    "user": None,
                    "description": _("Reached 100+ usages"),
                }
            )

        return sorted(events, key=lambda x: x["date"])


# ---------------------------------------------------------------------
# Tagged Person (Enhanced Through Model)
# ---------------------------------------------------------------------
class TaggedPerson(ItemBase):
    """Through model for tagging persons"""

    tag = models.ForeignKey(PersonTag, on_delete=models.CASCADE, related_name="tagged_persons")

    # Link to content object (uncommented and enhanced)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="tagged_persons"
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")

    # Additional fields
    notes = RichTextField(
        blank=True, verbose_name=_("Notes"), help_text=_("Additional notes about this tagging")
    )
    confidence = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name=_("Confidence Score"),
        help_text=_("Confidence in this tagging (0.0 to 1.0)"),
    )
    importance = models.IntegerField(
        choices=TagImportanceChoices.choices,
        default=TagImportanceChoices.MEDIUM,
        verbose_name=_("Importance for this item"),
        help_text=_("How important is this tag for this specific person"),
    )

    # Verification
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_tag_assignments",
        verbose_name=_("Verified By"),
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Verified At"))

    # Dates
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Start Date"),
        help_text=_("When this tag becomes active"),
    )
    end_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("End Date"), help_text=_("When this tag expires")
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tag_assignments",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaggedPersonManager()

    class Meta:
        verbose_name = _("Tagged Person")
        verbose_name_plural = _("Tagged Persons")
        db_table = "person_tagged_items"
        unique_together = [["content_type", "object_id", "tag"]]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["importance"]),
            models.Index(fields=["confidence"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-importance", "-confidence", "-created_at"]

    def __str__(self):
        return f"{self.content_object} - {self.tag}"

    def clean(self):
        # Validate dates
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": _("End date must be after start date")})

        # Validate confidence
        if self.confidence < 0 or self.confidence > 1:
            raise ValidationError({"confidence": _("Confidence must be between 0.0 and 1.0")})

        # Check if tag category allows multiple tags
        if self.tag and self.tag.category and not self.tag.category.allow_multiple:
            existing_tags = TaggedPerson.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                tag__category=self.tag.category,
            ).exclude(pk=self.pk)
            if existing_tags.exists():
                raise ValidationError(
                    _('Only one tag from category "%(category)s" is allowed per person.')
                    % {"category": self.tag.category.name}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None

        # Set start date to now if not specified
        if not self.start_date:
            self.start_date = timezone.now()

        super().save(*args, **kwargs)

        if is_new:
            # Update tag usage stats
            self.tag.update_usage_stats()

            # Update person tag count
            if hasattr(self.content_object, "update_tag_count"):
                self.content_object.update_tag_count()

            # Create history entry
            TagHistory.objects.create(
                tag=self.tag,
                action="applied",
                user=self.created_by,
                changes={
                    "person_id": str(self.object_id),
                    "person_type": self.content_type.model,
                },
                notes=self.notes,
            )

    def delete(self, *args, **kwargs):
        tag = self.tag
        content_object = self.content_object

        super().delete(*args, **kwargs)

        # Update tag usage stats
        tag.update_usage_stats()

        # Update person tag count
        if hasattr(content_object, "update_tag_count"):
            content_object.update_tag_count()

        # Create history entry
        TagHistory.objects.create(
            tag=tag,
            action="removed",
            user=None,  # Could pass request user if available
            changes={
                "person_id": str(self.object_id),
                "person_type": self.content_type.model,
            },
        )

    @property
    def is_active(self):
        """Check if this tag assignment is currently active"""
        now = timezone.now()

        # Check if tag itself is expired
        if self.tag.is_expired:
            return False

        # Check start and end dates
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False

        return True

    @property
    def duration_days(self):
        """Get duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    def verify_assignment(self, user):
        """Verify this tag assignment"""
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save(update_fields=["verified_by", "verified_at"])

    def get_importance_class(self):
        """Get CSS class for importance level"""
        classes = {
            1: "importance-low",
            2: "importance-medium",
            3: "importance-high",
            4: "importance-critical",
        }
        return classes.get(self.importance, "importance-medium")


# ---------------------------------------------------------------------
# Tag Analytics Model
# ---------------------------------------------------------------------
class TagAnalytics(models.Model):
    """Model for storing tag analytics"""

    tag = models.ForeignKey(PersonTag, on_delete=models.CASCADE, related_name="analytics")
    date = models.DateField()

    # Daily counts
    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    applications = models.PositiveIntegerField(default=0)
    removals = models.PositiveIntegerField(default=0)

    # User engagement
    unique_users = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("tag", "date")]
        ordering = ["-date"]
        verbose_name = _("Tag Analytics")
        verbose_name_plural = _("Tag Analytics")

    def __str__(self):
        return f"{self.tag.name} - {self.date}"

    @classmethod
    def update_daily_analytics(cls, tag, date=None):
        """Update daily analytics for a tag"""
        if date is None:
            date = timezone.now().date()

        analytics, created = cls.objects.get_or_create(tag=tag, date=date)

        # Update counts from tag
        analytics.views = tag.view_count
        analytics.clicks = tag.click_count

        # Calculate applications/removals from history
        # This would need to be implemented based on your TagHistory model

        analytics.save()

        return analytics


# ---------------------------------------------------------------------
# Custom Manager Methods
# ---------------------------------------------------------------------
class EnhancedPersonTagManager(PersonTagManager):
    """Enhanced manager for PersonTag"""

    def get_popular_tags(self, days=30, limit=20):
        """Get popular tags from the last N days"""
        from django.db.models import Count, Q
        from django.utils.timezone import now

        cutoff_date = now() - timezone.timedelta(days=days)

        return (
            self.annotate(
                recent_usage=Count(
                    "tagged_persons", filter=Q(tagged_persons__created_at__gte=cutoff_date)
                )
            )
            .filter(recent_usage__gt=0)
            .order_by("-recent_usage", "-usage_count")[:limit]
        )

    def get_trending_tags(self, limit=10):
        """Get trending tags based on recent growth"""
        from django.db.models import ExpressionWrapper, F, FloatField
        from django.db.models.functions import Coalesce

        # Calculate growth rate (recent usage vs total usage)
        tags = (
            self.annotate(
                growth_rate=ExpressionWrapper(
                    F("view_count") * 1.0 / Coalesce(F("usage_count"), 1), output_field=FloatField()
                )
            )
            .filter(usage_count__gt=10, growth_rate__gt=0.1)
            .order_by("-growth_rate")[:limit]
        )

        return tags

    def get_recommended_tags(self, person, limit=5):
        """Get recommended tags for a person based on similar persons"""
        # This is a simplified example - you'd want to implement
        # a more sophisticated recommendation algorithm

        from django.db.models import Count

        # Get tags of similar persons
        person_tags = person.tags.values_list("id", flat=True)

        return (
            self.exclude(id__in=person_tags)
            .annotate(
                common_count=Count(
                    "tagged_persons__content_object__tags",
                    filter=models.Q(tagged_persons__content_object__tags__in=person_tags),
                )
            )
            .filter(common_count__gt=0)
            .order_by("-common_count", "-usage_count")[:limit]
        )


# Apply enhanced manager
PersonTag.objects = EnhancedPersonTagManager()
