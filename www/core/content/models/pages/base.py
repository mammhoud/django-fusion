import logging

from colorfield.fields import ColorField
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django_osoul.site._context_mixins import WagtailPageMixin
from django_rseal.comp import ContactMethodBlock, FAQSectionBlock
from django_rseal.handlers.models.manage_company import Organization
from plugins.accounts.models.manage.service import Service
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from wagtail.models import Page
from wagtail.search import index

from www.core.content.models.contact import ContactSubmission

from ..blocks.form import MinimalContactFormBlock

logger = logging.getLogger(__name__)


class BasePage(WagtailPageMixin, Page):
    """
    🧩 Base Wagtail Page — powered by django-osoul's WagtailPageMixin.

    Rendering pipeline (same order as ComponentViews/PageHandler):
      1. resolve_strategy(request)   → "fragment" | "document"
      2. resolve_template_name()     → template path
      3. get_context(request)        → context dict
      4. render_response(request, context)
           fragment  → content template only (no layout)
           document  → outer layout (base_page.html) + {% include template_name %}

    Subclasses set:
      template      = "base_page.html"   # outer layout (Wagtail attr)
      template_name = "my/content.html"  # inner content
      fragment_name = "my.content"       # dotted → "my/content.html" for HTMX
    """

    # osoul pipeline attributes
    layout_path = "landing/skeleton.html"
    fragment_name = None
    template_name = None

    # === Footer Control ===
    show_page_at_footer = models.BooleanField(
        default=False,
        verbose_name=_("Show Page at Footer"),
        help_text=_("If enabled, this page will appear as a link in the footer menu."),
    )

    # === Panels ===
    content_panels = Page.content_panels

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [FieldPanel("show_page_at_footer")],
            heading=_("Page Options"),
            classname="collapsible",
        ),
    ]

    class Meta:
        abstract = True

    # === Context ===
    def get_context(self, request, *args, **kwargs):
        """
        Build context via WagtailPageMixin (injects strategy/template keys)
        then add site-wide data: partners, footer pages, services summary.
        """
        # WagtailPageMixin.get_context() calls super() which is Page.get_context()
        # and then injects strategy, template_name, fragment_name, etc.
        context = super().get_context(request, *args, **kwargs)

        context["page_title"] = getattr(self, "page_title", self.title)

        # Partners
        try:
            context["partners"] = Organization.get_partners()
        except Exception as e:
            logger.warning("[ContextWarning] partners: %s", e)
            context["partners"] = []

        # Page options
        context["options"] = {"show_page_at_footer": self.show_page_at_footer}

        # Footer pages
        try:
            from wagtail.models import Locale
            locale = Locale.get_active()
            footer_pages = [
                p for p in Page.objects.live().filter(locale=locale).specific()
                if isinstance(p, BasePage) and p.show_page_at_footer
            ]
            context["footer_pages"] = footer_pages
        except Exception as e:
            logger.warning("[FooterPagesError] %s", e)
            context["footer_pages"] = []

        # Listed data
        listed = self.get_listed_data(request)
        if isinstance(listed, dict):
            context.update(listed)

        return context

    def get_listed_data(self, request=None):
        """Structured data for templates. Override in subclasses."""
        try:
            return {
                "services_summary": list(
                    Service.objects.filter(is_active=True).values("id", "name", "category")
                ),
                "metadata": {
                    "page_type": self.__class__.__name__,
                    "page_id": self.id,
                    "timestamp": timezone.now().isoformat(),
                },
            }
        except Exception as e:
            logger.warning("[ListedData] %s: %s", self.__class__.__name__, e)
            return {}


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
        [("contact_form", MinimalContactFormBlock(template="blocks/minimal_contact_form.html"))],
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
            form_data = request.POST.dict()
            form_id = form_data.pop("form_id", "contact-form")
            form_data.pop("csrfmiddlewaretoken", None)

            # Save submission
            submission = ContactSubmission(
                form_id=form_id,
                page_id=self.id,
                page_title=self.title,
                page_url=request.build_absolute_uri(),
                submitted_data=form_data,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                referrer=request.META.get("HTTP_REFERER", ""),
            )
            submission.save()

            # Send automated email
            try:
                self.send_submission_email(submission)
            except Exception as e:
                logger.error(f"[EmailError] Failed to send submission email: {e}")

            # Handle HTMX response
            if getattr(request, "htmx", False):
                from django.template.response import TemplateResponse
                context = self.get_context(request)
                context.update({
                    "form_submitted": True,
                    "form_success": True,
                    "value": {"form_id": form_id}
                })
                return TemplateResponse(
                    request,
                    "partials/form_notification.html",
                    context
                )

            return super().serve(request, *args, **kwargs)
        return super().serve(request, *args, **kwargs)

    def send_submission_email(self, submission):
        """
        Send an automated email notification for a new submission.
        Also sends confirmation email to submitter if email is provided.
        """
        site_name = getattr(settings, 'SITE_NAME', 'Alliance')
        subject = f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '[Alliance] ')} New Submission: {submission.page_title}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@structa.cloud')
        recipient_list = [getattr(settings, 'CONTACT_FORM_RECIPIENT', from_email)]

        context = {
            "page_title": submission.page_title,
            "form_id": submission.form_id,
            "form_data": submission.submitted_data,
            "submission_date": submission.submission_date,
            "ip_address": submission.ip_address,
            "page_url": submission.page_url,
            "current_year": timezone.now().year,
            "site_name": site_name,
        }

        try:
            html_content = render_to_string("emails/contact_submission.html", context)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            logger.info(f"[Email] Admin notification sent for submission on '{submission.page_title}'")
        except Exception as e:
            logger.error(f"[Email] Failed to send admin notification: {e}", exc_info=True)

        # Send confirmation email to submitter if email field exists
        submitter_email = submission.submitted_data.get("email") or submission.submitted_data.get("Email")
        if submitter_email:
            try:
                confirm_context = {
                    "page_title": submission.page_title,
                    "submission_date": submission.submission_date,
                    "submitter_name": submission.submitted_data.get("name", submission.submitted_data.get("Name", "")),
                    "site_name": site_name,
                    "current_year": timezone.now().year,
                }
                confirm_html = render_to_string("emails/contact_confirmation.html", confirm_context)
                confirm_text = strip_tags(confirm_html)
                confirm_subject = f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '[Alliance] ')} We received your message"

                confirm_msg = EmailMultiAlternatives(confirm_subject, confirm_text, from_email, [submitter_email])
                confirm_msg.attach_alternative(confirm_html, "text/html")
                confirm_msg.send()
                logger.info(f"[Email] Confirmation sent to {submitter_email}")
            except Exception as e:
                logger.error(f"[Email] Failed to send confirmation to {submitter_email}: {e}", exc_info=True)

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
                            SimpleImageBlock(template="django_grep/comp/blocks/media/simple_image.html")
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
                            SimpleImageBlock(template="django_grep/comp/blocks/media/simple_image.html")
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
        default=9,
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
