from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from django.db import models
from django.http import HttpResponseServerError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.search import index

from pages import logger
from colorfield.fields import ColorField
from pages.connect.blocks import ContactFormBlock
from wagtail.admin.panels import TabbedInterface, ObjectList


class BasePage(Page):
    """
    🧩 Base Wagtail Page class
    Provides:
      - Fragment and full render support
      - Global "options" and footer visibility
      - Shared context with footer pages
      - JSON-style data (via get_listed_data)
    """

    fragment_template = "base_fragment.html"
    template_name = None  # This will now be used for the fragment part

    # === Panels ===
    content_panels = Page.content_panels

    settings_panels = Page.settings_panels

    class Meta:
        abstract = True

    # === Serve ===
    def serve(self, request, *args, **kwargs):
        """Handle both fragment and full-page requests.

        Also respects ``DisplayModeMixin.display_mode``:
          - ``"modal"`` → forces fragment rendering with modal headers
          - ``"detail"`` → normal fragment / document detection
        """
        # ── DisplayModeMixin integration ─────────────────────────────────────
        is_modal_requested = (
            hasattr(self, "display_mode") and self.display_mode == "modal"
        )
        modal_size = getattr(self, "modal_size", "lg") if is_modal_requested else None

        is_fragment_request = (
            is_modal_requested
            or getattr(request, "htmx", False)
            or getattr(request, "is_unpoly", False)
        )

        try:
            if is_fragment_request:
                context = self.get_context(request)
                if self.template_name:
                    logger.info(
                        f"[FragmentHandler] Using template_name: {self.template_name}"
                    )
                    # Mapping 'resume' -> 'resume/fragment.html'
                    # Special case: 'contact' maps to 'connect/fragment.html'
                    folder = self.template_name
                    if folder == "contact":
                        folder = "connect"
                    fragment_path = f"{folder}/fragment.html"
                    from django.shortcuts import render
                    response = render(request, fragment_path, context)
                    # Modal headers for Unpoly / HTMX
                    if is_modal_requested:
                        if getattr(request, "is_unpoly", False):
                            response["X-Up-Target-Layer"] = f"new-modal .modal-{modal_size}"
                        else:
                            response["HX-Trigger"] = '{"openModal": true}'
                    return response
            
            # Default Wagtail serve (uses self.template)
            return super().serve(request, *args, **kwargs)

        except Exception as e:
            logger.error(f"[ServeError] {self.title}: {str(e)}", exc_info=True)
            from django.shortcuts import render
            return render(
                request,
                "errors/500.html",
                {"error_message": str(e), "page_title": _("Server Error")},
                status=500,
            )

    # === Context ===
    def get_context(self, request, *args, **kwargs):
        """
        Extend context for all inheriting pages.
        Includes:
          - Common service data
          - Global options
          - Pages marked 'show_page_at_footer'
          - JSON-like structured data
        """
        context = super().get_context(request, *args, **kwargs)

        is_modal_requested = (
            hasattr(self, "display_mode") and self.display_mode == "modal"
        )

        context.update(
            {
                "template_name": getattr(self, "template_name", None),
                "is_fragment_request": getattr(request, "htmx", False)
                or getattr(request, "is_unpoly", False),
                "is_modal": is_modal_requested,
                "modal_size": getattr(self, "modal_size", "lg") if is_modal_requested else None,
            }
        )

        # === vResume Global Settings & Tabs ===
        from pages.home.models import VResumeSettings
        from wagtail.models import Site
        try:
            site = Site.find_for_request(request)
            context["vresume_settings"] = VResumeSettings.for_site(site)
        except Exception:
            logger.debug("Could not load VResumeSettings for request")
            context["vresume_settings"] = None

        context["tabs"] = getattr(self, "VCARD_TABS", [
            ("home", "Home"),
            ("about", "About"),
            ("resume", "Resume"),
            ("portfolio", "Portfolio"),
            ("blog", "Blog"),
            ("contact", "Contact"),
        ])

        # ✅ Add listed data if any
        listed_data = self.get_listed_data(request)
        if isinstance(listed_data, dict):
            context.update(listed_data)

        return context

    # === JSON-like data provider ===
    def get_listed_data(self, request=None):
        """
        Returns structured JSON-like data for templates or APIs.
        """
        data = {
            "metadata": {
                "page_type": self.__class__.__name__,
                "page_id": self.id,
                "timestamp": timezone.now().isoformat(),
            },
        }
        
        # Try to include services if available
        try:
            from pages.home.models import Service
            services_qs = Service.objects.filter(is_active=True).values(
                "id", "name", "category"
            )
            data["services_summary"] = list(services_qs)
        except Exception as e:
            logger.debug("Could not load services summary: %s", e)
            data["services_summary"] = []
        
        return data


