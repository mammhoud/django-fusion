"""
Seed the ported landing-slice page models into the LMS tree.

Creates the product catalog (``ProductsPage`` + ``ProductPage`` children), the
dedicated ``PricingPage`` and ``BrandPage``, the delivery phases/prompts under
the native ``ServicesPage``, and matching ``Product`` snippets — the Wagtail
source of truth behind ``/apis/products/``, ``/apis/pricing/`` and
``/apis/brand/``.

Idempotent: pages are found by slug and only *empty* content fields are
backfilled, so editor changes are never clobbered. This deliberately omits the
structa.cloud / personal-brand seed from precis-landing and uses lms-native
Wagtail locales instead of landing's ``PageTranslation`` overlays.

Usage:
    python manage.py seed_landing_pages
"""

from __future__ import annotations

import logging

from django.core.management.base import BaseCommand
from wagtail.models import Page

logger = logging.getLogger(__name__)


# ── Product catalog ─────────────────────────────────────────────────────────
# One entry per live product in BRAND_SPEC (apps/pages/pages/brand_spec.py).
# Content is deliberately clean product copy — no personal links or
# structa.cloud URLs — so the merged catalog stays on-brand for CTC/Precis.
DEFAULT_PRODUCTS = {
    "formint-pos": {
        "title": "Formints",
        "version": "beta 0.2",
        "logo_style": "crest",
        "category": "application",
        "tagline": "Desktop point-of-sale in four editions: Community, Standard, Pro, Cloud.",
        "hero": [
            (
                "hero",
                {
                    "title": "Formints",
                    "subtitle": "A desktop point-of-sale application with a Tauri 2 + Rust core and a React shell.",
                    "primary_cta": {"label": "See the editions", "href": "/products/formint-pos/", "style": "secondary"},
                    "secondary_cta": {"label": "Talk to sales", "href": "/contact/", "style": "white"},
                    "trusted_by": "Community · Standard · Pro · Cloud",
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Four editions, one codebase",
                    "description": "Every edition shares the Tauri + Rust core. Upgrade as your terminal grows.",
                    "editions": [
                        {
                            "name": "Community",
                            "tagline": "Free and open source. Offline-first POS for a single terminal.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Tauri 2 + Rust core", "SQLite storage", "Sales, receipting + inventory", "Offline-first mode", "i18n: en, fr, ar"],
                            "cta_label": "Get Community",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Standard",
                            "tagline": "Standalone terminal with analytics, integrations and a high-end interface.",
                            "price": "$119",
                            "period": "/one-time license",
                            "features": ["Everything in Community", "Inventory adjustments + stock control", "Food & beverage menu support", "Invoice PDF generation", "Loyalty & rewards"],
                            "cta_label": "Buy Standard",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "default",
                        },
                        {
                            "name": "Pro",
                            "tagline": "Multi-terminal with a cloud master and real-time streaming.",
                            "price": "$79",
                            "period": "/per year",
                            "features": ["Everything in Standard", "Multi-terminal sync (cloud master)", "WebSocket real-time streaming", "Employee scheduling + KPIs"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                        {
                            "name": "Cloud",
                            "tagline": "Fully hosted multi-terminal. The Pro cloud master, managed for you.",
                            "price": "Custom",
                            "period": "/per month",
                            "features": ["Everything in Pro", "Hosted cloud master", "Unlimited terminals", "Managed backups + monitoring"],
                            "cta_label": "Talk to Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "managed",
                        },
                    ],
                },
            )
        ],
    },
    "lms": {
        "title": "Precis LMS",
        "logo_style": "ribbon",
        "category": "platform",
        "tagline": "The learning platform: courses, enrollments, payments and progress.",
        "hero": [
            (
                "hero",
                {
                    "title": "Precis LMS",
                    "subtitle": "A content-driven learning platform built on Django, Wagtail and Astro.",
                    "primary_cta": {"label": "See the editions", "href": "/products/lms/", "style": "secondary"},
                    "secondary_cta": {"label": "Learn more", "href": "/about/", "style": "white"},
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Scale from one course to a cohort",
                    "editions": [
                        {
                            "name": "Solo",
                            "tagline": "For creators and small academies who want a polished learning experience.",
                            "price": "$29",
                            "period": "/per month",
                            "features": ["Unlimited courses", "Priority support", "Advanced analytics", "Certificates"],
                            "cta_label": "Go Solo",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                        {
                            "name": "Business",
                            "tagline": "For organizations with cohorts, staff and connected systems.",
                            "price": "$99",
                            "period": "/per month",
                            "features": ["Everything in Solo", "Custom branding", "API access"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "default",
                        },
                    ],
                },
            )
        ],
    },
    "cms": {
        "title": "Loop CRM",
        "version": "coming soon",
        "status": "development",
        "logo_style": "isometric",
        "category": "platform",
        "tagline": "A calmer path from social attention to the next customer conversation.",
        "hero": [
            (
                "hero",
                {
                    "title": "Loop CRM",
                    "subtitle": "A connected customer workspace that turns attention into useful conversations.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cms/", "style": "secondary"},
                    "secondary_cta": {"label": "Contact us", "href": "/contact/", "style": "white"},
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "A customer workspace in two editions",
                    "editions": [
                        {
                            "name": "Community",
                            "tagline": "Open-source CRM + social scheduling for a single workspace.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["CRM pipeline", "Social scheduling", "Contact timeline"],
                            "cta_label": "Get Community",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Cloud",
                            "tagline": "Hosted multi-workspace with attribution and integrations.",
                            "price": "Custom",
                            "period": "/per month",
                            "features": ["Everything in Community", "Hosted workspace", "Attribution reporting"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                    ],
                },
            )
        ],
    },
    "cypercloud": {
        "title": "Syntara",
        "version": "under development",
        "status": "development",
        "logo_style": "orbit",
        "category": "platform",
        "tagline": "AI chat customizer: route every conversation around your model and your data.",
        "hero": [
            (
                "hero",
                {
                    "title": "Syntara",
                    "subtitle": "Chat, routed around your brand. Customize AI conversations with your own model and data.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cypercloud/", "style": "secondary"},
                    "secondary_cta": {"label": "Contact us", "href": "/contact/", "style": "white"},
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Two editions, one customization engine",
                    "editions": [
                        {
                            "name": "Community",
                            "tagline": "Self-hosted AI chat customizer.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Custom model routing", "MCP integrations", "Template discovery"],
                            "cta_label": "Get Community",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Cloud",
                            "tagline": "Managed customization with streaming responses.",
                            "price": "Custom",
                            "period": "/per month",
                            "features": ["Everything in Community", "Managed streaming", "Brand customization"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                    ],
                },
            )
        ],
    },
    "vresume": {
        "title": "vResume",
        "logo_style": "ascent",
        "category": "application",
        "tagline": "Portfolio and resume platform with AI-powered summaries.",
        "hero": [
            (
                "hero",
                {
                    "title": "vResume",
                    "subtitle": "Your career, on the record. A portfolio and resume platform with Syntara-powered summaries.",
                    "primary_cta": {"label": "See the editions", "href": "/products/vresume/", "style": "secondary"},
                    "secondary_cta": {"label": "Contact us", "href": "/contact/", "style": "white"},
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "A portfolio that works for you",
                    "editions": [
                        {
                            "name": "Free",
                            "tagline": "A clean portfolio and resume.",
                            "price": "$0",
                            "period": "/forever",
                            "features": ["Portfolio pages", "Resume builder", "Cloud hosting"],
                            "cta_label": "Get Free",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Pro",
                            "tagline": "AI summaries and custom domains.",
                            "price": "$9",
                            "period": "/per month",
                            "features": ["Everything in Free", "AI summaries", "Custom domain"],
                            "cta_label": "Go Pro",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                    ],
                },
            )
        ],
    },
    "precis-ctc": {
        "title": "CTC Research",
        "logo_style": "research",
        "category": "platform",
        "tagline": "Research workspace: evidence, decisions and team progress in one orbit.",
        "hero": [
            (
                "hero",
                {
                    "title": "CTC Research",
                    "subtitle": "A research workspace for evidence, decisions and team progress.",
                    "primary_cta": {"label": "See the editions", "href": "/products/precis-ctc/", "style": "secondary"},
                    "secondary_cta": {"label": "Contact us", "href": "/contact/", "style": "white"},
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Evidence, carried forward",
                    "editions": [
                        {
                            "name": "Standard",
                            "tagline": "A focused research workspace for one team.",
                            "price": "Custom",
                            "period": "/per month",
                            "features": ["Evidence tracking", "Decision log", "Team progress"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                    ],
                },
            )
        ],
    },
}


# ── Delivery phases (under the native ServicesPage) ─────────────────────────
PHASE_SEED = [
    {
        "title": "Discover",
        "slug": "discover",
        "phase_number": 1,
        "phase_label": "discovery",
        "body": "<p>Turn the brief into a clear document model, visual direction, and measurable first release.</p>",
        "outcomes": "A bounded brief\nA content and route map\nA first-release decision log",
        "prompts": [
            {
                "title": "Shape the brief",
                "slug": "shape-the-brief",
                "prompt": "Turn this product brief into a focused first release with user, content, route, and success constraints.",
                "context": "Use this before design or implementation begins.",
                "output": "A concise scope, assumptions, risks, and acceptance checklist.",
                "tool": "Wagtail + product discovery",
            }
        ],
    },
    {
        "title": "Build",
        "slug": "build",
        "phase_number": 2,
        "phase_label": "build",
        "body": "<p>Build the smallest complete path as server-rendered HTML, then add progressive enhancement where it helps.</p>",
        "outcomes": "A working content model\nA responsive document route\nProgressive enhancement checks",
        "prompts": [
            {
                "title": "Build the first vertical slice",
                "slug": "build-the-first-vertical-slice",
                "prompt": "Implement one complete user journey from Wagtail model to accessible HTML, with progressive enhancement only where needed.",
                "context": "Keep the server-rendered path usable without JavaScript.",
                "output": "A tested vertical slice with model, API, template, and browser states.",
                "tool": "Astro + HTMX + Alpine",
            }
        ],
    },
    {
        "title": "Launch",
        "slug": "launch",
        "phase_number": 3,
        "phase_label": "launch",
        "body": "<p>Ship a dependable release with content parity, observability, and a handoff the team can own.</p>",
        "outcomes": "SEO and accessibility checks\nDeployment runbook\nEditor handoff",
        "prompts": [
            {
                "title": "Prepare the release",
                "slug": "prepare-the-release",
                "prompt": "Audit this release for broken routes, missing content, accessibility regressions, and backend/frontend parity before deployment.",
                "context": "Run the same checklist against the Astro and Django roads.",
                "output": "A prioritized release report with fixes and explicit sign-off criteria.",
                "tool": "Django + Astro verification",
            }
        ],
    },
    {
        "title": "Enhance",
        "slug": "enhance",
        "phase_number": 4,
        "phase_label": "enhance",
        "body": "<p>Improve the living system through measured content, performance, and interaction enhancements.</p>",
        "outcomes": "A measured improvement backlog\nReusable content patterns\nA safe iteration loop",
        "prompts": [
            {
                "title": "Enhance without drift",
                "slug": "enhance-without-drift",
                "prompt": "Improve this page while preserving content ownership, render parity, accessibility, and the existing design language.",
                "context": "Prefer reusable components and Wagtail-managed content over one-off page markup.",
                "output": "A small change set with regression checks and a documented reason for each change.",
                "tool": "django-fusion components",
            }
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the ported landing-slice page models and product snippets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing content fields with seed values (default: backfill empty fields only).",
        )

    def handle(self, *args, **options):
        self.force = options.get("force", False)
        self.stdout.write("Seeding landing-slice pages…")

        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stdout.write(self.style.ERROR("No root page — run migrations first."))
            return

        home = self._home_page(root)
        if home is None:
            self.stdout.write(self.style.ERROR("No home page found — run populate_content first."))
            return

        # ── Product catalog ──────────────────────────────────────────────
        products_page, _ = self._get_or_create_child(
            home, "ProductsPage", title="Products", slug="products"
        )
        for slug, product in DEFAULT_PRODUCTS.items():
            fields = {
                "title": product["title"],
                "category": product.get("category", "application"),
                "tagline": product.get("tagline", ""),
                "version": product.get("version", ""),
                "logo_style": product.get("logo_style", "crest"),
                "status": product.get("status", "live"),
                "hidden": product.get("hidden", False),
                "show_on_home": product.get("show_on_home", True),
                "hero": product.get("hero", []),
                "editions": product.get("editions", []),
            }
            _, created = self._get_or_create_child(products_page, "ProductPage", slug=slug, **fields)
            self._created(created, f"products:{slug}")

        # ── Pricing + brand pages ────────────────────────────────────────
        _, created = self._get_or_create_child(home, "PricingPage", title="Pricing", slug="pricing")
        self._created(created, "pricing")

        _, created = self._get_or_create_child(home, "BrandPage", title="Brand", slug="brand")
        self._created(created, "brand")

        # ── Delivery phases under the native ServicesPage ───────────────
        services = self._services_page(home)
        if services is not None:
            for phase_data in PHASE_SEED:
                prompts = phase_data.pop("prompts")
                phase, phase_created = self._get_or_create_child(services, "PhasePage", **phase_data)
                self._created(phase_created, f"services:phase:{phase.slug}")
                for prompt_data in prompts:
                    prompt, prompt_created = self._get_or_create_child(phase, "PromptPage", **prompt_data)
                    self._created(prompt_created, f"services:phase:{phase.slug}:prompt:{prompt.slug}")
        else:
            self.stdout.write(self.style.WARNING("ServicesPage not found — skipping delivery phases/prompts."))

        # ── Product snippets (catalog-of-record for /apis/products/) ─────
        self._seed_product_snippets()

        self.stdout.write(self.style.SUCCESS("Landing-slice seed complete."))

    # ── Model + page-tree helpers ──────────────────────────────────────

    def _home_page(self, root):
        """Find the native LMS HomePage (or fall back to the site root page)."""
        from apps.content.models.pages.home import HomePage

        home = HomePage.objects.live().first()
        if home is not None:
            return home
        site_root = root.get_children().live().first()
        return site_root

    def _services_page(self, home):
        from apps.content.models.pages.services import ServicesPage

        return ServicesPage.objects.live().first()

    def _get_or_create_child(self, parent, model_name, **fields):
        """Idempotently create a treebeard page under ``parent`` by slug."""
        model = self._resolve_model(model_name)
        slug = fields["slug"]
        existing_node = parent.get_children().filter(slug=slug).first()
        if existing_node is not None:
            existing = existing_node.specific
            if isinstance(existing, model):
                self._backfill_empty_fields(existing, fields)
                return existing, False
        page = model(**fields)
        parent.add_child(instance=page)
        return page, True

    def _resolve_model(self, model_name):
        from django.apps import apps as django_apps

        if model_name in ("PhasePage", "PromptPage", "BrandPage", "PricingPage", "ProductPage", "ProductsPage"):
            # Ported landing-slice models (app label "pages").
            from apps.content.models.landing import (  # noqa: F401
                BrandPage,
                PhasePage,
                PricingPage,
                ProductPage,
                ProductsPage,
                PromptPage,
            )

            return {
                "PhasePage": PhasePage,
                "PromptPage": PromptPage,
                "BrandPage": BrandPage,
                "PricingPage": PricingPage,
                "ProductPage": ProductPage,
                "ProductsPage": ProductsPage,
            }[model_name]
        raise ValueError(f"Unknown landing page model: {model_name}")

    def _backfill_empty_fields(self, existing, fields):
        """Apply seed values to an existing page's empty content fields.

        Titles and slugs anchor the tree and are never rewritten; only empty
        content fields are backfilled (or every field under ``--force``).
        """
        changed = False
        for name, value in fields.items():
            if name in ("slug", "title"):
                continue
            current = getattr(existing, name, None)
            if self.force or (not current and value):
                setattr(existing, name, value)
                changed = True
        if changed:
            existing.save()
        return changed

    def _seed_product_snippets(self):
        """Create matching Product snippets for the catalog (idempotent)."""
        from apps.content.models.products import Product

        for slug, product in DEFAULT_PRODUCTS.items():
            defaults = {
                "title": product["title"],
                "short_description": product.get("tagline", ""),
                "category": product.get("category", "application"),
                "version": product.get("version", ""),
                "status": product.get("status", "live"),
                "is_published": True,
                "is_featured": slug in ("lms", "formint-pos"),
            }
            _, created = Product.objects.get_or_create(slug=slug, defaults=defaults)
            self._created(created, f"product-snippet:{slug}")

    def _created(self, created, label):
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created {label}."))
        else:
            self.stdout.write(f"{label} already exists.")
