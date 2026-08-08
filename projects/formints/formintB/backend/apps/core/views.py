"""POS Cloud — REST API views with django-fusion viewsets + filters."""

from django_fusion.routes.models.crud import ModelViewset
from django_fusion.routes.core.base import viewprop
from django_fusion.fragments.forms.search import SearchableViewMixin
from django_filters import rest_framework as filters

from .models import (
    Organization, Branch, Lead, Contact, Deal,
    InventoryReport, BranchReport,
)


# ══════════════════════════════════════════════════════════════════════
# Filters
# ══════════════════════════════════════════════════════════════════════

class LeadFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Lead.LEAD_STATUS_CHOICES)
    source = filters.ChoiceFilter(choices=Lead.LEAD_SOURCE_CHOICES)
    organization = filters.NumberFilter(field_name="organization_id")
    branch = filters.NumberFilter(field_name="branch_id")
    assigned_to = filters.NumberFilter(field_name="assigned_to_id")

    class Meta:
        model = Lead
        fields = ["status", "source", "organization", "branch", "assigned_to"]


class InventoryReportFilter(filters.FilterSet):
    report_type = filters.ChoiceFilter(choices=InventoryReport.REPORT_TYPES)
    organization = filters.NumberFilter(field_name="organization_id")
    date_from = filters.DateFilter(field_name="date_from", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="date_to", lookup_expr="lte")

    class Meta:
        model = InventoryReport
        fields = ["report_type", "organization"]


class BranchReportFilter(filters.FilterSet):
    report_type = filters.ChoiceFilter(choices=BranchReport.REPORT_TYPES)
    branch = filters.NumberFilter(field_name="branch_id")
    organization = filters.NumberFilter(field_name="organization_id")
    date_from = filters.DateFilter(field_name="date_from", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="date_to", lookup_expr="lte")

    class Meta:
        model = BranchReport
        fields = ["report_type", "branch", "organization"]


# ══════════════════════════════════════════════════════════════════════
# Viewsets
# ══════════════════════════════════════════════════════════════════════

class OrganizationViewSet(ModelViewset):
    model = Organization
    url_prefix = "organizations"
    url_namespace = "organizations"
    list_display = ["name", "slug", "subscription_plan", "is_active"]


class BranchViewSet(ModelViewset):
    model = Branch
    url_prefix = "branches"
    url_namespace = "branches"
    list_display = ["name", "code", "organization", "pos_type", "is_active"]


class LeadViewSet(SearchableViewMixin, ModelViewset):
    model = Lead
    url_prefix = "leads"
    url_namespace = "leads"
    list_display = [
        "first_name", "last_name", "email", "status", "source",
        "organization", "assigned_to", "created_at",
    ]
    filterset_class = LeadFilter
    search_fields = ["first_name", "last_name", "email", "company_name"]


class ContactViewSet(SearchableViewMixin, ModelViewset):
    model = Contact
    url_prefix = "contacts"
    url_namespace = "contacts"
    list_display = ["first_name", "last_name", "email", "organization"]
    search_fields = ["first_name", "last_name", "email"]


class DealViewSet(ModelViewset):
    model = Deal
    url_prefix = "deals"
    url_namespace = "deals"
    list_display = ["title", "organization", "stage", "value", "created_at"]


class InventoryReportViewSet(ModelViewset):
    model = InventoryReport
    url_prefix = "inventory-reports"
    url_namespace = "inventory_reports"
    list_display = ["title", "report_type", "organization", "created_at"]
    filterset_class = InventoryReportFilter

    @viewprop
    def generate_report(self, request, **kwargs):
        """POST /api/inventory-reports/generate — Generate a new inventory report."""
        from datetime import date
        data = request.json()
        org = Organization.objects.get(id=data["organization_id"])
        branches = Branch.objects.filter(organization=org, is_active=True)
        report = InventoryReport.objects.create(
            organization=org,
            title=data.get("title", f"Inventory Report {date.today()}"),
            report_type=data.get("report_type", "stock_level"),
            date_from=data.get("date_from"),
            date_to=data.get("date_to"),
            generated_by=request.user if request.user.is_authenticated else None,
            summary={"branches": branches.count(), "status": "generated"},
        )
        report.branches.set(branches)
        return {"status": "generated", "report_id": report.id}


class BranchReportViewSet(ModelViewset):
    model = BranchReport
    url_prefix = "branch-reports"
    url_namespace = "branch_reports"
    list_display = ["title", "report_type", "branch", "date_from", "date_to", "created_at"]
    filterset_class = BranchReportFilter

    @viewprop
    def generate_report(self, request, **kwargs):
        """POST /api/branch-reports/generate — Generate a new branch report."""
        from datetime import date
        data = request.json()
        branch = Branch.objects.get(id=data["branch_id"])
        report = BranchReport.objects.create(
            organization=branch.organization,
            branch=branch,
            title=data.get("title", f"{branch.name} Report {date.today()}"),
            report_type=data.get("report_type", "daily_sales"),
            date_from=data.get("date_from", date.today()),
            date_to=data.get("date_to", date.today()),
            category_filter=data.get("category_filter", ""),
            employee_filter=data.get("employee_filter", ""),
            format=data.get("format", "json"),
            summary={"status": "generated", "branch": branch.name},
        )
        return {"status": "generated", "report_id": report.id}
