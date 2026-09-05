"""Compatibility JSON endpoints for the Loop-CRM shell.

The canonical API is ``apps.core.bolt_api`` when django-bolt is installed.
These views keep the same resource contract available to older Django clients.
"""

from __future__ import annotations

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from django_fusion.plugins.apis.auth import (
    FusionTokenError,
    TokenUserError,
    refresh_payload,
    user_token_payload,
    verify_request_user,
)

from apps.core.permissions import (
    can_manage_deals,
    can_manage_posts,
    is_marketing,
    is_revops,
    is_sales,
)
from apps.crm.custom_fields import custom_object_catalog
from apps.marketing.connectors import platform_catalog

from .bolt_api import RESOURCE_MODELS
from .export import resource_export_rows, to_csv
from .realtime import safe_publish_workspace_event
from .resource_tables import resource_table
from .resources import (
    RESOURCES,
    bounded_int,
    count_rows,
    create_row,
    delete_row,
    get_row,
    list_rows,
    resolve_resource,
    update_row,
)
from .tenancy import current_workspace_id
from .workflows import persisted_workflow_catalog


def _json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _body_json(request):
    try:
        return json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return None


def _saved_view_config(request, resource: str) -> dict | None:
    """Resolve ``?view=<pk>`` to the caller's saved view config (or None).

    The view must belong to this user, workspace, and resource; anything else
    is ignored so a foreign view id can never leak another member's filters.
    """
    view_pk = request.GET.get("view")
    if not view_pk:
        return None
    try:
        view_pk = int(view_pk)
    except (TypeError, ValueError):
        return None
    from .models import SavedView

    queryset = SavedView.objects.filter(pk=view_pk, user=request.user, resource=resource)
    workspace_id = current_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    view = queryset.first()
    return view.config if view is not None else None


@login_required
def tables_api(request, resource: str):
    """Schema-aware fusion table projection for one API resource.

    Mirrors the canonical ``/bolt/tables/{resource}`` contract on the
    compatibility road: headers carry type metadata (text/money/date/pill/
    link) and rows are formatted cell lists aligned to the headers.
    """
    if resolve_resource(resource) is None:
        return JsonResponse({"detail": _("Unknown resource.")}, status=404)
    workspace_id = current_workspace_id(request)
    queryset = RESOURCES[resource].model.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    return JsonResponse(resource_table(queryset, resource))


@login_required
def resource_api(request, resource: str, pk: int | None = None):
    """Full tenant-scoped CRUD for a registered resource.

    GET (list) / POST (create) on the collection, and GET / PATCH / DELETE on
    the ``/<pk>/`` detail route. Every write is scoped to the caller's
    workspace and validated against the resource's write allowlist.
    """
    if resolve_resource(resource) is None:
        return JsonResponse({"detail": _("Unknown resource.")}, status=404)
    workspace_id = current_workspace_id(request)
    method = request.method

    if pk is None:
        if method == "GET":
            limit = bounded_int(request.GET.get("limit"), 100, 1, 200)
            offset = bounded_int(request.GET.get("offset"), 0, 0, 10**9)
            search = request.GET.get("search", "")
            view_config = _saved_view_config(request, resource)
            rows = list_rows(
                resource,
                workspace_id,
                limit=limit,
                offset=offset,
                search=search,
                view_config=view_config,
            )
            total = count_rows(resource, workspace_id, search=search, view_config=view_config)
            return JsonResponse(
                {
                    "results": rows,
                    "count": total,
                    "next": offset + limit if offset + limit < total else None,
                    "previous": offset - limit if offset > 0 else None,
                }
            )
        if method == "POST":
            payload = _body_json(request)
            if payload is None:
                return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
            row, errors, status = create_row(resource, payload, workspace_id)
            if errors:
                return JsonResponse(errors, status=status)
            safe_publish_workspace_event(
                workspace_id, "resource.created", {"resource": resource, "row": row}
            )
            return JsonResponse(row, status=201)
        return JsonResponse({"detail": f"This endpoint does not accept {method}."}, status=405)

    if method == "GET":
        row = get_row(resource, pk, workspace_id)
        if row is None:
            return JsonResponse({"detail": _("Not found.")}, status=404)
        return JsonResponse(row)
    if method == "PATCH":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        row, errors, status = update_row(resource, pk, payload, workspace_id)
        if status == 404:
            return JsonResponse({"detail": _("Not found.")}, status=404)
        if errors:
            return JsonResponse(errors, status=status)
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": resource, "pk": pk, "row": row}
        )
        return JsonResponse(row)
    if method == "DELETE":
        if not delete_row(resource, pk, workspace_id):
            return JsonResponse({"detail": _("Not found.")}, status=404)
        safe_publish_workspace_event(
            workspace_id, "resource.deleted", {"resource": resource, "pk": pk}
        )
        return JsonResponse({"ok": True}, status=204)
    return JsonResponse({"detail": f"This endpoint does not accept {method}."}, status=405)


