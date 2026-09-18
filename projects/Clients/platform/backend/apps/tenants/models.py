"""Course Center registry models — shared public schema for django-tenants.

All django-tenants imports are lazily resolved at class-definition time
so the module loads cleanly under SQLite (where the backend is inactive).
The ``auto_create_schema`` gate mirrors Formint Cloud's proven pattern:
it only fires when ``TENANCY_ENABLED`` is True (PostgreSQL).

Model map:
    CenterPlan       — subscription tier (free / starter / pro)
    CourseCenter     — one PostgreSQL schema per org (TenantMixin)
    CourseDomain     — domain → center mapping (DomainMixin)
    CenterRegistration — pending signup before CourseCenter provisioned

Roles per center (Django groups, created inside the tenant schema):
    instructor  — create & manage courses, modules, lessons
    student     — enroll, complete courses, view progress
    editor      — Wagtail pages + StreamField blocks
    admin       — center owner: users, billing, settings
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ── Lazy django-tenants bases (SQLite-safe) ──────────────────────────
try:
    from django_tenants.models import DomainMixin, TenantMixin
except ImportError:  # pragma: no cover — django-tenants is always installed
    TenantMixin = object  # type: ignore[misc,assignment]
    DomainMixin = object  # type: ignore[misc,assignment]


# ══════════════════════════════════════════════════════════════════════
# CenterPlan — subscription tier (shared public schema)
# ══════════════════════════════════════════════════════════════════════
class CenterPlan(models.Model):
    """What a Course Center gets for its subscription level."""

    class Slug(models.TextChoices):
        FREE = "free", _("Free")
        STARTER = "starter", _("Starter")
        PRO = "pro", _("Pro")

    name = models.CharField(_("name"), max_length=100)
    slug = models.CharField(
        _("slug"),
        max_length=20,
        unique=True,
        choices=Slug.choices,
    )
    max_courses = models.PositiveSmallIntegerField(
        _("max courses"),
        default=5,
        help_text=_("Maximum published courses (0 = unlimited)."),
    )
    max_instructors = models.PositiveSmallIntegerField(
        _("max instructors"),
        default=1,
        help_text=_("Maximum instructor accounts (0 = unlimited)."),
    )
    max_students = models.PositiveSmallIntegerField(
        _("max students"),
        default=50,
        help_text=_("Maximum enrolled students (0 = unlimited)."),
    )
    custom_domain = models.BooleanField(
        _("custom domain"),
        default=False,
        help_text=_("Can the center use its own domain?"),
    )
    custom_branding = models.BooleanField(
        _("custom branding"),
        default=False,
        help_text=_("Can the center customize logo/colors/landing page?"),
    )
    analytics = models.BooleanField(
        _("analytics"),
        default=False,
        help_text=_("Student progress & enrollment analytics dashboard?"),
    )
    trial_days = models.PositiveSmallIntegerField(_("trial days"), default=14)
    is_active = models.BooleanField(_("active"), default=True)
    features = models.JSONField(
        _("features"),
        default=dict,
        blank=True,
        help_text=_("Display metadata: icon, description, highlights."),
    )

    class Meta:
        verbose_name = _("center plan")
        verbose_name_plural = _("center plans")
        ordering = ["slug"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


# ══════════════════════════════════════════════════════════════════════
# CourseCenter — one PostgreSQL schema per organisation (TenantMixin)
# ══════════════════════════════════════════════════════════════════════
class CourseCenter(TenantMixin):
    """A course center / training organisation with its own schema.

    ``schema_name`` is provided by TenantMixin and doubles as the center's
    URL slug. ``auto_create_schema`` is gated on ``TENANCY_ENABLED`` so
    CREATE SCHEMA never fires under SQLite.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        SUSPENDED = "suspended", _("Suspended")
        ARCHIVED = "archived", _("Archived")
        DELETED = "deleted", _("Deleted")

    organization_name = models.CharField(
        _("organization name"),
        max_length=200,
        db_index=True,
    )
    slug = models.SlugField(
        _("slug"),
        max_length=63,
        unique=True,
        help_text=_("URL-safe center identifier (also the schema name)."),
    )
    plan = models.ForeignKey(
        CenterPlan,
        on_delete=models.PROTECT,
        related_name="centers",
        verbose_name=_("plan"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    tagline = models.CharField(
        _("tagline"),
        max_length=255,
        blank=True,
        help_text=_("One-line description for the center's landing page."),
    )
    settings = models.JSONField(
        _("settings"),
        default=dict,
        blank=True,
        help_text=_(
            "Per-center overrides: site_name, primary_color, logo_url, "
            "smtp_*, social_providers, allow_self_signup, require_mfa."
        ),
    )
    subscription_id = models.CharField(
        _("subscription ID"),
        max_length=255,
        blank=True,
        help_text=_("External billing reference (deferred to Loop-CRM)."),
    )
    trial_ends_at = models.DateTimeField(_("trial ends"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), default=timezone.now)

    auto_create_schema = getattr(settings, "TENANCY_ENABLED", False)

    class Meta:
        verbose_name = _("course center")
        verbose_name_plural = _("course centers")
        ordering = ["organization_name"]

    def __str__(self):
        return f"{self.organization_name} ({self.slug})"

    @property
    def primary_domain(self):
        return self.domains.filter(is_primary=True).first()


# ══════════════════════════════════════════════════════════════════════
# CourseDomain — domain → center mapping (DomainMixin)
# ══════════════════════════════════════════════════════════════════════
class CourseDomain(DomainMixin):
    """Maps a hostname or path slug to a CourseCenter.

    ``DomainMixin`` already provides a ``tenant`` FK → CourseCenter (via
    ``settings.TENANT_MODEL``) and a ``domain`` field.  We only add the
    ``is_primary`` flag so a center can have multiple domains with one
    designated as the canonical landing URL.
    """

    is_primary = models.BooleanField(
        _("primary"),
        default=True,
        help_text=_("Canonical domain for this center."),
    )

    class Meta:
        verbose_name = _("course domain")
        verbose_name_plural = _("course domains")


# ══════════════════════════════════════════════════════════════════════
# CenterRegistration — pending signup before CourseCenter provisioned
# ══════════════════════════════════════════════════════════════════════
class CenterRegistration(models.Model):
    """Two-step signup: verify email → approve → provision center + schema."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        VERIFIED = "verified", _("Verified")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    email = models.EmailField(_("email"), db_index=True)
    organization_name = models.CharField(_("organization name"), max_length=200)
    plan = models.ForeignKey(
        CenterPlan,
        on_delete=models.PROTECT,
        related_name="registrations",
        verbose_name=_("plan"),
    )
    subdomain = models.SlugField(
        _("subdomain"),
        max_length=63,
        help_text=_("Desired URL slug (checked for uniqueness)."),
    )
    tagline = models.CharField(
        _("tagline"),
        max_length=255,
        blank=True,
        help_text=_("What courses will this center offer?"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    verification_token = models.UUIDField(
        _("verification token"),
        null=True,
        blank=True,
        unique=True,
    )
    created_at = models.DateTimeField(_("created"), default=timezone.now)

    class Meta:
        verbose_name = _("center registration")
        verbose_name_plural = _("center registrations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization_name} <{self.email}> [{self.status}]"