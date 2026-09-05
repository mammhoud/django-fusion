"""Render-first pages and HTMX interactions for Loop-CRM."""
from __future__ import annotations

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import OperationalError, ProgrammingError, transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django_fusion.tasks.views import TaskCenterView as FusionTaskCenterView

from apps.crm.custom_fields import custom_object_catalog
from apps.crm.models import CustomObjectDefinition
from apps.marketing.connectors import platform_catalog

from .forms import WorkflowDefinitionForm
from .importer import EXPECTED_COLUMNS, IMPORTABLE_OBJECTS, import_rows, parse_csv
from .models import (
    AuditLog,
    EmailAccount,
    EmailMessage,
    SavedView,
    UserProfile,
    WorkflowDefinition,
    WorkflowRun,
)
from .navigation import breadcrumbs_for, module_by_id, navigation_context
from .permissions import (
    can_manage_deals,
    can_manage_posts,
    is_marketing,
    is_revops,
    is_sales,
    role_of,
)
from .realtime import safe_publish_workspace_event
from .resource_tables import resource_table
from .resources import resolve_resource
from .tables import MemberTable
from .tenancy import current_workspace_id
from .workflows import (
    WORKFLOW_ACTION_CATALOG,
    graph_from_actions,
    normalize_workflow_graph,
    trigger_catalog,
    workflow_action_catalog,
)


def is_htmx_request(request: HttpRequest) -> bool:
    """Detect HTMX without requiring a project-specific middleware package."""
    return request.headers.get("HX-Request", "").lower() == "true"


def _workflow_queryset(workspace_id: int | None):
    """Workflows a caller may see: global templates + their own workspace's."""
    queryset = WorkflowDefinition.objects.all()
    if workspace_id is None:
        return queryset.filter(workspace__isnull=True)
    return queryset.filter(Q(workspace__isnull=True) | Q(workspace_id=workspace_id))


def workflow_rows(request: HttpRequest) -> list[WorkflowDefinition]:
    """Return persisted definitions the caller may see; an empty database stays an honest empty state."""
    try:
        return list(
            _workflow_queryset(current_workspace_id(request))
            .prefetch_related("runs")
            .exclude(status="archived")
            .order_by("name")
        )
    except (OperationalError, ProgrammingError):
        return []


def workflow_context(request: HttpRequest) -> dict:
    definitions = workflow_rows(request)
    workspace_id = current_workspace_id(request)
    runs = WorkflowRun.objects.select_related("definition")
    if workspace_id is None:
        runs = runs.filter(workspace__isnull=True)
    else:
        runs = runs.filter(Q(workspace__isnull=True) | Q(workspace_id=workspace_id))
    return {
        "workflows": definitions,
        "workflow_catalog": definitions,
        "recent_workflow_runs": list(runs.order_by("-queued_at")[:8])
        if definitions
        else [],
        "action_catalog": workflow_action_catalog(),
        "trigger_catalog": trigger_catalog(),
        # Serialized for the visual editor's vanilla-JS state.
        "action_catalog_json": json.dumps(workflow_action_catalog()),
        "trigger_catalog_json": json.dumps(trigger_catalog()),
        "workflows_json": json.dumps(
            [
                {
                    "id": d.pk,
                    "name": d.name,
                    "trigger": d.trigger,
                    "actions": list(d.actions or []),
                    "graph": d.graph
                    or graph_from_actions(d.trigger, list(d.actions or [])),
                }
                for d in definitions
            ]
        ),
    }


class LoopPageView(LoginRequiredMixin, TemplateView):
    """Shared page context for the dashboard, navigation, and subpages."""

    template_name = "dashboard/module.html"
    module_id = "overview"
    page_title = _("Overview")
    page_kicker = _("Workspace")
    page_description = _("")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "navigation": navigation_context(self.request.path),
                "breadcrumbs": breadcrumbs_for(self.request.path, self.page_title),
                "module": module_by_id(self.module_id),
                "page_title": self.page_title,
                "page_kicker": self.page_kicker,
                "page_description": self.page_description,
                "workflow_catalog": workflow_rows(self.request),
                "platform_catalog": platform_catalog(),
            }
        )
        return context