def _dashboard_workspace_id(request):
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - anonymous or profile-less requests stay unscoped
        return None


@login_required
def dashboard_api(request):
    if request.method != "GET":
        return JsonResponse({"detail": _("This read endpoint accepts GET only.")}, status=405)
    workspace_id = _dashboard_workspace_id(request)
    counts = {}
    for key, (model, _fields) in RESOURCE_MODELS.items():
        try:
            queryset = (
                model.objects.filter(workspace_id=workspace_id)
                if workspace_id is not None
                else model.objects
            )
            counts[key] = queryset.count()
        except (OperationalError, ProgrammingError):
            counts[key] = 0
    return JsonResponse(
        {
            "data": {
                "counts": counts,
                "workflow_count": len(persisted_workflow_catalog(workspace_id=workspace_id)),
            }
        }
    )


def token_api(request):
    """Issue a compatibility JWT when the optional Bolt road is unavailable."""
    if request.method != "POST":
        return JsonResponse({"detail": "This token endpoint accepts POST only."}, status=405)
    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)

    if not getattr(request.user, "is_authenticated", False):
        return JsonResponse({"detail": "Sign in is required to issue a user token."}, status=401)
    requested_subject = str(payload.get("subject") or "").strip()
    if requested_subject and requested_subject != str(request.user.pk):
        return JsonResponse(
            {"detail": "A token can only be issued for the current user."}, status=403
        )
    try:
        ttl = min(max(int(payload.get("ttl") or 3600), 60), 86_400)
        result = user_token_payload(request.user, ttl_seconds=ttl)
    except (FusionTokenError, TokenUserError, ValueError, TypeError) as exc:
        return JsonResponse({"detail": str(exc)}, status=503)
    return JsonResponse(result)


def current_user_api(request):
    """Verify a bearer token against the live Django user and role profile."""
    try:
        user = verify_request_user(request)
    except (FusionTokenError, TokenUserError) as exc:
        return JsonResponse({"detail": str(exc)}, status=401)
    profile = getattr(user, "profile", None)
    return JsonResponse(
        {
            "user": {
                "id": user.pk,
                "email": user.email,
                "name": user.get_full_name() or user.username,
                "role": getattr(profile, "role", "viewer"),
                "workspace_id": getattr(profile, "workspace_id", None),
                "is_staff": user.is_staff,
            }
        }
    )


@login_required
@require_GET
def me_api(request: HttpRequest) -> JsonResponse:
    """Session-based current-user identity for the Astro profile road (``/apis/me/``).

    Returns the same identity + role + effective-capability shape the Django
    road renders in ``account/profile.html``, so both roads stay in sync
    without exposing tokens or secrets.
    """
    profile = getattr(request.user, "profile", None)
    workspace = getattr(profile, "workspace", None) if profile else None
    return JsonResponse(
        {
            "user": {
                "id": request.user.pk,
                "email": request.user.email,
                "username": request.user.username,
                "name": request.user.get_full_name() or request.user.username,
                "role": getattr(profile, "role", "viewer"),
                "title": getattr(profile, "title", "") or "",
                "workspace_id": getattr(workspace, "pk", None),
                "workspace_name": getattr(workspace, "name", None),
                "is_staff": request.user.is_staff,
            },
            "capabilities": {
                "sales": is_sales(request.user),
                "marketing": is_marketing(request.user),
                "revops": is_revops(request.user),
                "manage_deals": can_manage_deals(request.user),
                "manage_posts": can_manage_posts(request.user),
            },
        }
    )


