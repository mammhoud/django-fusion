"""
Allauth-backed Login and Signup Views
======================================
Wraps allauth's LoginView and SignupView inside PageHandler so that
HTMX fragment rendering and the auth skeleton work without duplication.

Both views call trigger_notification() on every HTMX response (success
and error) so the client-side notification bundle always fires.
"""

from allauth.account.views import LoginView as AllauthBaseLoginView
from allauth.account.views import SignupView as AllauthBaseSignupView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django_fusion.site.interface.page_handler import PageHandler

from ..services.notifications import trigger_notification


class AllauthLoginView(PageHandler, AllauthBaseLoginView):
    """
    Wraps allauth LoginView inside PageHandler so HTMX fragment
    rendering and the auth skeleton work without duplication.
    """

    template_name = "registration/login.html"
    fragment_template = "registration/fragments/login_form.html"
    page_title = "Sign In"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("handlers:dashboard")
        if self.strategy == "fragment":
            return self.render_fragment(request, self.get_context_data())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            htmx_response = HttpResponse(status=200)
            htmx_response["HX-Redirect"] = self.get_success_url()
            trigger_notification(htmx_response, "Welcome back!", "success")
            return htmx_response
        return response

    def form_invalid(self, form):
        first_error = next(iter(form.errors.values()))[0] if form.errors else "Login failed."
        if self.request.headers.get("HX-Request"):
            context = self.get_context_data(form=form)
            response = self.render_fragment(self.request, context)
            trigger_notification(response, first_error, "error")
            return response
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
        try:
            return reverse("handlers:dashboard")
        except Exception:
            return "/"


class AllauthSignupView(PageHandler, AllauthBaseSignupView):
    """
    Wraps allauth SignupView inside PageHandler.
    On success, delegates email sending to RegistrationAdapter.
    """

    template_name = "registration/register.html"
    fragment_template = "registration/fragments/register_form.html"
    page_title = "Register"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("handlers:dashboard")
        if self.strategy == "fragment":
            return self.render_fragment(request, self.get_context_data())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            context = self.get_context_data(
                form=form,
                success=True,
                email=form.cleaned_data.get("email", ""),
            )
            htmx_response = self.render_fragment(self.request, context)
            trigger_notification(htmx_response, "Account created! Check your email.", "success")
            return htmx_response
        return response

    def form_invalid(self, form):
        first_error = next(iter(form.errors.values()))[0] if form.errors else "Signup failed."
        if self.request.headers.get("HX-Request"):
            context = self.get_context_data(form=form)
            response = self.render_fragment(self.request, context)
            trigger_notification(response, first_error, "error")
            return response
        return super().form_invalid(form)