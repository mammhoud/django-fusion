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
    BlogPage,
    BlogPostPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    HomePage,
    PricingPage,
    PrivacyPage,
    ProductPage,
    ProductsPage,
    ProjectsPage,
    ServicesPage,
)

# Services the project offers — the “feature” grid on the Services page.
# Mirrors the frontend services page (feature cards with deliverables).
DEFAULT_SERVICES_SECTIONS = {
    "services": [
        (
            "services",
            {
                "eyebrow": "What we do",
                "title": "Sites that ship as documents",
                "description": (
                    "Server-rendered HTML first. Every engagement below delivers "
                    "a finished page — no heavy SPA, no hydration waterfall."
                ),
                "services": [
                    {
                        "icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z",
                        "title": "Django + Wagtail build",
                        "description": "Content-managed sites with StreamField blocks — editors compose, Django renders server-side.",
                        "deliverables": ["Wagtail page tree", "StreamField sections", "django-fusion rendering"],
                        "cta_label": "See the stack",
                        "cta_href": "/features/",
                    },
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "HTMX integrations",
                        "description": "Dynamic regions stream from Django as HTML fragments — no JSON API layer, no decoder to maintain.",
                        "deliverables": ["Fragment endpoints", "HTMX swap targets", "In-flight indicators"],
                        "cta_label": "See a live demo",
                        "cta_href": "/#cta",
                    },
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Astro + Alpine frontends",
                        "description": "Zero-JS landing pages with Alpine micro-interactions only where the page needs them.",
                        "deliverables": ["Astro SSG shell", "Alpine components", "Theme persistence"],
                        "cta_label": "Read the docs",
                        "cta_href": "/about/",
                    },
                    {
                        "icon": "M17 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM21 21v-2a4 4 0 00-3-3.87",
                        "title": "Monorepo architecture",
                        "description": "Shared configs, assets and components across every site — one repo, one CI pipeline.",
                        "deliverables": ["Shared settings", "Shared assets", "Reusable libraries"],
                        "cta_label": "Browse the repo",
                        "cta_href": "/projects/",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "AI-powered tooling",
                        "description": "ceptor-ai MCP server for agent communication, code generation, and prompt-to-design conversion.",
                        "deliverables": ["MCP server", "AI chat client", "Agent scaffolding"],
                        "cta_label": "Meet ceptor-ai",
                        "cta_href": "/products/",
                    },
                    {
                        "icon": "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20",
                        "title": "Open-source first",
                        "description": "django-fusion, ceptor-ai and django-bolt are public on GitHub under permissive licenses.",
                        "deliverables": ["Public libraries", "Contribution guides", "Semver releases"],
                        "cta_label": "Contribute",
                        "cta_href": "https://github.com/mammhoud",
                    },
                ],
            },
        )
    ],
    "process": [
        (
            "process",
            {
                "eyebrow": "Build as you go",
                "title": "From brief to shipped, in four steps",
                "description": (
                    "No big-bang rewrite. We ship incrementally — each step "
                    "delivers working HTML you can put in front of users."
                ),
                "steps": [
                    {
                        "title": "Discover",
                        "description": "We map the content, the routes, and the one thing each page must do.",
                        "deliverable": "Content + route map",
                    },
                    {
                        "title": "Design",
                        "description": "Tokens first — type, color, spacing — then the page as a component tree.",
                        "deliverable": "Fusion token set",
                    },
                    {
                        "title": "Build",
                        "description": "Wagtail models + block templates render finished HTML on day one.",
                        "deliverable": "Live server-rendered pages",
                    },
                    {
                        "title": "Ship & grow",
                        "description": "Deploy behind the proxy, then add fragments, analytics and content editing.",
                        "deliverable": "Production site + CMS",
                    },
                ],
            },
        )
    ],
}


