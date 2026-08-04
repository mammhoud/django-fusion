"""
Seed the landing Wagtail page tree with default content.

Creates the site record plus Home / About / Company / Services / Products /
Features / Projects / Contact / FAQ / Privacy pages mirroring the Astro
frontend content (see src/lib/site.ts and the pages in frontend/src/pages/).

Idempotent: pages already present under the site root are left untouched;
empty content fields added by later migrations are backfilled.

Usage:
    python manage.py seed_pages
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.pages.models import (
    AboutPage,
    CompanyPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    HomePage,
    PrivacyPage,
    ProductsPage,
    ProjectsPage,
    ServicesPage,
)

DEFAULT_HOME_CONTENT = {
    "hero": [
        (
            "hero",
            {
                "badge": "structa.cloud · full-stack engineering",
                "title": "Platforms that ship as documents",
                "subtitle": (
                    "Structa Cloud builds server-rendered web platforms, AI tools, "
                    "and open-source libraries — Django + Wagtail on the backend, "
                    "Astro + HTMX + Alpine on the frontend. Every page is finished HTML."
                ),
                "primary_cta": {"label": "Explore the stack", "href": "/products", "style": "secondary"},
                "secondary_cta": {"label": "About the engineer", "href": "/about", "style": "white"},
                "trusted_by": "Trusted by teams building on Django + Wagtail",
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Everything is open source",
                "subtitle": "All structa.cloud libraries are public on GitHub. Explore the monorepo at github.com/mammhoud.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Read the Docs", "href": "/about", "style": "outline"},
            },
        )
    ],
}


# Projects the repo ships — name, edition, category, path and features that
# are either shared across the monorepo (reused by other projects) or
# standalone (project-only). Mirrors frontend/src/pages/projects.astro.
DEFAULT_PROJECTS = {
    "projects": [
        (
            "project",
            {
                "name": "Fusion CMS",
                "edition": "Wagtail backend",
                "category": "website",
                "path": "projects/landing-fusion/backend",
                "description": (
                    "The Wagtail content engine behind every landing page — StreamField "
                    "sections rendered server-side by django-fusion handlers."
                ),
                "features": [
                    {"label": "django-fusion fragment pipeline", "shared": True},
                    {"label": "HTMX fragment rendering", "shared": True},
                    {"label": "Wagtail StreamField blocks", "shared": False},
                ],
            },
        ),
        (
            "project",
            {
                "name": "Fusion Sites",
                "edition": "Astro frontend",
                "category": "website",
                "path": "projects/landing-fusion/frontend",
                "description": (
                    "The AHA shell — Astro SSG, HTMX fragment swaps, Alpine "
                    "micro-interactions. Zero framework JS in the critical path."
                ),
                "features": [
                    {"label": "Astro SSG", "shared": False},
                    {"label": "HTMX + Alpine runtime", "shared": True},
                    {"label": "Fusion design tokens", "shared": True},
                ],
            },
        ),
        (
            "project",
            {
                "name": "Forge POS",
                "edition": "Minimal · Solo · Full",
                "category": "product",
                "path": "projects/pos/forge-pos",
                "description": (
                    "A desktop point-of-sale app in three editions — Tauri 2 + Rust "
                    "core with a React/Vite frontend and SQLite storage."
                ),
                "features": [
                    {"label": "Tauri 2 + Rust core", "shared": True},
                    {"label": "SQLite schema", "shared": True},
                    {"label": "Kitchen display", "shared": False},
                    {"label": "Employee scheduling", "shared": False},
                ],
            },
        ),
        (
            "project",
            {
                "name": "django-fusion",
                "edition": "library · generic",
                "category": "library",
                "path": "libs/django-fusion",
                "description": (
                    "The component system + routing framework shared by every site — "
                    "PageHandler views, fragment rendering, {% comp %} templates."
                ),
                "features": [
                    {"label": "Component registry", "shared": True},
                    {"label": "FragmentHandlerMixin", "shared": True},
                    {"label": "Wagtail blocks bridge", "shared": True},
                ],
            },
        ),
        (
            "project",
            {
                "name": "ceptor-ai",
                "edition": "library · generic",
                "category": "library",
                "path": "libs/ceptor-ai",
                "description": (
                    "AI chat client + MCP server used by the Cypercloud platform "
                    "and agent tooling."
                ),
                "features": [
                    {"label": "MCP server", "shared": True},
                    {"label": "Chat client", "shared": True},
                ],
            },
        ),
        (
            "project",
            {
                "name": "Cypercloud",
                "edition": "AI platform",
                "category": "product",
                "path": "projects/cypercloud",
                "description": (
                    "The AI chat customizer platform — ceptor-ai powered chat "
                    "embedded into customer sites."
                ),
                "features": [
                    {"label": "ceptor-ai chat", "shared": True},
                    {"label": "Customizer UI", "shared": False},
                ],
            },
        ),
    ]
}


# The full document lives on the About page (mirrors the Astro frontend where
# /about carries hero + mission + stats + features + pricing + testimonials +
# faq + cta and / is a slim hero + cta entry point).
DEFAULT_ABOUT_SECTIONS = {
    "stats": [
        (
            "stats",
            {
                "title": "Numbers that speak for themselves",
                "stats": [
                    {"value": "15", "suffix": "+", "label": "Open-source repos"},
                    {"value": "18", "suffix": "", "label": "Blog posts"},
                    {"value": "4", "suffix": "+", "label": "Production sites"},
                    {"value": "5", "suffix": "+", "label": "Years building"},
                ],
            },
        )
    ],
    "features": [
        (
            "features",
            {
                "eyebrow": "Features",
                "title": "Everything you need to launch",
                "description": (
                    "A complete landing and marketing stack, ported from the heavy "
                    "Next.js SPA to a lightweight AHA architecture."
                ),
                "features": [
                    {
                        "icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z",
                        "title": "Django + Wagtail",
                        "description": "Content managed in Wagtail 7.4 with StreamField blocks — editors compose, django-fusion renders server-side.",
                    },
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "HTMX Fragment Rendering",
                        "description": "Dynamic updates stream from Django as HTML fragments — no JSON API layer, no decoder to maintain.",
                    },
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Astro + Alpine.js",
                        "description": "Astro SSG for zero-JS landing pages. Alpine.js for micro-interactions only where the page needs them.",
                    },
                    {
                        "icon": "M17 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM21 21v-2a4 4 0 00-3-3.87",
                        "title": "Monorepo Architecture",
                        "description": "Six projects, one repository, one CI pipeline. Shared configs, assets, and components across all sites.",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "AI-Powered Tools",
                        "description": "ceptor-ai MCP server for agent communication, code generation, and prompt-to-design conversion.",
                    },
                    {
                        "icon": "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20",
                        "title": "Open Source First",
                        "description": "All core libraries are public on GitHub. django-fusion, ceptor-ai, and django-bolt are open for contribution.",
                    },
                ],
            },
        )
    ],
    "testimonials": [
        (
            "testimonials",
            {
                "eyebrow": "Testimonials",
                "title": "Trusted by developers",
                "description": "What teams say about building with django-fusion and the AHA stack.",
                "testimonials": [
                    {
                        "quote": "The switch from a heavy React SPA to HTMX fragments cut our page load time in half. django-fusion's component system made the migration straightforward.",
                        "author": "Sarah Mitchell",
                        "role": "CTO, EduStart",
                        "avatar_initials": "SM",
                    },
                    {
                        "quote": "Alpine.js replaced all our custom UI state code. The FAQ accordion and modals took an afternoon instead of a week.",
                        "author": "David Chen",
                        "role": "Lead Developer, LearnLoop",
                        "avatar_initials": "DC",
                    },
                    {
                        "quote": "Server-rendered HTML means perfect SEO without any extra work. Our blog traffic doubled within a month.",
                        "author": "Amira Hassan",
                        "role": "Marketing Director, SkillBridge",
                        "avatar_initials": "AH",
                    },
                ],
            },
        )
    ],
    "pricing": [
        (
            "pricing",
            {
                "eyebrow": "Pricing",
                "title": "Simple, transparent pricing",
                "description": "Start free and scale as you grow. No hidden fees, cancel anytime.",
                "tiers": [
                    {
                        "name": "Starter",
                        "description": "Perfect for individuals exploring the platform.",
                        "price": "$0",
                        "period": "/forever",
                        "features": [
                            "Up to 3 courses",
                            "Community support",
                            "Basic progress tracking",
                            "Public profile",
                        ],
                        "cta_label": "Start Free",
                        "cta_href": "/#cta",
                        "featured": False,
                    },
                    {
                        "name": "Pro",
                        "description": "For active learners and content creators.",
                        "price": "$29",
                        "period": "/per month",
                        "features": [
                            "Unlimited courses",
                            "Priority support",
                            "Advanced analytics",
                            "Offline downloads",
                            "Certificates",
                        ],
                        "cta_label": "Go Pro",
                        "cta_href": "/#cta",
                        "featured": True,
                    },
                    {
                        "name": "Team",
                        "description": "For teams and organizations of any size.",
                        "price": "$99",
                        "period": "/per month",
                        "features": [
                            "Everything in Pro",
                            "SSO & role management",
                            "Dedicated success manager",
                            "Custom branding",
                            "API access",
                        ],
                        "cta_label": "Contact Sales",
                        "cta_href": "/contact/",
                        "featured": False,
                    },
                ],
            },
        )
    ],
    "faq": [
        (
            "faq",
            {
                "eyebrow": "FAQ",
                "title": "Frequently asked questions",
                "description": "Everything you need to know about structa.cloud, django-fusion, and the stack.",
                "items": [
                    {
                        "question": "What is structa.cloud?",
                        "answer": "Structa Cloud is the portfolio and product hub for Mahmoud Ezzat Moustafa — a full-stack developer building Django/Wagtail platforms, AI tools, and open-source libraries.",
                    },
                    {
                        "question": "What is the AHA stack?",
                        "answer": "AHA stands for Astro + HTMX + Alpine.js — a server-first rendering stack that ships minimal client-side JavaScript.",
                    },
                    {
                        "question": "Are the libraries free to use?",
                        "answer": "Yes. django-fusion, ceptor-ai, and django-bolt are all open-source on GitHub under permissive licenses.",
                    },
                    {
                        "question": "Can I use this for a client project?",
                        "answer": "Absolutely. The libraries are production-tested across vResume, Cypercloud, and the landing pages.",
                    },
                    {
                        "question": "How do I get started?",
                        "answer": "Clone the monorepo from github.com/mammhoud, run 'make dev' in projects/landing-fusion, and explore the Wagtail admin at /admin/.",
                    },
                    {
                        "question": "How do I deploy a Fusion site?",
                        "answer": "The monorepo includes Docker Compose orchestration with Traefik + Nginx + Postgres. One 'make deploy' provisions the full stack with HTTPS.",
                    },
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built open-source, shipped as HTML",
                "subtitle": "Everything structa.cloud builds is on GitHub. Explore the monorepo and reach out for collaboration.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Get in Touch", "href": "/contact/", "style": "outline"},
            },
        )
    ],
}


class Command(BaseCommand):
    help = "Seed the landing Wagtail page tree with default content."

    def handle(self, *args, **options):
        self.stdout.write("Seeding landing pages…")

        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stdout.write(self.style.ERROR("No root page — run migrations first."))
            return

        landing_models = {
            HomePage,
            AboutPage,
            CompanyPage,
            ServicesPage,
            ProductsPage,
            FeaturesPage,
            ProjectsPage,
            ContactPage,
            FaqPage,
            PrivacyPage,
        }

        # Repoint-or-drop any Site that does not point at one of our landing
        # pages (Wagtail's migrations create a default site rooted on the
        # "Welcome" page, which we remove below).
        for site in Site.objects.all():
            try:
                rooted_in_landing = site.root_page.specific_class in landing_models
            except Page.DoesNotExist:  # pragma: no cover — orphaned pointer
                rooted_in_landing = False
            if not rooted_in_landing:
                self.stdout.write(f"Removing default site: {site.hostname}")
                site.delete()

        # Remove Wagtail's default "Welcome" page (created by migrations) so
        # this command can own the site root and the '/' route.
        for child in root.get_children():
            if child.specific_class not in landing_models:
                self.stdout.write(f"Removing default page: {child.title} (slug={child.slug})")
                child.delete()

        # ── Home page (root child) ──────────────────────────────────────
        home, created = self._get_or_create_child(
            root, HomePage, title="Home", slug="home", **DEFAULT_HOME_CONTENT
        )
        self._created(created, "home")

        # Site record — root_page points at the home page.
        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"port": 8074, "is_default_site": True, "root_page": home},
        )
        site.root_page = home
        site.save()
        self.stdout.write(f"Site root set to {home.title} (http://localhost:{site.port}/)")

        # ── About (the full document) ────────────────────────────────
        about, created = self._get_or_create_child(
            home,
            AboutPage,
            title="About Us",
            slug="about",
            hero=[
                (
                    "hero",
                    {
                        "title": "About Us",
                        "subtitle": "The story behind Fusion CMS and the AHA stack.",
                        "primary_cta": {"label": "Our Features", "href": "/#features", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/#cta", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>Fusion CMS started with a simple belief: marketing sites "
                "should be fast, secure, and easy to maintain.</p>"
                "<p>We migrated our own landing pages from a heavy Next.js SPA "
                "to the AHA stack — Astro for server rendering, HTMX for dynamic "
                "updates, and Alpine.js for client-side polish.</p>"
                "<p>The result: sub-second loads, perfect SEO, and a codebase "
                "that a small team can own.</p>"
            ),
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "about")

        # ── Company ─────────────────────────────────────────────────────
        company, created = self._get_or_create_child(
            home,
            CompanyPage,
            title="Company",
            slug="company",
            hero=[
                (
                    "hero",
                    {
                        "title": "Who We Are",
                        "subtitle": "The people and principles behind Fusion CMS.",
                        "primary_cta": {"label": "Our Services", "href": "/services/", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/#cta", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>Fusion CMS is built by a small team that believes the web "
                "should be fast by default.</p>"
                "<p>Our mission is to give every team a landing stack that ships "
                "as plain HTML — no heavy SPA, no maintenance treadmill.</p>"
                "<p>We value performance, simplicity, and boring technology that "
                "keeps working.</p>"
            ),
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "company")

        # ── Services ────────────────────────────────────────────────────
        services, created = self._get_or_create_child(
            home,
            ServicesPage,
            title="Services",
            slug="services",
            hero=[
                (
                    "hero",
                    {
                        "title": "Services",
                        "subtitle": "Server-rendered sites, HTMX integrations, and Alpine-powered UX.",
                        "primary_cta": {"label": "Our Products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>We design and build landing pages on the AHA stack — Astro, "
                "HTMX, and Alpine.js.</p>"
                "<p>From static marketing sites to dynamic, form-driven pages, "
                "every deliverable is server-rendered HTML.</p>"
                "<p>Ongoing support covers hosting, CMS content editing, and "
                "performance tuning.</p>"
            ),
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "services")

        # ── Products (full document, like About) ───────────────────────
        products, created = self._get_or_create_child(
            home,
            ProductsPage,
            title="Products",
            slug="products",
            hero=[
                (
                    "hero",
                    {
                        "title": "Products",
                        "subtitle": "Fusion CMS and the tools that ship your sites as plain HTML.",
                        "primary_cta": {"label": "See the Features", "href": "/features/", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/#cta", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>Fusion CMS is our flagship — a Wagtail-powered content engine "
                "that renders every page server-side.</p>"
                "<p>Paired with the Astro frontend, HTMX fragments, and Alpine "
                "components, it covers the full landing stack.</p>"
                "<p>Every product ships with the same promise: 0 KB of framework "
                "JavaScript in the critical path.</p>"
            ),
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "products")

        # ── Features (full document, like About) ────────────────────────
        features, created = self._get_or_create_child(
            home,
            FeaturesPage,
            title="Features",
            slug="features",
            hero=[
                (
                    "hero",
                    {
                        "title": "Features",
                        "subtitle": "The AHA stack, documented — every capability of Fusion CMS.",
                        "primary_cta": {"label": "Our Products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/#cta", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>The AHA stack is Astro + HTMX + Alpine.js — a server-first "
                "rendering stack that ships finished HTML in one response.</p>"
                "<p>Every capability below exists to keep the page a document: "
                "fast by default, secure by default, editable by editors.</p>"
            ),
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "features")

        # ── Projects (full document, like About) ────────────────────────
        projects, created = self._get_or_create_child(
            home,
            ProjectsPage,
            title="Projects",
            slug="projects",
            hero=[
                (
                    "hero",
                    {
                        "title": "Projects",
                        "subtitle": "The monorepo at a glance — every project, its edition, and what it shares.",
                        "primary_cta": {"label": "See the Features", "href": "/features/", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/#cta", "style": "white"},
                    },
                )
            ],
            # No body — the frontend /projects goes straight from hero to the
            # project grid, so the backend mirrors it (the grid section header
            # carries the "Projects in this repo" heading).
            **DEFAULT_PROJECTS,
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "projects")

        # ── Contact ─────────────────────────────────────────────────────
        contact, created = self._get_or_create_child(
            home,
            ContactPage,
            title="Contact",
            slug="contact",
            hero=[
                (
                    "hero",
                    {
                        "title": "Get in Touch",
                        "subtitle": "We'd love to hear from you. Reach out any time.",
                    },
                )
            ],
            contact=[
                (
                    "contact",
                    {
                        "eyebrow": "Contact",
                        "title": "We'd love to hear from you",
                        "description": "Send us a message and we'll respond within 24 hours.",
                        "methods": [
                            {
                                "method_type": "email",
                                "label": "Email",
                                "value": "structa.cloud@gmail.com",
                                "href": "mailto:structa.cloud@gmail.com",
                            },
                            {
                                "method_type": "phone",
                                "label": "Phone",
                                "value": "+1 (555) 010-2030",
                                "href": "tel:+15550102030",
                            },
                            {
                                "method_type": "address",
                                "label": "Address",
                                "value": "123 Fusion Lane, Suite 400",
                            },
                            {
                                "method_type": "hours",
                                "label": "Working Hours",
                                "value": "Mon – Fri, 9:00 – 18:00",
                            },
                        ],
                        "form_title": "Send us a message",
                        "form_description": "Fill out the form and our team will get back to you.",
                    },
                )
            ],
            cta=[
                (
                    "cta",
                    {
                        "title": "Prefer email?",
                        "subtitle": "Write to structa.cloud@gmail.com and we'll reply within a day.",
                        "primary_cta": {"label": "Send an Email", "href": "mailto:structa.cloud@gmail.com", "style": "white"},
                    },
                )
            ],
        )
        self._created(created, "contact")

        # ── FAQ ─────────────────────────────────────────────────────────
        faq, created = self._get_or_create_child(
            home,
            FaqPage,
            title="FAQ",
            slug="faq",
            hero=[
                (
                    "hero",
                    {
                        "title": "Frequently Asked Questions",
                        "subtitle": "Quick answers to the most common questions.",
                    },
                )
            ],
            faq=DEFAULT_ABOUT_SECTIONS["faq"],
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "faq")

        # ── Privacy ─────────────────────────────────────────────────────
        privacy, created = self._get_or_create_child(
            home,
            PrivacyPage,
            title="Privacy Policy",
            slug="privacy",
            body=(
                "<p>This privacy policy explains how Fusion CMS collects, uses, "
                "and protects your information.</p>"
                "<h3>What we collect</h3>"
                "<p>Account details, course progress, and usage analytics.</p>"
                "<h3>How we use it</h3>"
                "<p>To deliver courses, personalize content, and improve the platform.</p>"
                "<h3>Your rights</h3>"
                "<p>You can request a copy or deletion of your data at any time "
                "by contacting us.</p>"
            ),
        )
        self._created(created, "privacy")

        self.stdout.write(self.style.SUCCESS("✅ Landing pages seeded."))

    # ── Helpers ─────────────────────────────────────────────────────
    def _get_or_create_child(self, parent, model, **fields):
        """Idempotently create a treebeard page under ``parent``.

        Treebeard nodes cannot be created with ``Model.objects.get_or_create``
        (``save()`` runs ``full_clean`` before ``path``/``depth`` are set), so
        we look up by slug first and otherwise use ``parent.add_child``.

        If the page already exists, only *empty* content fields are backfilled
        from the seed values — editor changes to non-empty fields are never
        clobbered. This also refreshes pages whose fields were added by a
        later migration (e.g. Products upgraded to a full document).
        """
        slug = fields["slug"]
        existing = model.objects.filter(slug=slug, depth=parent.depth + 1).first()
        if existing is not None:
            self._backfill_empty_fields(existing, fields)
            return existing, False
        page = model(**fields)
        parent.add_child(instance=page)
        return page, True

    def _backfill_empty_fields(self, existing, fields):
        """Set seed values on empty content fields of an existing page."""
        changed = False
        for name, value in fields.items():
            if name in ("title", "slug"):
                continue
            current = getattr(existing, name, None)
            # StreamFields/RichTextFields are falsy when empty.
            if not current and value:
                setattr(existing, name, value)
                changed = True
        if changed:
            existing.save()

    def _created(self, created, label):
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created {label} page."))
        else:
            self.stdout.write(f"{label} page already exists.")