# ------------------------------------------------------------------------
# 📝 Base Form Page
# ------------------------------------------------------------------------
class BaseFormPage(BasePage):
    """
    📝 Abstract base for pages with forms (Contact, Quote, Inquiry)
    Provides:
      - Form styling and configuration
      - Submission handling and validation
      - Spam protection and notifications
    """

    # -------------------------------------------------------------------------
    # FORM STYLING SETTINGS
    # -------------------------------------------------------------------------
    form_background_color = ColorField(
        default="#ffffff",
        verbose_name=_("Form Background Color"),
        help_text=_("Background color for the contact form container"),
    )
    form_text_color = ColorField(
        default="#000000",
        verbose_name=_("Form Text Color"),
        help_text=_("Text color for the form labels and inputs"),
    )
    form_button_color = ColorField(
        default="#0d6efd",
        verbose_name=_("Button Background Color"),
        help_text=_("Background color for the submit button"),
    )
    form_button_text_color = ColorField(
        default="#ffffff",
        verbose_name=_("Button Text Color"),
        help_text=_("Text color for the submit button"),
    )

    # -------------------------------------------------------------------------
    contact_form = StreamField(
        [("contact_form", ContactFormBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Form Block"),
    )

    # -------------------------------------------------------------------------
    # FORM CONFIGURATION
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # FORM CONFIGURATION
    # -------------------------------------------------------------------------
    form_title = RichTextField(
        blank=True,
        verbose_name=_("Form Title"),
        help_text=_("Optional heading above the form"),
    )
    form_intro = RichTextField(
        blank=True,
        verbose_name=_("Form Introduction"),
        help_text=_("Optional introductory text displayed above the form"),
    )
    button_text = models.CharField(
        max_length=50,
        default="Send Message",
        verbose_name=_("Submit Button Text"),
    )
    success_message = RichTextField(
        blank=True,
        default=(
            "<p>✨ <strong>Your message has wings!</strong></p>"
            "<p>Thank you for reaching out. Like a carefully sealed envelope,<br/>"
            "your words are now in our hands. We'll respond within 24 hours,<br/>"
            "bringing thoughtful answers to your thoughtful questions.</p>"
        ),
        verbose_name=_("Success Message"),
        help_text=_("Message shown after successful form submission"),
    )
    error_message = RichTextField(
        blank=True,
        default=(
            "<p>🔄 <strong>A temporary detour...</strong></p>"
            "<p>Sometimes even the best-laid plans need a second try.<br/>"
            "Your message couldn't be sent, but don't let this pause stop you.<br/>"
            "Please try again, or reach us directly through the contact details below.</p>"
        ),
        verbose_name=_("Error Message"),
        help_text=_("Message shown when form submission fails"),
    )

    # -------------------------------------------------------------------------
    # PANELS
    # -------------------------------------------------------------------------
    form_settings_panels = [
        MultiFieldPanel(
            [
                FieldPanel("form_title"),
                FieldPanel("form_intro"),
                FieldPanel("button_text"),
                FieldPanel("success_message"),
                FieldPanel("error_message"),
            ],
            heading=_("Content & Messages"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("form_background_color"),
                FieldPanel("form_text_color"),
                FieldPanel("form_button_color"),
                FieldPanel("form_button_text_color"),
            ],
            heading=_("Styling"),
        ),
    ]

    class Meta:
        abstract = True

    # -------------------------------------------------------------------------
    # SUBMISSION LOGIC
    # -------------------------------------------------------------------------
    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            from pages.connect.models import FormSubmission
            submission = FormSubmission(
                page=self,
                form_id="contact",
                data=request.POST.dict(),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            submission.save()
            return super().serve(request, *args, **kwargs)
        return super().serve(request, *args, **kwargs)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


# ------------------------------------------------------------------------
# 🔹 Unified Base Index Page
# ------------------------------------------------------------------------
class BaseIndexPage(BasePage):
    """
    🔹 Abstract base for index-type pages (Courses, Services, Partners, Blogs)
    Provides:
      - Header / CTA sections
      - Pagination
      - Inherits BasePage context (including footer pages)
    """

    fragment_name = "generic.index"

    # === Header Section ===
    header_section = StreamField(
        [
            (
                "hero",
                blocks.StructBlock(
                    [
                        (
                            "background_image",
                            SimpleImageBlock(template="blocks/media/image_lite.html")
                        ),
                        (
                            "subtitle",
                            blocks.CharBlock(
                                required=False, max_length=255, label=_("Subtitle")
                            ),
                        ),
                        (
                            "title",
                            blocks.CharBlock(
                                required=True, max_length=255, label=_("Title")
                            ),
                        ),
                        (
                            "intro_text",
                            blocks.RichTextBlock(required=False, label=_("Intro Text")),
                        ),
                    ],
                    icon="id-card",
                    label=_("Header Section"),
                ),
            )
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Header Section"),
    )

    cta_section = StreamField(
        [
            (
                "cta",
                blocks.StructBlock(
                    [
                        (
                            "background_image",
                            SimpleImageBlock(template="blocks/media/image_lite.html")
                        ),
                        (
                            "title",
                            blocks.CharBlock(
                                required=False, max_length=200, label=_("CTA Title")
                            ),
                        ),
                        (
                            "subtitle",
                            blocks.CharBlock(
                                required=False, max_length=255, label=_("CTA Subtitle")
                            ),
                        ),
                        (
                            "button_text",
                            blocks.CharBlock(
                                required=False, max_length=50, label=_("Button Text")
                            ),
                        ),
                        (
                            "button_link",
                            blocks.PageChooserBlock(
                                required=False, label=_("Button Link")
                            ),
                        ),
                    ],
                    icon="bullhorn",
                    label=_("Call To Action"),
                ),
            )
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Call To Action"),
    )

    intro_text = RichTextField(
        _("Intro Text"),
        blank=True,
        help_text=_("Short summary or introduction for this page."),
    )

    items_per_page = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Items per Page"),
        help_text=_("Pagination setting for listed items."),
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("header_section"), FieldPanel("intro_text")],
            heading=_("Header"),
        ),
        FieldPanel("cta_section"),
        FieldPanel("items_per_page"),
    ]

    search_fields = BasePage.search_fields + [index.SearchField("intro_text")]

    class Meta:
        abstract = True
        verbose_name = _("Base Index Page")
        verbose_name_plural = _("Base Index Pages")

    def get_listed_items(self):
        """Override in subclasses to return queryset or iterable."""
        return []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        try:
            items = self.get_listed_items()
            paginator = Paginator(items, self.items_per_page or 9)
            page = request.GET.get("page")

            try:
                paged_items = paginator.page(page)
            except PageNotAnInteger:
                paged_items = paginator.page(1)
            except EmptyPage:
                paged_items = paginator.page(paginator.num_pages)

            context.update(
                {
                    "page_items": paged_items,
                    "total_items": paginator.count,
                    "has_pagination": paginator.num_pages > 1,
                }
            )
        except Exception as e:
            logger.error(
                f"[PaginationError] {self.__class__.__name__}: {e}", exc_info=True
            )
            context.update(
                {"page_items": [], "total_items": 0, "has_pagination": False}
            )

        return context
