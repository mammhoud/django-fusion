"""Seed the Wagtail landing pages for the Loop-CRM public site.

Creates the Wagtail Site + root ``HomePage`` and its children (Pricing, FAQ,
Privacy, Terms) with the current landing copy as initial content. Idempotent:
re-running only ensures pages exist and are published; editor changes are
never overwritten unless ``--refresh`` restores the seeded copy.
"""
from __future__ import annotations

import os

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.pages.models import FaqPage, HomePage, PricingPage, PrivacyPage, TermsPage


def _btn(label: str, href: str, style: str = "primary") -> dict:
    return {"label": label, "href": href, "page": None, "style": style}


# ── Home page content (initial copy from the hard-coded landing) ────────────

HOME_HERO = {
    "badge": "Loop CRM · unified revenue platform",
    "title": "From social impression to closed deal, in one loop.",
    "accent": "",
    "subtitle": (
        "CRM, social publishing, attribution, and finance in one workspace. "
        "Every touchpoint is traced to the revenue it creates."
    ),
    "primary_cta": _btn("Start free", "/accounts/signup/"),
    "secondary_cta": _btn("Sign in to your workspace", "/accounts/login/", "outline"),
    "note": "Built from the Twenty and Postiz DNA · Django + Dramatiq runtime",
}

HOME_DNA = {
    "items": [
        {"label": "CRM DNA", "value": "Twenty"},
        {"label": "Publishing DNA", "value": "Postiz"},
        {"label": "Runtime", "value": "Django + Dramatiq"},
    ]
}

HOME_FEATURES = {
    "eyebrow": "One platform",
    "title": "Three modules, one source of truth",
    "description": (
        "Sales, marketing, and RevOps stop syncing spreadsheets. Every record "
        "lives in the same workspace, so attribution survives the handoff."
    ),
    "features": [
        {
            "icon": "crm",
            "label": "CRM",
            "title": "The relationship graph, not a spreadsheet",
            "description": (
                "Companies, contacts, configurable pipelines, activities, and "
                "custom fields. Ownership and roles stay clear from first touch "
                "to close."
            ),
            "href": "/crm/",
            "page": None,
        },
        {
            "icon": "marketing",
            "label": "Social publishing",
            "title": "Plan, approve, and publish from one calendar",
            "description": (
                "A channel-aware content calendar with media, approvals, and "
                "scheduled publishing. Providers are replaceable behind one "
                "connector surface."
            ),
            "href": "/marketing/",
            "page": None,
        },
        {
            "icon": "attribution",
            "label": "Attribution + finance",
            "title": "Every touchpoint traces to revenue",
            "description": (
                "First, last, linear, time-decay, and position-based models. "
                "Won deals create invoices, payments, and recognized revenue "
                "automatically."
            ),
            "href": "/finance/",
            "page": None,
        },
    ],
}

HOME_STEPS = {
    "eyebrow": "The loop",
    "title": "Four steps, fully auditable",
    "steps": [
        {
            "number": "01",
            "title": "Connect channels",
            "copy": "Link your social accounts once. Loop CRM records every interaction as a touchpoint.",
        },
        {
            "number": "02",
            "title": "Run the content calendar",
            "copy": "Drafts move through approval to scheduled publishing, with honest status at every step.",
        },
        {
            "number": "03",
            "title": "Close deals with context",
            "copy": "Sales sees which content influenced each opportunity, in the deal record itself.",
        },
        {
            "number": "04",
            "title": "Recognize revenue",
            "copy": "A won deal creates the invoice, payment, and revenue event. No double entry.",
        },
    ],
}

PRICING_HEAD = {
    "eyebrow": "Pricing",
    "title": "Start free, scale when the loop is proven",
    "description": "",
}

PRICING_TIERS = [
    {
        "name": "Free",
        "description": "For small teams proving the loop.",
        "price": "$0",
        "period": "forever",
        "features": ["1 workspace", "3 members", "1 pipeline", "5 scheduled posts per month"],
        "cta_label": "Start free",
        "cta_href": "/accounts/signup/",
        "cta_page": None,
        "featured": False,
    },
    {
        "name": "Pro",
        "description": "For revenue teams running real campaigns.",
        "price": "$29",
        "period": "per user / month",
        "features": [
            "Unlimited pipelines",
            "100 scheduled posts per month",
            "All attribution models",
            "Finance ledger",
            "Workflow automation",
        ],
        "cta_label": "Start free",
        "cta_href": "/accounts/signup/",
        "cta_page": None,
        "featured": True,
    },
    {
        "name": "Enterprise",
        "description": "For organizations with compliance needs.",
        "price": "Custom",
        "period": "annual",
        "features": ["SSO and audit log", "Custom fields", "Dedicated support", "On-prem or VPC deploy"],
        "cta_label": "Talk to us",
        "cta_href": "/accounts/signup/",
        "cta_page": None,
        "featured": False,
    },
]

