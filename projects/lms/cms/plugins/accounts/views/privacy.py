"""
Privacy Policy and Terms of Service Views

Handles privacy policy modal display and consent tracking.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from plugins.accounts.models.profiles.privacy import (
    PrivacyConsent,
    PrivacyPolicy,
    TermsConsent,
    TermsOfService,
)


@require_http_methods(["GET"])
def privacy_policy_modal(request):
    """Display privacy policy modal via HTMX."""
    policy = PrivacyPolicy.objects.filter(is_active=True).first()

    if not policy:
        return HttpResponse("<p>No privacy policy available</p>", status=404)

    has_consented = PrivacyConsent.has_consented(request.user, policy)

    context = {
        "policy": policy,
        "has_consented": has_consented,
    }

    return render(request, "privacy/privacy_modal.html", context)


@require_http_methods(["GET"])
def terms_modal(request):
    """Display terms of service modal via HTMX."""
    terms = TermsOfService.objects.filter(is_active=True).first()

    if not terms:
        return HttpResponse("<p>No terms of service available</p>", status=404)

    has_consented = TermsConsent.has_consented(request.user, terms)

    context = {
        "terms": terms,
        "has_consented": has_consented,
    }

    return render(request, "privacy/terms_modal.html", context)


@require_http_methods(["POST"])
@login_required
def accept_privacy_policy(request):
    """Record user consent to privacy policy."""
    policy = PrivacyPolicy.objects.filter(is_active=True).first()

    if not policy:
        return JsonResponse({"error": "No active policy"}, status=404)

    # Get client IP address
    ip_address = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    # Record consent
    consent, created = PrivacyConsent.record_consent(
        request.user, policy, ip_address, user_agent
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Privacy policy consent recorded",
            "created": created,
        }
    )


@require_http_methods(["POST"])
@login_required
def accept_terms(request):
    """Record user consent to terms of service."""
    terms = TermsOfService.objects.filter(is_active=True).first()

    if not terms:
        return JsonResponse({"error": "No active terms"}, status=404)

    # Get client IP address
    ip_address = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    # Record consent
    consent, created = TermsConsent.record_consent(
        request.user, terms, ip_address, user_agent
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Terms consent recorded",
            "created": created,
        }
    )


@require_http_methods(["GET"])
def check_consent_status(request):
    """Check if user has consented to privacy policy and terms."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "authenticated": False,
                "privacy_consented": False,
                "terms_consented": False,
            }
        )

    policy = PrivacyPolicy.objects.filter(is_active=True).first()
    terms = TermsOfService.objects.filter(is_active=True).first()

    privacy_consented = (
        PrivacyConsent.has_consented(request.user, policy) if policy else False
    )
    terms_consented = (
        TermsConsent.has_consented(request.user, terms) if terms else False
    )

    return JsonResponse(
        {
            "authenticated": True,
            "privacy_consented": privacy_consented,
            "terms_consented": terms_consented,
        }
    )


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
