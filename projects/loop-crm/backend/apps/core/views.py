"""Render-first pages and HTMX interactions for Loop-CRM."""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import OperationalError, ProgrammingError, transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django_fusion.tasks.views import TaskCenterView as FusionTaskCenterView

from apps.marketing.connectors import platform_catalog

from .forms import WorkflowDefinitionForm
from .models import UserProfile, WorkflowDefinition, WorkflowRun
from .navigation import breadcrumbs_for, module_by_id, navigation_context
from .permissions import (
    can_manage_deals,
    can_manage_posts,
    is_marketing,
    is_revops,
    is_sales,
    role_of,
)
from .tables import MemberTable


def is_htmx_request(request: HttpRequest) -> bool:
    """Detect HTMX without requiring a project-specific middleware package."""
    return request.headers.get("HX-Request", "").lower() == "true"


def workflow_rows() -> list[WorkflowDefinition]:
    """Return persisted definitions; an empty database stays an honest empty state."""
    try:
        return list(
            WorkflowDefinition.objects.prefetch_related("runs")
            .exclude(status="archived")
            .order_by("name")
        )
    except (OperationalError, ProgrammingError):
        return []


def workflow_context() -> dict:
    definitions = workflow_rows()
    return {
        "workflows": definitions,
        "workflow_catalog": definitions,
        "recent_workflow_runs": list(
            WorkflowRun.objects.select_related("definition").order_by("-queued_at")[:8]
        )
        if definitions
        else [],
    }


class LoopPageView(TemplateView):
    """Shared page context for the dashboard, navigation, and subpages."""

    template_name = "dashboard/module.html"
    module_id = "overview"
    page_title = "Overview"
    page_kicker = "Workspace"
    page_description = ""

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
                "workflow_catalog": workflow_rows(),
                "platform_catalog": platform_catalog(),
            }
        )
        return context


class DashboardView(LoopPageView):
    template_name = "dashboard/index.html"
    page_title = "Revenue workspace"
    page_kicker = "Loop CRM"
    page_description = "From social impression to closed deal — one source of truth."


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
    page_title = "Tasks"
    page_kicker = "Operations · background jobs"
    page_description = "Workflow, attribution, publishing, and finance jobs — the shared audit trail merged with the website-local record."

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
    page_title = "Members & roles"
    page_kicker = "Workspace · access"
    page_description = "See the live role and capability boundary for every workspace member."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = User.objects.select_related("profile", "profile__workspace").order_by("username", "email")
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


class WorkflowListView(LoopPageView):
    """Workspace workflow editor backed by WorkflowDefinition records."""

    template_name = "dashboard/workflows.html"
    module_id = "workspace"
    page_title = "Workflows"
    page_kicker = "Workspace · automation"
    page_description = "Define triggers, review the action plan, and queue an auditable run."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(workflow_context())
        context["workflow_form"] = WorkflowDefinitionForm()
        return context


def _workflow_fragment_context() -> dict:
    context = workflow_context()
    context["workflow_form"] = WorkflowDefinitionForm()
    return context


@require_POST
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
    response = render(
        request,
        "dashboard/partials/workflow_success.html",
        _workflow_fragment_context(),
    )
    response["HX-Trigger"] = "workflowCreated"
    return response


@require_POST
def workflow_toggle(request: HttpRequest, pk: int) -> HttpResponse:
    """Toggle a workflow between active and paused, preserving its run history."""
    workflow = get_object_or_404(WorkflowDefinition, pk=pk)
    workflow.status = "paused" if workflow.status == "active" else "active"
    workflow.save(update_fields=["status", "updated_at"])
    return render(
        request,
        "dashboard/partials/workflow_row.html",
        {"workflow": workflow},
    )


@require_POST
@transaction.atomic
def workflow_run(request: HttpRequest, pk: int) -> HttpResponse:
    """Queue one workflow run and report the actual queue state to the user."""
    workflow = get_object_or_404(WorkflowDefinition, pk=pk)
    if workflow.status != "active":
        return JsonResponse({"detail": "Only active workflows can be queued."}, status=409)

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
    """Return the complete navigator; only active flags depend on the path."""
    context = {
        "navigation": navigation_context(request.GET.get("path", request.path)),
        "navigation_fragment": True,
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