class DashboardView(LoopPageView):
    template_name = "dashboard/index.html"
    page_title = _("Revenue workspace")
    page_kicker = _("Loop CRM")
    page_description = _("From social impression to closed deal — one source of truth.")


class ModuleView(LoopPageView):
    """Generic subpage view: real navigation works before domain screens land."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_description"] = self.page_description or context["module"]["description"]
        return context


class TaskCenterView(FusionTaskCenterView):
    """Loop-CRM task history — shared audit trail merged with the website record."""

    template_name = "dashboard/tasks.html"
    site_name = "loop-crm"
    page_title = _("Tasks")
    page_kicker = _("Operations · background jobs")
    page_description = _("Workflow, attribution, publishing, and finance jobs — the shared audit trail merged with the website-local record.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "navigation": navigation_context(self.request.path),
                "breadcrumbs": breadcrumbs_for(self.request.path, self.page_title),
                "module": module_by_id("tasks"),
                "page_title": self.page_title,
                "page_kicker": self.page_kicker,
                "page_description": self.page_description,
            }
        )
        return context


class MemberListView(LoopPageView):
    """Role-aware member directory rendered through django-tables2."""

    template_name = "dashboard/members.html"
    module_id = "workspace"
    page_title = _("Members & roles")
    page_kicker = _("Workspace · access")
    page_description = _("See the live role and capability boundary for every workspace member.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        members = User.objects.select_related("profile", "profile__workspace")
        if workspace_id is not None:
            members = members.filter(profile__workspace_id=workspace_id)
        members = members.order_by("username", "email")
        context["member_table"] = MemberTable(members)
        context["role_matrix"] = [
            {
                "role": label,
                "key": key,
                "sales": key in {"super_admin", "sales_manager", "sales_rep"},
                "marketing": key in {"super_admin", "marketing_manager", "marketing_specialist"},
                "attribution": key in {"super_admin", "sales_manager", "marketing_manager", "revops_manager", "viewer"},
                "manage_deals": key in {"super_admin", "sales_manager", "revops_manager"},
                "manage_posts": key in {"super_admin", "marketing_manager", "revops_manager"},
            }
            for key, label in UserProfile.ROLE_CHOICES
        ]
        context["current_role"] = role_of(self.request.user)
        context["current_capabilities"] = {
            "sales": is_sales(self.request.user),
            "marketing": is_marketing(self.request.user),
            "revops": is_revops(self.request.user),
            "manage_deals": can_manage_deals(self.request.user),
            "manage_posts": can_manage_posts(self.request.user),
        }
        return context


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Show account identity and effective permissions without exposing tokens."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(
        request,
        "account/profile.html",
        {
            "profile": profile,
            "role": role_of(request.user),
            "capabilities": {
                "sales": is_sales(request.user),
                "marketing": is_marketing(request.user),
                "revops": is_revops(request.user),
                "manage_deals": can_manage_deals(request.user),
                "manage_posts": can_manage_posts(request.user),
            },
        },
    )


class AihubView(LoopPageView):
    """Consent-gated AI workspace surface with provider-neutral operations."""

    template_name = "dashboard/ai.html"
    module_id = "ai"
    page_title = _("AI Hub")
    page_kicker = _("Workspace · assisted operations")
    page_description = _(
        "Draft and score from CRM context without auto-publishing, auto-emailing, or hidden provider calls."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .ai import consent_enabled, operation_catalog, provider_catalog

        profile = getattr(self.request.user, "profile", None)
        context.update(
            {
                "ai_consent": consent_enabled(profile) if profile else False,
                "ai_operations": operation_catalog(),
                "ai_providers": provider_catalog(),
            }
        )
        return context


class WorkflowListView(LoopPageView):
    """Workspace workflow editor backed by WorkflowDefinition records."""

    template_name = "dashboard/workflows.html"
    module_id = "workspace"
    page_title = _("Workflows")
    page_kicker = _("Workspace · automation")
    page_description = _("Define triggers, review the action plan, and queue an auditable run.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(workflow_context(self.request))
        context["workflow_form"] = WorkflowDefinitionForm()
        return context


def _workflow_fragment_context(request: HttpRequest) -> dict:
    context = workflow_context(request)
    context["workflow_form"] = WorkflowDefinitionForm()
    return context


@require_POST
@login_required
def workflow_create(request: HttpRequest) -> HttpResponse:
    """Create a workflow and return only the updated HTMX list fragment."""
    form = WorkflowDefinitionForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "dashboard/partials/workflow_form.html",
            {"workflow_form": form},
            status=422,
        )
    workflow = form.save(commit=False)
    if getattr(request.user, "is_authenticated", False):
        workflow.created_by = request.user
        profile = getattr(request.user, "profile", None)
        workflow.workspace = getattr(profile, "workspace", None)
    workflow.save()
    safe_publish_workspace_event(
        workflow.workspace_id, "resource.created", {"resource": "workflows", "pk": workflow.pk}
    )
    response = render(
        request,
        "dashboard/partials/workflow_success.html",
        _workflow_fragment_context(request),
    )
    response["HX-Trigger"] = "workflowCreated"
    return response


@require_POST
@login_required
def workflow_steps_update(request: HttpRequest, pk: int) -> JsonResponse:
    """Update a workflow's trigger + ordered action steps from the visual editor.

    Actions are validated against the product action catalog so a client can
    never persist an executable step the executor does not know how to run.
    """
    workflow = get_object_or_404(_workflow_queryset(current_workspace_id(request)), pk=pk)
    try:
        payload = json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
    trigger = str(payload.get("trigger") or "").strip()
    actions = payload.get("actions")
    allowed_actions = {item["id"] for item in WORKFLOW_ACTION_CATALOG}
    if not trigger:
        return JsonResponse({"trigger": "A trigger is required."}, status=400)
    if not isinstance(actions, list) or not all(
        isinstance(action, str) and action.strip() in allowed_actions for action in actions
    ):
        return JsonResponse({"actions": "Actions must be an array of known action ids."}, status=400)
    workflow.trigger = trigger
    workflow.actions = [action.strip() for action in actions]
    # Keep the canvas topology in sync with the flat order so the two editors
    # never disagree (the step editor is the linear special case of the DAG).
    workflow.graph = graph_from_actions(trigger, workflow.actions)
    workflow.save(update_fields=["trigger", "actions", "graph", "updated_at"])
    safe_publish_workspace_event(
        workflow.workspace_id, "resource.updated", {"resource": "workflows", "pk": workflow.pk}
    )
    return JsonResponse({"id": workflow.pk, "trigger": workflow.trigger, "actions": workflow.actions})


@require_POST
@login_required
def workflow_graph_update(request: HttpRequest, pk: int) -> JsonResponse:
    """Persist the visual DAG (nodes + edges) for a workflow.

    The graph is validated as acyclic, trigger-rooted, and action-safe; the
    flat ``actions`` list is re-derived as the topological execution order so
    the executor, the step editor, and the Bolt road stay in lockstep.
    """
    workflow = get_object_or_404(_workflow_queryset(current_workspace_id(request)), pk=pk)
    try:
        payload = json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
    trigger = str(payload.get("trigger") or "").strip() or workflow.trigger
    allowed_actions = {item["id"] for item in WORKFLOW_ACTION_CATALOG}
    try:
        graph, actions = normalize_workflow_graph(payload, allowed_actions, trigger=trigger)
    except ValueError as exc:
        return JsonResponse({"graph": str(exc)}, status=400)
    workflow.trigger = trigger
    workflow.actions = actions
    workflow.graph = graph
    workflow.save(update_fields=["trigger", "actions", "graph", "updated_at"])
    safe_publish_workspace_event(
        workflow.workspace_id, "resource.updated", {"resource": "workflows", "pk": workflow.pk}
    )
    return JsonResponse({"id": workflow.pk, "trigger": trigger, "actions": actions, "graph": graph})


@require_POST
@login_required
def workflow_toggle(request: HttpRequest, pk: int) -> HttpResponse:
    """Toggle a workflow between active and paused, preserving its run history."""
    workflow = get_object_or_404(_workflow_queryset(current_workspace_id(request)), pk=pk)
    workflow.status = "paused" if workflow.status == "active" else "active"
    workflow.save(update_fields=["status", "updated_at"])
    safe_publish_workspace_event(
        workflow.workspace_id, "resource.updated", {"resource": "workflows", "pk": workflow.pk}
    )
    return render(
        request,
        "dashboard/partials/workflow_row.html",
        {"workflow": workflow},
    )


@require_POST
@login_required
@transaction.atomic
def workflow_run(request: HttpRequest, pk: int) -> HttpResponse:
    """Queue one workflow run and report the actual queue state to the user."""
    workflow = get_object_or_404(_workflow_queryset(current_workspace_id(request)), pk=pk)
    if workflow.status != "active":
        return JsonResponse({"detail": _("Only active workflows can be queued.")}, status=409)

    run = WorkflowRun.objects.create(
        definition=workflow,
        workspace=workflow.workspace,
        trigger_payload={"source": "manual", "path": request.path},
    )
    try:
        from plugins.workers.tasks import execute_workflow

        execute_workflow.send(run.pk)
    except Exception as exc:  # noqa: BLE001 - persist queue failure for operators
        run.status = "failed"
        run.error = f"Workflow queue unavailable: {exc.__class__.__name__}"
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error", "finished_at"])

    response = render(
        request,
        "dashboard/partials/workflow_run.html",
        {"run": run, "workflow": workflow},
    )
    response["HX-Trigger"] = "workflowQueued"
    return response


def navigation_fragment(request: HttpRequest) -> HttpResponse:
    """Return the complete navigator; only active flags depend on the path.

    Also carries ``workspace_id`` so the Astro shell (which is statically
    built and cannot know the tenant at build time) can open the same
    workspace-scoped SSE stream the render-first shell uses.
    """
    context = {
        "navigation": navigation_context(request.GET.get("path", request.path)),
        "navigation_fragment": True,
        "workspace_id": current_workspace_id(request),
    }
    template = (
        "dashboard/navigation_astro.html"
        if request.GET.get("variant") == "astro"
        else "dashboard/sidebar.html"
    )
    return render(request, template, context)


def navigation_api(request: HttpRequest) -> JsonResponse:
    """Expose the same navigation contract to the Astro shell before boot."""
    response = JsonResponse(
        {
            "version": 2,
            "navigation": navigation_context(request.GET.get("path", request.path)),
            "breadcrumbs": breadcrumbs_for(
                request.GET.get("path", request.path),
                request.GET.get("title", "Loop CRM"),
            ),
        }
    )
    response["Cache-Control"] = "private, max-age=300, stale-while-revalidate=60"
    response["Vary"] = "Cookie"
    return response


def _field_label(field_name: str) -> str:
    """Turn a read-field lookup like ``company__name`` into a column label."""
    return " ".join(part.replace("_", " ").title() for part in field_name.split("__"))


def _table(headers: list[str], rows: list[dict]) -> tuple[list[str], list[list[str]]]:
    """Flatten dict rows into a header list and aligned string cell rows."""
    return headers, [[str(row.get(key, "")) for key in headers] for row in rows]


class ResourceListView(LoopPageView):
    """Generic data-backed list screen for any registered API resource.

    Replaces the placeholder module card with a real, workspace-scoped table
    drawn from the same ``apps.core.resources`` registry that powers the JSON
    roads, so every navigation target resolves to live data.
    """

    template_name = "dashboard/resource_list.html"
    resource = ""
    empty_message = _("No records yet.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = resolve_resource(self.resource)
        table = {"headers": [], "rows": []}
        if resource:
            queryset = resource.model.objects.all()
            workspace_id = current_workspace_id(self.request)
            if workspace_id is not None and any(
                field.name == "workspace" for field in resource.model._meta.concrete_fields
            ):
                queryset = queryset.filter(workspace_id=workspace_id)
            try:
                # Render-first and both JSON roads now consume the same
                # django-fusion RowGenerator projection. Bolt remains the
                # canonical API boundary; this only removes presentation drift.
                table = resource_table(queryset, self.resource)
            except (OperationalError, ProgrammingError):
                table = {"headers": [], "rows": []}
        context.update(
            {
                "table_headers": [header["label"] for header in table["headers"]],
                "table_header_meta": table["headers"],
                "table_rows": table["rows"],
                "table_empty": self.empty_message,
            }
        )
        return context


class CustomFieldsView(LoopPageView):
    """Tenant custom-field catalog (Twenty-style extensibility)."""

    template_name = "dashboard/resource_list.html"
    module_id = "workspace"
    page_title = _("Custom fields")
    page_kicker = _("Workspace · custom fields")
    page_description = _("Built-in and workspace-defined field metadata for companies, contacts, deals, campaigns, and posts.")
    empty_message = _("No custom fields are defined.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        workspace = getattr(profile, "workspace", None) if profile else None
        catalog = custom_object_catalog(workspace)
        rows = []
        for obj in catalog:
            for field in obj["fields"]:
                rows.append(
                    {
                        "object": obj["label"],
                        "field": field["label"],
                        "key": field["key"],
                        "type": field["type"],
                    }
                )
        headers, table_rows = _table(["object", "field", "key", "type"], rows)
        context["table_headers"] = ["Object", "Field", "Key", "Type"]
        context["table_rows"] = table_rows
        context["table_empty"] = self.empty_message
        return context


class IntegrationsView(LoopPageView):
    """Provider-neutral connector catalog."""

    template_name = "dashboard/resource_list.html"
    module_id = "workspace"
    page_title = _("Integrations")
    page_kicker = _("Workspace · integrations")
    page_description = _("The social platform surface Loop-CRM can publish to, with the capabilities each connector advertises.")
    empty_message = _("No integrations are available.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = [
            {"platform": platform["label"], "capabilities": ", ".join(platform["capabilities"])}
            for platform in platform_catalog()
        ]
        headers, table_rows = _table(["platform", "capabilities"], rows)
        context["table_headers"] = ["Platform", "Capabilities"]
        context["table_rows"] = table_rows
        context["table_empty"] = self.empty_message
        return context


class EmailInboxView(LoopPageView):
    """Manage connected Gmail/Outlook mailboxes and start an OAuth connect."""

    template_name = "dashboard/email_inbox.html"
    module_id = "workspace"
    page_title = _("Email inbox")
    page_kicker = _("Workspace · email")
    page_description = _("Connect Gmail or Outlook to sync inbound messages into the CRM timeline, matched to contacts and deals.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        accounts = EmailAccount.objects.all()
        if workspace_id is not None:
            accounts = accounts.filter(workspace_id=workspace_id)
        context["email_accounts"] = list(accounts.select_related("workspace").order_by("-created_at"))

        messages = EmailMessage.objects.select_related("account", "contact", "deal")
        if workspace_id is not None:
            messages = messages.filter(workspace_id=workspace_id)
        context["email_messages"] = list(messages.order_by("-received_at")[:50])
        context["gmail_configured"] = bool(settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET)
        context["outlook_configured"] = bool(settings.OUTLOOK_CLIENT_ID and settings.OUTLOOK_CLIENT_SECRET)
        return context


class ReportsView(LoopPageView):
    """Real attribution/finance report: campaign revenue + pipeline value."""

    template_name = "dashboard/reports.html"
    module_id = "attribution"
    page_title = _("Revenue reports")
    page_kicker = _("Attribution · reports")
    page_description = _("Campaign revenue, pipeline value, and attribution touchpoints — workspace-scoped.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        from django.db.models import Count, Sum

        from apps.attribution.models import AttributionTouchpoint
        from apps.crm.models import Deal
        from apps.finance.models import RevenueEvent

        revenue = RevenueEvent.objects.all()
        deals = Deal.objects.all()
        touchpoints = AttributionTouchpoint.objects.all()
        if workspace_id is not None:
            revenue = revenue.filter(workspace_id=workspace_id)
            deals = deals.filter(workspace_id=workspace_id)
            touchpoints = touchpoints.filter(workspace_id=workspace_id)

        campaign_rows = []
        for row in revenue.values("campaign__name").annotate(total=Sum("amount"), count=Count("id")).order_by("-total"):
            campaign_rows.append(
                {"campaign": row["campaign__name"] or "Unattributed", "revenue": str(row["total"] or "0"), "events": row["count"]}
            )
        stage_rows = []
        for row in deals.values("stage__name").annotate(total=Sum("value"), count=Count("id")).order_by("stage__name"):
            stage_rows.append(
                {"stage": row["stage__name"] or "No stage", "value": str(row["total"] or "0"), "deals": row["count"]}
            )
        context["campaign_revenue"] = campaign_rows
        context["pipeline_value"] = stage_rows
        context["touchpoint_count"] = touchpoints.count()
        return context


class CustomObjectsView(LoopPageView):
    """Workspace-defined object types (runtime schema, validated JSON rows)."""

    template_name = "dashboard/resource_list.html"
    module_id = "workspace"
    page_title = _("Custom objects")
    page_kicker = _("Workspace · data model")
    page_description = _("Add a new record type without a migration — declarative fields with validated JSON rows.")
    empty_message = _("No custom objects are defined yet.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        definitions = CustomObjectDefinition.objects.filter(is_active=True)
        if workspace_id is not None:
            definitions = definitions.filter(workspace_id=workspace_id)
        rows = []
        for definition in definitions.order_by("name"):
            rows.append(
                {
                    "name": definition.name,
                    "key": definition.key,
                    "fields": len(definition.fields or []),
                    "records": definition.records.count(),
                }
            )
        headers, table_rows = _table(["name", "key", "fields", "records"], rows)
        context["table_headers"] = ["Name", "Key", "Fields", "Records"]
        context["table_rows"] = table_rows
        context["table_empty"] = self.empty_message
        return context


class CustomObjectRecordsView(LoopPageView):
    """One custom object's rows, columns derived from the definition schema."""

    template_name = "dashboard/resource_list.html"
    module_id = "workspace"
    page_title = _("Custom object records")
    page_kicker = _("Workspace · data model")
    page_description = _("Workspace-scoped rows for a custom object type.")
    empty_message = _("No records for this object yet.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        queryset = CustomObjectDefinition.objects.filter(is_active=True, key=self.kwargs["key"])
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        definition = get_object_or_404(queryset)
        field_keys = [field["key"] for field in (definition.fields or [])]
        headers = ["id", *field_keys, "updated_at"]
        rows = []
        for record in definition.records.order_by("-updated_at")[:100]:
            row = {"id": record.pk, **{key: record.data.get(key, "") for key in field_keys}}
            row["updated_at"] = record.updated_at.isoformat() if record.updated_at else ""
            rows.append(row)
        labels, table_rows = _table(headers, rows)
        context["table_headers"] = [_field_label(header) for header in labels]
        context["table_rows"] = table_rows
        context["table_empty"] = self.empty_message
        return context


class ImportView(LoopPageView):
    """CSV upload → tenant-scoped records for companies/contacts/deals."""

    template_name = "dashboard/import.html"
    module_id = "workspace"
    page_title = _("Import")
    page_kicker = _("Workspace · data")
    page_description = _("Import companies, contacts, and deals from a CSV upload — validated and workspace-scoped.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("import_object_types", IMPORTABLE_OBJECTS)
        context.setdefault("expected_columns", EXPECTED_COLUMNS)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        object_type = (request.POST.get("object_type") or "").strip()
        csv_file = request.FILES.get("csv_file")
        if object_type not in IMPORTABLE_OBJECTS:
            context["import_result"] = {"created": 0, "errors": [{"row": 0, "message": _("Choose a valid object type.")}]}
            return render(request, self.template_name, context, status=422)
        if csv_file is None:
            context["import_result"] = {"created": 0, "errors": [{"row": 0, "message": _("Choose a CSV file to upload.")}]}
            return render(request, self.template_name, context, status=422)
        try:
            text = csv_file.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            context["import_result"] = {"created": 0, "errors": [{"row": 0, "message": _("CSV must be UTF-8 encoded.")}]}
            return render(request, self.template_name, context, status=422)
        try:
            rows = parse_csv(text)
        except Exception as exc:  # noqa: BLE001 - surface a parse failure honestly
            context["import_result"] = {"created": 0, "errors": [{"row": 0, "message": f"Could not parse CSV: {exc}"}]}
            return render(request, self.template_name, context, status=422)
        if not rows:
            context["import_result"] = {"created": 0, "errors": [{"row": 0, "message": _("The CSV has no data rows.")}]}
            return render(request, self.template_name, context, status=422)
        result = import_rows(object_type, rows, current_workspace_id(request), request.user)
        context["import_result"] = result
        context["import_object_type"] = object_type
        return render(request, self.template_name, context)


class SavedViewsView(LoopPageView):
    """A member's saved list/kanban view configurations across resources."""

    template_name = "dashboard/resource_list.html"
    module_id = "workspace"
    page_title = _("Saved views")
    page_kicker = _("Workspace · views")
    page_description = _("Your persisted list and kanban view configurations for every resource.")
    empty_message = _("You have not saved any views yet.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        queryset = SavedView.objects.filter(user=self.request.user)
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        rows = [
            {
                "resource": view.resource,
                "name": view.name,
                "type": view.view_type,
                "default": "yes" if view.is_default else "",
            }
            for view in queryset.order_by("resource", "name")
        ]
        headers, table_rows = _table(["resource", "name", "type", "default"], rows)
        context["table_headers"] = ["Resource", "Name", "Type", "Default"]
        context["table_rows"] = table_rows
        context["table_empty"] = self.empty_message
        return context


class AuditLogView(LoopPageView):
    """Append-only workspace audit trail."""

    template_name = "dashboard/resource_list.html"
    module_id = "workspace"
    page_title = _("Audit log")
    page_kicker = _("Workspace · audit")
    page_description = _("The write-once record of workspace mutations, newest first.")
    empty_message = _("No audit events have been recorded.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        queryset = AuditLog.objects.select_related("user")
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        rows = list(
            queryset.order_by("-created_at")[:50].values(
                "action", "model_name", "object_id", "created_at", "user__username"
            )
        )
        for row in rows:
            if row["created_at"]:
                row["created_at"] = row["created_at"].isoformat()
        headers, table_rows = _table(["action", "model_name", "object_id", "created_at", "user__username"], rows)
        context["table_headers"] = ["Action", "Model", "Object", "When", "User"]
        context["table_rows"] = table_rows
        context["table_empty"] = self.empty_message
        return context
