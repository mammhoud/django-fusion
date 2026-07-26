"""
Unified views for vResume pages app.
Consolidated from multiple files to simplify structure.
"""
import json
import logging

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic.base import RedirectView
from wagtail.models import Locale, Site

logger = logging.getLogger(__name__)

# ── Tab Navigation Views ──────────────────────────────────────────────────

def get_current_locale(request):
    """
    Get the current locale from the request.
    """
    current_language = translation.get_language()

    try:
        locale = Locale.objects.get(language_code=current_language)
    except Locale.DoesNotExist:
        try:
            locale = Locale.objects.get(language_code__startswith=current_language.split('-')[0])
        except Locale.DoesNotExist:
            locale = Locale.objects.first()

    return locale


@require_http_methods(["GET"])
def tab_view(request, tab_name):
    # Allowed vResume tabs
    valid_tabs = ["about", "resume", "portfolio", "blog", "contact", "home"]
    if tab_name not in valid_tabs:
        raise Http404("Tab not found")

    site = Site.find_for_request(request)
    if not site:
        return HttpResponse("Site not found", status=500)

    locale = get_current_locale(request)

    if tab_name == "about":
        from pages.about.models import AboutPage
        page = AboutPage.objects.live().filter(locale=locale).first() or AboutPage.objects.live().first()
    elif tab_name == "resume":
        from pages.cv.models import ResumePage
        page = ResumePage.objects.live().filter(locale=locale).first() or ResumePage.objects.live().first()
    elif tab_name == "portfolio":
        from pages.portfolio.models import PortfolioPage
        page = PortfolioPage.objects.live().filter(locale=locale).first() or PortfolioPage.objects.live().first()
    elif tab_name == "contact":
        from pages.connect.models import ContactPage
        page = ContactPage.objects.live().filter(locale=locale).first() or ContactPage.objects.live().first()
    elif tab_name == "blog":
        from pages.blog.models import BlogPage as BlogIndexPage
        page = BlogIndexPage.objects.live().filter(
            locale=locale, depth__lte=3
        ).first() or BlogIndexPage.objects.live().filter(depth__lte=3).first()
    elif tab_name == "home":
        from pages.home.models import HomePage
        page = HomePage.objects.live().filter(locale=locale).first() or HomePage.objects.live().first()
    else:
        page = site.root_page.specific

    if not page:
        page = site.root_page.specific

    context = page.get_context(request)
    context["active_tab"] = tab_name
    context["page"] = page

    context["tabs"] = [
        ("home", _("Home")),
        ("about", _("About")),
        ("resume", _("Resume")),
        ("portfolio", _("Portfolio")),
        ("blog", _("Blog")),
        ("contact", _("Contact")),
    ]

    if "vresume_settings" not in context:
        from pages.home.models import VResumeSettings
        try:
            context["vresume_settings"] = VResumeSettings.for_site(site)
        except Exception:
            logger.debug("Could not load VResumeSettings for tab_view")
            context["vresume_settings"] = None

    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        tab_templates = {
            "home":      "home/fragment.html",
            "about":     "about/fragment.html",
            "resume":    "resume/fragment.html",
            "portfolio": "portfolio/fragment.html",
            "blog":      "blog/fragment.html",
            "contact":   "connect/fragment.html",
        }
        template = tab_templates.get(tab_name, "home/fragment.html")
    else:
        template = "skeleton.html"

    return render(request, template, context)


class LocalePreservingRedirectView(RedirectView):
    """
    RedirectView that preserves the active i18n language prefix.
    When the active language differs from LANGUAGE_CODE, prepend /{lang}/.
    """
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        redirect_url = super().get_redirect_url(*args, **kwargs)
        from django.utils.translation import get_language
        current_lang = get_language()
        default_lang = settings.LANGUAGE_CODE
        if current_lang and current_lang != default_lang and redirect_url:
            redirect_url = f"/{current_lang}{redirect_url}"
        return redirect_url


@require_http_methods(["GET"])
def team_view(request):
    """
    Serve the team page — an AboutPage instance with slug='team'.
    Since 'team' isn't a valid tab in tab_view, we serve it manually
    through the about tab template showing the team page's content.
    """
    from pages.about.models import AboutPage

    locale = get_current_locale(request)
    page = AboutPage.objects.live().filter(slug='team', locale=locale).first()
    if not page:
        page = AboutPage.objects.live().filter(slug='team').first()
    if not page:
        raise Http404("Team page not found")

    site = Site.find_for_request(request)

    context = page.get_context(request)
    context["page"] = page
    context["active_tab"] = "about"
    context["tabs"] = [
        ("home", _("Home")),
        ("about", _("About")),
        ("resume", _("Resume")),
        ("portfolio", _("Portfolio")),
        ("blog", _("Blog")),
        ("contact", _("Contact")),
    ]

    if "vresume_settings" not in context:
        from pages.home.models import VResumeSettings
        try:
            context["vresume_settings"] = VResumeSettings.for_site(site)
        except Exception:
            logger.debug("Could not load VResumeSettings for team_view")
            context["vresume_settings"] = None

    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "about/fragment.html" if is_htmx else "skeleton.html"

    return render(request, template, context)


