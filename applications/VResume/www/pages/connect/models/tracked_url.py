"""
🔗 Tracked URL Model
====================
Manages tracked URLs within email campaigns.
Generates short URLs with hash identifiers for click tracking.
"""
import hashlib
import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _


class TrackedURL(models.Model):
    """
    🔗 Tracked URL Model
    
    Tracks URLs embedded in email campaigns.
    Features:
    - Unique URL hash for short/tracked URLs
    - Click counting (total and unique)
    - Per-campaign URL tracking
    - Unique constraint on campaign + original_url
    """

    # ── Relationships ──
    campaign = models.ForeignKey(
        'connect.Campaign',
        on_delete=models.CASCADE,
        related_name='tracked_urls',
        verbose_name=_("Campaign"),
    )

    # ── URL Information ──
    original_url = models.URLField(
        max_length=2048,
        verbose_name=_("Original URL"),
        help_text=_("The actual URL to redirect to"),
    )

    url_hash = models.CharField(
        max_length=32,
        unique=True,
        verbose_name=_("URL Hash"),
        help_text=_("Short hash for tracking"),
        db_index=True,
    )

    # ── Click Metrics ──
    click_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Click Count"),
        help_text=_("Total number of clicks"),
    )

    unique_clicks = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Unique Clicks"),
        help_text=_("Number of unique clicks (based on IP)"),
    )

    # ── Audit Trail ──
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    class Meta:
        app_label = "connect"
        verbose_name = _("Tracked URL")
        verbose_name_plural = _("Tracked URLs")
        ordering = ["-created_at"]
        unique_together = [
            ["campaign", "original_url"],
        ]
        indexes = [
            models.Index(fields=["url_hash"]),
            models.Index(fields=["campaign", "click_count"]),
        ]

    def __str__(self):
        return f"{self.original_url} ({self.click_count} clicks)"

    def save(self, *args, **kwargs):
        """Generate URL hash if not set."""
        if not self.url_hash:
            self.url_hash = self._generate_url_hash(self.original_url)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_hash(url: str) -> str:
        """
        Generate a unique hash for a URL.
        
        Args:
            url (str): The URL to hash
            
        Returns:
            str: A unique hash for the URL
        """
        return TrackedURL._generate_url_hash(url)

    @staticmethod
    def _generate_url_hash(url: str) -> str:
        """
        Generate a unique hash for a URL.
        
        Uses a combination of URL hash and random suffix to ensure uniqueness.
        
        Args:
            url (str): The URL to hash
            
        Returns:
            str: A unique hash for the URL
        """
        # Create initial hash from URL
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]
        # Add random suffix to ensure uniqueness
        random_suffix = secrets.token_hex(8)
        return f"{url_hash}{random_suffix}"

    # ── Click Tracking Methods ──

    def increment_click_count(self, is_unique: bool = False) -> None:
        """
        Increment click count.
        
        Args:
            is_unique (bool): Whether this is a unique click
        """
        self.click_count = models.F('click_count') + 1
        if is_unique:
            self.unique_clicks = models.F('unique_clicks') + 1
        self.save(update_fields=["click_count", "unique_clicks", "updated_at"])
        self.refresh_from_db()

    # ── Property Methods ──

    @property
    def has_clicks(self) -> bool:
        """Check if URL has been clicked."""
        return self.click_count > 0

    @property
    def click_rate(self) -> float:
        """Calculate click rate based on campaign delivery count."""
        if self.campaign.total_sent == 0:
            return 0.0
        return round((self.click_count / self.campaign.total_sent) * 100, 2)

    @property
    def unique_click_rate(self) -> float:
        """Calculate unique click rate based on campaign delivery count."""
        if self.campaign.total_sent == 0:
            return 0.0
        return round((self.unique_clicks / self.campaign.total_sent) * 100, 2)