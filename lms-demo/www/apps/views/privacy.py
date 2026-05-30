"""
Privacy Policy and Terms of Service Views — www.apps layer

Supports three rendering modes:
  - Full page  (direct GET, no Unpoly header)
  - Unpoly overlay / modal  (X-Up-Mode: modal | drawer | popup)
  - HTMX fragment  (HX-Request header)
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from www.apps.models.profiles.privacy import (
    PrivacyConsent,
    PrivacyPolicy,
    TermsConsent,
    TermsOfService,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client_ip(request: HttpRequest) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _is_overlay(request: HttpRequest) -> bool:
    return request.headers.get("X-Up-Mode", "") in ("modal", "drawer", "popup", "cover")


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def _pick_template(base: str, request: HttpRequest) -> str:
    if _is_overlay(request) or _is_htmx(request):
        return f"privacy/{base}_fragment.html"
    return f"privacy/{base}_page.html"


# ---------------------------------------------------------------------------
# Privacy Policy
# ---------------------------------------------------------------------------

@require_http_methods(["GET"])
def privacy_policy(request: HttpRequest) -> HttpResponse:
    """Display the privacy policy as a full page or overlay fragment."""
    policy = PrivacyPolicy.objects.filter(is_active=True).first()

    if not policy:
        return HttpResponse(_("No privacy policy is currently available."), status=404)

    has_consented = (
        PrivacyConsent.has_consented(request.user, policy)
        if request.user.is_authenticated
        else False
    )

    context = {
        "policy": policy,
        "has_consented": has_consented,
        "accept_url": "privacy:accept_policy",
        "page_title": _("Privacy Policy"),
    }
    return render(request, _pick_template("privacy_policy", request), context)


@require_http_methods(["POST"])
@login_required
def accept_privacy_policy(request: HttpRequest) -> HttpResponse:
    """Record user consent to the active privacy policy."""
    policy = PrivacyPolicy.objects.filter(is_active=True).first()

    if not policy:
        if _is_htmx(request) or _is_overlay(request):
            return JsonResponse({"error": str(_("No active privacy policy found."))}, status=404)
        messages.error(request, _("No active privacy policy found."))
        return redirect("privacy:policy")

    PrivacyConsent.record_consent(
        user=request.user,
        policy=policy,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    if _is_htmx(request) or _is_overlay(request):
        return render(request, "privacy/consent_accepted_fragment.html", {
            "message": _("Privacy policy accepted. Thank you."),
            "type": "privacy",
        })

    messages.success(request, _("Privacy policy accepted. Thank you."))
    return redirect(request.POST.get("next") or request.GET.get("next") or "/")


# ---------------------------------------------------------------------------
# Terms of Service
# ---------------------------------------------------------------------------

@require_http_methods(["GET"])
def terms_of_service(request: HttpRequest) -> HttpResponse:
    """Display the terms of service as a full page or overlay fragment."""
    terms = TermsOfService.objects.filter(is_active=True).first()

    if not terms:
        return HttpResponse(_("No terms of service are currently available."), status=404)

    has_consented = (
        TermsConsent.has_consented(request.user, terms)
        if request.user.is_authenticated
        else False
    )

    context = {
        "terms": terms,
        "has_consented": has_consented,
        "accept_url": "privacy:accept_terms",
        "page_title": _("Terms of Service"),
    }
    return render(request, _pick_template("terms_of_service", request), context)


@require_http_methods(["POST"])
@login_required
def accept_terms(request: HttpRequest) -> HttpResponse:
    """Record user consent to the active terms of service."""
    terms = TermsOfService.objects.filter(is_active=True).first()

    if not terms:
        if _is_htmx(request) or _is_overlay(request):
            return JsonResponse({"error": str(_("No active terms of service found."))}, status=404)
        messages.error(request, _("No active terms of service found."))
        return redirect("privacy:terms")

    TermsConsent.record_consent(
        user=request.user,
        terms=terms,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    if _is_htmx(request) or _is_overlay(request):
        return render(request, "privacy/consent_accepted_fragment.html", {
            "message": _("Terms of service accepted. Thank you."),
            "type": "terms",
        })

    messages.success(request, _("Terms of service accepted. Thank you."))
    return redirect(request.POST.get("next") or request.GET.get("next") or "/")


# ---------------------------------------------------------------------------
# Consent status (JSON API)
# ---------------------------------------------------------------------------

@require_http_methods(["GET"])
def consent_status(request: HttpRequest) -> JsonResponse:
    """Return the current user's consent status as JSON."""
    if not request.user.is_authenticated:
        return JsonResponse({
            "authenticated": False,
            "privacy_consented": False,
            "terms_consented": False,
        })

    policy = PrivacyPolicy.objects.filter(is_active=True).first()
    terms = TermsOfService.objects.filter(is_active=True).first()

    return JsonResponse({
        "authenticated": True,
        "privacy_consented": PrivacyConsent.has_consented(request.user, policy) if policy else False,
        "terms_consented": TermsConsent.has_consented(request.user, terms) if terms else False,
    })


# ---------------------------------------------------------------------------
# Consent required gate page
# ---------------------------------------------------------------------------

@require_http_methods(["GET"])
def consent_required(request: HttpRequest) -> HttpResponse:
    """Gate page shown when a user must accept policies before continuing."""
    policy = PrivacyPolicy.objects.filter(is_active=True).first()
    terms = TermsOfService.objects.filter(is_active=True).first()

    privacy_consented = (
        PrivacyConsent.has_consented(request.user, policy)
        if request.user.is_authenticated and policy
        else False
    )
    terms_consented = (
        TermsConsent.has_consented(request.user, terms)
        if request.user.is_authenticated and terms
        else False
    )

    return render(request, "privacy/consent_required_page.html", {
        "policy": policy,
        "terms": terms,
        "privacy_consented": privacy_consented,
        "terms_consented": terms_consented,
        "next": request.GET.get("next", "/"),
        "page_title": _("Consent Required"),
    })
