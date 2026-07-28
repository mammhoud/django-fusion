"""
Allauth-backed Login and Signup Views
======================================
Wraps allauth's LoginView and SignupView inside PageHandler so that
HTMX fragment rendering and the auth skeleton work without duplication.

PageHandler.post() delegates to process_post(), which we implement here
to hand control back to allauth's form-based POST pipeline (get_form →
form_valid / form_invalid).

Both views call trigger_notification() on every HTMX response (success
and error) so the client-side notification bundle always fires.
"""

from allauth.account.views import LoginView as AllauthBaseLoginView
from allauth.account.views import SignupView as AllauthBaseSignupView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django_fusion.site.interface.page_handler import PageHandler

from .management.services.notifications import trigger_notification


class AllauthLoginView(PageHandler, AllauthBaseLoginView):
    """
    Wraps allauth LoginView inside PageHandler so HTMX fragment
    rendering and the auth skeleton work without duplication.

    process_post() hands POST back to allauth's form pipeline so that
    PageHandler.post() does not swallow allauth's form_valid/form_invalid.
    """

    template_name = "account/login.html"
    fragment_template = "account/fragments/login_form.html"
    page_title = "Sign In"

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        if self.strategy == "fragment":
            return render(request, self.fragment_template, self.get_context_data())
        return AllauthBaseLoginView.get(self, request, *args, **kwargs)

    # ------------------------------------------------------------------
    # POST — required by PageHandler; delegates to allauth form pipeline
    # ------------------------------------------------------------------

    def process_post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Delegate POST to allauth's form-based pipeline."""
        return AllauthBaseLoginView.post(self, request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Form callbacks
    # ------------------------------------------------------------------

    def form_valid(self, form):
        response = AllauthBaseLoginView.form_valid(self, form)
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
            response = render(self.request, self.fragment_template, context)
            trigger_notification(response, first_error, "error")
            return response
        return AllauthBaseLoginView.form_invalid(self, form)

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

    process_post() hands POST back to allauth's form pipeline so that
    PageHandler.post() does not swallow allauth's form_valid/form_invalid.
    """

    template_name = "account/register.html"
    fragment_template = "account/fragments/register_form.html"
    page_title = "Register"

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        if self.strategy == "fragment":
            return render(request, self.fragment_template, self.get_context_data())
        return AllauthBaseSignupView.get(self, request, *args, **kwargs)

    # ------------------------------------------------------------------
    # POST — required by PageHandler; delegates to allauth form pipeline
    # ------------------------------------------------------------------

    def process_post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Delegate POST to allauth's form-based pipeline."""
        return AllauthBaseSignupView.post(self, request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Form callbacks
    # ------------------------------------------------------------------

    def form_valid(self, form):
        response = AllauthBaseSignupView.form_valid(self, form)
        if self.request.headers.get("HX-Request"):
            context = self.get_context_data(
                form=form,
                success=True,
                email=form.cleaned_data.get("email", ""),
            )
            htmx_response = render(self.request, self.fragment_template, context)
            trigger_notification(htmx_response, "Account created! Check your email.", "success")
            return htmx_response
        return response

    def form_invalid(self, form):
        first_error = next(iter(form.errors.values()))[0] if form.errors else "Signup failed."
        if self.request.headers.get("HX-Request"):
            context = self.get_context_data(form=form)
            response = render(self.request, self.fragment_template, context)
            trigger_notification(response, first_error, "error")
            return response
        return AllauthBaseSignupView.form_invalid(self, form)