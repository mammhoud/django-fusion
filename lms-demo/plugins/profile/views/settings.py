from typing import Dict

from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_osoul.site import NotificationMixin, PageHandler
from django_rseal.workflows.pipelines.models import Person
from django_rseal.workflows.pipelines.site.mixins import ProfileContextMixin, ProfileOperationsMixin

from plugins.accounts.forms import (
    AccountSettingsForm,
    BillingSettingsForm,
    NotificationSettingsForm,
    PreferencesSettingsForm,
    PrivacySettingsForm,
    SecuritySettingsForm,
)
from plugins.accounts.services import PersonService


class SettingsView(PageHandler, NotificationMixin, ProfileContextMixin, ProfileOperationsMixin):
    """
    Settings view with tab-based navigation and traditional form submissions.
    All sections are loaded on a single page with Bootstrap tabs.
    """

    page_title = _("Settings")
    template_name = "profile/settings.html"
    fragment_name = "profile.settings"
    layout_path = "profile/skeleton.html"

    # Form classes for each section
    form_classes = {
        "account": AccountSettingsForm,
        "privacy": PrivacySettingsForm,
        "notifications": NotificationSettingsForm,
        "security": SecuritySettingsForm,
        "preferences": PreferencesSettingsForm,
        "billing": BillingSettingsForm,
    }

    def get(self, request: HttpRequest, *args, **kwargs):
        """Handle GET requests for settings page."""
        # Only handle the main settings page
        if request.path != '/profile/settings/':
            # Redirect any other GET requests to the main settings page
            return redirect('profile:settings')

        # Check for notification in session
        notification_data = None
        if 'notification_data' in request.session:
            notification_data = request.session.pop('notification_data')

        # Regular GET request for settings page
        context = self.get_context_data(request)

        # Add notification data to context if exists
        if notification_data:
            context['notification_data'] = notification_data

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args, **kwargs):
        """Handle POST requests for settings page."""
        # Determine action based on URL
        action_url = request.path

        # Map action URLs to handlers
        action_handlers = {
            '/profile/settings/change-password/': self._handle_password_change,
            '/profile/settings/enable-2fa/': self._handle_enable_2fa,
            '/profile/settings/disable-2fa/': self._handle_disable_2fa,
            '/profile/settings/verify-2fa/': self._handle_verify_2fa,
            '/profile/settings/test-notification/': self._handle_test_notification,
            '/profile/settings/export-data/': self._handle_export_data,
            '/profile/settings/delete-account/': self._handle_delete_account,
            '/profile/settings/revoke-sessions/': self._handle_revoke_sessions,
            '/profile/settings/update-plan/': self._handle_update_plan,
            '/profile/settings/cancel-subscription/': self._handle_cancel_subscription,
        }

        # Check for specific action URL
        for url, handler in action_handlers.items():
            if action_url == url:
                return handler(request)

        # Default: handle main settings page form submission
        return self._handle_settings_post(request)

    def _handle_settings_post(self, request: HttpRequest):
        """Handle POST request for main settings page (form submissions)."""
        if not request.user.is_authenticated:
            return self.show_notification(
                message=_("Authentication required"),
                level="error",
                title=_("Access Denied"),
                redirect_url='login',
                request=request
            )

        person = Person.objects.filter(user=request.user).first()
        if not person:
            return self.show_notification(
                message=_("User profile not found"),
                level="error",
                title=_("Profile Error"),
                request=request
            )

        # Check if this is just a tab update request
        update_tab_only = request.POST.get('update_tab_only', 'false') == 'true'
        if update_tab_only:
            section = request.POST.get('section', 'account')
            request.session['active_settings_tab'] = section
            return JsonResponse({'success': True, 'active_tab': section})

        # Determine which section form was submitted
        section = request.POST.get('section', 'account')

        if section not in self.form_classes:
            return self.show_notification(
                message=_("Invalid settings section"),
                level="error",
                title=_("Form Error"),
                request=request
            )

        # Process form submission
        profile_info = PersonService.get_user_profile_information(request.user)
        initial_data = self._get_form_initial_data(section, person, profile_info)
        form = self.form_classes[section](request.POST, initial=initial_data)

        if form.is_valid():
            try:
                self._save_section_data(section, form.cleaned_data, person)

                # Store the active tab in session to keep it selected
                request.session['active_settings_tab'] = section

                # Return with success notification
                return self.show_notification(
                    message=_("Settings updated successfully"),
                    level="success",
                    title=_("Settings Saved"),
                    duration=3000,
                    redirect_url='profile:settings',
                    request=request
                )

            except Exception as e:
                error_msg = str(e)
                # Return with error notification and re-render page
                request.session['active_settings_tab'] = section
                context = self.get_context_data(request)
                # Update the form with errors
                context['all_sections_data'][section]['form'] = form
                return render(request, self.template_name, context)
        else:
            # Return with form errors
            request.session['active_settings_tab'] = section
            context = self.get_context_data(request)
            # Update the form with errors
            context['all_sections_data'][section]['form'] = form
            return render(request, self.template_name, context)

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get comprehensive context data for settings page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            # Get person record
            person = Person.objects.filter(user=request.user).first()

            if person:
                # Get detailed profile information
                profile_info = PersonService.get_user_profile_information(request.user)

                # Get settings data
                context.update(self._get_settings_context(person, profile_info))

                # Get all sections data
                context["all_sections_data"] = self._get_all_sections_data(person, profile_info)

                # Determine active tab (from session or default to account)
                context["active_tab"] = request.session.get('active_settings_tab', 'account')

                # Add 2FA session data if exists
                if '2fa_qr_code' in request.session:
                    context['two_factor_data'] = {
                        'qr_code': request.session.get('2fa_qr_code'),
                        'secret': request.session.get('2fa_secret_display'),
                    }

        return context

    def _get_settings_context(self, person: Person, profile_info: Dict) -> Dict:
        """
        Get all context needed for the settings panel template.
        """
        return {
            "person": person,
            "profile_info": profile_info,
            "completion_percentage": person.completion_percentage,
            "is_complete": person.is_complete,
            "settings_tabs": [
                {
                    "id": "account",
                    "title": _("Account"),
                    "icon": "user",
                },
                {
                    "id": "privacy",
                    "title": _("Privacy"),
                    "icon": "shield-alt",
                },
                {
                    "id": "notifications",
                    "title": _("Notifications"),
                    "icon": "bell",
                },
                {
                    "id": "security",
                    "title": _("Security"),
                    "icon": "lock",
                },
                {
                    "id": "preferences",
                    "title": _("Preferences"),
                    "icon": "palette",
                },
                {
                    "id": "billing",
                    "title": _("Billing"),
                    "icon": "credit-card",
                },
            ],
            "stats_overview": {
                "total_courses": person.enrolled_courses.count()
                if hasattr(person, "enrolled_courses")
                else 0,
                "completed_courses": person.completed_courses.count()
                if hasattr(person, "completed_courses")
                else 0,
                "total_certifications": person.certifications.count()
                if hasattr(person, "certifications")
                else 0,
                "active_projects": person.projects.filter(status="in_progress").count()
                if hasattr(person, "projects")
                else 0,
                "total_connections": getattr(person, "connection_count", 0),
                "profile_views": getattr(person, "profile_views", 0),
            },
        }

    def _get_all_sections_data(self, person: Person, profile_info: Dict) -> Dict:
        """Get form data for all sections."""
        sections_data = {}
        for section in self.form_classes.keys():
            sections_data[section] = {
                "form": self.form_classes[section](initial=self._get_form_initial_data(section, person, profile_info)),
                "title": self._get_section_title(section),
            }
        return sections_data

    def _get_form_initial_data(self, section: str, person: Person, profile_info: Dict) -> Dict:
        """Get initial data for form based on section."""
        initial_data = {
            "user_id": person.user.id,
        }

        if section == "account":
            initial_data.update(
                {
                    "first_name": person.user.first_name,
                    "last_name": person.user.last_name,
                    "email": person.user.email,
                    "username": person.user.username,
                    "phone": getattr(person, "phone", ""),
                    "location": getattr(person, "location", ""),
                    "bio": getattr(person, "bio", ""),
                    "public_profile": getattr(person, "public_profile", False),
                }
            )
        elif section == "privacy":
            initial_data.update(
                {
                    "profile_visibility": getattr(person, "profile_visibility", "public"),
                    "share_usage_data": getattr(person, "share_usage_data", True),
                    "allow_search_indexing": getattr(person, "allow_search_indexing", True),
                    "show_online_status": getattr(person, "show_online_status", True),
                    "allow_contact": getattr(person, "allow_contact", True),
                    "show_email": getattr(person, "show_email", False),
                }
            )
        elif section == "notifications":
            initial_data.update(
                {
                    "course_updates": getattr(person, "course_updates_notifications", True),
                    "instructor_messages": getattr(
                        person, "instructor_messages_notifications", True
                    ),
                    "marketing_emails": getattr(person, "marketing_emails", False),
                    "weekly_reports": getattr(person, "weekly_reports_notifications", True),
                    "assignment_notifications": getattr(person, "assignment_notifications", True),
                    "forum_activity": getattr(person, "forum_activity_notifications", False),
                    "deadline_reminders": getattr(person, "deadline_reminders_notifications", True),
                    "sms_notifications": getattr(person, "sms_notifications", False),
                }
            )
        elif section == "security":
            initial_data.update(
                {
                    "two_factor_enabled": getattr(person, "two_factor_enabled", False),
                    "password_last_changed": getattr(person, "password_last_changed", None),
                }
            )
        elif section == "preferences":
            initial_data.update(
                {
                    "language": getattr(person, "language", "en-us"),
                    "timezone": getattr(person, "timezone", "UTC"),
                    "dark_mode": getattr(person, "dark_mode", True),
                    "high_contrast": getattr(person, "high_contrast", False),
                    "reduce_animations": getattr(person, "reduce_animations", True),
                    "density": getattr(person, "ui_density", "comfortable"),
                }
            )
        elif section == "billing":
            initial_data.update(
                {
                    "plan": getattr(person, "subscription_plan", "free"),
                    "payment_method": getattr(person, "payment_method", ""),
                    "auto_renew": getattr(person, "auto_renew", True),
                }
            )

        return initial_data

    def _get_section_title(self, section: str) -> str:
        """Get title for section."""
        titles = {
            "account": _("Account Settings"),
            "privacy": _("Privacy Settings"),
            "notifications": _("Notification Settings"),
            "security": _("Security Settings"),
            "preferences": _("Preferences"),
            "billing": _("Billing Settings"),
        }
        return titles.get(section, _("Settings"))

    # Action handlers using show_notification
    def _handle_password_change(self, request: HttpRequest):
        """Handle password change request."""
        try:
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            # Validate current password
            from django.contrib.auth import authenticate
            user = authenticate(
                username=request.user.username,
                password=current_password
            )

            if not user:
                return self.show_notification(
                    message=_("Current password is incorrect"),
                    level="error",
                    title=_("Password Change Failed"),
                    duration=5000,
                    request=request
                )

            # Validate new password
            if not new_password or len(new_password) < 8:
                return self.show_notification(
                    message=_("New password must be at least 8 characters long"),
                    level="error",
                    title=_("Password Change Failed"),
                    duration=5000,
                    request=request
                )

            if new_password != confirm_password:
                return self.show_notification(
                    message=_("New passwords do not match"),
                    level="error",
                    title=_("Password Change Failed"),
                    duration=5000,
                    request=request
                )

            # Update password
            user.set_password(new_password)
            user.save()

            # Update password change timestamp
            person = Person.objects.filter(user=request.user).first()
            if person:
                person.password_last_changed = timezone.now()
                person.save()

            # Set security tab as active
            request.session['active_settings_tab'] = 'security'

            return self.show_notification(
                message=_("Password updated successfully"),
                level="success",
                title=_("Password Changed"),
                duration=3000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'security'
            return self.show_notification(
                message=_("Failed to change password: {}").format(str(e)),
                level="error",
                title=_("Password Change Failed"),
                duration=5000,
                request=request
            )

    def _handle_enable_2fa(self, request: HttpRequest):
        """Handle 2FA enable request."""
        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return self.show_notification(
                    message=_("User not found"),
                    level="error",
                    title=_("2FA Setup Failed"),
                    duration=5000,
                    request=request
                )

            # Generate 2FA secret and QR code
            import base64
            import io

            import pyotp
            import qrcode

            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)

            # Generate QR code
            provisioning_uri = totp.provisioning_uri(
                name=person.user.email,
                issuer_name="Your App Name"
            )

            qr = qrcode.make(provisioning_uri)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")
            qr_code = base64.b64encode(buffer.getvalue()).decode()

            # Store secret temporarily in session
            request.session['2fa_secret'] = secret
            request.session['2fa_qr_code'] = f"data:image/png;base64,{qr_code}"
            request.session['2fa_secret_display'] = secret

            # Store notification in session for GET request
            request.session['notification_data'] = {
                'message': _("Please scan the QR code with your authenticator app"),
                'level': 'info',
                'title': _("2FA Setup"),
                'duration': 10000,
            }

            request.session['active_settings_tab'] = 'security'
            return redirect('profile:settings')

        except Exception as e:
            request.session['active_settings_tab'] = 'security'
            return self.show_notification(
                message=_("Failed to setup 2FA: {}").format(str(e)),
                level="error",
                title=_("2FA Setup Failed"),
                duration=5000,
                request=request
            )

    def _handle_disable_2fa(self, request: HttpRequest):
        """Handle 2FA disable request."""
        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return self.show_notification(
                    message=_("User not found"),
                    level="error",
                    title=_("2FA Disable Failed"),
                    duration=5000,
                    request=request
                )

            # Disable 2FA
            person.two_factor_enabled = False
            person.two_factor_secret = None
            person.save()

            # Clean up session
            if '2fa_secret' in request.session:
                del request.session['2fa_secret']
            if '2fa_qr_code' in request.session:
                del request.session['2fa_qr_code']
            if '2fa_secret_display' in request.session:
                del request.session['2fa_secret_display']

            request.session['active_settings_tab'] = 'security'

            return self.show_notification(
                message=_("Two-factor authentication disabled successfully"),
                level="success",
                title=_("2FA Disabled"),
                duration=3000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'security'
            return self.show_notification(
                message=_("Failed to disable 2FA: {}").format(str(e)),
                level="error",
                title=_("2FA Disable Failed"),
                duration=5000,
                request=request
            )

    def _handle_verify_2fa(self, request: HttpRequest):
        """Handle 2FA verification."""
        try:
            code = request.POST.get('code', '')

            person = Person.objects.filter(user=request.user).first()
            if not person:
                return self.show_notification(
                    message=_("User not found"),
                    level="error",
                    title=_("2FA Verification Failed"),
                    duration=5000,
                    request=request
                )

            # Verify the code
            secret = request.session.get('2fa_secret')
            if not secret:
                return self.show_notification(
                    message=_("Session expired. Please try again."),
                    level="error",
                    title=_("2FA Verification Failed"),
                    duration=5000,
                    request=request
                )

            import pyotp
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                person.two_factor_enabled = True
                person.two_factor_secret = secret
                person.save()

                # Clean up session
                if '2fa_secret' in request.session:
                    del request.session['2fa_secret']
                if '2fa_qr_code' in request.session:
                    del request.session['2fa_qr_code']
                if '2fa_secret_display' in request.session:
                    del request.session['2fa_secret_display']

                request.session['active_settings_tab'] = 'security'

                return self.show_notification(
                    message=_("Two-factor authentication enabled successfully"),
                    level="success",
                    title=_("2FA Enabled"),
                    duration=3000,
                    redirect_url='profile:settings',
                    request=request
                )
            else:
                request.session['active_settings_tab'] = 'security'
                return self.show_notification(
                    message=_("Invalid verification code"),
                    level="error",
                    title=_("2FA Verification Failed"),
                    duration=5000,
                    request=request
                )

        except Exception as e:
            request.session['active_settings_tab'] = 'security'
            return self.show_notification(
                message=_("Failed to verify 2FA: {}").format(str(e)),
                level="error",
                title=_("2FA Verification Failed"),
                duration=5000,
                request=request
            )

    def _handle_test_notification(self, request: HttpRequest):
        """Handle test notification request."""
        try:
            request.session['active_settings_tab'] = 'notifications'

            return self.show_notification(
                message=_("Test notification sent successfully!"),
                level="success",
                title=_("Test Notification"),
                duration=3000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'notifications'
            return self.show_notification(
                message=_("Failed to send test notification: {}").format(str(e)),
                level="error",
                title=_("Test Failed"),
                duration=5000,
                request=request
            )

    def _handle_export_data(self, request: HttpRequest):
        """Handle data export request."""
        try:
            # Generate data export
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return self.show_notification(
                    message=_("User not found"),
                    level="error",
                    title=_("Export Failed"),
                    duration=5000,
                    request=request
                )

            # In a real implementation, you would:
            # 1. Create a data export task
            # 2. Send email with download link
            # 3. Log the export request

            request.session['active_settings_tab'] = 'privacy'

            return self.show_notification(
                message=_("Data export requested. You will receive an email when it's ready."),
                level="info",
                title=_("Export Requested"),
                duration=5000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'privacy'
            return self.show_notification(
                message=_("Failed to request data export: {}").format(str(e)),
                level="error",
                title=_("Export Failed"),
                duration=5000,
                request=request
            )

    def _handle_delete_account(self, request: HttpRequest):
        """Handle account deletion request."""
        try:
            confirm = request.POST.get('confirm', '').lower() == 'true'
            password = request.POST.get('password', '')

            if not confirm:
                request.session['active_settings_tab'] = 'privacy'
                return self.show_notification(
                    message=_("Please confirm account deletion"),
                    level="error",
                    title=_("Deletion Cancelled"),
                    duration=5000,
                    request=request
                )

            # Verify password
            from django.contrib.auth import authenticate
            user = authenticate(
                username=request.user.username,
                password=password
            )

            if not user:
                request.session['active_settings_tab'] = 'privacy'
                return self.show_notification(
                    message=_("Invalid password"),
                    level="error",
                    title=_("Deletion Failed"),
                    duration=5000,
                    request=request
                )

            # In a real implementation, you would:
            # 1. Schedule account deletion (not immediate)
            # 2. Send confirmation email
            # 3. Logout user

            # Store success message in session for after logout
            request.session['post_logout_message'] = _("Account deletion requested. You will receive a confirmation email.")

            # Note: In production, don't delete immediately
            # user.delete()

            return redirect('logout')  # Redirect to logout after deletion request

        except Exception as e:
            request.session['active_settings_tab'] = 'privacy'
            return self.show_notification(
                message=_("Failed to delete account: {}").format(str(e)),
                level="error",
                title=_("Deletion Failed"),
                duration=5000,
                request=request
            )

    def _handle_revoke_sessions(self, request: HttpRequest):
        """Handle session revocation request."""
        try:
            # In a real implementation, you would:
            # 1. Delete all user sessions except current
            # 2. Log the action

            from django.contrib.auth import get_user_model
            from django.contrib.sessions.models import Session

            User = get_user_model()
            user_sessions = []

            # Get all sessions for the current user
            for session in Session.objects.all():
                session_data = session.get_decoded()
                if 'auth_user_id' in session_data:
                    if str(session_data['auth_user_id']) == str(request.user.id):
                        user_sessions.append(session)

            # Delete all sessions except current
            current_session_key = request.session.session_key
            for session in user_sessions:
                if session.session_key != current_session_key:
                    session.delete()

            request.session['active_settings_tab'] = 'security'

            return self.show_notification(
                message=_("All other sessions have been revoked"),
                level="success",
                title=_("Sessions Revoked"),
                duration=3000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'security'
            return self.show_notification(
                message=_("Failed to revoke sessions: {}").format(str(e)),
                level="error",
                title=_("Revoke Failed"),
                duration=5000,
                request=request
            )

    def _handle_update_plan(self, request: HttpRequest):
        """Handle subscription plan update."""
        try:
            plan = request.POST.get('plan', '')
            billing_cycle = request.POST.get('billing_cycle', 'monthly')

            person = Person.objects.filter(user=request.user).first()
            if not person:
                return self.show_notification(
                    message=_("User not found"),
                    level="error",
                    title=_("Update Failed"),
                    duration=5000,
                    request=request
                )

            # Update subscription plan
            person.subscription_plan = plan
            person.billing_cycle = billing_cycle
            person.save()

            request.session['active_settings_tab'] = 'billing'

            return self.show_notification(
                message=_("Subscription plan updated successfully"),
                level="success",
                title=_("Plan Updated"),
                duration=3000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'billing'
            return self.show_notification(
                message=_("Failed to update plan: {}").format(str(e)),
                level="error",
                title=_("Update Failed"),
                duration=5000,
                request=request
            )

    def _handle_cancel_subscription(self, request: HttpRequest):
        """Handle subscription cancellation."""
        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return self.show_notification(
                    message=_("User not found"),
                    level="error",
                    title=_("Cancellation Failed"),
                    duration=5000,
                    request=request
                )

            # Cancel subscription
            person.subscription_status = 'cancelled'
            person.auto_renew = False
            person.save()

            request.session['active_settings_tab'] = 'billing'

            return self.show_notification(
                message=_("Subscription cancelled successfully"),
                level="success",
                title=_("Subscription Cancelled"),
                duration=3000,
                redirect_url='profile:settings',
                request=request
            )

        except Exception as e:
            request.session['active_settings_tab'] = 'billing'
            return self.show_notification(
                message=_("Failed to cancel subscription: {}").format(str(e)),
                level="error",
                title=_("Cancellation Failed"),
                duration=5000,
                request=request
            )

    def _save_section_data(self, section: str, data: Dict, person: Person):
        """Save data for specific section."""
        if section == "account":
            self._save_account_data(data, person)
        elif section == "privacy":
            self._save_privacy_data(data, person)
        elif section == "notifications":
            self._save_notification_data(data, person)
        elif section == "security":
            self._save_security_data(data, person)
        elif section == "preferences":
            self._save_preferences_data(data, person)
        elif section == "billing":
            self._save_billing_data(data, person)

        person.save()
        person.user.save()

    def _save_account_data(self, data: Dict, person: Person):
        """Save account data."""
        if "first_name" in data:
            person.user.first_name = data["first_name"]
        if "last_name" in data:
            person.user.last_name = data["last_name"]
        if "email" in data and data["email"] != person.user.email:
            person.user.email = data["email"]
            person.email_verified = False

        # Update profile fields
        for field in ["phone", "location", "bio", "public_profile"]:
            if field in data:
                setattr(person, field, data[field])

    def _save_privacy_data(self, data: Dict, person: Person):
        """Save privacy data."""
        for field in [
            "profile_visibility",
            "share_usage_data",
            "allow_search_indexing",
            "show_online_status",
            "allow_contact",
            "show_email",
        ]:
            if field in data:
                setattr(person, field, data[field])

    def _save_notification_data(self, data: Dict, person: Person):
        """Save notification data."""
        notification_fields = [
            "course_updates",
            "instructor_messages",
            "marketing_emails",
            "weekly_reports",
            "assignment_notifications",
            "forum_activity",
            "deadline_reminders",
            "sms_notifications",
        ]

        for field in notification_fields:
            attr_name = f"{field}_notifications"
            if field in data:
                setattr(person, attr_name, data[field])

    def _save_security_data(self, data: Dict, person: Person):
        """Save security data."""
        if "two_factor_enabled" in data:
            person.two_factor_enabled = data["two_factor_enabled"]

    def _save_preferences_data(self, data: Dict, person: Person):
        """Save preferences data."""
        for field in [
            "language",
            "timezone",
            "dark_mode",
            "high_contrast",
            "reduce_animations",
            "density",
        ]:
            if field in data:
                setattr(person, field, data[field])

    def _save_billing_data(self, data: Dict, person: Person):
        """Save billing data."""
        for field in ["plan", "payment_method", "auto_renew"]:
            if field in data:
                setattr(person, field, data[field])