def refresh_token_api(request):
    """Rotate a refresh token on the compatibility API road."""
    if request.method != "POST":
        return JsonResponse({"detail": "This refresh endpoint accepts POST only."}, status=405)
    try:
        payload = json.loads(request.body or "{}")
        result = refresh_payload(str(payload.get("refresh_token") or ""))
    except (TypeError, ValueError, FusionTokenError) as exc:
        return JsonResponse({"detail": str(exc)}, status=401)
    return JsonResponse(result)


@login_required
def resource_export(request):
    """Export any registered resource table as CSV or JSON, workspace-scoped.

    ``?resource=<slug>&format=csv|json[&search=<term>]``. The resource must be
    registered in ``apps.core.resources.RESOURCES``; the read projection is the
    same allowlist both API roads already expose, so no field is exported that
    the resource contract does not already project.
    """
    slug = (request.GET.get("resource") or "").strip()
    fmt = (request.GET.get("format") or "csv").strip().lower()
    if resolve_resource(slug) is None:
        return JsonResponse({"detail": _("Unknown resource.")}, status=404)
    if fmt not in {"csv", "json"}:
        return JsonResponse({"detail": "Format must be csv or json."}, status=400)
    workspace_id = current_workspace_id(request)
    search = request.GET.get("search", "")
    rows = resource_export_rows(slug, workspace_id, search=search)
    if fmt == "json":
        return JsonResponse({"results": rows, "count": len(rows)})
    response = HttpResponse(to_csv(rows), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="loop-crm-{slug}.csv"'
    return response


@login_required
def email_accounts_api(request):
    """List/create connected Gmail/Outlook sync accounts.

    OAuth tokens are writable on create but never projected back out, so the
    sync road is the only place a credential lives.
    """
    from .email_sync import provider_catalog, sync_account
    from .models import EmailAccount

    workspace_id = current_workspace_id(request)
    if request.method == "GET":
        queryset = EmailAccount.objects.filter(is_active=True)
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        results = [
            {
                "id": account.pk,
                "provider": account.provider,
                "email": account.email,
                "last_synced_at": account.last_synced_at.isoformat()
                if account.last_synced_at
                else None,
                "message_count": account.messages.count(),
            }
            for account in queryset.select_related("workspace")
        ]
        return JsonResponse(
            {"results": results, "count": len(results), "providers": provider_catalog()}
        )
    if request.method == "POST":
        if workspace_id is None:
            return JsonResponse({"detail": _("A workspace is required.")}, status=403)
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        provider = str(payload.get("provider") or "").strip().lower()
        email = str(payload.get("email") or "").strip().lower()
        if provider not in {"gmail", "outlook"}:
            return JsonResponse({"provider": "provider must be gmail or outlook."}, status=400)
        if not email:
            return JsonResponse({"email": "An account email is required."}, status=400)
        account, created = EmailAccount.objects.update_or_create(
            workspace_id=workspace_id,
            provider=provider,
            email=email,
            defaults={
                "oauth_token": str(payload.get("oauth_token") or ""),
                "oauth_refresh_token": str(payload.get("oauth_refresh_token") or ""),
                "is_active": True,
                "created_by": request.user,
            },
        )
        # Run an immediate sync when a token was supplied so the connect flow
        # gives instant feedback; an unconfigured account degrades honestly.
        summary = sync_account(account) if account.oauth_token else None
        safe_publish_workspace_event(
            workspace_id,
            "resource.created" if created else "resource.updated",
            {"resource": "email_accounts", "pk": account.pk},
        )
        return JsonResponse(
            {
                "id": account.pk,
                "provider": account.provider,
                "email": account.email,
                "sync": (
                    {"status": summary.status, "synced": summary.synced, "matched": summary.matched}
                    if summary
                    else None
                ),
            },
            status=201 if created else 200,
        )
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


@login_required
def email_account_sync_api(request, pk: int):
    """Trigger an on-demand sync for one connected mailbox."""
    from .email_sync import sync_account
    from .models import EmailAccount

    if request.method != "POST":
        return JsonResponse({"detail": _("This endpoint accepts POST only.")}, status=405)
    workspace_id = current_workspace_id(request)
    queryset = EmailAccount.objects.filter(pk=pk)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    account = queryset.first()
    if account is None:
        return JsonResponse({"detail": _("Not found.")}, status=404)
    result = sync_account(account)
    status = 200 if result.status == "synced" else (400 if result.status == "error" else 409)
    return JsonResponse(
        {
            "status": result.status,
            "synced": result.synced,
            "matched": result.matched,
            "detail": result.detail,
        },
        status=status,
    )


@login_required
def email_messages_api(request):
    """List synced email messages, workspace-scoped, newest first."""
    from .models import EmailMessage

    if request.method != "GET":
        return JsonResponse({"detail": _("This read endpoint accepts GET only.")}, status=405)
    workspace_id = current_workspace_id(request)
    queryset = EmailMessage.objects.select_related("account", "contact", "deal")
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    limit = bounded_int(request.GET.get("limit"), 100, 1, 200)
    offset = bounded_int(request.GET.get("offset"), 0, 0, 10**9)
    total = queryset.count()
    results = [
        {
            "id": message.pk,
            "provider": message.account.provider,
            "subject": message.subject,
            "snippet": message.snippet,
            "sender_email": message.sender_email,
            "sender_name": message.sender_name,
            "received_at": message.received_at.isoformat() if message.received_at else None,
            "contact_id": message.contact_id,
            "deal_id": message.deal_id,
        }
        for message in queryset.order_by("-received_at")[offset : offset + limit]
    ]
    return JsonResponse(
        {
            "results": results,
            "count": total,
            "next": offset + limit if offset + limit < total else None,
        }
    )


@login_required
@require_GET
def ai_catalog_api(request: HttpRequest) -> JsonResponse:
    """Expose AI capabilities and consent state without exposing credentials."""
    from .ai import consent_enabled, operation_catalog, provider_catalog

    profile = getattr(request.user, "profile", None)
    return JsonResponse(
        {
            "consent": consent_enabled(profile) if profile else False,
            "operations": operation_catalog(),
            "providers": provider_catalog(),
        }
    )


@login_required
def ai_consent_api(request: HttpRequest) -> JsonResponse:
    """Read or update the workspace member's explicit AI consent."""
    from .ai import consent_enabled, set_consent

    profile = getattr(request.user, "profile", None)
    if profile is None:
        return JsonResponse({"detail": _("A user profile is required.")}, status=400)
    if request.method == "GET":
        return JsonResponse({"consent": consent_enabled(profile)})
    if request.method != "POST":
        return JsonResponse({"detail": "This consent endpoint accepts POST only."}, status=405)
    payload = _body_json(request)
    if payload is None or not isinstance(payload.get("enabled"), bool):
        return JsonResponse({"enabled": "enabled must be a boolean."}, status=400)
    set_consent(profile, payload["enabled"])
    workspace_id = current_workspace_id(request)
    if workspace_id is not None:
        from .models import AuditLog

        AuditLog.objects.create(
            user=request.user,
            workspace_id=workspace_id,
            action="update",
            model_name="AIConsent",
            object_id=str(request.user.pk),
            changes={"enabled": payload["enabled"]},
        )
    return JsonResponse({"consent": payload["enabled"]})


@login_required
@require_POST
def ai_operation_api(request: HttpRequest, operation: str) -> JsonResponse:
    """Run one consent-gated AI operation; outputs are never auto-published."""
    from .ai import consent_enabled, operation_catalog, run_operation

    profile = getattr(request.user, "profile", None)
    if profile is None or not consent_enabled(profile):
        return JsonResponse(
            {"status": "deferred", "reason": "Workspace AI consent is required."}, status=403
        )
    allowed = {item["id"] for item in operation_catalog()}
    if operation not in allowed:
        return JsonResponse({"detail": _("Unknown AI operation.")}, status=404)
    payload = _body_json(request)
    if payload is None:
        return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
    context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    result = run_operation(operation, context)
    workspace_id = current_workspace_id(request)
    if workspace_id is not None:
        from .models import AuditLog

        AuditLog.objects.create(
            user=request.user,
            workspace_id=workspace_id,
            action="view",
            model_name="AIOperation",
            object_id=operation,
            changes={"operation": operation, "status": result.status, "provider": result.provider},
        )
    response = {
        "status": result.status,
        "provider": result.provider,
        "operation": result.operation,
    }
    if result.output is not None:
        response["output"] = result.output
    if result.reason:
        response["reason"] = result.reason
    return JsonResponse(response, status=200 if result.status != "failed" else 502)


@login_required
@require_GET
def employees_api(request):
    """List workspace members with live activity, deal, post, and invoice counts."""
    from django.contrib.auth.models import User

    from apps.crm.models import Activity, Deal
    from apps.finance.models import Invoice
    from apps.marketing.models import Post

    workspace_id = current_workspace_id(request)
    members = User.objects.select_related("profile", "profile__workspace")
    if workspace_id is not None:
        members = members.filter(profile__workspace_id=workspace_id)
    results = []
    for member in members.order_by("username", "email"):
        results.append(
            {
                "id": member.pk,
                "name": member.get_full_name() or member.username,
                "email": member.email,
                "username": member.username,
                "role": getattr(member.profile, "role", "viewer"),
                "title": getattr(member.profile, "title", ""),
                "workspace_name": getattr(getattr(member.profile, "workspace", None), "name", None),
                "metrics": {
                    "activities": Activity.objects.filter(workspace_id=workspace_id, created_by=member).count(),
                    "deals": Deal.objects.filter(workspace_id=workspace_id, owner=member).count(),
                    "posts": Post.objects.filter(workspace_id=workspace_id, created_by=member).count(),
                    "invoices": Invoice.objects.filter(workspace_id=workspace_id, created_by=member).count(),
                },
            }
        )
    return JsonResponse({"results": results, "count": len(results)})


@login_required
@require_GET
def employee_report_api(request, pk: int):
    """Return a live performance dossier for one workspace member."""
    from django.contrib.auth.models import User
    from django.db.models import Sum

    from apps.crm.models import Activity, Deal
    from apps.finance.models import Invoice
    from apps.marketing.models import Post

    workspace_id = current_workspace_id(request)
    queryset = User.objects.select_related("profile", "profile__workspace")
    if workspace_id is not None:
        queryset = queryset.filter(profile__workspace_id=workspace_id)
    member = queryset.filter(pk=pk).first()
    if member is None:
        return JsonResponse({"detail": _("Employee not found.")}, status=404)
    deals = Deal.objects.filter(workspace_id=workspace_id, owner=member)
    posts = Post.objects.filter(workspace_id=workspace_id, created_by=member)
    activities = Activity.objects.filter(workspace_id=workspace_id, created_by=member)
    invoices = Invoice.objects.filter(workspace_id=workspace_id, created_by=member)
    return JsonResponse(
        {
            "employee": {
                "id": member.pk,
                "name": member.get_full_name() or member.username,
                "email": member.email,
                "role": getattr(member.profile, "role", "viewer"),
                "title": getattr(member.profile, "title", ""),
            },
            "metrics": {
                "activities": activities.count(),
                "deals": deals.count(),
                "deal_value": str(deals.aggregate(total=Sum("value"))["total"] or 0),
                "posts": posts.count(),
                "published_posts": posts.filter(status="published").count(),
                "invoices": invoices.count(),
                "invoice_value": str(invoices.aggregate(total=Sum("total"))["total"] or 0),
            },
            "recent": {
                "activities": list(activities.order_by("-created_at").values("id", "subject", "activity_type")[:5]),
                "deals": list(deals.order_by("-updated_at").values("id", "name", "value")[:5]),
                "posts": list(posts.order_by("-updated_at").values("id", "content", "status")[:5]),
            },
        }
    )


@login_required
@require_GET
def search_api(request):
    """Federated tenant-scoped search for the command palette."""
    query = (request.GET.get("q") or "").strip()
    if len(query) < 2:
        return JsonResponse({"results": [], "count": 0})
    workspace_id = current_workspace_id(request)
    from django.contrib.auth.models import User

    from apps.crm.models import Company, Contact, Deal
    from apps.marketing.models import Post

    results = []
    for label, model, fields, href in [
        ("Company", Company, ("name", "industry", "email"), "/crm/companies/"),
        ("Contact", Contact, ("first_name", "last_name", "email", "title"), "/crm/contacts/"),
        ("Deal", Deal, ("name",), "/crm/deals/"),
        ("Post", Post, ("content",), "/marketing/calendar/"),
    ]:
        condition = Q()
        for field in fields:
            condition |= Q(**{f"{field}__icontains": query})
        queryset = model.objects.filter(condition)
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        for row in queryset[:6]:
            title = getattr(row, "full_name", None) or getattr(row, "name", None) or getattr(row, "content", "")
            results.append({"type": label.lower(), "title": str(title)[:100], "meta": getattr(row, "email", ""), "href": href})
    members = User.objects.filter(profile__workspace_id=workspace_id).filter(
        Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
    )[:6]
    results.extend(
        {"type": "employee", "title": member.get_full_name() or member.username, "meta": member.email, "href": f"/employees/?employee={member.pk}"}
        for member in members
    )
    return JsonResponse({"results": results[:24], "count": len(results[:24])})


@login_required
@require_GET
def badge_counts_api(request):
    """Return live sidebar counters for the caller's workspace."""
    from apps.finance.models import Invoice
    from apps.marketing.models import Post

    from .models import TaskExecution, WorkflowRun

    workspace_id = current_workspace_id(request)
    posts = Post.objects.filter(workspace_id=workspace_id, status="pending_approval").count()
    invoices = Invoice.objects.filter(workspace_id=workspace_id, status__in=["issued", "partially_paid", "overdue"]).count()
    tasks = WorkflowRun.objects.filter(workspace_id=workspace_id, status__in=["queued", "running"]).count()
    tasks += TaskExecution.objects.filter(site_name="loop-crm", status__in=["queued", "started", "retrying"]).count()
    return JsonResponse({"approvals": posts, "invoices": invoices, "tasks": tasks})


@login_required
def workspace_current_api(request):
    """Expose the caller's workspace id so client islands can open the
    workspace-scoped WebSocket without hardcoding a tenant id.
    """
    return JsonResponse({"workspace_id": current_workspace_id(request)})


@login_required
def workflows_api(request):
    results = persisted_workflow_catalog(workspace_id=current_workspace_id(request))
    return JsonResponse({"results": results, "count": len(results)})


@login_required
def reports_api(request):
    """Report catalog for the webapp /reports/ surface."""
    from .reports import report_catalog

    catalog = report_catalog()
    return JsonResponse({"results": catalog, "count": len(catalog)})


def integrations_api(request):
    return JsonResponse({"results": platform_catalog(), "count": len(platform_catalog())})


@login_required
def custom_fields_api(request):
    profile = getattr(request.user, "profile", None)
    workspace = getattr(profile, "workspace", None) if profile else None
    catalog = custom_object_catalog(workspace)
    return JsonResponse({"results": catalog, "count": len(catalog)})


def _custom_object_queryset(workspace_id, key: str | None = None):
    from apps.crm.models import CustomObjectDefinition

    queryset = CustomObjectDefinition.objects.filter(is_active=True)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    if key is not None:
        queryset = queryset.filter(key=key)
    return queryset


def _custom_definition_payload(definition) -> dict:
    return {
        "id": definition.pk,
        "key": definition.key,
        "name": definition.name,
        "icon": definition.icon,
        "fields": definition.fields,
        "record_count": definition.records.count(),
    }


@login_required
def custom_objects_api(request):
    """List/create workspace custom-object definitions."""
    from django.core.exceptions import ValidationError

    from apps.crm.custom_objects import validate_definition_fields
    from apps.crm.models import CustomObjectDefinition

    workspace_id = current_workspace_id(request)
    if request.method == "GET":
        definitions = _custom_object_queryset(workspace_id).order_by("name")
        results = [_custom_definition_payload(d) for d in definitions]
        return JsonResponse({"results": results, "count": len(results)})
    if request.method == "POST":
        if workspace_id is None:
            return JsonResponse({"detail": _("A workspace is required.")}, status=403)
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        name = str(payload.get("name") or "").strip()
        key = str(payload.get("key") or "").strip().lower()
        if not name or not key:
            return JsonResponse({"detail": _("name and key are required.")}, status=400)
        try:
            fields = validate_definition_fields(payload.get("fields") or [])
        except ValidationError as exc:
            return JsonResponse({"fields": exc.messages}, status=400)
        try:
            definition = CustomObjectDefinition.objects.create(
                workspace_id=workspace_id,
                name=name,
                key=key,
                icon=str(payload.get("icon") or "dataset"),
                fields=fields,
                created_by=request.user,
            )
        except Exception as exc:  # noqa: BLE001 - normalize uniqueness/DB errors
            return JsonResponse({"__all__": str(exc)}, status=400)
        safe_publish_workspace_event(
            workspace_id, "resource.created", {"resource": "custom_objects", "pk": definition.pk}
        )
        return JsonResponse(_custom_definition_payload(definition), status=201)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


def _get_definition_or_404(workspace_id, key: str):
    from django.shortcuts import get_object_or_404

    queryset = _custom_object_queryset(workspace_id, key=key)
    return get_object_or_404(queryset, key=key)


@login_required
def custom_object_records_api(request, key: str):
    """List/create rows for one workspace custom-object definition."""
    from django.core.exceptions import ValidationError

    from apps.crm.custom_objects import validate_record_data
    from apps.crm.models import CustomObjectRecord

    workspace_id = current_workspace_id(request)
    definition = _get_definition_or_404(workspace_id, key)
    if request.method == "GET":
        records = definition.records.all()
        if workspace_id is not None:
            records = records.filter(workspace_id=workspace_id)
        rows = list(
            records.order_by("-updated_at").values(
                "id", "data", "updated_at", "created_by__username"
            )
        )
        for row in rows:
            if row["updated_at"]:
                row["updated_at"] = row["updated_at"].isoformat()
        return JsonResponse({"results": rows, "count": len(rows)})
    if request.method == "POST":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        try:
            data = validate_record_data(definition, payload.get("data"))
        except ValidationError as exc:
            return JsonResponse(
                exc.message_dict if hasattr(exc, "message_dict") else {"data": exc.messages},
                status=400,
            )
        record = CustomObjectRecord.objects.create(
            workspace_id=workspace_id,
            definition=definition,
            data=data,
            created_by=request.user,
        )
        safe_publish_workspace_event(
            workspace_id, "resource.created", {"resource": "custom_object_records", "pk": record.pk}
        )
        return JsonResponse({"id": record.pk, "data": record.data}, status=201)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


@login_required
def custom_object_record_detail_api(request, key: str, pk: int):
    """GET/PATCH/DELETE one custom-object row, tenant-scoped."""
    from django.core.exceptions import ValidationError

    from apps.crm.custom_objects import validate_record_data
    from apps.crm.models import CustomObjectRecord

    workspace_id = current_workspace_id(request)
    definition = _get_definition_or_404(workspace_id, key)
    queryset = CustomObjectRecord.objects.filter(definition=definition)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    record = queryset.filter(pk=pk).first()
    if record is None:
        return JsonResponse({"detail": _("Not found.")}, status=404)
    if request.method == "GET":
        return JsonResponse({"id": record.pk, "data": record.data})
    if request.method == "PATCH":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        merged = {**(record.data or {}), **(payload.get("data") or {})}
        try:
            record.data = validate_record_data(definition, merged)
        except ValidationError as exc:
            return JsonResponse(
                exc.message_dict if hasattr(exc, "message_dict") else {"data": exc.messages},
                status=400,
            )
        record.save(update_fields=["data", "updated_at"])
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": "custom_object_records", "pk": record.pk}
        )
        return JsonResponse({"id": record.pk, "data": record.data})
    if request.method == "DELETE":
        record.delete()
        safe_publish_workspace_event(
            workspace_id, "resource.deleted", {"resource": "custom_object_records", "pk": pk}
        )
        return JsonResponse({"ok": True}, status=204)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


