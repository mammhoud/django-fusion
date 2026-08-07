"""
Event Fragment Components for lms-fusion.com
===============================================

HTMX fragment components for Events, matching the ``BlogPostListFragment``
and ``BlogPostCreateFragment`` patterns in ``apps/pages/blog/components.py``.

Template convention: ``fragment_name`` uses dotted notation.
  "events.fragments.event_list"          → events/fragments/event_list.html
  "events.fragments.event_create_form"   → events/fragments/event_create_form.html
"""

from __future__ import annotations

from django import forms
from django.db.models import Q
from django.http import HttpResponse
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.components.dual_mode import FusionDualModeMixin

import logging

logger = logging.getLogger(__name__)


class EventListFragment(FusionDualModeMixin, FragmentComponent):
    """
    Event list as HTMX fragment with pagination, search, and filters.

    URL: /events/list-fragment/

    Dual-mode: ``fusion_render_first=True`` renders the HTML fragment;
    ``False`` returns codec-encoded JSON with Site navigation.
    """

    route_name = "event-list-fragment"
    route_path = "list-fragment/"
    fragment_name = "events.fragments.event_list"
    htmx_only = True
    paginate_by = 10

    # OOB: event-count badge refreshed on every list render
    oob_fragments = {
        "event-count": "events.fragments.event_count",
    }

    def has_permission(self, user):
        return True  # Public

    def get_queryset(self):
        from apps.pages.accounts.models import Event

        qs = Event.objects.filter(is_visible=True, is_active=True).select_related()

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        event_type = self.request.GET.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)

        return qs.order_by("-start_date", "title")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        from apps.pages.accounts.models import Event

        context["event_types"] = Event.EventType.choices
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_event_type"] = self.request.GET.get("event_type", "")
        context["show_success"] = self.request.session.pop("event_created", False)
        context["event_count"] = Event.objects.filter(is_visible=True, is_active=True).count()
        return context

    def get_fragment_data(self) -> dict:
        """Serialise the event list for data mode (fusion_render_first=False)."""
        from apps.pages.accounts.models import Event

        qs = self.get_queryset()
        page = max(1, int(self.request.GET.get("page", 1)))
        per_page = self.paginate_by or 10
        total = qs.count()
        events = qs[(page - 1) * per_page : page * per_page]

        return {
            "events": [
                {
                    "id": e.pk, "title": e.title,
                    "description": e.description or "",
                    "event_type": e.event_type,
                    "event_type_label": e.get_event_type_display(),
                    "start_date": e.start_date.isoformat() if e.start_date else None,
                    "end_date": e.end_date.isoformat() if e.end_date else None,
                    "location": e.location or "",
                    "is_active": e.is_active,
                }
                for e in events
            ],
            "event_types": [
                {"value": key, "label": label}
                for key, label in Event.EventType.choices
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
            "search_query": self.request.GET.get("q", ""),
            "selected_event_type": self.request.GET.get("event_type", ""),
            "event_count": Event.objects.filter(is_visible=True, is_active=True).count(),
        }


class EventCreateFragment(FragmentComponent):
    """
    Event creation form as HTMX fragment.

    URL: /events/create-fragment/
    """

    route_name = "event-create-fragment"
    route_path = "create-fragment/"
    fragment_name = "events.fragments.event_create_form"
    htmx_only = True

    oob_fragments: dict = {}

    def has_permission(self, user):
        return user.is_staff

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["form"] = _get_event_form_class()()
        return context

    def post(self, request, *args, **kwargs):
        form = _get_event_form_class()(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            return self._render_success_response(event)

        context = self.get_fragment_context()
        context["form"] = form
        return self.render_to_response(context)

    def _render_success_response(self, event):
        from django.template.loader import render_to_string

        success_html = render_to_string(
            "events/fragments/event_create_success.html",
            {"event": event},
            request=self.request,
        )
        response = HttpResponse(f'<div id="event-create-success">{success_html}</div>')
        response["HX-Reswap"] = "innerHTML"
        response["HX-Retarget"] = "#event-list"
        oob_html = f'<div id="event-create-success" hx-swap-oob="true">{success_html}</div>'
        response.content = response.content.decode() + oob_html
        return response


def _get_event_form_class():
    """Return EventForm lazily to avoid import-time model conflicts."""
    from apps.pages.accounts.models import Event

    class EventForm(forms.ModelForm):
        class Meta:
            model = Event
            fields = [
                "title", "description", "event_type",
                "start_date", "end_date", "location",
                "is_visible", "is_active", "tags",
            ]
            widgets = {
                "title": forms.TextInput(attrs={
                    "class": "form-control", "placeholder": "Event title",
                }),
                "description": forms.Textarea(attrs={
                    "class": "form-control", "rows": 3,
                    "placeholder": "Brief description...",
                }),
                "event_type": forms.Select(attrs={"class": "form-control"}),
                "start_date": forms.DateTimeInput(attrs={
                    "class": "form-control", "type": "datetime-local",
                }),
                "end_date": forms.DateTimeInput(attrs={
                    "class": "form-control", "type": "datetime-local",
                }),
                "location": forms.TextInput(attrs={
                    "class": "form-control", "placeholder": "Venue or online link",
                }),
                "is_visible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
                "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
                "tags": forms.SelectMultiple(attrs={"class": "form-control"}),
            }

        def clean_title(self):
            title = self.cleaned_data.get("title", "").strip()
            if not title:
                from django.core.exceptions import ValidationError
                raise ValidationError("Title is required.")
            return title

    return EventForm


__all__ = ["EventListFragment", "EventCreateFragment"]