# Blog posts — the “Insights” grid on the Blog page (mirrors the repo's 18-post
# count loosely; the grid is editor-driven so more posts can be added anytime).
# Each post ALSO becomes a BlogPostPage child (see handle()) so grid cards link
# to live /blog/<slug>/ detail pages — slugs here must match those pages.
DEFAULT_BLOG_POSTS = [
    {
        "title": "Why we ship landing pages as documents",
        "slug": "why-landing-pages-as-documents",
        "category": "Architecture",
        "date": "2026-07-28",
        "read_time": "6 min read",
        "excerpt": "Every page is finished HTML in one response. No SPA shell, no hydration waterfall — just the web as it should be.",
    },
    {
        "title": "HTMX fragments vs. JSON APIs",
        "slug": "htmx-fragments-vs-json-apis",
        "category": "HTMX",
        "date": "2026-07-14",
        "read_time": "5 min read",
        "excerpt": "Streaming HTML from Django removes the decoder, the API contract, and half the frontend state.",
    },
    {
        "title": "Wagtail StreamField for marketing sites",
        "slug": "wagtail-streamfield-marketing",
        "category": "Wagtail",
        "date": "2026-06-30",
        "read_time": "8 min read",
        "excerpt": "Section blocks give editors composition superpowers without handing them a page builder.",
    },
    {
        "title": "Alpine.js is all the reactivity a landing page needs",
        "slug": "alpine-reactivity-landing",
        "category": "Frontend",
        "date": "2026-06-12",
        "read_time": "4 min read",
        "excerpt": "Accordions, toggles, counters — a few x-data attributes instead of a framework.",
    },
    {
        "title": "A monorepo that ships six products",
        "slug": "monorepo-six-products",
        "category": "Monorepo",
        "date": "2026-05-20",
        "read_time": "7 min read",
        "excerpt": "Shared configs, assets and libraries across Django sites, an Astro frontend, and a desktop POS.",
    },
    {
        "title": "Server time, streamed: a tiny HTMX fragment",
        "slug": "server-time-streamed-htmx",
        "category": "HTMX",
        "date": "2026-05-04",
        "read_time": "3 min read",
        "excerpt": "The smallest useful fragment endpoint, and why /fragment/ping/ proves the whole pipeline.",
    },
]


DEFAULT_BLOG_SECTION = {
    "blog": [
        (
            "blog",
            {
                "eyebrow": "Insights",
                "title": "From the blog",
                "description": (
                    "Notes on the AHA stack, Wagtail, HTMX, and shipping "
                    "server-rendered sites that stay fast."
                ),
                "posts": DEFAULT_BLOG_POSTS,
            },
        )
    ],
}


# Full body content for each seeded post — rendered on the /blog/<slug>/
# detail pages (BlogPostPage children of the Blog index). Keys match the
# ``slug`` values in DEFAULT_BLOG_SECTION so grid cards link to live pages.
DEFAULT_BLOG_POST_BODIES = {
    "why-landing-pages-as-documents": (
        "<p>When we rebuilt the structa.cloud landing pages, the first "
        "decision was the rendering model. The old stack shipped a heavy "
        "React SPA: a shell, a hydration step, and a JSON API feeding it. "
        "The browser waited through all three before a user saw text.</p>"
        "<h2>The document model</h2>"
        "<p>We switched to the AHA stack — Astro, HTMX, Alpine. Every page is "
        "finished HTML in one response. The server composes the document from "
        "Wagtail StreamField blocks; the browser just paints it.</p>"
        "<p>The difference is measurable: first paint dropped from seconds to "
        "tens of milliseconds, and SEO tools stopped complaining about empty "
        "shells. A page is a document again, not an application bootstrap.</p>"
        "<h2>What we kept</h2>"
        "<ul><li>HTMX fragments for the rare dynamic region</li>"
        "<li>Alpine.js for micro-interactions — accordions, toggles, counters</li>"
        "<li>Wagtail as the single source of content truth</li></ul>"
        "<p>No SPA shell, no hydration waterfall — just the web as it should "
        "be.</p>"
    ),
    "htmx-fragments-vs-json-apis": (
        "<p>Every interactive region on a marketing site is a trade: fetch "
        "JSON and render it client-side, or fetch HTML and let the server do "
        "the rendering. HTMX picks the second, and it is the right default "
        "for content sites.</p>"
        "<h2>The API contract tax</h2>"
        "<p>JSON APIs force you to maintain a schema, a serializer, and a "
        "client-side renderer that all agree. Add a field and you touch three "
        "files. Streaming HTML removes the decoder entirely — the response is "
        "the UI.</p>"
        "<h2>Where it shines</h2>"
        "<p>Our contact form, newsletter subscribe, and server-time demo all "
        "swap small HTML fragments into place. The Django view returns a "
        "finished fragment; HTMX does the swap. There is no frontend state to "
        "desync.</p>"
        "<p>Half the frontend state we used to maintain simply no longer "
        "exists.</p>"
    ),
    "wagtail-streamfield-marketing": (
        "<p>Marketing sites live and die by iteration speed. A page builder "
        "gives editors speed but fights developers; hand-rolled templates give "
        "developers control but bottleneck editors. StreamField sits in the "
        "middle.</p>"
        "<h2>Sections, not pages</h2>"
        "<p>Each section of a landing page is a StructBlock with its own "
        "Django template. Editors compose and reorder sections; developers own "
        "the templates. Nobody needs a drag-drop page builder.</p>"
        "<p>The result is composition superpowers without the complexity: "
        "hero, stats, features, testimonials, pricing, FAQ — each a block, "
        "each rendered server-side, each editable in the Wagtail admin.</p>"
        "<h2>Why it scales</h2>"
        "<p>Blocks are plain Python classes with plain Django templates. New "
        "sections ship in a day, and the API serializer and server renderer "
        "pick them up automatically from the same field list.</p>"
    ),
    "alpine-reactivity-landing": (
        "<p>Landing pages need a little reactivity — an accordion, a theme "
        "toggle, a count-up on scroll. They do not need a framework's "
        "reconciliation engine.</p>"
        "<h2>A few x-data attributes</h2>"
        "<p>Alpine.js adds declarative behavior with plain HTML attributes. "
        "Our FAQ accordion is an <code>x-data</code> directive and a couple "
        "of <code>x-show</code> toggles. The contact modal is the same shape. "
        "There is no component tree to mount.</p>"
        "<h2>The AHA promise</h2>"
        "<p>Astro renders the document, HTMX swaps fragments, Alpine hydrates "
        "micro-interactions. Each tool does one job and stays out of the "
        "critical path. Accordions, toggles, counters — a few x-data "
        "attributes instead of a framework.</p>"
    ),
    "monorepo-six-products": (
        "<p>Six projects, one repository, one CI pipeline. The structa.cloud "
        "monorepo holds Django sites, an Astro frontend, a desktop POS, and "
        "the libraries that bind them.</p>"
        "<h2>Shared everything</h2>"
        "<p>Configs, assets, and component templates live once under "
        "<code>projects/</code>. Sites pick from them instead of copying. A "
        "fix in django-fusion propagates to every site in one commit.</p>"
        "<h2>The cost</h2>"
        "<p>Monorepos trade isolation for consistency. We pay it down with a "
        "strict Makefile dispatcher and per-site tests, so a change to shared "
        "code is validated against every consumer before it lands.</p>"
        "<p>For a small team shipping products that share a stack, the "
        "trade is worth it.</p>"
    ),
    "server-time-streamed-htmx": (
        "<p>The smallest useful fragment endpoint proves the whole pipeline: "
        "a button, an HTMX attribute, and a Django view that returns the "
        "server time as an HTML fragment.</p>"
        "<h2>The endpoint</h2>"
        "<p><code>/fragment/ping/</code> renders the current timestamp into a "
        "small <code>div</code>. A request with the <code>HX-Request</code> "
        "header swaps it into the page — no JSON, no re-render of the "
        "document, no client state.</p>"
        "<h2>Why it matters</h2>"
        "<p>If a five-line fragment endpoint works end to end, the heavier "
        "regions — contact forms, newsletter signup, product filters — ride "
        "the same rails. The demo is trivial; the architecture it proves is "
        "not.</p>"
    ),
}