def _saved_view_payload(view) -> dict:
    return {
        "id": view.pk,
        "resource": view.resource,
        "name": view.name,
        "view_type": view.view_type,
        "config": view.config,
        "is_default": view.is_default,
    }


@login_required
def saved_views_api(request):
    """List/create the caller's saved views (member- and workspace-scoped)."""
    from .models import SavedView

    workspace_id = current_workspace_id(request)
    if request.method == "GET":
        queryset = SavedView.objects.filter(user=request.user)
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        results = [_saved_view_payload(v) for v in queryset.order_by("resource", "name")]
        return JsonResponse({"results": results, "count": len(results)})
    if request.method == "POST":
        if workspace_id is None:
            return JsonResponse({"detail": _("A workspace is required.")}, status=403)
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        name = str(payload.get("name") or "").strip()
        resource = str(payload.get("resource") or "").strip()
        if not name or not resource:
            return JsonResponse({"detail": "name and resource are required."}, status=400)
        if resolve_resource(resource) is None:
            return JsonResponse({"detail": _("Unknown resource.")}, status=404)
        config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
        view_type = (
            payload.get("view_type") if payload.get("view_type") in {"list", "kanban"} else "list"
        )
        view, created = SavedView.objects.update_or_create(
            workspace_id=workspace_id,
            user=request.user,
            resource=resource,
            name=name,
            defaults={
                "view_type": view_type,
                "config": config,
                "is_default": bool(payload.get("is_default")),
            },
        )
        safe_publish_workspace_event(
            workspace_id,
            "resource.created" if created else "resource.updated",
            {"resource": "saved_views", "pk": view.pk},
        )
        return JsonResponse(_saved_view_payload(view), status=201 if created else 200)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


