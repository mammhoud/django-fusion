"""
CRM models — Company, Contact, Pipeline, Stage, Deal, Activity, CRMNote.

Replaces the deleted shared/cloud/crm_models.py.
Used by pos-full/sidecar/routes/crm.py.

@tested pos-full — CRM models for Robyn server
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """CRM Company entity."""

    name = models.CharField(_("name"), max_length=200)
    website = models.URLField(_("website"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    address = models.TextField(_("address"), blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    industry = models.CharField(_("industry"), max_length=100, blank=True)
    description = models.TextField(_("description"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_companies"
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Pipeline(models.Model):
    """CRM Pipeline — a collection of stages deals flow through."""

    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    is_default = models.BooleanField(_("default"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    display_order = models.IntegerField(_("display order"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_pipelines"
        verbose_name = _("pipeline")
        verbose_name_plural = _("pipelines")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class Stage(models.Model):
    """CRM Stage — a step within a pipeline."""

    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="stages",
        verbose_name=_("pipeline"),
    )
    name = models.CharField(_("name"), max_length=200)
    display_order = models.IntegerField(_("display order"), default=0)
    probability = models.IntegerField(_("probability (%)"), default=0)
    color = models.CharField(_("color"), max_length=20, default="#6366f1")
    is_active = models.BooleanField(_("active"), default=True)
    is_won_stage = models.BooleanField(_("won stage"), default=False)
    is_lost_stage = models.BooleanField(_("lost stage"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_stages"
        verbose_name = _("stage")
        verbose_name_plural = _("stages")
        ordering = ["pipeline", "display_order"]

    def __str__(self) -> str:
        return f"{self.pipeline.name} → {self.name}"


class Contact(models.Model):
    """CRM Contact entity — linked to Company."""

    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contacts", verbose_name=_("company"),
    )
    first_name = models.CharField(_("first name"), max_length=200)
    last_name = models.CharField(_("last name"), max_length=200)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    mobile = models.CharField(_("mobile"), max_length=50, blank=True)
    job_title = models.CharField(_("job title"), max_length=200, blank=True)
    source = models.CharField(_("source"), max_length=100, blank=True)
    notes = models.TextField(_("notes"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    pos_customer_id = models.IntegerField(
        _("POS customer ID"), blank=True, null=True, editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_contacts"
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Deal(models.Model):
    """CRM Deal entity — tracked in pipeline stages."""

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deals", verbose_name=_("contact"),
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deals", verbose_name=_("company"),
    )
    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.PROTECT, null=True, blank=True,
        related_name="deals", verbose_name=_("pipeline"),
    )
    stage = models.ForeignKey(
        Stage, on_delete=models.PROTECT, null=True, blank=True,
        related_name="deals", verbose_name=_("stage"),
    )
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    value = models.DecimalField(_("value"), max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(_("currency"), max_length=3, default="USD")
    probability = models.IntegerField(_("probability (%)"), default=10)
    expected_close_date = models.DateField(_("expected close date"), blank=True, null=True)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_won = models.BooleanField(_("won"), default=False)
    lost_reason = models.TextField(_("lost reason"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_deals"
        verbose_name = _("deal")
        verbose_name_plural = _("deals")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.stage.name if self.stage else 'no stage'})"


class Activity(models.Model):
    """CRM Activity — calls, meetings, emails, tasks linked to contacts/deals."""

    ACTIVITY_TYPES = [
        ("call", _("Call")),
        ("meeting", _("Meeting")),
        ("email", _("Email")),
        ("task", _("Task")),
        ("note", _("Note")),
        ("other", _("Other")),
    ]

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name=_("contact"),
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name=_("deal"),
    )
    activity_type = models.CharField(_("type"), max_length=20, choices=ACTIVITY_TYPES, default="note")
    subject = models.CharField(_("subject"), max_length=300)
    description = models.TextField(_("description"), blank=True)
    is_completed = models.BooleanField(_("completed"), default=False)
    due_date = models.DateTimeField(_("due date"), blank=True, null=True)
    completed_at = models.DateTimeField(_("completed at"), blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_activities"
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_activity_type_display()}: {self.subject}"


class CRMNote(models.Model):
    """CRM Note — pinned/unpinned notes linked to contacts/deals."""

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="notes", verbose_name=_("contact"),
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="notes", verbose_name=_("deal"),
    )
    content = models.TextField(_("content"))
    is_pinned = models.BooleanField(_("pinned"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared_models"
        db_table = "pos_crm_notes"
        verbose_name = _("CRM note")
        verbose_name_plural = _("CRM notes")
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self) -> str:
        return f"Note {self.id} ({'pinned' if self.is_pinned else 'unpinned'})"
