import logging

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.fields import StreamField
from wagtail.models import Site
from wagtail.snippets.blocks import SnippetChooserBlock

from core.pages_base import BasePage
from pages.home.models.snippets import Slider, TeamMember, Service, VResumeSettings

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """
    🏠 VResume HomePage
    Sections: Slider · Team · Services · Skills · Newsletter toggle
    """
    template = "base.html"
    template_name = "home"
    page_title = "Home Page"

    VCARD_TABS = [
        ("home", "Home"),
        ("about", "About"),
        ("resume", "Resume"),
        ("portfolio", "Portfolio"),
        ("blog", "Blog"),
        ("contact", "Contact"),
    ]

    slider = StreamField(
        [("slider_item", SnippetChooserBlock(Slider))],
        use_json_field=True, blank=True,
        verbose_name=_("Slider Section"),
    )
    services = StreamField(
        [("service", SnippetChooserBlock(Service))],
        use_json_field=True, blank=True,
        verbose_name=_("Services Section"),
    )
    subscribe_newsletter = models.BooleanField(
        default=True,
        verbose_name=_("Show Newsletter Subscribe Section"),
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel([FieldPanel("slider")], heading=_("Slider")),
        MultiFieldPanel([FieldPanel("services")], heading=_("Services")),
        FieldPanel("subscribe_newsletter"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Content")),
        ObjectList(BasePage.promote_panels, heading=_("Promote")),
        ObjectList(BasePage.settings_panels, heading=_("Settings")),
    ])

    def get_context(self, request, *args, **kwargs):
        from django.utils import translation
        from wagtail.models import Locale

        context = super().get_context(request, *args, **kwargs)

        try:
            site = Site.find_for_request(request)
            context["vresume_settings"] = VResumeSettings.for_site(site)
        except Exception:
            logger.debug("Could not load VResumeSettings in HomePage")
            context["vresume_settings"] = None

        context["tabs"] = self.VCARD_TABS
        context.setdefault("active_tab", request.GET.get("tab", "home"))

        # Add page content fields to context
        context["page"] = self
        context["slider"] = self.slider
        context["services"] = self.services
        context["subscribe_newsletter"] = self.subscribe_newsletter

        try:
            from pages.blog.models import BlogPage
            lang = translation.get_language()
            try:
                locale = Locale.objects.get(language_code=lang)
            except Locale.DoesNotExist:
                try:
                    locale = Locale.objects.get(language_code__startswith=lang.split("-")[0])
                except Locale.DoesNotExist:
                    locale = Locale.objects.first()
            qs = BlogPage.objects.live()
            if locale:
                qs = qs.filter(locale=locale)
            context["blog_posts"] = list(qs.order_by("-first_published_at")[:6])
        except Exception:
            logger.debug("Could not load blog posts for HomePage")
            context["blog_posts"] = []

        return context

    class Meta:
        verbose_name = _("Home Page")
        verbose_name_plural = _("Home Pages")
        app_label = "home"
