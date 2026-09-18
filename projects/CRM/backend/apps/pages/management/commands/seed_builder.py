"""Seed the Loop-CRM landing-builder demo pages.

Creates a couple of ``BuilderPage`` children under the seeded home page that
exercise the landing builder: theme picking, dark mode, dynamic template
fields (``{{ company.name }}`` backed by ``template_context``), and the full
section stack. Idempotent — re-running only ensures the pages exist.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from wagtail.models import Page

from apps.pages.models import BuilderPage, HomePage


def _btn(label: str, href: str, style: str = "primary") -> dict:
    return {"label": label, "href": href, "page": None, "style": style}


# ── Demo: SaaS-themed launch page with dynamic fields ───────────────────────

SAAS_CONTEXT = {
    "company": {"name": "Structa Cloud", "tagline": "One platform, one source of truth"},
    "product": {"name": "Loop CRM", "price": "$29"},
}

SAAS_SECTIONS = [
    (
        "hero",
        {
            "badge": "Built with the landing builder",
            "title": "Welcome to {{ company.name }}",
            "accent": "{{ product.name }}",
            "subtitle": "{{ company.tagline }} — assembled from the fu-* component catalog with theme picking and dynamic template fields.",
            "primary_cta": _btn("Start free", "/accounts/signup/"),
            "secondary_cta": _btn("Sign in", "/accounts/login/", "outline"),
            "note": "Theme: Modern SaaS · data-theme=saas",
        },
    ),
    (
        "features",
        {
            "eyebrow": "One platform",
            "title": "Three modules, one source of truth",
            "description": "Sales, marketing, and RevOps stop syncing spreadsheets.",
            "features": [
                {"icon": "crm", "label": "CRM", "title": "The relationship graph", "description": "Companies, contacts, pipelines, and custom fields.", "href": "/crm/", "page": None},
                {"icon": "marketing", "label": "Publishing", "title": "One calendar", "description": "Plan, approve, and publish from one content calendar.", "href": "/marketing/", "page": None},
                {"icon": "attribution", "label": "Finance", "title": "Trace to revenue", "description": "Every touchpoint credits the deals it influenced.", "href": "/finance/", "page": None},
            ],
        },
    ),
    (
        "stats",
        {
            "eyebrow": "By the numbers",
            "title": "{{ product.name }} in numbers",
            "stats": [
                {"value": "12", "suffix": "", "label": "Social channels cataloged"},
                {"value": "6", "suffix": "", "label": "Real publishers connected"},
                {"value": "{{ company.name|truncate:6 }}", "suffix": "", "label": "Brand, truncated"},
                {"value": "100", "suffix": "%", "label": "Workspace-scoped tenancy"},
            ],
        },
    ),
    (
        "pricing",
        {
            "eyebrow": "Pricing",
            "title": "Start free, scale when the loop is proven",
            "description": "Every tier includes attribution and the finance ledger.",
            "tiers": [
                {"name": "Free", "description": "For small teams.", "price": "$0", "period": "forever", "features": ["1 workspace", "3 members"], "cta_label": "Start free", "cta_href": "/accounts/signup/", "cta_page": None, "featured": False},
                {"name": "Pro", "description": "For revenue teams.", "price": "{{ product.price }}", "period": "per user / month", "features": ["Unlimited pipelines", "All attribution models"], "cta_label": "Start free", "cta_href": "/accounts/signup/", "cta_page": None, "featured": True},
                {"name": "Enterprise", "description": "For compliance needs.", "price": "Custom", "period": "annual", "features": ["SSO and audit log", "Dedicated support"], "cta_label": "Talk to us", "cta_href": "/accounts/signup/", "cta_page": None, "featured": False},
            ],
        },
    ),
    (
        "faq",
        {
            "eyebrow": "FAQ",
            "title": "Questions, answered",
            "description": "",
            "items": [
                {"question": "What powers {{ company.name }}?", "answer": "The landing builder: Wagtail page assembly, the fu-* theme engine, and dynamic template fields."},
                {"question": "Can I change the theme?", "answer": "Yes — every builder page has a theme, brand, and dark-mode setting rendered as data-theme on <html>."},
            ],
        },
    ),
    (
        "cta",
        {
            "title": "Start closing the loop",
            "subtitle": "Connect a channel, publish one post, and watch it trace to a deal.",
            "primary_cta": _btn("Start free", "/accounts/signup/"),
            "secondary_cta": _btn("Sign in", "/accounts/login/", "outline"),
        },
    ),
]

# ── Demo: dark contrast landing page ────────────────────────────────────────

DARK_CONTEXT = {
    "company": {"name": "Structa Cloud"},
}

DARK_SECTIONS = [
    (
        "hero",
        {
            "badge": "High-contrast demo",
            "title": "Dark mode, high contrast",
            "accent": "WCAG AAA",
            "subtitle": "data-theme=dark + class=dark — the same sections, a different design system.",
            "primary_cta": _btn("Explore", "/apis/builder/saas-launch/"),
            "secondary_cta": _btn("Back to light", "/apis/builder/dark-contrast/", "outline"),
            "note": "",
        },
    ),
    (
        "steps",
        {
            "eyebrow": "The loop",
            "title": "Four steps, fully auditable",
            "steps": [
                {"number": "01", "title": "Connect channels", "copy": "Link your social accounts once."},
                {"number": "02", "title": "Run the calendar", "copy": "Drafts move through approval to scheduled publishing."},
                {"number": "03", "title": "Close with context", "copy": "Sales sees which content influenced each opportunity."},
                {"number": "04", "title": "Recognize revenue", "copy": "A won deal creates the invoice, payment, and revenue event."},
            ],
        },
    ),
    (
        "cta",
        {
            "title": "Built by {{ company.name }}",
            "subtitle": "One assembly layer for every landing shell.",
            "primary_cta": _btn("Read the docs", "/apis/builder/saas-launch/"),
            "secondary_cta": _btn("View source", "/apis/builder/dark-contrast/", "outline"),
        },
    ),
]


class Command(BaseCommand):
    help = "Seed the landing-builder demo pages (theme + dynamic template fields)."

    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if home is None:
            self.stderr.write("No HomePage found — run seed_pages first.")
            return
        self._seed(
            home,
            slug="saas-launch",
            title="SaaS Launch",
            theme="saas",
            brand="loop",
            dark_mode=False,
            context=SAAS_CONTEXT,
            sections=SAAS_SECTIONS,
        )
        self._seed(
            home,
            slug="dark-contrast",
            title="Dark Contrast",
            theme="dark",
            brand="",
            dark_mode=True,
            context=DARK_CONTEXT,
            sections=DARK_SECTIONS,
        )
        self.stdout.write(self.style.SUCCESS(
            "Seeded landing-builder pages: /apis/builder/saas-launch/ and /apis/builder/dark-contrast/ "
            "(edit at /cms/)."
        ))

    def _seed(self, home, *, slug, title, theme, brand, dark_mode, context, sections):
        existing = home.get_children().filter(slug=slug).first()
        if existing is not None:
            page = existing.specific
            self.stdout.write(self.style.SUCCESS(f"  builder page /{slug}/ already exists"))
            return
        page = BuilderPage(title=title, slug=slug, theme=theme, brand=brand, dark_mode=dark_mode)
        page.template_context = context
        page.sections = sections
        home.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  created BuilderPage /{slug}/ (theme={theme})"))
