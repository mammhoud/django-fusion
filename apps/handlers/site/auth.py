import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from django_grep.comp.site import PageHandler
# Assuming a custom form exists, otherwise fallback to UserCreationForm would be needed
from apps.users.forms import UserRegisterForm
from apps.handlers.services import trigger_notification

class RegisterView(PageHandler):
    """
    HTMX-based Registration View.
    Handles user creation, group assignment, and notification triggers.
    """
    page_title = "Create Account"
    template_name = "auth/register.html"
    fragment_name = "auth.register"
    layout_path = "auth/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = UserRegisterForm()
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # 1. Handle Activation Logic
            # If normal registration, user might need email activation
            # For now, we set active=True for immediate access unless configured otherwise
            user.is_active = True
            user.save()

            # 2. Group Handling
            # Default to 'Student' or 'Instructor' based on form data or default
            # Ensuring groups exist safely
            group_name = form.cleaned_data.get('account_type', 'Student')
            if group_name not in ['Instructor', 'Content Manager', 'Student']:
                group_name = 'Student'

            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            # 3. Login the user immediately
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # 4. HTMX Response Strategy
            if request.headers.get('HX-Request'):
                # Use trigger_notification helper for consistent notification format
                response = HttpResponse(status=204)
                trigger_notification(response, "Account created successfully! Redirecting...", "success")
                # Redirect to dashboard after short delay handled by client or immediate redirect
                response['HX-Redirect'] = settings.LOGIN_REDIRECT_URL
                return response

            # Fallback for non-HTMX
            return redirect(settings.LOGIN_REDIRECT_URL)

        else:
            # Form Invalid
            context = self.get_context_data(request)
            context['form'] = form

            if request.headers.get('HX-Request'):
                # Return just the form fragment with errors
                return render(request, "auth/partials/register_form.html", context)

            return render(request, self.template_name, context)

class LoginView(PageHandler):
    """
    HTMX-based Login View.
    """
    page_title = "Sign In"
    template_name = "auth/login.html"
    fragment_name = "auth.login"
    layout_path = "auth/skeleton.html"

    def post(self, request: HttpRequest, *args, **kwargs):
        # Implementation of login logic would go here
        # For brevity, focusing on the requested RegisterView
        pass

def email_activation_sent(request):
    """
    Static view for email sent confirmation.
    """
    return render(request, "auth/activation_sent.html")
