"""Course Center API — registration, directory, subdomain check.

Public schema endpoints consumed by the Astro frontend (center directory,
registration form) and the Alpine login modal (center-scoped auth)."""

from __future__ import annotations

import json
import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import CenterPlan, CenterRegistration, CourseCenter
from .services import CenterQueryService, generate_verification_token


@require_GET
def plan_list(request: HttpRequest) -> JsonResponse:
    plans = CenterPlan.objects.filter(is_active=True).values(
        "name",
        "slug",
        "max_courses",
        "max_instructors",
        "max_students",
        "custom_domain",
        "custom_branding",
        "trial_days",
        "features",
    )
    return JsonResponse({"plans": list(plans)})


@require_GET
def center_list(request: HttpRequest) -> JsonResponse:
    """Public center directory — active centers with plan + tagline."""
    centers = (
        CourseCenter.objects.filter(status=CourseCenter.Status.ACTIVE)
        .select_related("plan")
        .order_by("organization_name")
    )
    data = [
        {
            "slug": c.slug,
            "organization_name": c.organization_name,
            "tagline": c.tagline,
            "plan": c.plan.slug,
            "plan_name": c.plan.name,
            "created_at": c.created_at.isoformat(),
        }
        for c in centers
    ]
    return JsonResponse({"centers": data})


@require_GET
def check_subdomain(request: HttpRequest) -> JsonResponse:
    subdomain = request.GET.get("subdomain", "").strip().lower()
    if not subdomain:
        return JsonResponse(
            {"available": False, "error": "Subdomain required."}, status=400
        )
    available = CenterQueryService.is_subdomain_available(subdomain)
    return JsonResponse({"available": available, "subdomain": subdomain})


@csrf_exempt
@require_POST
@transaction.atomic
def center_register(request: HttpRequest) -> JsonResponse:
    """Create a CenterRegistration (step 1 of 2-step signup)."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    email = (body.get("email") or "").strip().lower()
    organization_name = (body.get("organization_name") or "").strip()
    plan_slug = (body.get("plan") or "").strip().lower()
    subdomain = (body.get("subdomain") or "").strip().lower()
    tagline = (body.get("tagline") or "").strip()[:255]

    errors = {}
    if not email:
        errors["email"] = "Email is required."
    if not organization_name:
        errors["organization_name"] = "Organization name is required."
    if not subdomain:
        errors["subdomain"] = "Subdomain is required."
    elif not subdomain.replace("-", "").isalnum() or len(subdomain) > 63:
        errors["subdomain"] = "Invalid subdomain (alphanumeric + hyphens, ≤63 chars)."
    elif not CenterQueryService.is_subdomain_available(subdomain):
        errors["subdomain"] = "Subdomain is already taken."

    try:
        plan = CenterPlan.objects.get(slug=plan_slug, is_active=True)
    except CenterPlan.DoesNotExist:
        errors["plan"] = "Invalid or inactive plan."

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    token = generate_verification_token()
    registration = CenterRegistration.objects.create(
        email=email,
        organization_name=organization_name,
        plan=plan,
        subdomain=subdomain,
        tagline=tagline,
        verification_token=token,
    )

    _send_verification_email(registration)

    return JsonResponse(
        {
            "status": "pending",
            "message": (
                "Registration received! Check your email to verify. "
                "Once verified, we'll review your center."
            ),
        },
        status=201,
    )


@require_GET
def center_verify(request: HttpRequest, token: str) -> JsonResponse:
    try:
        token_uuid = uuid.UUID(token)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid verification token."}, status=400)

    try:
        reg = CenterRegistration.objects.get(
            verification_token=token_uuid,
            status=CenterRegistration.Status.PENDING,
        )
    except CenterRegistration.DoesNotExist:
        return JsonResponse({"error": "Token not found or already used."}, status=404)

    reg.status = CenterRegistration.Status.VERIFIED
    reg.save(update_fields=["status"])

    if reg.plan.slug == CenterPlan.Slug.FREE:
        _auto_approve(reg)

    return JsonResponse(
        {
            "status": reg.status,
            "message": (
                "Email verified! Your center is ready."
                if reg.status == CenterRegistration.Status.APPROVED
                else "Email verified! Your application is pending review."
            ),
        }
    )


def _send_verification_email(reg: CenterRegistration) -> None:
    base_url = getattr(settings, "TENANT_BASE_URL", "https://dev.structa.cloud")
    verify_url = f"{base_url}/register/verify/?token={reg.verification_token}"
    send_mail(
        subject=f"Verify your course center: {reg.organization_name}",
        message=f"Hi {reg.organization_name},\n\n"
        f"Verify your email to launch your course center:\n{verify_url}\n\n"
        f"— Structa Cloud",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reg.email],
        fail_silently=True,
    )


def _auto_approve(reg: CenterRegistration) -> None:
    """Auto-approve free-plan registrations after verification."""
    reg.status = CenterRegistration.Status.APPROVED
    reg.save(update_fields=["status"])

    try:
        from django_fusion.tasks import enqueue

        enqueue("system", "centers.provision", registration_id=reg.id)
    except Exception:
        from .services import ProvisioningService

        ProvisioningService.create_center(reg)