# ── Product pages ───────────────────────────────────────────────────
# One ProductPage per product, created as children of the Products page so
# /products/ lists them (get_product_cards) and each gets /products/<slug>/.
# Each page is a reference document: overview + tech stack + editions with
# per-edition pricing + reference snippets/models other projects can copy
# (e.g. LMS reusing Forge POS patterns).

DEFAULT_PRODUCT_PAGES = {
    "forge-pos": {
        "title": "Forge POS",
        "tagline": "Desktop point-of-sale in three editions — Minimal, Solo, Full.",
        "hero": [
            (
                "hero",
                {
                    "title": "Forge POS",
                    "subtitle": "A desktop point-of-sale application in three editions — Tauri 2 + Rust core, React/Vite shell, SQLite storage.",
                    "primary_cta": {"label": "See the editions", "href": "/products/forge-pos/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "View the repo", "href": "https://github.com/mammhoud/forge-pos", "style": "white"},
                    "trusted_by": "Minimal · Solo · Full — one codebase, three ships",
                },
            )
        ],
        "body": (
            "<p>Forge POS is a desktop point-of-sale application built on "
            "Tauri 2 + Rust with a React/Vite frontend and SQLite storage.</p>"
            "<p>It ships in three editions that share one codebase: Minimal "
            "(bare-bones Tauri + Rust + SQLite), Solo (embedded Python "
            "sidecar), and Full (multi-terminal with an external sidecar and "
            "cloud CRM).</p>"
        ),
        "tech": [
            ("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Rust", "Tauri 2", "React", "TypeScript", "SQLite", "Diesel"]}),
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Three editions, one codebase",
                    "description": "Every edition shares the Tauri + Rust core. Upgrade as your terminal grows.",
                    "editions": [
                        {
                            "name": "Minimal",
                            "tagline": "Bare-bones Tauri + Rust + SQLite for a single terminal.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Tauri 2 + Rust core", "SQLite storage", "Sales + receipting", "Local dashboard"],
                            "cta_label": "Download",
                            "cta_href": "https://github.com/mammhoud/forge-pos",
                            "featured": False,
                        },
                        {
                            "name": "Solo",
                            "tagline": "Standalone terminal with an embedded Python sidecar.",
                            "price": "$49",
                            "period": "/one-time",
                            "features": ["Everything in Minimal", "Embedded Python sidecar", "Inventory tracking", "Sales analytics", "Receipt branding"],
                            "cta_label": "Buy Solo",
                            "cta_href": "/contact/",
                            "featured": True,
                        },
                        {
                            "name": "Full",
                            "tagline": "Multi-terminal with external sidecar + cloud CRM.",
                            "price": "$99",
                            "period": "/month",
                            "features": ["Everything in Solo", "Multi-terminal sync", "External sidecar", "Cloud CRM", "Employee scheduling", "Kitchen display", "Time-bucketed KPIs"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                        },
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "eyebrow": "Reference",
                    "title": "Models & snippets you can reuse",
                    "description": "The core schema and entrypoint — the same patterns LMS and other projects borrow.",
                    "snippets": [
                        {
                            "title": "SQLite schema (Diesel up.sql)",
                            "language": "sql",
                            "code": "CREATE TABLE sales (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  terminal_id TEXT NOT NULL,\n  total_cents INTEGER NOT NULL,\n  payment_method TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);\n\nCREATE TABLE sale_items (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  product_id TEXT NOT NULL,\n  quantity INTEGER NOT NULL,\n  unit_cents INTEGER NOT NULL\n);",
                        },
                        {
                            "title": "Rust model (src-tauri/src/db/models.rs)",
                            "language": "rust",
                            "code": "#[derive(Queryable, Insertable, Serialize)]\n#[diesel(table_name = crate::db::schema::sales)]\npub struct Sale {\n    pub id: i32,\n    pub terminal_id: String,\n    pub total_cents: i32,\n    pub payment_method: String,\n    pub created_at: String,\n}",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "eyebrow": "Capabilities",
                    "title": "What Forge POS ships",
                    "description": "The features that move a terminal from a cash register to a business tool.",
                    "features": [
                        {"icon": "M4 7v10c0 2.2 1.8 4 4 4h8c2.2 0 4-1.8 4-4V7M4 7h16M4 7l2-3h12l2 3", "title": "Fast, native checkout", "description": "A Rust core keeps every keystroke instant — no web latency on the counter."},
                        {"icon": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.6a2 2 0 011.4.6l4.4 4.4a2 2 0 01.6 1.4V19a2 2 0 01-2 2z", "title": "SQLite by default", "description": "Zero-config local storage that scales up to a synced multi-terminal setup in Full."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Three editions", "description": "Minimal, Solo, Full — one codebase, feature-gated per edition."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "eyebrow": "FAQ",
                    "title": "Forge POS questions",
                    "items": [
                        {"question": "Which edition should I start with?", "answer": "Minimal is open source and perfect for a single terminal. Upgrade to Solo for inventory + analytics, or Full for multi-terminal + cloud CRM."},
                        {"question": "Can I reuse the schema in another project?", "answer": "Yes — the SQLite schema and Rust models are public reference material under the repo's license."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Run a terminal in minutes",
                    "subtitle": "Clone the repo, run the Minimal edition, and upgrade editions as you grow.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/forge-pos", "style": "white"},
                    "secondary_cta": {"label": "Get in Touch", "href": "/contact/", "style": "outline"},
                },
            )
        ],
    },
    "lms": {
        "title": "Fusion LMS",
        "tagline": "The learning platform behind structa.cloud — courses, enrollments, payments.",
        "hero": [
            (
                "hero",
                {
                    "title": "Fusion LMS",
                    "subtitle": "A content-driven learning platform built on Django + django-fusion with a Next.js frontend.",
                    "primary_cta": {"label": "See the editions", "href": "/products/lms/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "Learn more", "href": "/about/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Fusion LMS powers the Structa Cloud learning platform — courses, "
            "enrollments, payments (Stripe), and progress tracking, all served "
            "by Django/Wagtail with django-fusion's component pipeline.</p>"
            "<p>Its frontend is a Next.js app consuming django-fusion APIs and "
            "server-rendered fragments — the same content-driven pattern the "
            "landing CMS uses.</p>"
        ),
        "tech": [
            ("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Django", "Wagtail", "django-fusion", "Next.js", "React", "Stripe"]}),
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Scale from one course to a cohort",
                    "editions": [
                        {
                            "name": "Starter",
                            "tagline": "For solo creators publishing their first course.",
                            "price": "$0",
                            "period": "/forever",
                            "features": ["Up to 3 courses", "Community support", "Basic progress tracking", "Public profile"],
                            "cta_label": "Start Free",
                            "cta_href": "/#cta",
                            "featured": False,
                        },
                        {
                            "name": "Pro",
                            "tagline": "For active creators and small academies.",
                            "price": "$29",
                            "period": "/per month",
                            "features": ["Unlimited courses", "Priority support", "Advanced analytics", "Offline downloads", "Certificates"],
                            "cta_label": "Go Pro",
                            "cta_href": "/#cta",
                            "featured": True,
                        },
                        {
                            "name": "Team",
                            "tagline": "For organizations with cohorts and staff.",
                            "price": "$99",
                            "period": "/per month",
                            "features": ["Everything in Pro", "SSO & role management", "Dedicated success manager", "Custom branding", "API access"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                        },
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "eyebrow": "Reference",
                    "title": "Content-driven models & snippets",
                    "description": "How the LMS models content — the pattern the CMS site builder generalizes.",
                    "snippets": [
                        {
                            "title": "Wagtail course page",
                            "language": "python",
                            "code": "class CoursePage(Page):\n    title = models.CharField(max_length=255)\n    description = RichTextField(blank=True)\n    price_cents = models.IntegerField(default=0)\n    curriculum = StreamField([\n        ('lesson', LessonBlock()),\n        ('quiz', QuizBlock()),\n    ], use_json_field=True)\n\n    content_panels = Page.content_panels + [\n        FieldPanel('description'),\n        FieldPanel('price_cents'),\n        FieldPanel('curriculum'),\n    ]",
                        },
                        {
                            "title": "Enrollment (django-fusion)",
                            "language": "python",
                            "code": "from django_fusion.routes import ModelViewset\n\nclass EnrollmentViewset(ModelViewset):\n    model = Enrollment\n    fields = ['id', 'course', 'user', 'progress', 'completed_at']",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "eyebrow": "Capabilities",
                    "title": "What Fusion LMS ships",
                    "features": [
                        {"icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z", "title": "Content-driven courses", "description": "Lessons, quizzes and certificates composed in Wagtail StreamFields."},
                        {"icon": "M3 3v18h18M7 15l4-4 3 3 5-6", "title": "Payments built in", "description": "Stripe checkout for courses, enrollments, and subscriptions."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Fragment-rendered UI", "description": "django-fusion HTMX fragments keep the app server-rendered and fast."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "eyebrow": "FAQ",
                    "title": "Fusion LMS questions",
                    "items": [
                        {"question": "How does this relate to the landing CMS?", "answer": "LMS and CMS share django-fusion. The CMS is the content-driven website builder; LMS is its highest-value use case."},
                        {"question": "Can I embed LMS on my own site?", "answer": "Yes — courses and progress are served as server-rendered fragments that any Fusion site can embed."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Teach on the AHA stack",
                    "subtitle": "From one course to a full academy — content-driven, payment-enabled, server-rendered.",
                    "primary_cta": {"label": "See pricing", "href": "/products/lms/#editions", "style": "white"},
                    "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"},
                },
            )
        ],
    },
    "cms": {
        "title": "Fusion CMS",
        "tagline": "Build content-driven websites from Wagtail blocks — this very site is built with it.",
        "hero": [
            (
                "hero",
                {
                    "title": "Fusion CMS",
                    "subtitle": "A content-driven website builder — Wagtail StreamFields composed into server-rendered pages by django-fusion.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cms/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "Explore the stack", "href": "/features/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Fusion CMS is the content-driven website builder behind every "
            "structa.cloud landing page. Editors compose Wagtail StreamField "
            "blocks; django-fusion renders them as finished server-side HTML.</p>"
            "<p>It powers both render roads — Django's fusion-render HTML and the "
            "Astro frontend's data APIs — from one source of content.</p>"
        ),
        "tech": [
            ("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Wagtail", "Django", "django-fusion", "HTMX", "Alpine.js", "Astro"]}),
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "From one page to a whole site",
                    "editions": [
                        {
                            "name": "Basic",
                            "tagline": "A single landing page with the core section blocks.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Wagtail StreamField blocks", "django-fusion rendering", "HTMX fragments", "MIT license"],
                            "cta_label": "Self-host",
                            "cta_href": "https://github.com/mammhoud/django-fusion",
                            "featured": False,
                        },
                        {
                            "name": "Pro",
                            "tagline": "A full marketing site with custom blocks + analytics.",
                            "price": "$149",
                            "period": "/project",
                            "features": ["Everything in Basic", "Custom StreamField blocks", "Blog + FAQ sections", "Analytics + SEO", "HTMX forms"],
                            "cta_label": "Get Started",
                            "cta_href": "/contact/",
                            "featured": True,
                        },
                        {
                            "name": "Enterprise",
                            "tagline": "Multi-site, multi-editor, fully managed.",
                            "price": "Custom",
                            "period": "",
                            "features": ["Everything in Pro", "Multi-site + roles", "Design system tokens", "Dedicated support", "SLAs"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                        },
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "eyebrow": "Reference",
                    "title": "Blocks & snippets you can reuse",
                    "description": "The building blocks that make a site content-driven — copy them into any Fusion project.",
                    "snippets": [
                        {
                            "title": "A StreamField section block",
                            "language": "python",
                            "code": "class HeroBlock(blocks.StructBlock):\n    badge = blocks.CharBlock(max_length=80, required=False)\n    title = blocks.CharBlock(max_length=200)\n    subtitle = blocks.TextBlock(required=False)\n    primary_cta = ButtonBlock(required=False)\n\n    class Meta:\n        template = 'content/blocks/hero.html'\n        label = 'Hero'\n",
                        },
                        {
                            "title": "Server-rendered fragment",
                            "language": "html",
                            "code": "<section class=\"container-fusion py-20 text-center\">\n  <h1 class=\"text-4xl font-bold sm:text-6xl\">{{ value.title }}</h1>\n  {% if value.subtitle %}<p class=\"mx-auto mt-6 max-w-2xl text-lg text-fu-muted\">{{ value.subtitle }}</p>{% endif %}\n</section>",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "eyebrow": "Capabilities",
                    "title": "What Fusion CMS ships",
                    "features": [
                        {"icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z", "title": "Block-based editing", "description": "Editors compose sections; developers own the templates."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Two render roads", "description": "Fusion-render HTML and data APIs from one Wagtail source of truth."},
                        {"icon": "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20", "title": "Open source", "description": "django-fusion is public on GitHub under a permissive license."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "eyebrow": "FAQ",
                    "title": "Fusion CMS questions",
                    "items": [
                        {"question": "Is this the same CMS that runs this site?", "answer": "Yes — every page you're reading is composed from these StreamField blocks and rendered by django-fusion."},
                        {"question": "Can I add my own blocks?", "answer": "Absolutely. Blocks are plain Wagtail StructBlocks with Django templates — no framework lock-in."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Ships as HTML, edits as blocks",
                    "subtitle": "The CMS is open source. Clone it, add your blocks, ship your site.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/django-fusion", "style": "white"},
                    "secondary_cta": {"label": "Read the Docs", "href": "/about/", "style": "outline"},
                },
            )
        ],
    },
    "cypercloud": {
        "title": "Cypercloud",
        "tagline": "AI chat customizer — embed ceptor-ai powered chat into any site.",
        "hero": [
            (
                "hero",
                {
                    "title": "Cypercloud",
                    "subtitle": "An AI chat customizer platform — ceptor-ai powered chat embedded into customer sites.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cypercloud/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "About ceptor-ai", "href": "/products/ceptor-ai/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Cypercloud lets you embed intelligent chat into customer sites with "
            "full customization — branding, behavior, and model selection.</p>"
            "<p>It is powered by ceptor-ai (the MCP server + chat client library) "
            "and ships as an embeddable widget.</p>"
        ),
        "tech": [("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Python", "Django", "ceptor-ai", "MCP"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Free to embed, paid to customize",
                    "editions": [
                        {"name": "Free", "tagline": "The open-source chat client, self-hosted.", "price": "$0", "period": "/open source", "features": ["ceptor-ai chat client", "MCP server", "Multi-model support"], "cta_label": "Self-host", "cta_href": "https://github.com/mammhoud/ceptor-ai", "featured": False},
                        {"name": "Pro", "tagline": "Managed chat with full branding.", "price": "$39", "period": "/per month", "features": ["Everything in Free", "Branded widget", "Behavior rules", "Analytics"], "cta_label": "Get Started", "cta_href": "/contact/", "featured": True},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Chat that looks like your brand", "subtitle": "Embed ceptor-ai chat in an afternoon.", "primary_cta": {"label": "Get Started", "href": "/contact/", "style": "white"}, "secondary_cta": {"label": "See the library", "href": "/products/ceptor-ai/", "style": "outline"}})],
    },
    "vresume": {
        "title": "vResume",
        "tagline": "Cloud resume platform — create, update, publish professional resumes.",
        "hero": [
            (
                "hero",
                {
                    "title": "vResume",
                    "subtitle": "A cloud-hosted resume builder with modern templates, custom domains, and CI/CD deployments.",
                    "primary_cta": {"label": "Launch vResume", "href": "https://vresume.structa.cloud", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/vresume/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>vResume lets you create, update, and publish professional resumes "
            "with modern templates — cloud-hosted at vresume.structa.cloud.</p>"
            "<p>Custom domains and a CI/CD pipeline make it a production showcase "
            "of the monorepo's deploy tooling.</p>"
        ),
        "tech": [("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Django", "Wagtail", "Next.js", "Cloud", "CI/CD"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "From one resume to a hosted portfolio",
                    "editions": [
                        {"name": "Free", "tagline": "One resume with the default template.", "price": "$0", "period": "/forever", "features": ["Modern resume templates", "Live preview", "PDF export"], "cta_label": "Try it", "cta_href": "https://vresume.structa.cloud", "featured": False},
                        {"name": "Pro", "tagline": "Custom domain + multiple resumes.", "price": "$9", "period": "/per month", "features": ["Everything in Free", "Custom domain", "Multiple resumes", "Analytics"], "cta_label": "Upgrade", "cta_href": "/contact/", "featured": True},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Your career, published", "subtitle": "Build a resume that ships like a product.", "primary_cta": {"label": "Launch vResume", "href": "https://vresume.structa.cloud", "style": "white"}, "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"}})],
    },
    "django-bolt": {
        "title": "django-bolt",
        "tagline": "High-performance Rust-backed API framework for Django.",
        "hero": [
            (
                "hero",
                {
                    "title": "django-bolt",
                    "subtitle": "A high-performance Rust-backed API framework that integrates with Django models.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/dj-bolt/django-bolt", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/django-bolt/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>django-bolt is a Rust-backed API framework (BoltAPI) for Django — "
            "fast, concurrent request handling while keeping Django ORM "
            "compatibility.</p>"
        ),
        "tech": [("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Rust", "Python", "Django", "API"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "One library, one license",
                    "editions": [
                        {"name": "Open Source", "tagline": "The full BoltAPI framework.", "price": "$0", "period": "/MIT", "features": ["Rust-powered API framework", "Django ORM compatibility", "Performance-optimized serialization"], "cta_label": "View on GitHub", "cta_href": "https://github.com/dj-bolt/django-bolt", "featured": True},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Fast APIs, Django models", "subtitle": "Drop BoltAPI into any Django project.", "primary_cta": {"label": "View on GitHub", "href": "https://github.com/dj-bolt/django-bolt", "style": "white"}, "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"}})],
    },
    "ceptor-ai": {
        "title": "ceptor-ai",
        "tagline": "AI chat client + MCP server — agent communication and generation.",
        "hero": [
            (
                "hero",
                {
                    "title": "ceptor-ai",
                    "subtitle": "An AI chat client with a Model Context Protocol (MCP) server — powers Cypercloud and agent tooling.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/ceptor-ai/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>ceptor-ai is the AI layer of the monorepo — an MCP server for agent "
            "communication, a chat client with multi-model support, and a BEM "
            "converter for prompt-to-component generation.</p>"
        ),
        "tech": [("tech", {"eyebrow": "Stack", "title": "Built on", "items": ["Python", "MCP", "AI/ML", "Node.js"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "One library, one license",
                    "editions": [
                        {"name": "Open Source", "tagline": "The full MCP server + chat client.", "price": "$0", "period": "/MIT", "features": ["MCP server", "Chat client", "BEM converter", "Agent generation"], "cta_label": "View on GitHub", "cta_href": "https://github.com/mammhoud/ceptor-ai", "featured": True},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Agents that talk to your tools", "subtitle": "ceptor-ai connects LLMs to anything via MCP.", "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "white"}, "secondary_cta": {"label": "See Cypercloud", "href": "/products/cypercloud/", "style": "outline"}})],
    },
}


DEFAULT_HOME_CONTENT = {
    "hero": [
        (
            "hero",
            {
                "badge": "structa.cloud · full-stack engineering",
                # NB: the Astro Hero component renders ``title`` + ``accent``
                # separately, so the accent word ("documents") is NOT part of
                # the stored title. Keep titles free of the accent phrase.
                "title": "Platforms that ship as",
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

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Overwrite existing content fields with seed values "
                "(default: only backfill empty fields, preserving edits)."
            ),
        )

    def handle(self, *args, **options):
        self.force = options.get("force", False)
        self.stdout.write("Seeding landing pages…")

        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stdout.write(self.style.ERROR("No root page — run migrations first."))
            return

        landing_models = {
            HomePage,
            AboutPage,
            ServicesPage,
            ProductsPage,
            FeaturesPage,
            ProjectsPage,
            BlogPage,
            PricingPage,
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
                        # "Mahmoud Ezzat" + Astro accent "Moustafa" → clean H1.
                        "title": "Mahmoud Ezzat",
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
                "<p>Fusion CMS is built by a small team that believes the web "
                "should be fast by default. Our mission is to give every team a "
                "landing stack that ships as plain HTML — no heavy SPA, no "
                "maintenance treadmill. We value performance, simplicity, and "
                "boring technology that keeps working.</p>"
            ),
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "about")

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
                        "subtitle": "Server-rendered sites, HTMX integrations, and Alpine-powered UX — built as you go.",
                        "primary_cta": {"label": "Our Products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "white"},
                        "trusted_by": "From brief to shipped in four steps — each one delivers working HTML",
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
            **DEFAULT_SERVICES_SECTIONS,
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
                        # + Astro accent "open source"
                        "title": "Everything we build, shipped as",
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
            **DEFAULT_PROJECTS,
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "products")

        # ── Product pages (children of Products) ─────────────────────────
        # Each is a reference document with editions & pricing + snippets.
        for slug, product in DEFAULT_PRODUCT_PAGES.items():
            product_page, created = self._get_or_create_child(
                products,
                ProductPage,
                slug=slug,
                title=product["title"],
                tagline=product.get("tagline", ""),
                hero=product.get("hero", []),
                body=product.get("body", ""),
                tech=product.get("tech", []),
                editions=product.get("editions", []),
                snippets=product.get("snippets", []),
                features=product.get("features", []),
                faq=product.get("faq", []),
                cta=product.get("cta", []),
            )
            self._created(created, f"product:{slug}")

        # ── Blog (index grid, mirror of the frontend /blog) ───────────────
        blog, created = self._get_or_create_child(
            home,
            BlogPage,
            title="Blog",
            slug="blog",
            hero=[
                (
                    "hero",
                    {
                        "title": "The Blog",
                        "subtitle": "Notes on the AHA stack — Astro, HTMX, Alpine — and shipping server-rendered sites.",
                        "primary_cta": {"label": "Explore Projects", "href": "/projects/", "style": "secondary"},
                        "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            **DEFAULT_BLOG_SECTION,
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "blog")

        # ── Blog post pages (children of Blog — each has /blog/<slug>/) ────
        # One BlogPostPage per seeded post: same slug as the grid card so the
        # links resolve, plus real body content for the detail page.
        for post in DEFAULT_BLOG_POSTS:
            slug = post.get("slug")
            if not slug:
                continue
            post_page, post_created = self._get_or_create_child(
                blog,
                BlogPostPage,
                slug=slug,
                title=post.get("title", ""),
                category=post.get("category", ""),
                post_date=post.get("date") or None,
                read_time=post.get("read_time", ""),
                excerpt=post.get("excerpt", ""),
                body=DEFAULT_BLOG_POST_BODIES.get(slug, ""),
                hero=[
                    (
                        "hero",
                        {
                            "title": post.get("title", ""),
                            "subtitle": post.get("excerpt", ""),
                            "primary_cta": {"label": "Back to Blog", "href": "/blog/", "style": "secondary"},
                            "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "white"},
                        },
                    )
                ],
                cta=DEFAULT_HOME_CONTENT["cta"],
            )
            self._created(post_created, f"blog-post:{slug}")

        # ── Pricing (dedicated page with its own tiers + faq) ─────────────
        pricing, created = self._get_or_create_child(
            home,
            PricingPage,
            title="Pricing",
            slug="pricing",
            hero=[
                (
                    "hero",
                    {
                        "title": "Pricing",
                        "subtitle": "Simple, transparent pricing — start free and scale as you grow.",
                        "primary_cta": {"label": "Start Free", "href": "/#cta", "style": "secondary"},
                        "secondary_cta": {"label": "Contact Sales", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            pricing=DEFAULT_ABOUT_SECTIONS["pricing"],
            faq=DEFAULT_ABOUT_SECTIONS["faq"],
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "pricing")

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
                        # + Astro accent "documents"
                        "title": "Built to ship as",
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
                        # + Astro accent "one monorepo"
                        "title": "Everything we build, shipped as",
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
        """Apply seed values to an existing page's content fields.

        Without ``--force`` only *empty* fields are set (editor changes to
        non-empty fields are preserved and content added by later migrations
        is backfilled). With ``--force`` every content field is overwritten,
        refreshing pages that hold content from an older seed revision.
        """
        changed = False
        for name, value in fields.items():
            if name in ("title", "slug"):
                continue
            current = getattr(existing, name, None)
            # StreamFields/RichTextFields are falsy when empty.
            if self.force or (not current and value):
                setattr(existing, name, value)
                changed = True
        if changed:
            existing.save()

    def _created(self, created, label):
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created {label} page."))
        else:
            self.stdout.write(f"{label} page already exists.")