FAQ_HEAD = {
    "eyebrow": "FAQ",
    "title": "Questions, answered",
    "description": "",
}

FAQ_ITEMS = [
    {
        "question": "Is Loop CRM really free to start?",
        "answer": (
            "Yes — the Free tier includes one workspace, three members, a single "
            "pipeline, and five scheduled posts per month. No credit card required."
        ),
    },
    {
        "question": "Which social platforms can I publish to?",
        "answer": (
            "The calendar ships with channel-aware publishing. LinkedIn, X, "
            "Mastodon, Bluesky, Discord, and Slack publish for real, and more "
            "providers are cataloged behind the same connector surface."
        ),
    },
    {
        "question": "How does attribution work?",
        "answer": (
            "Every social interaction is recorded as a touchpoint and credited to "
            "the deals it influenced using first, last, linear, time-decay, or "
            "position-based models."
        ),
    },
    {
        "question": "Can I export my data?",
        "answer": (
            "Yes — invoices, payments, revenue events, and audit trails export to "
            "CSV from the corresponding screens."
        ),
    },
    {
        "question": "Do you self-host, or is this a hosted workspace?",
        "answer": (
            "Both. The hosted workspace at structa.cloud runs the latest release; "
            "deployments can also run the application on their own infrastructure."
        ),
    },
]

HOME_CTA = {
    "title": "Start closing the loop",
    "subtitle": "Connect a channel, publish one post, and watch it trace to a deal.",
    "primary_cta": _btn("Start free", "/accounts/signup/"),
    "secondary_cta": _btn("Sign in", "/accounts/login/", "outline"),
}

HOME_PRICING = {
    **PRICING_HEAD,
    "tiers": PRICING_TIERS,
}
HOME_FAQ = {
    **FAQ_HEAD,
    "items": FAQ_ITEMS,
}

# ── Pricing page ─────────────────────────────────────────────────────────────

PRICING_HERO = {
    "badge": "Pricing",
    "title": "Pricing that scales with the loop",
    "accent": "",
    "subtitle": (
        "Start free and upgrade when the loop is proven. Every tier includes "
        "attribution and the finance ledger."
    ),
    "primary_cta": _btn("Start free", "/accounts/signup/"),
    "secondary_cta": _btn("Sign in", "/accounts/login/", "outline"),
    "note": "",
}

# ── FAQ page ─────────────────────────────────────────────────────────────────

FAQ_HERO = {
    "badge": "FAQ",
    "title": "Frequently asked questions",
    "accent": "",
    "subtitle": "Honest answers about the platform, publishing, attribution, and data.",
    "primary_cta": _btn("Start free", "/accounts/signup/"),
    "secondary_cta": _btn("Sign in", "/accounts/login/", "outline"),
    "note": "",
}

# ── Legal pages (plain SaaS copy — no license grant) ────────────────────────

LEGAL_HERO = {
    "badge": "Legal",
    "title": "",
    "accent": "",
    "subtitle": "",
    "primary_cta": _btn("Start free", "/accounts/signup/"),
    "secondary_cta": _btn("Sign in", "/accounts/login/", "outline"),
    "note": "",
}

PRIVACY_BODY = (
    "<p>When you use the Loop CRM hosted workspace at structa.cloud, the "
    "service processes only the data you enter: accounts, companies, contacts, "
    "deals, posts, and revenue records, to operate the workspace you asked for.</p>"
    "<p>We do not sell personal data. Authentication data (email, and optional "
    "GitHub or Google OAuth identity) is used solely to identify you in the "
    "workspace. You can export or delete your workspace data at any time by "
    "contacting the workspace administrator.</p>"
    "<p>This notice is intentionally short. If you self-host, your data stays "
    "on infrastructure you control, and you are responsible for your own data "
    "handling and retention practices.</p>"
)

TERMS_BODY = (
    "<p>By creating a workspace you agree to use the Loop CRM hosted service "
    "lawfully, keep your credentials confidential, and not disrupt other "
    "tenants of the service. Workspace administrators control member access "
    "and data retention for the teams they manage.</p>"
    "<p>The service is provided as is, without warranty of any kind. You are "
    "responsible for the data you enter and for complying with the laws that "
    "apply to your use of the service in your jurisdiction.</p>"
    "<p>For questions about the service, contact the workspace administrator "
    "or the Loop CRM team.</p>"
)


