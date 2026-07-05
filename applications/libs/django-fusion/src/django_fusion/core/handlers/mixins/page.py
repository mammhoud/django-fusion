"""
Page handler mixins for django_fusion.

Pure Django mixins for page handlers without Wagtail dependencies.
"""

from typing import Any, Dict

from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic.base import ContextMixin


class ProfileContextMixin(ContextMixin):
    """
    Mixin to add profile context data to views.

    Pure Django version without Wagtail dependencies.
    """

    def get_profile_context(self, request) -> Dict[str, Any]:
        """
        Get comprehensive profile context.

        Args:
            request: HTTP request

        Returns:
            Context dictionary
        """
        context = {}

        if request.user.is_authenticated:
            try:
                user = request.user

                # Basic user information
                context.update({
                    "user": user,
                    "user_email": user.email,
                    "user_first_name": user.first_name,
                    "user_last_name": user.last_name,
                    "user_is_staff": user.is_staff,
                    "user_is_superuser": user.is_superuser,
                    "user_date_joined": user.date_joined,
                    "user_last_login": user.last_login,
                })

                # Get user groups
                user_groups = list(user.groups.values_list("name", flat=True))
                context["user_groups"] = user_groups

                # Get user permissions
                user_permissions = list(user.get_all_permissions())
                context["user_permissions"] = user_permissions

                # Profile completion (simplified)
                completion_items = []
                if user.first_name and user.last_name:
                    completion_items.append("name")
                if user.email:
                    completion_items.append("email")

                completion_percentage = len(completion_items) / 2 * 100 if completion_items else 0
                context.update({
                    "profile_completion_percentage": completion_percentage,
                    "profile_is_complete": completion_percentage >= 100,
                })

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting profile context: {e}")

        return context

    def get_context_data(self, **kwargs):
        """
        Get context data with profile information.
        """
        context = super().get_context_data(**kwargs)

        if hasattr(self, "request"):
            profile_context = self.get_profile_context(self.request)
            context.update(profile_context)

        return context


class ProfileDashboardMixin(ProfileContextMixin):
    """
    Mixin for dashboard views with profile operations.

    Extends ProfileContextMixin with dashboard metrics and quick actions.
    Pure Django version without Wagtail dependencies.
    """

    def get_dashboard_metrics(self, request) -> Dict[str, Any]:
        """
        Get dashboard metrics for the user.

        Args:
            request: HTTP request

        Returns:
            Dashboard metrics dictionary
        """
        metrics = {}

        if request.user.is_authenticated:
            try:
                user = request.user

                # Example metrics (simplified)
                metrics.update({
                    "total_logins": getattr(user, "login_count", 0),
                    "account_age_days": (timezone.now().date() - user.date_joined.date()).days
                    if hasattr(user, "date_joined") else 0,
                    "is_active": user.is_active,
                    "has_verified_email": True,  # Simplified
                })

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting dashboard metrics: {e}")

        return metrics

    def get_quick_actions(self, request) -> Dict[str, Any]:
        """
        Get quick actions for the dashboard.

        Args:
            request: HTTP request

        Returns:
            Quick actions dictionary
        """
        actions = {}

        if request.user.is_authenticated:
            # Example quick actions (simplified)
            actions.update({
                "update_profile": {
                    "label": "Update Profile",
                    "url": "/profile/update/",
                    "icon": "user",
                },
                "change_password": {
                    "label": "Change Password",
                    "url": "/profile/security/",
                    "icon": "lock",
                },
                "notification_settings": {
                    "label": "Notifications",
                    "url": "/profile/notifications/",
                    "icon": "bell",
                },
            })

        return actions

    def get_context_data(self, **kwargs):
        """
        Get context data with dashboard information.
        """
        context = super().get_context_data(**kwargs)

        if hasattr(self, "request"):
            dashboard_metrics = self.get_dashboard_metrics(self.request)
            quick_actions = self.get_quick_actions(self.request)

            context.update({
                "dashboard_metrics": dashboard_metrics,
                "quick_actions": quick_actions,
            })

        return context
