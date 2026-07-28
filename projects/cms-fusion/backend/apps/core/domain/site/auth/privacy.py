"""
Privacy Modal HTMX view.
Serves privacy policy content as an HTMX fragment for lazy-loading modals.
"""
from django.http import HttpResponse
from django.template.loader import render_to_string
from django_fusion.site.interface.page_handler import ComponentViews

from apps.core.domain.contrib.privacy import get_privacy_html


class PrivacyModalView(ComponentViews):
    """
    HTMX-powered privacy modal view.

    Base: ComponentViews (FragmentHandlerMixin + TemplateView)
    Serves the modal body content lazily via hx-get.

    Usage in templates:
        <a href="#" hx-get="{% url 'pipelines:privacy_modal' %}"
           hx-target="#privacyModalContainer"
           hx-swap="innerHTML">Privacy Policy</a>
        <div id="privacyModalContainer"></div>
    """

    page_title = "Privacy Policy"
    template_name = "account/privacy_modal_content.html"
    require_auth = False

    def get(self, request, *args, **kwargs):
        """Serve privacy modal content as HTMX fragment."""
        privacy_html = get_privacy_html()

        html = render_to_string(self.template_name, {
            "privacy_content": privacy_html,
        }, request=request)

        response = HttpResponse(html)

        # HTMX: trigger modal open after swap
        if getattr(request, "htmx", False):
            response["HX-Trigger-After-Swap"] = "privacyModalLoaded"

        return response