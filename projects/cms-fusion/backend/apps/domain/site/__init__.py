"""
Site views module.

Exports authentication views and non-auth views.

Canonical imports::
    from apps.domain.site.auth import LoginView
    from apps.domain.site.views import NotificationView
    from django_fusion.health.views import health_check
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy

# Auth views
from apps.domain.site.auth import *  # noqa: F401, F403

# Non-auth views
from apps.domain.site.views import (  # noqa: F401
    NotificationView,
    PaymentsView,
    SearchView,
    TagsView,
)


def profile_page(request):
    return redirect(reverse_lazy("handlers:profile"))
