from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.learning.models import Course, Wishlist

from .common import _hx_or_json, learning_login_required


@learning_login_required
@require_POST
def toggle_wishlist(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    with transaction.atomic():
        item, created = Wishlist.objects.get_or_create(user=request.user, course=course)
        if not created:
            item.delete()
    return _hx_or_json(
        request,
        "learning/fragments/wishlist_button.html",
        {"course": course, "wishlisted": created},
        {"wishlisted": created, "course": course.slug},
        redirect_to=course.get_absolute_url(),
    )
