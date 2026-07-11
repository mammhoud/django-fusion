"""Customizer viewset registration using canonical django_fusion.site imports.

Import customizer site integrations from ``django_fusion.site`` rather than the
legacy ``django_fusion.comp.site`` shim.  This module intentionally keeps the
registry small and explicit so URL modules can opt in to the class-based views
that expose the customizer SPA fragments.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.urls import path
from django.views import View
from django_fusion.site import HtmxDetails

from chat.views import (
    MessageSendResultFragmentView,
    PageCardGridFragmentView,
    PageNavigatorFragmentView,
    PageSectionListFragmentView,
    PagesEndpointView,
    WebsiteListView,
)


@dataclass(frozen=True)
class CustomizerViewSet:
    """Small URL-registration adapter for customizer class-based views."""

    route: str
    view: type[View]
    name: str

    def as_urlpattern(self):
        return path(self.route, self.view.as_view(), name=self.name)


class CustomizerSite:
    """Registry for customizer viewsets and fragment endpoints."""

    viewsets: tuple[CustomizerViewSet, ...] = (
        CustomizerViewSet("websites/", WebsiteListView, "customizer_websites"),
        CustomizerViewSet(
            "websites/<slug:website_slug>/pages/",
            PagesEndpointView,
            "customizer_pages",
        ),
        CustomizerViewSet(
            "fragments/page-navigator/",
            PageNavigatorFragmentView,
            "fragment_page_navigator",
        ),
        CustomizerViewSet(
            "fragments/page-card-grid/<slug:website_slug>/",
            PageCardGridFragmentView,
            "fragment_page_card_grid",
        ),
        CustomizerViewSet(
            "fragments/page-section-list/<slug:website_slug>/<path:page_path>/",
            PageSectionListFragmentView,
            "fragment_page_section_list",
        ),
        CustomizerViewSet(
            "fragments/message-send-result/",
            MessageSendResultFragmentView,
            "fragment_message_send_result",
        ),
    )

    def get_urlpatterns(self) -> list:
        return [viewset.as_urlpattern() for viewset in self.viewsets]

    def htmx_details(self, request) -> HtmxDetails:
        return HtmxDetails(request)


customizer_site = CustomizerSite()
urlpatterns = customizer_site.get_urlpatterns()
