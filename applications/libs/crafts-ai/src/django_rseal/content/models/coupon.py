"""
Coupon — Reusable discount coupon model for django-grep.

Provides admin-managed coupon codes with:
- Percentage or fixed amount discounts
- Validity period (start/end dates)
- Max usage count + per-user usage tracking
- ManyToMany to courses (optional — blank = all courses)
- Active/inactive toggle

Shared via django-grep so both Structa and CTC-Research can use the same coupon system.
"""
import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel


def _generate_code():
    """Generate a random 8-char uppercase alphanumeric coupon code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


class Coupon(models.Model):
    """
    Reusable discount coupon with validation and tracking.
    Can be applied to specific courses or globally.
    """

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage (%)")
        FIXED = "fixed", _("Fixed Amount")

    # === Identity ===
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Coupon Code"),
        help_text=_("Unique alphanumeric code. Auto-generated if blank."),
        default=_generate_code,
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Description"),
        help_text=_("Internal description for this coupon."),
        default="",
        blank=True,
    )

    # === Discount ===
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
        verbose_name=_("Discount Type"),
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Discount Value"),
        help_text=_("Percentage (0-100) or fixed amount depending on type."),
        validators=[MinValueValidator(0)],
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Max Discount Cap"),
        help_text=_("Maximum discount amount for percentage coupons. Leave blank for no cap."),
    )

    # === Validity ===
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    valid_from = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Valid From"),
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Valid Until"),
        help_text=_("Leave blank for no expiry."),
    )

    # === Usage ===
    max_uses = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Max Total Uses"),
        help_text=_("Maximum total redemptions. 0 = unlimited."),
    )
    max_uses_per_user = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Max Uses Per User"),
        help_text=_("Maximum times a single user can use this coupon."),
    )
    times_used = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Times Used"),
        help_text=_("Auto-incremented. Do not edit manually."),
    )

    # === Minimum ===
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Minimum Order Amount"),
        help_text=_("Minimum cart/course price required to apply this coupon."),
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # === Panels ===
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("code"),
                FieldPanel("name"),
                FieldPanel("is_active"),
            ],
            heading=_("Identity"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("discount_type"),
                    FieldPanel("discount_value"),
                ]),
                FieldPanel("max_discount_amount"),
                FieldPanel("minimum_order_amount"),
            ],
            heading=_("Discount"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("valid_from"),
                    FieldPanel("valid_until"),
                ]),
            ],
            heading=_("Validity Period"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("max_uses"),
                    FieldPanel("max_uses_per_user"),
                ]),
                FieldPanel("times_used"),
            ],
            heading=_("Usage Limits"),
        ),
    ]

    class Meta:
        app_label = "django_rseal"
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")
        ordering = ["-is_active", "-created_at"]

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return f"{status} {self.code} — {self.discount_value}% off"
        return f"{status} {self.code} — ${self.discount_value} off"

    def clean(self):
        super().clean()
        if self.discount_type == self.DiscountType.PERCENTAGE and self.discount_value > 100:
            raise ValidationError({
                "discount_value": _("Percentage discount cannot exceed 100%."),
            })

    # === Validation Methods ===
    def is_valid(self, order_amount=0, user=None):
        """
        Check if coupon is valid for use.
        Returns (is_valid, error_message).
        """
        now = timezone.now()

        if not self.is_active:
            return False, _("This coupon is no longer active.")

        if self.valid_from and now < self.valid_from:
            return False, _("This coupon is not yet valid.")

        if self.valid_until and now > self.valid_until:
            return False, _("This coupon has expired.")

        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False, _("This coupon has reached its usage limit.")

        if order_amount < self.minimum_order_amount:
            return False, _(
                f"Minimum order amount is ${self.minimum_order_amount}."
            )

        # Per-user check
        if user and self.max_uses_per_user > 0:
            user_uses = CouponUsage.objects.filter(
                coupon=self, user=user
            ).count()
            if user_uses >= self.max_uses_per_user:
                return False, _("You have already used this coupon.")

        return True, ""

    def calculate_discount(self, amount):
        """
        Calculate discount amount for a given price.
        Returns the discount amount (not the final price).
        """
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = amount * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = min(self.discount_value, amount)

        return round(discount, 2)

    def apply(self, amount):
        """
        Apply coupon to an amount.
        Returns (final_price, discount_amount).
        """
        discount = self.calculate_discount(amount)
        final = max(amount - discount, 0)
        return round(final, 2), discount

    def record_usage(self, user=None):
        """Record a coupon usage."""
        self.times_used += 1
        self.save(update_fields=["times_used"])
        if user:
            CouponUsage.objects.create(coupon=self, user=user)


class CouponUsage(models.Model):
    """Track per-user coupon usage."""
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "django_rseal"
        verbose_name = _("Coupon Usage")
        verbose_name_plural = _("Coupon Usages")

    def __str__(self):
        return f"{self.user} used {self.coupon.code} at {self.used_at}"