@login_required
def saved_view_detail_api(request, pk: int):
    """GET/PATCH/DELETE one of the caller's saved views."""
    from .models import SavedView

    workspace_id = current_workspace_id(request)
    queryset = SavedView.objects.filter(user=request.user)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    view = queryset.filter(pk=pk).first()
    if view is None:
        return JsonResponse({"detail": _("Not found.")}, status=404)
    if request.method == "GET":
        return JsonResponse(_saved_view_payload(view))
    if request.method == "PATCH":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": _("Request body must be valid JSON.")}, status=400)
        if "config" in payload and isinstance(payload["config"], dict):
            view.config = payload["config"]
        if "view_type" in payload and payload["view_type"] in {"list", "kanban"}:
            view.view_type = payload["view_type"]
        if "is_default" in payload:
            view.is_default = bool(payload["is_default"])
        if "name" in payload and str(payload["name"]).strip():
            view.name = str(payload["name"]).strip()
        view.save(update_fields=["config", "view_type", "is_default", "name", "updated_at"])
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": "saved_views", "pk": view.pk}
        )
        return JsonResponse(_saved_view_payload(view))
    if request.method == "DELETE":
        view.delete()
        safe_publish_workspace_event(
            workspace_id, "resource.deleted", {"resource": "saved_views", "pk": pk}
        )
        return JsonResponse({"ok": True}, status=204)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)
