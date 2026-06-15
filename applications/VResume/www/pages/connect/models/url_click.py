"""
🔗 URL Click Model
==================
Tracks individual clicks on tracked URLs in email campaigns.
Captures device, location, and referrer information for analytics.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class URLClick(models.Model):
    """
    🔗 URL Click Tracking Model
    
    Records each click event on tracked URLs in email campaigns.
    Captures:
    - Which tracked URL was clicked
    - Which email delivery triggered the click
    - IP address for geo-location and unique click detection
    - User agent for device/browser analytics
    - Referrer for traffic source analysis
    - Timestamp of click
    
    Features:
    - Device type detection (mobile, desktop, tablet)
    - Geo-location based on IP
    - Timestamp tracking for time-series analysis
    """

    # ── Relationships ──
    tracked_url = models.ForeignKey(
        'connect.TrackedURL',
        on_delete=models.CASCADE,
        related_name='clicks',
        verbose_name=_("Tracked URL"),
    )

    email_delivery = models.ForeignKey(
        'connect.EmailDelivery',
        on_delete=models.CASCADE,
        related_name='url_clicks',
        verbose_name=_("Email Delivery"),
        null=True,
        blank=True,
        help_text=_("The email delivery that triggered this click"),
    )

    # ── Click Information ──
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address"),
        help_text=_("IP address of the clicker"),
    )

    user_agent = models.TextField(
        verbose_name=_("User Agent"),
        help_text=_("Browser and device information"),
        blank=True,
        default="",
    )

    referrer = models.URLField(
        max_length=2048,
        blank=True,
        default="",
        verbose_name=_("Referrer"),
        help_text=_("URL that linked to the tracked URL"),
    )

    # ── Device Information ──
    device_type = models.CharField(
        max_length=20,
        choices=[
            ("desktop", _("Desktop")),
            ("mobile", _("Mobile")),
            ("tablet", _("Tablet")),
            ("other", _("Other")),
        ],
        default="desktop",
        verbose_name=_("Device Type"),
    )

    # ── Timestamp ──
    clicked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Clicked At"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("URL Click")
        verbose_name_plural = _("URL Clicks")
        ordering = ["-clicked_at"]
        indexes = [
            models.Index(fields=["tracked_url", "clicked_at"]),
            models.Index(fields=["email_delivery", "clicked_at"]),
            models.Index(fields=["device_type"]),
        ]

    def __str__(self):
        return f"{self.tracked_url.original_url} - {self.ip_address} at {self.click_at}"

    @property
    def click_at(self):
        """Alias for clicked_at for string representation."""
        return self.clicked_at

    def save(self, *args, **kwargs):
        """Detect device type from user agent if not set."""
        if self.user_agent and not self.device_type:
            self.device_type = self._detect_device_type(self.user_agent)
        super().save(*args, **kwargs)

    @staticmethod
    def _detect_device_type(user_agent: str) -> str:
        """
        Detect device type from user agent string.
        
        Args:
            user_agent (str): The user agent string
            
        Returns:
            str: Device type (mobile, desktop, tablet, other)
        """
        user_agent_lower = user_agent.lower()
        
        # Mobile detection
        mobile_indicators = [
            'mobile', 'android', 'iphone', 'ipod', 'blackberry', 
            'windows phone', 'opera mini', 'webos', 'fennec'
        ]
        if any(indicator in user_agent_lower for indicator in mobile_indicators):
            return "mobile"
        
        # Tablet detection
        tablet_indicators = ['ipad', 'tablet', 'playbook', 'silk']
        if any(indicator in user_agent_lower for indicator in tablet_indicators):
            return "tablet"
        
        # Desktop detection
        desktop_indicators = ['windows', 'macintosh', 'linux', 'chrome', 'firefox', 'safari', 'edge']
        if any(indicator in user_agent_lower for indicator in desktop_indicators):
            return "desktop"
        
        return "other"