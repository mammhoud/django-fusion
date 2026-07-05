"""
Enhanced login forms with dual-framework styling.
Supports email, username, and phone authentication with code/password options.
"""

from allauth.account import app_settings
from allauth.account.app_settings import LoginMethod
from allauth.account.internal import flows
from allauth.account.utils import get_adapter
from allauth.core import context
from allauth.core.internal.httpkit import headed_redirect_response
from allauth.utils import get_username_max_length, set_form_field_order
from crispy_forms.layout import HTML
from django import forms
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_fusion.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin
from .code import RequestLoginCodeForm


class LoginForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                       ValidationMixin, forms.Form):
    """
    Enhanced login form supporting both password and code-based authentication.
    Compatible with Bootstrap and Tailwind CSS frameworks.
    """

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    remember = forms.BooleanField(
        label=_("Remember me"),
        required=False,
        help_text=_("Keep me logged in for 30 days"),
    )

    user = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Setup login field based on configuration
        adapter = get_adapter()
        login_field = self._get_login_field(adapter)
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])

        # Remove remember field if session remember is forced
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]

        # Setup form layout
        self.setup_layout(
            fields=["login", "password", "remember"],
            submit_text=_("Sign In"),
            show_links=True
        )

        # Configure password help text
        self._setup_password_help_text()

        # Apply initial styling
        self.apply_initial_styling()

    def apply_initial_styling(self):
        """Apply initial styling to form fields."""
        # Style password field
        self.apply_field_styling(
            self.fields['password'],
            field_type='password',
            placeholder=_("Enter your password")
        )

        # Style remember checkbox
        if 'remember' in self.fields:
            self.apply_field_styling(
                self.fields['remember'],
                field_type='checkbox'
            )

    def _get_login_field(self, adapter):
        """Determine the login field based on configuration."""
        if app_settings.LOGIN_METHODS == {LoginMethod.EMAIL}:
            return forms.EmailField(
                label=_("Email"),
                widget=forms.EmailInput(
                    attrs={
                        "placeholder": _("Email address"),
                        "autocomplete": "email",
                    }
                ),
            )
        elif app_settings.LOGIN_METHODS == {LoginMethod.USERNAME}:
            return forms.CharField(
                label=_("Username"),
                widget=forms.TextInput(
                    attrs={
                        "placeholder": _("Username"),
                        "autocomplete": "username",
                    }
                ),
                max_length=get_username_max_length(),
            )
        elif app_settings.LOGIN_METHODS == {LoginMethod.PHONE}:
            return adapter.phone_form_field(required=True)
        else:
            return forms.CharField(
                label=_("Login"),
                widget=forms.TextInput(
                    attrs={
                        "placeholder": self._get_login_placeholder(),
                        "autocomplete": "email",
                    }
                ),
            )

    def _get_login_placeholder(self):
        """Get appropriate placeholder based on login methods."""
        methods = app_settings.LOGIN_METHODS
        if len(methods) == 3:
            return _("Username, email or phone")
        elif methods == {LoginMethod.USERNAME, LoginMethod.EMAIL}:
            return _("Username or email")
        elif methods == {LoginMethod.USERNAME, LoginMethod.PHONE}:
            return _("Username or phone")
        elif methods == {LoginMethod.EMAIL, LoginMethod.PHONE}:
            return _("Email or phone")
        raise ValueError("Unsupported login method combination")

    def _setup_password_help_text(self):
        """Setup password help text with reset link."""
        try:
            self.fields["password"].help_text = render_to_string(
                f"account/password_reset_help_text.{app_settings.TEMPLATE_EXTENSION}"
            )
        except TemplateDoesNotExist:
            try:
                reset_url = reverse("account_reset_password")
                style = self.get_styling('button', 'types')

                self.fields["password"].help_text = mark_safe(
                    f'<a href="{reset_url}" class="text-decoration-none {style.get("secondary", "")}">'
                    f'{_("Forgot your password?")}</a>'
                )
            except NoReverseMatch:
                pass

    # Authentication methods
    def user_credentials(self) -> dict:
        """Collect user credentials for authentication."""
        login = self.cleaned_data["login"].strip()
        method = flows.login.derive_login_method(login)
        credentials = {method: login}

        # Allow username fallback if it looks like an email but username is allowed.
        if LoginMethod.USERNAME in app_settings.LOGIN_METHODS and method != LoginMethod.USERNAME:
            credentials[LoginMethod.USERNAME] = login

        if password := self.cleaned_data.get("password"):
            credentials["password"] = password
        return credentials

    def clean(self):
        super().clean()
        if self.errors:
            return
        credentials = self.user_credentials()
        if "password" in credentials:
            return self._clean_with_password(credentials)
        return self._clean_without_password(
            credentials.get("email"), credentials.get("phone")
        )

    def _clean_with_password(self, credentials: dict):
        adapter = get_adapter(self.request)
        user = adapter.authenticate(self.request, **credentials)
        if user:
            login = flows.login.Login(user=user, email=credentials.get("email"))
            if flows.login.is_login_rate_limited(context.request, login):
                raise adapter.validation_error("too_many_login_attempts")
            self.user = user
        else:
            method = flows.login.derive_login_method(login=self.cleaned_data["login"])
            raise adapter.validation_error(f"{method.value}_password_mismatch")
        return self.cleaned_data

    def _clean_without_password(self, email: str | None, phone: str | None):
        data = {"email": email, "phone": phone}
        data = {k: v for k, v in data.items() if v}
        if not data:
            self.add_error("login", get_adapter().validation_error("invalid_login"))
        else:
            form = RequestLoginCodeForm(data)
            if not form.is_valid():
                for field in ["phone", "email"]:
                    for error in form.errors.get(field, []):
                        self.add_error("login", error)
            else:
                self.user = getattr(form, "_user", None)
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        credentials = self.user_credentials()
        if "password" in credentials:
            return self._login_with_password(request, redirect_url, credentials)
        return self._login_by_code(request, redirect_url, credentials)

    def _login_by_code(self, request, redirect_url, credentials):
        user = getattr(self, "user", None)
        flows.login_by_code.LoginCodeVerificationProcess.initiate(
            request=request,
            user=user,
            phone=credentials.get("phone"),
            email=credentials.get("email"),
        )
        query = {app_settings.REDIRECT_FIELD_NAME: redirect_url} if redirect_url else None
        return headed_redirect_response("account_confirm_login_code", query=query)

    def _login_with_password(self, request, redirect_url, credentials):
        login = flows.login.Login(user=self.user, email=credentials.get("email"))
        login.redirect_url = redirect_url
        response = flows.login.perform_password_login(request, credentials, login)

        remember = (
            app_settings.SESSION_REMEMBER
            if app_settings.SESSION_REMEMBER is not None
            else self.cleaned_data.get("remember", False)
        )
        request.session.set_expiry(
            app_settings.SESSION_COOKIE_AGE if remember else 0
        )
        return response

    def get_form_links(self):
        """Override to add signup link."""
        links = super().get_form_links()
        style = self.get_styling('button', 'types')

        signup_link = HTML(f'''
            <div class="text-center mt-2">
                <span class="text-muted">{_("Don't have an account?")}</span>
                <a href="{reverse("account_signup")}"
                   class="text-decoration-none ms-1 {style.get('primary', '')}">
                    {_("Sign up")}
                </a>
            </div>
        ''')

        return links + [signup_link]
