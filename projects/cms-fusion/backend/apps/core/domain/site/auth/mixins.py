"""
Streamlined Authentication System with Unified Pages & Mixins
============================================================
Smooth integration between page components and auth logic with:
- No duplication between pages and mixins
- Clean separation of concerns
- Automatic context management
- Seamless HTMX/SSE support

Generic authentication logic is imported from django_fusion.contrib.auth.
Wagtail-specific page components are defined here.
"""

import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_fusion.site.interface.page_handler import PageHandler
from django_fusion.site.interface.auth.mixins import (
    AuthBaseMixin,
    AuthConfig,
    AuthProcessorMixin,
)

logger = logging.getLogger(__name__)


# ===============================================
# AUTH PAGE COMPONENTS (PAGE RENDERING ONLY)
# ===============================================


class AuthPageBase(PageHandler, AuthProcessorMixin):
    """Base class for all authentication pages."""

    template_name = "base_auth.html"
    layout_path = "account/skeleton.html"
    # Page configuration
    show_breadcrumbs = False
    show_sidebar = False
    full_width = False
    require_auth = False  # Auth pages don't require authentication

    # HTMX configuration
    htmx_config = {
        "reswap": "innerHTML",
        "retarget": AuthConfig.FORM_TARGET,
    }

    def get_context_data(self, **kwargs):
        """Add auth-specific context to all auth pages."""
        context = super().get_context_data(**kwargs)

        # Auth-specific context
        context.update(
            {
                "next": self.request.GET.get("next", ""),
                "is_auth_page": True,
                "form_target": AuthConfig.FORM_TARGET,
            }
        )

        # Privacy policy content (loaded from MD)
        try:
            from apps.core.domain.contrib.privacy import get_privacy_html
            context["privacy_content"] = get_privacy_html()
        except Exception:
            context["privacy_content"] = ""

        return context

    def setup(self, request, *args, **kwargs):
        """Setup with auth-specific checks."""
        super().setup(request, *args, **kwargs)

        # Redirect authenticated users away from auth pages
        if request.user.is_authenticated and self.require_auth is False:
            # This will be handled in get() method
            pass


# ===============================================
# AUTH MODAL COMPONENTS (FOR MODAL DIALOGS)
# ===============================================


class AuthModalBase(PageHandler, AuthProcessorMixin):
    """Base class for auth modals."""

    # Modal configuration
    modal_size = "md"
    modal_title = ""
    close_button = True
    backdrop = True

    # Page configuration overrides for modals
    template_name = "components/modal_auth.html"
    fragment_name = "auth.modal"

    def get_context_data(self, **kwargs):
        """Add modal-specific context."""
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "modal_size": self.modal_size,
                "modal_title": self.modal_title or self.page_title,
                "close_button": self.close_button,
                "backdrop": self.backdrop,
                "is_modal": True,
            }
        )

        return context


class LoginModal(AuthModalBase):
    """Login modal component."""

    page_title = "Login"
    modal_title = "Login to Your Account"
    modal_size = "sm"

    def get(self, request, *args, **kwargs):
        """Handle GET for login modal."""
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST for login modal."""
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        # Process login but don't redirect (stay in modal)
        response = self.process_login(request)

        # If login was successful and we're in HTMX, trigger modal close
        if request.htmx and response.status_code == 200:
            # Check if response has redirect header
            if "HX-Redirect" in response:
                # Login successful, redirect will happen client-side
                pass

        return response


class RegisterModal(AuthModalBase):
    """Registration modal component."""

    page_title = "Register"
    modal_title = "Create New Account"
    modal_size = "md"

    def get(self, request, *args, **kwargs):
        """Handle GET for registration modal."""
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST for registration modal."""
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        return self.process_registration(request)