# ── Content Detail Views (HTMX Modals) ──────────────────────────────────

@require_http_methods(["GET"])
def blog_detail_view(request, blog_id):
    """
    Return blog post detail partial for HTMX modal.
    blog_id is always an integer from the URL pattern blog/<int:blog_id>/.
    """
    from pages.blog.models.snippets.post import BlogPost
    try:
        post = BlogPost.objects.select_related('featured_image').prefetch_related(
            'tags', 'author_relationships__author'
        ).get(pk=blog_id, is_published=True)
    except BlogPost.DoesNotExist:
        # Return friendly HTMX error for modals
        if request.headers.get('HX-Request') == 'true':
            return HttpResponse(
                '<div class="alert alert-warning"><strong>Post not found</strong>'
                '<p>The requested content is no longer available. It may have been removed or unpublished.</p></div>',
                status=404,
            )
        raise Http404("Blog post not found")

    return render(request, "blog/modals/blog_detail.html", {"post": post})


@require_http_methods(["GET"])
def project_detail_view(request, project_id):
    """
    Return project detail partial for HTMX modal.
    project_id can be a numeric ID or a string slug.
    """
    from pages.portfolio.models.snippets.project import Project
    try:
        # Try numeric pk lookup first
        if project_id.isdigit():
            project = Project.objects.select_related('image').prefetch_related(
                'tags'
            ).get(pk=int(project_id), is_active=True)
        else:
            # Try slug lookup
            project = Project.objects.select_related('image').prefetch_related(
                'tags'
            ).get(slug=project_id, is_active=True)
    except Project.DoesNotExist:
        # Return friendly HTMX error for modals
        if request.headers.get('HX-Request') == 'true':
            return HttpResponse(
                '<div class="alert alert-warning"><strong>Project not found</strong>'
                '<p>The requested content is no longer available. It may have been removed or deactivated.</p></div>',
                status=404,
            )
        raise Http404("Project not found")

    return render(request, "portfolio/modals/project_detail.html", {"project": project})


# ── Form Submission Views ─────────────────────────────────────────────

@require_http_methods(["POST"])
def contact_submit(request):
    """
    Handle contact form submission via HTMX.
    """
    from wagtail.models import Site

    from pages.home.models import VResumeSettings

    fullname = request.POST.get('fullname', '').strip()
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()

    errors = []
    if not fullname: errors.append("Full name is required")
    if not email: errors.append("Email is required")
    if not message: errors.append("Message is required")

    if errors:
        error_html = '<div class="alert alert-danger"><strong>❌ Validation Error</strong><ul class="mb-0">'
        for error in errors:
            error_html += f'<li>{error}</li>'
        error_html += '</ul></div>'
        return HttpResponse(error_html, status=400)

    try:
        site = Site.find_for_request(request)
        settings = VResumeSettings.for_site(site)

        if settings.email:
            from pages.connect.services.form_submission import FormSubmissionService
            submission = FormSubmissionService.save_submission(
                form_id="contact_form",
                data={"fullname": fullname, "email": email, "message": message},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            FormSubmissionService.send_notification_email(
                submission=submission,
                recipients=[settings.email],
                subject=f"New Contact Form Submission from {fullname}"
            )

        from pages.connect.services.email import email_service
        email_service.send_simple(
            to=email,
            subject=f"We received your message, {fullname}",
            body=f"Thank you for reaching out! We'll get back to you soon.\n\nBest regards,\n{settings.full_name}",
            from_email=settings.email or 'noreply@vresume.local'
        )

        return HttpResponse(
            '<div class="alert alert-success"><strong>✅ Success!</strong> Your message has been sent. We\'ll get back to you soon.</div>'
        )
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return HttpResponse(
            '<div class="alert alert-danger"><strong>❌ Error!</strong> An error occurred. Please try again.</div>',
            status=500
        )


@require_http_methods(["POST"])
def subscribe_view(request):
    """
    Handle newsletter subscription via HTMX.
    """
    from pages.connect.models import Subscriber
    email = request.POST.get('email', '').strip()

    if not email:
        return HttpResponse(
            '<div class="alert alert-danger"><strong>❌ Error!</strong> Email is required</div>',
            status=400
        )

    try:
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={'status': 'pending'}
        )

        if created or subscriber.status == 'pending':
            from pages.connect.services.newsletter_tasks import send_confirmation_email
            send_confirmation_email.delay(subscriber.id)

            return HttpResponse(
                '<div class="alert alert-success"><strong>✅ Success!</strong> Thank you for subscribing! Check your email for confirmation.</div>'
            )
        else:
            return HttpResponse(
                '<div class="alert alert-info"><strong>ℹ️ Info</strong> You are already subscribed to our newsletter.</div>'
            )
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        return HttpResponse(
            '<div class="alert alert-danger"><strong>❌ Error!</strong> An error occurred. Please try again.</div>',
            status=500
        )
