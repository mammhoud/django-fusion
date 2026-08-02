"""Concrete CMS coupon models built on django-fusion's shared bases."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel

from django_fusion.models.coupon import (
    AbstractCoupon,
    AbstractCouponUsage,
    generate_coupon_code,
)

# Keep the migration-serialized callable importable for existing databases.
_generate_code = generate_coupon_code


class Coupon(AbstractCoupon):
    """Admin-managed CMS coupon."""

    panels = [
        MultiFieldPanel([FieldPanel("code"), FieldPanel("name"), FieldPanel("is_active")], heading=_("Identity")),
        MultiFieldPanel([
            FieldRowPanel([FieldPanel("discount_type"), FieldPanel("discount_value")]),
            FieldPanel("max_discount_amount"),
            FieldPanel("minimum_order_amount"),
        ], heading=_("Discount")),
        MultiFieldPanel([
            FieldRowPanel([FieldPanel("valid_from"), FieldPanel("valid_until")]),
        ], heading=_("Validity Period")),
        MultiFieldPanel([
            FieldRowPanel([FieldPanel("max_uses"), FieldPanel("max_uses_per_user")]),
            FieldPanel("times_used"),
        ], heading=_("Usage Limits")),
    ]

    class Meta:
        app_label = "shared"
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")
        ordering = ["-is_active", "-created_at"]


class CouponUsage(AbstractCouponUsage):
    """Concrete CMS per-user coupon usage record."""

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")

    class Meta:
        app_label = "shared"
        verbose_name = _("Coupon Usage")
        verbose_name_plural = _("Coupon Usages")