class Command(BaseCommand):
    help = "Seed the Wagtail landing pages (Home, Pricing, FAQ, Privacy, Terms)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Rewrite the seeded content on existing pages (restores the initial copy).",
        )

    def handle(self, *args, **options):
        refresh = options["refresh"]
        home = self._seed_home(refresh)
        self._seed_site(home)
        self._seed_pricing(home, refresh)
        self._seed_faq(home, refresh)
        self._seed_privacy(home, refresh)
        self._seed_terms(home, refresh)
        self.stdout.write(self.style.SUCCESS(
            "Seeded Wagtail landing pages: Home, Pricing, FAQ, Privacy, Terms "
            f"(root /cms/ admin -> site '{Site.objects.get(is_default_site=True).site_name}')."
        ))

    # ── helpers ─────────────────────────────────────────────────────────────

    def _apply_content(self, page, content: dict, refresh: bool):
        """Set stream/rich content on a page — only on create or --refresh."""
        if page.pk is None or refresh:
            for field, value in content.items():
                setattr(page, field, value)

    def _get_or_create(self, model, parent, slug, title, content: dict, refresh: bool):
        existing = (
            parent.get_children().filter(slug=slug).first()
            if parent is not None
            else model.objects.first()
        )
        if existing is not None:
            page = existing.specific
            self._apply_content(page, content, refresh)
            page.save_revision().publish()
            return page
        page = model(title=title, slug=slug)
        self._apply_content(page, content, refresh)
        if parent is not None:
            parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  created {model.__name__} /{slug}/"))
        return page

    def _seed_home(self, refresh: bool) -> HomePage:
        home = HomePage.objects.first()
        created = False
        if home is None:
            # Wagtail's initial migration leaves a generic placeholder page
            # (slug 'home', title 'Welcome to your new Wagtail site!') at the
            # root. Replace it with our HomePage so the site root stays put.
            placeholder = (
                Page.objects.filter(depth=2)
                .filter(slug="home")
                .exclude(content_type__model__in=["homepage", "pricingpage", "faqpage", "privacypage", "termspage"])
                .first()
            )
            if placeholder is not None and placeholder.get_children().count() == 0:
                placeholder.delete()
            home = HomePage(title="Home", slug="home")
            Page.get_first_root_node().add_child(instance=home)
            created = True
            self.stdout.write(self.style.SUCCESS("  created HomePage /"))
        home = home.specific
        self._apply_content(home, {
            "hero": [("hero", HOME_HERO)],
            "dna": [("dna", HOME_DNA)],
            "features": [("features", HOME_FEATURES)],
            "steps": [("steps", HOME_STEPS)],
            "pricing": [("pricing", HOME_PRICING)],
            "faq": [("faq", HOME_FAQ)],
            "cta": [("cta", HOME_CTA)],
        }, refresh or created)
        home.save_revision().publish()
        return home

    def _seed_site(self, home: HomePage):
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            site = Site(
                hostname=os.environ.get("DJANGO_SITE_HOST", "localhost"),
                port=int(os.environ.get("DJANGO_SITE_PORT", "8000")),
                root_page=home,
                site_name="Loop CRM",
                is_default_site=True,
            )
            site.save()
            self.stdout.write(self.style.SUCCESS(f"  created Wagtail Site {site.hostname}:{site.port}"))
        elif site.root_page_id != home.pk:
            site.root_page = home
            site.site_name = site.site_name or "Loop CRM"
            site.save()
            self.stdout.write(self.style.SUCCESS("  updated Wagtail Site root_page -> Home"))

    def _seed_pricing(self, home, refresh):
        self._get_or_create(PricingPage, home, "pricing", "Pricing", {
            "hero": [("hero", PRICING_HERO)],
            "pricing": [("pricing", HOME_PRICING)],
            "faq": [("faq", HOME_FAQ)],
            "cta": [("cta", HOME_CTA)],
        }, refresh)

    def _seed_faq(self, home, refresh):
        self._get_or_create(FaqPage, home, "faq", "FAQ", {
            "hero": [("hero", FAQ_HERO)],
            "faq": [("faq", HOME_FAQ)],
            "cta": [("cta", HOME_CTA)],
        }, refresh)

    def _seed_privacy(self, home, refresh):
        page = self._get_or_create(PrivacyPage, home, "privacy", "Privacy", {
            "hero": [("hero", LEGAL_HERO)],
            "body": PRIVACY_BODY,
            "cta": [("cta", HOME_CTA)],
        }, refresh)
        if page.title != "Privacy":
            page.title = "Privacy"
            page.save_revision().publish()
        return page

    def _seed_terms(self, home, refresh):
        page = self._get_or_create(TermsPage, home, "terms", "Terms", {
            "hero": [("hero", LEGAL_HERO)],
            "body": TERMS_BODY,
            "cta": [("cta", HOME_CTA)],
        }, refresh)
        if page.title != "Terms":
            page.title = "Terms"
            page.save_revision().publish()
        return page
