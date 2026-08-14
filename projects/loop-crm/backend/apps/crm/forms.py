"""Validated forms for CRM relationship-graph interactions."""
from __future__ import annotations

from django import forms

from apps.core.models import Workspace
from apps.marketing.models import Campaign

from .models import Company, Contact, Deal, Pipeline, PipelineStage


def _request_profile(request):
    if not request:
        return None
    try:
        return request.user.profile
    except Exception:  # noqa: BLE001 - legacy accounts may predate UserProfile
        return None


class WorkspaceScopedForm(forms.ModelForm):
    """Limit selectable workspaces to the signed-in member's workspace."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        profile = _request_profile(request)
        workspace = getattr(profile, "workspace", None) if profile else None
        if workspace is not None and "workspace" in self.fields:
            self.fields["workspace"].queryset = Workspace.objects.filter(pk=workspace.pk)

    def clean_workspace(self):
        workspace = self.cleaned_data["workspace"]
        profile = _request_profile(getattr(self, "request", None))
        member_workspace = getattr(profile, "workspace_id", None)
        if member_workspace is not None and workspace.pk != member_workspace:
            raise forms.ValidationError("Choose a record from your current workspace.")
        return workspace


class CompanyForm(WorkspaceScopedForm):
    class Meta:
        model = Company
        fields = [
            "workspace",
            "name",
            "industry",
            "website",
            "email",
            "phone",
            "city",
            "country",
            "annual_revenue",
            "employee_count",
            "description",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Northline Studio"}),
            "industry": forms.TextInput(attrs={"placeholder": "Architecture"}),
            "website": forms.URLInput(attrs={"placeholder": "https://northline.example"}),
            "email": forms.EmailInput(attrs={"placeholder": "hello@northline.example"}),
            "phone": forms.TextInput(attrs={"placeholder": "+1 312 847 1928"}),
            "city": forms.TextInput(attrs={"placeholder": "Chicago"}),
            "country": forms.TextInput(attrs={"placeholder": "United States"}),
            "annual_revenue": forms.NumberInput(attrs={"step": "0.01", "placeholder": "480000.00"}),
            "employee_count": forms.NumberInput(attrs={"min": "1", "placeholder": "18"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "What does this company need to accomplish?"}),
        }

    def save(self, commit=True):
        company = super().save(commit=False)
        user = getattr(getattr(self, "request", None), "user", None)
        if getattr(user, "is_authenticated", False):
            company.owner = user
        if commit:
            company.save()
        return company


class ContactForm(WorkspaceScopedForm):
    class Meta:
        model = Contact
        fields = [
            "workspace",
            "company",
            "first_name",
            "last_name",
            "email",
            "phone",
            "title",
            "linkedin_url",
        ]
        widgets = {
            "company": forms.Select(),
            "first_name": forms.TextInput(attrs={"placeholder": "Mara"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Ellison"}),
            "email": forms.EmailInput(attrs={"placeholder": "mara@northline.example"}),
            "phone": forms.TextInput(attrs={"placeholder": "+1 312 847 1928"}),
            "title": forms.TextInput(attrs={"placeholder": "Operations lead"}),
            "linkedin_url": forms.URLInput(attrs={"placeholder": "https://linkedin.com/in/..."}),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields["company"].queryset = Company.objects.select_related("workspace").order_by("name")
        profile_workspace_id = getattr(_request_profile(request), "workspace_id", None)
        if profile_workspace_id is not None:
            self.fields["company"].queryset = self.fields["company"].queryset.filter(workspace_id=profile_workspace_id)

    def clean(self):
        cleaned = super().clean()
        workspace = cleaned.get("workspace")
        company = cleaned.get("company")
        if workspace and company and company.workspace_id != workspace.pk:
            self.add_error("company", "The company must belong to the selected workspace.")
        return cleaned

    def save(self, commit=True):
        contact = super().save(commit=False)
        user = getattr(getattr(self, "request", None), "user", None)
        if getattr(user, "is_authenticated", False):
            contact.owner = user
        if commit:
            contact.save()
        return contact


class DealForm(WorkspaceScopedForm):
    class Meta:
        model = Deal
        fields = [
            "workspace",
            "company",
            "contact",
            "name",
            "value",
            "pipeline",
            "stage",
            "expected_close_date",
            "campaign",
        ]
        widgets = {
            "company": forms.Select(),
            "contact": forms.Select(),
            "name": forms.TextInput(attrs={"placeholder": "Northline annual planning"}),
            "value": forms.NumberInput(attrs={"step": "0.01", "placeholder": "92500.00"}),
            "pipeline": forms.Select(),
            "stage": forms.Select(),
            "expected_close_date": forms.DateInput(attrs={"type": "date"}),
            "campaign": forms.Select(),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        profile_workspace_id = getattr(_request_profile(request), "workspace_id", None)
        self.fields["company"].queryset = Company.objects.order_by("name")
        self.fields["contact"].queryset = Contact.objects.select_related("company").order_by("last_name", "first_name")
        self.fields["pipeline"].queryset = Pipeline.objects.order_by("order", "name")
        self.fields["stage"].queryset = PipelineStage.objects.select_related("pipeline").order_by("pipeline__order", "order")
        self.fields["campaign"].queryset = Campaign.objects.order_by("-created_at")
        if profile_workspace_id is not None:
            for field_name in ("company", "contact", "pipeline", "campaign"):
                self.fields[field_name].queryset = self.fields[field_name].queryset.filter(workspace_id=profile_workspace_id)
            self.fields["stage"].queryset = self.fields["stage"].queryset.filter(pipeline__workspace_id=profile_workspace_id)

    def clean(self):
        cleaned = super().clean()
        workspace = cleaned.get("workspace")
        company = cleaned.get("company")
        contact = cleaned.get("contact")
        pipeline = cleaned.get("pipeline")
        stage = cleaned.get("stage")
        campaign = cleaned.get("campaign")
        if workspace:
            for field_name, related in (("company", company), ("contact", contact), ("pipeline", pipeline), ("campaign", campaign)):
                if related and related.workspace_id != workspace.pk:
                    self.add_error(field_name, "This record must belong to the selected workspace.")
            if stage and stage.pipeline.workspace_id != workspace.pk:
                self.add_error("stage", "The stage must belong to the selected workspace.")
        if company and contact and contact.company_id != company.pk:
            self.add_error("contact", "The contact must belong to the selected company.")
        if pipeline and stage and stage.pipeline_id != pipeline.pk:
            self.add_error("stage", "The stage must belong to the selected pipeline.")
        return cleaned

    def save(self, commit=True):
        deal = super().save(commit=False)
        user = getattr(getattr(self, "request", None), "user", None)
        if getattr(user, "is_authenticated", False):
            deal.owner = user
        if commit:
            deal.save()
        return deal
