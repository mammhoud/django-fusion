"""
Site views module.

Exports authentication views and non-auth views.

Canonical imports::
    from ceptor_ai.content.site.auth import LoginView
    from ceptor_ai.content.site.views import NotificationView
    from django_osoul.health.views import health_check
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy

# Auth views
from ceptor_ai.content.site.auth import *  # noqa: F401, F403

# Non-auth views
from ceptor_ai.content.site.views import (  # noqa: F401
    NotificationView,
    PaymentsView,
    SearchView,
    TagsView,
)


def profile_page(request):
    return redirect(reverse_lazy("handlers:profile"))
