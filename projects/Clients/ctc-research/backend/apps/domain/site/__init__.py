"""
Site views module.

Exports authentication views and non-auth views.

Canonical imports::
    from apps.domain.site.auth import LoginView
    from django_fusion.routes.http.notifications import NotificationView
    from django_fusion.health.views import health_check
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy

# Auth views
from apps.domain.site.auth import *  # noqa: F401, F403

# Non-auth views
from apps.domain.site.views import (  # noqa: F401
    PaymentsView,
    SearchView,
)
from django_fusion.routes.views.notifications import NotificationView
from django_fusion.routes.views.tags import EnhancedTagsView as TagsView


def profile_page(request):
    return redirect(reverse_lazy("handlers:profile"))
