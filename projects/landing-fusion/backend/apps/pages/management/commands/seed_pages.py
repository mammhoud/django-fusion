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
import os

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.pages.models import (
    AboutPage,
    BlogPage,
    BlogPostPage,
    BrandPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    FounderPage,
    HomePage,
    PricingPage,
    PrivacyPage,
    ProductPage,
    ProductsPage,
    ServicesPage,
    StartupPage,
    PhasePage,
    PromptPage,
    TeamPage,
)
from apps.content.models.translations import PageTranslation

# Bilingual overlays are deliberately partial: untranslated fields continue to
# use the canonical Wagtail content through the API fallback contract.
DEFAULT_PAGE_TRANSLATIONS = {
    "home": {
        "title": "الرئيسية",
        "search_description": "منتجات رقمية هادئة وسريعة للفرق التي تخدم أسواق الخليج والمشرق وشمال أفريقيا.",
        "content": {
            "hero": {"title": "منتجات رقمية تنمو مع", "accent": "السوق", "subtitle": "نساعد الفرق على إطلاق تجارب عربية وإنجليزية واضحة، سريعة، وقابلة للتوسع."},
            "cta": {"title": "ابدأ من احتياج حقيقي", "subtitle": "نحوّل الفكرة أو النظام الحالي إلى تجربة عملية يمكن لفريقك امتلاكها."},
        },
    },
    "about": {
        "title": "من نحن",
        "search_description": "شريك منتج للفرق التي تبني خدمات رقمية في أسواق الخليج والمشرق وشمال أفريقيا.",
        "body": "<p>Structa Cloud استوديو منتجات يساعد الفرق على تحويل الأفكار والأنظمة القديمة إلى خدمات رقمية واضحة وقابلة للاستخدام.</p><p>نصمم تجارب عربية وإنجليزية، ونبدأ من رحلة العميل قبل اختيار التقنية. النتيجة منصة سريعة يستطيع فريقك إدارتها بعد الإطلاق.</p>",
        "content": {"hero": {"title": "شريكك في المنتج الرقمي", "subtitle": "نربط الاستراتيجية والتصميم والهندسة في مسار واحد من الفكرة إلى السوق."}, "cta": {"title": "لنصمم الخطوة التالية", "subtitle": "أخبرنا عن السوق والعميل والقيود، وسنقترح مساراً عملياً."}},
    },
    "services": {
        "title": "الخدمات",
        "body": "<p>نبني مواقع ومنتجات تساعد فرق التسويق والعمليات على خدمة العملاء في المنطقة بثقة.</p>",
        "content": {"hero": {"title": "من الفكرة إلى السوق", "subtitle": "نصمم ونبني ونحسن تجارب رقمية سريعة، ثنائية اللغة، ومهيأة للنمو."}},
    },
    "products": {
        "title": "المنتجات",
        "body": "<p>منتجات عملية لنقاط البيع والتعلم والمحتوى والملفات المهنية، مصممة لتناسب إيقاع الفرق والأسواق المتنوعة.</p>",
        "content": {"hero": {"title": "منتجات جاهزة للنمو", "subtitle": "أدوات ومنصات تساعد فريقك على البيع والتعلم والنشر وخدمة العملاء."}},
    },
    "features": {
        "title": "الميزات",
        "body": "<p>نوازن بين سرعة التجربة ومرونة الإدارة: صفحات خفيفة، محتوى ثنائي اللغة، وتفاعلات صغيرة لا تعيق العميل.</p>",
        "content": {"hero": {"title": "سريع من أول زيارة", "subtitle": "نظام محتوى وتجربة مصمم للأداء، والوضوح، والعمل عبر العربية والإنجليزية."}},
    },
    "blog": {"title": "المدونة", "content": {"hero": {"title": "أفكار من واقع الإطلاق", "subtitle": "ملاحظات عملية عن المنتجات الرقمية، الأداء، والمحتوى الذي يخدم أسواق المنطقة."}}},
    "pricing": {"title": "الأسعار", "content": {"hero": {"title": "اختر المنتج، ثم الإصدار", "subtitle": "ابدأ مجاناً وتوسع عندما ينمو مشروعك."}}},
    "contact": {"title": "تواصل معنا", "content": {"hero": {"title": "لنتحدث", "subtitle": "أرسل رسالتك وسنعود إليك قريباً."}}},
    "faq": {"title": "الأسئلة الشائعة", "content": {"hero": {"title": "الأسئلة الشائعة", "subtitle": "إجابات واضحة حول المكدس والمنتجات والإصدارات."}}},
    "privacy": {"title": "الخصوصية", "content": {"hero": {"title": "سياسة الخصوصية", "subtitle": "نحافظ على جمع البيانات بالحد الأدنى."}}},
    "brand": {"title": "الهوية", "content": {"hero": {"title": "عائلة واحدة، علامات متعددة", "subtitle": "نظام الهوية البصري لمنتجات Structa Cloud."}}},
}

# Seeded language catalog — mirrors the Astro ``LANG_META`` table in
# frontend/src/lib/translations.ts. Each row becomes a ``SiteLanguage``
# Wagtail snippet (admin-editable), and ``GET /apis/content/languages/``
# serves the active rows to the frontend switcher. Keep this list in sync
# with ``LANG_META`` and Django's ``LANGUAGES`` setting.
DEFAULT_SITE_LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English", "direction": "ltr", "flag": "🇬🇧", "is_active": True, "sort_order": 0},
    {"code": "ar", "name": "Arabic", "native_name": "العربية", "direction": "rtl", "flag": "🇸🇦", "is_active": True, "sort_order": 10},
    {"code": "sv", "name": "Swedish", "native_name": "Svenska", "direction": "ltr", "flag": "🇸🇪", "is_active": True, "sort_order": 20},
    {"code": "fr", "name": "French", "native_name": "Français", "direction": "ltr", "flag": "🇫🇷", "is_active": True, "sort_order": 30},
    {"code": "de", "name": "German", "native_name": "Deutsch", "direction": "ltr", "flag": "🇩🇪", "is_active": True, "sort_order": 40},
    {"code": "es", "name": "Spanish", "native_name": "Español", "direction": "ltr", "flag": "🇪🇸", "is_active": True, "sort_order": 50},
    {"code": "pt", "name": "Portuguese", "native_name": "Português", "direction": "ltr", "flag": "🇧🇷", "is_active": True, "sort_order": 60},
]

# Services the project offers — the “feature” grid on the Services page.
# Three service lines: website building, product & project development, and
# enhancements — mirrors the frontend services page (cards + deliverables).
DEFAULT_SERVICES_SECTIONS = {
    "services": [
        (
            "services",
            {
                "title": "Build for the market you serve",
                "description": (
                    "A focused path from customer need to a dependable digital service. "
                    "We help teams across the Gulf, Levant, and North Africa launch "
                    "clear, bilingual experiences without unnecessary complexity."
                ),
                "services": [
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Market-ready websites",
                        "description": "Clear Arabic and English journeys for campaigns, services, and products. Editors can update content without waiting for a release.",
                        "deliverables": ["Bilingual page structure", "Editorial sections your team can own", "Fast first visits on mobile networks", "Hosting, domains + HTTPS setup"],
                        "cta_label": "See the stack",
                        "cta_href": "/features/",
                    },
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "Digital product delivery",
                        "description": "Customer portals, learning services, commerce tools, and internal workflows shaped around how your team actually operates.",
                        "deliverables": ["Journey mapping and product direction", "Web or desktop delivery", "Arabic and English-ready interfaces", "Cloud deployment and handover"],
                        "cta_label": "See our products",
                        "cta_href": "/products/",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "Improve what already works",
                        "description": "Make an existing service easier to use and faster to operate, without forcing a risky rewrite.",
                        "deliverables": ["Conversion and content review", "Performance budget and Core Web Vitals", "Safe content migration", "Team training and ongoing support"],
                        "cta_label": "Contact us",
                        "cta_href": "/contact/",
                    },
                ],
            },
        )
    ],
    "process": [
        (
            "process",
            {
                "title": "A measured path to launch",
                "description": (
                    "We keep the work visible and incremental. Each phase leaves your team "
                    "with a clearer decision, a working slice, or a useful handoff."
                ),
                "steps": [
                    {
                        "title": "Discover",
                        "description": "We map the customer, the offer, the languages, and the moments that need to work first.",
                        "deliverable": "Customer and route map",
                    },
                    {
                        "title": "Design",
                        "description": "We turn the direction into a calm interface with clear content hierarchy and a flexible visual system.",
                        "deliverable": "Approved experience direction",
                    },
                    {
                        "title": "Build",
                        "description": "We build the first useful slice, connect content, and test the critical path on real devices.",
                        "deliverable": "Working product slice",
                    },
                    {
                        "title": "Ship & grow",
                        "description": "We launch with a performance budget, an editor handoff, and a simple plan for the next market.",
                        "deliverable": "Live service + growth plan",
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
        "title": "A fast first visit is a product decision",
        "slug": "why-landing-pages-as-documents",
        "category": "Product",
        "date": "2026-07-28",
        "read_time": "6 min read",
        "excerpt": "Performance is part of trust. A clear page that arrives quickly gives customers more confidence before the first conversation.",
    },
    {
        "title": "Designing bilingual journeys without duplication",
        "slug": "htmx-fragments-vs-json-apis",
        "category": "Content",
        "date": "2026-07-14",
        "read_time": "5 min read",
        "excerpt": "A practical way to keep Arabic and English content aligned while letting each language sound natural.",
    },
    {
        "title": "Give content teams a useful control room",
        "slug": "wagtail-streamfield-marketing",
        "category": "Operations",
        "date": "2026-06-30",
        "read_time": "8 min read",
        "excerpt": "Good editorial structure helps marketing teams move quickly without turning every page into a design negotiation.",
    },
    {
        "title": "Small interactions, better focus",
        "slug": "alpine-reactivity-landing",
        "category": "Experience",
        "date": "2026-06-12",
        "read_time": "4 min read",
        "excerpt": "Use interaction where it clarifies a decision, not where it adds noise to a page that should simply help someone move forward.",
    },
    {
        "title": "Build a system your team can inherit",
        "slug": "monorepo-six-products",
        "category": "Delivery",
        "date": "2026-05-20",
        "read_time": "7 min read",
        "excerpt": "The best platform handoff is not a technical monument. It is a set of understandable decisions that people can safely extend.",
    },
    {
        "title": "A practical performance budget for launch",
        "slug": "server-time-streamed-htmx",
        "category": "Performance",
        "date": "2026-05-04",
        "read_time": "3 min read",
        "excerpt": "Reserve space for the content that matters, keep the critical path small, and measure the experience on real regional networks.",
    },
]


DEFAULT_BLOG_SECTION = {
    "blog": [
        (
            "blog",
            {
                "title": "Ideas for the next release",
                "description": (
                    "Practical notes on launching digital services, keeping first visits fast, "
                    "and giving content teams control after handover."
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
# (e.g. LMS reusing Formints patterns).

DEFAULT_PRODUCT_PAGES = {
    "formint-pos": {
        "title": "Formints",
        "logo_style": "crest",
        "category": "application",
        "tagline": "Desktop point-of-sale in four editions: Community, Standard, Pro, Cloud.",
        "hero": [
            (
                "hero",
                {
                    "title": "Formints",
                    "subtitle": "A desktop point-of-sale application with a Tauri 2 + Rust core, React/Vite shell, and SQLite storage.",
                    "primary_cta": {"label": "See the editions", "href": "/products/formint-pos/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "View the repo", "href": "https://github.com/mammhoud/formint-pos", "style": "white"},
                    "trusted_by": "Community · Standard · Pro · Cloud",
                },
            )
        ],
        "body": (
            "<p>Formints is a desktop point-of-sale application built on "
            "Tauri 2 + Rust with a React/Vite frontend and SQLite storage.</p>"
            "<p>It ships in four editions that share one codebase: Community "
            "(free, offline-first single terminal), Standard (standalone with "
            "an embedded Python sidecar + cloud sync), Pro (multi-terminal "
            "with a cloud master), and Cloud (fully hosted multi-terminal "
            "with managed cloud CRM).</p>"
        ),
        "tech": [
            ("tech", {"title": "Built on", "items": ["Rust", "Tauri 2", "React", "TypeScript", "SQLite", "Diesel"]}),
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
                            "tagline": "Free and open source. The offline-first POS for a single terminal.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Tauri 2 + Rust core (Diesel ORM)", "SQLite storage", "Sales, receipting + inventory", "Payment types: cash, card, split", "Offline-first mode", "Refunds & returns", "i18n: en, fr, ar"],
                            "cta_label": "Download",
                            "cta_href": "https://github.com/mammhoud/formint-pos",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Standard",
                            "tagline": "Standalone terminal for growing businesses: high-end design, food & beverage tools, and integrations.",
                            "price": "$119",
                            "period": "/one-time license",
                            "features": ["Everything in Community", "High-end interface design", "Inventory adjustments + stock control", "Food & beverage (F&B) menu support", "Kitchen display + payroll", "REST API for integrations", "Inventory + sales analytics", "Invoice PDF generation", "Loyalty & rewards program", "Multi-currency & tax profiles", "Custom roles & permissions", "Data export (CSV/JSON)", "Deployment & support quoted per site"],
                            "cta_label": "Buy Standard",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "default",
                        },
                        {        "name": "Pro",
        "tagline": "Multi-terminal with a cloud master, WebSocket streaming, and a high-throughput Rust API.",
        "price": "$79",
        "period": "/per year",
        "offer_label": "50% off · launch",
        "offer_old_price": "$158",
                            "features": ["Everything in Standard", "Multi-terminal sync (cloud master)", "High-throughput Rust API (60k+ RPS)", "WebSocket real-time streaming", "Product sync engine (master)", "Employee scheduling + KPIs", "Change signals + approvals", "Deployment & support fees apply"],
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
                            "features": ["Everything in Pro", "Hosted cloud CRM master", "Unlimited terminals", "Cross-device data sync", "Automatic cloud backups + monitoring", "Dedicated onboarding + support", "Contact us for a managed-cloud quote"],
                            "cta_label": "Talk to Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "managed",
                        },
                    ],
                },
            )
        ],
        "comparison": [
            (
                "comparison",
                {
                    "eyebrow": "Compare editions",
                    "title": "Community vs Standard vs Pro vs Cloud",
                    "description": "Every edition shares the Tauri + Rust core. Rows below show exactly what moves you up the ladder.",
                    "columns": ["Community", "Standard", "Pro", "Cloud"],
                    "rows": [
                        {"feature": "React 19 + TypeScript frontend", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Tauri 2 + Rust backend", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "SQLite database", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "i18n (en/fr/ar)", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "POS terminal + inventory + analytics", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Payment types (cash, card, split)", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Employees, payroll, scheduling", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "High-end interface design", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Inventory adjustments + stock control", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Food & beverage (F&B) menu support", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Kitchen display system", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "POS-KO Gaming Center", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Django Portal (admin UI)", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "REST API (35+ endpoints)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Invoice PDF generation", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Chat support widget", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "WebSocket real-time streaming", "cells": ["No", "/ws/config", "/ws/config + /ws/nodes", "/ws/config + /ws/nodes"]},
                        {"feature": "Django Signals (config_changed, etc.)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Moderated Approvals (SyncApproval)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Product Sync Engine", "cells": ["No", "child", "master", "master"]},
                        {"feature": "Cross-device data sync", "cells": ["No", "push to master", "cloud master", "cloud master"]},
                        {"feature": "Cloud CRM (shared-portal)", "cells": ["No", "sync client", "sync master", "sync master"]},
                        {"feature": "JSON seed fixtures", "cells": ["No", "No", "Yes", "Yes"]},
                        {"feature": "Change signals (broadcast)", "cells": ["No", "No", "Yes", "Yes"]},
                        {"feature": "High-throughput Rust API (60k+ RPS)", "cells": ["No", "No", "Yes", "Yes"]},
                        {"feature": "Hosted deployment + managed backups", "cells": ["No", "No", "No", "Yes"]},
                        {"feature": "Offline-first mode", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Refunds & returns", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Loyalty & rewards program", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Multi-currency & tax profiles", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Custom roles & permissions", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Data export (CSV/JSON)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Automatic cloud backups", "cells": ["No", "No", "No", "Yes"]},
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "title": "Models & snippets you can reuse",
                    "description": "The core schema and entrypoint. The same patterns LMS and other projects borrow.",
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
                        {
                            "title": "Diesel migration (up.sql)",
                            "language": "sql",
                            "code": "-- Loyalty + refunds land on top of the core schema.\nALTER TABLE sales ADD COLUMN loyalty_points INTEGER NOT NULL DEFAULT 0;\n\nCREATE TABLE refunds (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  amount_cents INTEGER NOT NULL,\n  reason TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);",
                        },
                        {
                            "title": "Tauri command (invoice PDF)",
                            "language": "rust",
                            "code": "#[tauri::command]\npub fn generate_invoice(sale_id: i32, state: State<AppState>) -> Result<String, String> {\n    let conn = &mut state.pool.get().map_err(|e| e.to_string())?;\n    let sale: Sale = sales::table\n        .find(sale_id)\n        .first(conn)\n        .map_err(|e| e.to_string())?;\n    let items: Vec<SaleItem> = sale_items::table\n        .filter(sale_items::sale_id.eq(sale_id))\n        .load(conn)\n        .map_err(|e| e.to_string())?;\n    render_invoice_pdf(&sale, &items)\n}",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "title": "What Formints POS ships",
                    "description": "The features that move a terminal from a cash register to a business tool.",
                    "features": [
                        {"icon": "M4 7v10c0 2.2 1.8 4 4 4h8c2.2 0 4-1.8 4-4V7M4 7h16M4 7l2-3h12l2 3", "title": "Fast, native checkout", "description": "A Rust core keeps every keystroke instant, with no web latency on the counter."},
                        {"icon": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.6a2 2 0 011.4.6l4.4 4.4a2 2 0 01.6 1.4V19a2 2 0 01-2 2z", "title": "SQLite by default", "description": "Zero-config local storage that scales up to a synced multi-terminal setup in Pro."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Four editions, one codebase", "description": "Community, Standard, Pro, Cloud, feature-gated from a single Tauri + Rust core."},
                    ],
                },
            ),
            (
                "features",
                {
                    "title": "Product roadmap",
                    "description": "What ships next across the four editions — the loyalty engine, multi-currency, and managed backups are already in the comparison above.",
                    "features": [
                        {"icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z", "title": "Loyalty & rewards engine", "description": "Points, tiers and voucher redemption built into the sale flow — Standard and up."},
                        {"icon": "M3 3v18h18M7 15l4-4 3 3 5-6", "title": "Multi-currency & tax profiles", "description": "Per-terminal currency and tax profiles for border regions — Standard and up."},
                        {"icon": "M17 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM21 21v-2a4 4 0 00-3-3.87", "title": "Automatic cloud backups", "description": "Scheduled encrypted backups of the cloud master with point-in-time restore — Cloud."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "title": "Formints POS questions",
                    "items": [
                        {"question": "Which edition should I start with?", "answer": "Community is open source and perfect for a single terminal. Upgrade to Standard for the sidecar API + cloud sync, to Pro for a multi-terminal cloud master, or to Cloud for the fully hosted setup."},
                        {"question": "Can I reuse the schema in another project?", "answer": "Yes. The SQLite schema and Rust models are public reference material under the repo's license."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Run a terminal in minutes",
                    "subtitle": "Clone the repo, run the Community edition, and upgrade editions as you grow.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/formint-pos", "style": "white"},
                    "secondary_cta": {"label": "Get in Touch", "href": "/contact/", "style": "outline"},
                },
            )
        ],
    },
    "lms": {
        "title": "Precis LMS",
        "logo_style": "ribbon",
        "category": "platform",
        "tagline": "The learning platform behind structa.cloud: courses, enrollments, payments.",
        "hero": [
            (
                "hero",
                {
                    "title": "Precis LMS",
                    "subtitle": "A content-driven learning platform built on Django + django-fusion with a Next.js frontend.",
                    "primary_cta": {"label": "See the editions", "href": "/products/lms/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "Learn more", "href": "/about/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Precis LMS powers the Structa Cloud learning platform: courses, "
            "enrollments, payments (Stripe), and progress tracking, all served "
            "by Django/Wagtail with django-fusion's component pipeline.</p>"
            "<p>Its frontend is a Next.js app consuming django-fusion APIs and "
            "server-rendered fragments, the same content-driven pattern the "
            "landing CMS uses.</p>"
        ),
        "tech": [
            ("tech", {"title": "Built on", "items": ["Django", "Wagtail", "django-fusion", "Next.js", "React", "Stripe"]}),
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
                            "tagline": "For active creators and small academies who want a polished learning experience.",
                            "price": "$29",
                            "period": "/per month",
                            "features": ["Unlimited courses", "Priority support", "Advanced analytics", "Offline downloads", "Certificates", "SSO & role management", "Dedicated success manager", "High-end learning experience design"],
                            "cta_label": "Go Solo",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                        {
                            "name": "Business",
                            "tagline": "For organizations with cohorts, staff, and connected systems.",
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
        "snippets": [
            (
                "snippets",
                {
                    "title": "Content-driven models & snippets",
                    "description": "How the LMS models content. The pattern the CMS site builder generalizes.",
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
                    "title": "What Precis LMS ships",
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
                    "title": "Precis LMS questions",
                    "items": [
                        {"question": "How does this relate to the landing CMS?", "answer": "LMS and CMS share django-fusion. The CMS is the content-driven website builder; LMS is its highest-value use case."},
                        {"question": "Can I embed LMS on my own site?", "answer": "Yes. Courses and progress are served as server-rendered fragments that any Fusion site can embed."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Teach on the AHA stack",
                    "subtitle": "From one course to a full academy: content-driven, payment-enabled, server-rendered.",
                    "primary_cta": {"label": "See pricing", "href": "/products/lms/#editions", "style": "white"},
                    "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"},
                },
            )
        ],
    },
    "cms": {
        "title": "Loop",
        "logo_style": "isometric",
        "category": "platform",
        "tagline": "Build content-driven websites from Wagtail blocks. This very site is built with it.",
        "hero": [
            (
                "hero",
                {
                    "title": "Loop",
                    "subtitle": "A content-driven website builder. Wagtail StreamFields composed into server-rendered pages by django-fusion.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cms/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "Explore the stack", "href": "/features/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Loop is the content-driven website builder behind every "
            "structa.cloud landing page. Editors compose Wagtail StreamField "
            "blocks; django-fusion renders them as finished server-side HTML.</p>"
            "<p>It powers both render roads: Django's fusion-render HTML and the "
            "Astro frontend's data APIs, from one source of content.</p>"
        ),
        "tech": [
            ("tech", {"title": "Built on", "items": ["Wagtail", "Django", "django-fusion", "HTMX", "Alpine.js", "Astro"]}),
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "From one page to a whole site",
                    "editions": [
                        {
                            "name": "Community",
                            "tagline": "A single landing page with the core section blocks.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Wagtail StreamField blocks", "django-fusion rendering", "HTMX fragments", "MIT license"],
                            "cta_label": "Self-host",
                            "cta_href": "https://github.com/mammhoud/django-fusion",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Business",
                            "tagline": "A full marketing site with custom blocks + analytics. Multi-site, multi-editor, fully managed.",
                            "price": "Custom",
                            "period": "/project",
                            "features": ["Everything in Community", "Custom StreamField blocks", "Blog + FAQ sections", "Analytics + SEO", "HTMX forms", "Multi-site + roles", "Dedicated support"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "title": "Blocks & snippets you can reuse",
                    "description": "The building blocks that make a site content-driven. Copy them into any Fusion project.",
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
                    "title": "What Loop ships",
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
                    "title": "Loop questions",
                    "items": [
                        {"question": "Is this the same CMS that runs this site?", "answer": "Yes. Every page you're reading is composed from these StreamField blocks and rendered by django-fusion."},
                        {"question": "Can I add my own blocks?", "answer": "Absolutely. Blocks are plain Wagtail StructBlocks with Django templates, no framework lock-in."},
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
        "title": "Syntara",
        "logo_style": "orbit",
        "status": "development",
        "category": "platform",
        "tagline": "AI chat customizer. Embed Syntara-powered chat into any site.",
        "hero": [
            (
                "hero",
                {
                    "title": "Syntara",
                    "subtitle": "An AI chat customizer platform. Ceptor-ai powered chat embedded into customer sites, fully branded.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cypercloud/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "View ceptor-ai on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Syntara lets you embed intelligent chat into customer sites with "
            "full customization: branding, behavior, and model selection.</p>"
            "<p>It is powered by ceptor-ai (the MCP server + chat client library) "
            "and ships as an embeddable widget.</p>"
            "<p><strong>Status: under development.</strong> Syntara is an early "
            "preview — its APIs, editions and pricing may change before the 1.0 "
            "release. Treat everything below as a roadmap, not a contract.</p>"
        ),
        "tech": [("tech", {"title": "Built on", "items": ["Python", "Django", "ceptor-ai", "MCP"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Free to embed, paid to customize",
                    "editions": [
                        {"name": "Community", "tagline": "The open-source chat client, self-hosted.", "price": "$0", "period": "/open source", "features": ["ceptor-ai chat client", "MCP server", "Multi-model support"], "cta_label": "Self-host", "cta_href": "https://github.com/mammhoud/ceptor-ai", "featured": False, "tier": "outline"},
                        {"name": "Business", "tagline": "Managed chat with full branding.", "price": "$39", "period": "/per month", "features": ["Everything in Community", "Branded widget", "Behavior rules", "Analytics"], "cta_label": "Get Started", "cta_href": "/contact/", "featured": True, "tier": "featured"},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Chat that looks like your brand", "subtitle": "Embed Syntara-powered chat in an afternoon.", "primary_cta": {"label": "Get Started", "href": "/contact/", "style": "white"}, "secondary_cta": {"label": "View ceptor-ai on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "outline"}})],
    },
    "vresume": {
        "title": "vResume",
        "logo_style": "ascent",
        "category": "platform",
        "tagline": "Cloud resume platform. Create, update, publish professional resumes — with Syntara-powered AI summaries.",
        "hero": [
            (
                "hero",
                {
                    "title": "vResume",
                    "subtitle": "A cloud-hosted resume builder with modern templates, custom domains, CI/CD deployments, and Syntara-powered AI profile summaries.",
                    "primary_cta": {"label": "Launch vResume", "href": "https://vresume.structa.cloud", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/vresume/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>vResume lets you create, update, and publish professional resumes "
            "with modern templates, cloud-hosted at vresume.structa.cloud.</p>"
            "<p>Custom domains and a CI/CD pipeline make it a production showcase "
            "of the monorepo's deploy tooling.</p>"
            "<p>It pairs with Syntara, the AI chat customizer, for AI-assisted "
            "resume summaries and a chat-ready profile on every page.</p>"
        ),
        "tech": [("tech", {"title": "Built on", "items": ["Django", "Wagtail", "Next.js", "Syntara", "CI/CD"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "From one resume to a hosted portfolio",
                    "editions": [
                        {"name": "Community", "tagline": "One resume with the default template.", "price": "$0", "period": "/forever", "features": ["Modern resume templates", "Live preview", "PDF export"], "cta_label": "View on GitHub", "cta_href": "https://github.com/mammhoud", "featured": False, "tier": "outline"},
                        {"name": "Business", "tagline": "Custom domain + multiple resumes.", "price": "$9", "period": "/per month", "features": ["Everything in Community", "Custom domain", "Multiple resumes", "Syntara AI summaries", "Analytics"], "cta_label": "Upgrade", "cta_href": "/contact/", "featured": True, "tier": "featured"},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Your career, published", "subtitle": "Build a resume that ships like a product.", "primary_cta": {"label": "Launch vResume", "href": "https://vresume.structa.cloud", "style": "white"}, "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"}})],
    },
    "ceptor-ai": {
        "title": "ceptor-ai",
        "logo_style": "orbit",
        "category": "library",
        "hidden": True,
        "tagline": "AI chat client + MCP server. Agent communication and generation.",
        "hero": [
            (
                "hero",
                {
                    "title": "ceptor-ai",
                    "subtitle": "An AI chat client with a Model Context Protocol (MCP) server. Powers Syntara and agent tooling.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/ceptor-ai/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>ceptor-ai is the AI layer of the monorepo: an MCP server for agent "
            "communication, a chat client with multi-model support, and a BEM "
            "converter for prompt-to-component generation.</p>"
        ),
        "tech": [("tech", {"title": "Built on", "items": ["Python", "MCP", "AI/ML", "Node.js"]})],
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
        "cta": [("cta", {"title": "Agents that talk to your tools", "subtitle": "ceptor-ai connects LLMs to anything via MCP.", "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "white"}, "secondary_cta": {"label": "See Syntara", "href": "/products/cypercloud/", "style": "outline"}})],
    },
}


DEFAULT_HOME_CONTENT = {
    "hero": [
        (
            "hero",
            {
                "badge": "structa.cloud · digital product partner",
                # NB: the Hero renders ``title`` + ``accent`` separately (both
                # roads — Astro Hero.astro and content/blocks/hero.html), so
                # the accent word is NOT part of the stored title. Keep titles
                # free of the accent phrase.
                "title": "Digital products, shipped as",
                "accent": "documents",
                "subtitle": (
                    "We help teams serving the Gulf, Levant, and North Africa launch clear, "
                    "bilingual services that feel fast and stay easy to operate."
                ),
                "primary_cta": {"label": "Explore products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Work with us", "href": "/contact/", "style": "white"},
                "trusted_by": "Arabic-ready · English-ready · built for real teams",
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "A useful first release beats a noisy roadmap",
                "subtitle": "We start with the customer journey, launch a focused slice, and leave your team with the content and tools to keep improving it.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Read the Docs", "href": "/about/", "style": "outline"},
            },
        )
    ],
}


# The full document lives on the About page (mirrors the Astro frontend where
# /about carries hero + mission + stats + features + pricing + testimonials +
# faq + cta and / is a slim hero + cta entry point).
DEFAULT_ABOUT_SECTIONS = {
    "stats": [
        (
            "stats",
            {
                "title": "Built for steady growth",
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
                "title": "Built by one engineer, for real teams",
                "description": (
                    "Structa Cloud is a one-person studio with an open-source backbone: "
                    "the founder designs, builds, and ships every product, and the "
                    "libraries that make them possible are public on GitHub."
                ),
                "features": [
                    {
                        "icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z",
                        "title": "A founder who ships",
                        "description": "One engineer owns the full stack — Django, Wagtail, Rust, React — and ships every product as finished, server-rendered documents.",
                    },
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "Your team owns the content",
                        "description": "Structured content lets marketing and operations teams update Arabic and English pages without waiting for engineering.",
                    },
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Arabic and English by design",
                        "description": "Language direction, navigation, content fallbacks, and editorial fields are considered from the first page, not added at the end.",
                    },
                    {
                        "icon": "M17 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM21 21v-2a4 4 0 00-3-3.87",
                        "title": "A system that can be handed over",
                        "description": "Reusable blocks, clear controls, and practical documentation keep the service maintainable after launch.",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "Automation with a human check",
                        "description": "AI can accelerate research, support, and content workflows while your team keeps the final say.",
                    },
                    {
                        "icon": "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20",
                        "title": "A performance budget, not a promise",
                        "description": "We reserve room for content, images, and future features, then check Core Web Vitals on the devices and networks your customers use.",
                    },
                ],
            },
        )
    ],
    "testimonials": [
        (
            "testimonials",
            {
                "title": "Designed around the people using it",
                "description": "The strongest product decisions come from clear journeys, useful content, and teams who can keep the experience moving.",
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
                        "cta_href": "/contact/",
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
                        "cta_href": "/contact/",
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
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open, shipped as HTML",
                "subtitle": "Community editions and the core libraries are public on GitHub. Paid editions are commercial.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Get in Touch", "href": "/contact/", "style": "outline"},
            },
        )
    ],
}


# The dedicated FAQ page — the single home for general questions. Unlike the
# section stacks on About/Products/Features (which no longer carry a generic
# FAQ), this list is the one place with the platform-wide answers, expanded
# across the domain: the stack, the products, editions, licensing, auth,
# privacy/cookies and support. Product pages keep their own short
# product-specific FAQ (e.g. "Formints POS questions").
DEFAULT_FAQ_SECTIONS = {
    "faq": [
        (
            "faq",
            {
                "title": "Frequently Asked Questions",
                "description": "The honest answers to the questions technical buyers ask — the stack, the products, the editions, and the fine print.",
                "items": [
                    {
                        "question": "What is structa.cloud?",
                        "answer": "Structa Cloud is the portfolio and product hub for Mahmoud Ezzat Moustafa: a full-stack developer building Django/Wagtail platforms, AI tools, and open-source libraries.",
                    },
                    {
                        "question": "What is the AHA stack?",
                        "answer": "AHA stands for Astro + HTMX + Alpine.js: a server-first rendering stack that ships minimal client-side JavaScript. Astro renders the document, HTMX swaps server-rendered fragments, and Alpine hydrates micro-interactions.",
                    },
                    {
                        "question": "Which products are available and in what editions?",
                        "answer": "Formints POS (Community, Standard, Pro, Cloud), Precis LMS (Solo, Business), Loop CMS (Community, Business), Syntara AI chat (Community, Business) and vResume (Community, Business). Product editions are priced by capability; paid tiers add richer learning operations, integrations, cloud sync, multi-terminal and hosted features.",
                    },
                    {
                        "question": "Are the libraries free to use?",
                        "answer": "Yes. django-fusion, ceptor-ai, and the Formints POS core are all open-source on GitHub under permissive licenses. You can use them in commercial and client projects.",
                    },
                    {
                        "question": "Can I use this for a client project?",
                        "answer": "Absolutely. The libraries are production-tested across vResume, Syntara, and the landing pages. The monorepo even documents the licensing terms for reuse.",
                    },
                    {
                        "question": "How do I get started?",
                        "answer": "Clone the monorepo from github.com/mammhoud, run 'make dev' in projects/landing-fusion, and explore the Wagtail admin at /admin/. Each product page ships reference snippets and models you can copy.",
                    },
                    {
                        "question": "How do I deploy a Fusion site?",
                        "answer": "The monorepo includes Docker Compose orchestration with Traefik + Nginx + Postgres. One 'make deploy' provisions the full stack with HTTPS, and the docs cover DNS-01 Let's Encrypt via Cloudflare.",
                    },
                    {
                        "question": "What is django-fusion?",
                        "answer": "django-fusion is the component system + routing framework used across every structa.cloud product: StreamField blocks rendered server-side, HTMX fragments, and a dual-mode API pipeline.",
                    },
                    {
                        "question": "What is ceptor-ai?",
                        "answer": "ceptor-ai is the AI layer of the monorepo: an MCP server for agent communication, a chat client with multi-model support, and a BEM converter for prompt-to-component generation. It powers Syntara.",
                    },
                    {
                        "question": "Is there an account or login system?",
                        "answer": "Yes — sign-in is powered by django-allauth (headless API + social providers like GitHub and Google). The Log In button in the header opens a modal; after sign-in your session is stored server-side.",
                    },
                    {
                        "question": "What data does the site collect, and what about cookies?",
                        "answer": "We only use essential cookies (theme preference + HTMX navigation state) and never sell data. The privacy policy lists exactly what is collected and how you can request deletion. Non-essential analytics are opt-in via the cookie banner.",
                    },
                    {
                        "question": "Which editions need a license vs. deployment fees?",
                        "answer": "Community editions are open source. Standard/Pro list a per-month license; deployment and support are quoted per site. Cloud is fully hosted and quoted on contact. Pricing pages always state the exact model.",
                    },
                    {
                        "question": "How do the POS editions differ?",
                        "answer": "Community is a free offline single-terminal POS. Standard adds an embedded Python sidecar + cloud sync client. Pro is multi-terminal with a cloud master and high-throughput Rust API. Cloud is the Pro master, hosted and managed for you.",
                    },
                    {
                        "question": "How is this different from a React or Vue site?",
                        "answer": "A React site sends a shell plus a bundle, then builds the page in the browser. Fusion sends the finished HTML in one response. Less to download, less to run, and search engines read exactly what visitors see.",
                    },
                    {
                        "question": "Can I still build dynamic dashboards?",
                        "answer": "Yes. HTMX streams HTML fragments from Django over plain HTTP — the same technology as the landing page. Dynamic regions stay server-rendered, so there is never a second, parallel API to maintain.",
                    },
                    {
                        "question": "How do I get support?",
                        "answer": "Open an issue on GitHub for open-source questions, or use the contact form on the Contact page for deployment, licensing and Cloud quoting. Business and Cloud editions include dedicated support.",
                    },
                ],
            },
        )
    ],
}


# About → Team subpage (child of About, served at /about/team/).
# The people behind structa.cloud: the founder + product leads, each with
# their social links. Links use the mammhoud handles (GitHub / LinkedIn /
# Facebook) so the team page and the rest of the site stay consistent.
DEFAULT_TEAM_SECTIONS = {
    "hero": [
        (
            "hero",
            {
                "title": "The people behind structa.cloud",
                "subtitle": "One engineer, three product leads, and the open-source contributors who make the monorepo ship.",
                "primary_cta": {"label": "Meet the founder", "href": "/about/", "style": "secondary"},
                "secondary_cta": {"label": "Get in touch", "href": "/contact/", "style": "white"},
            },
        )
    ],
    "body": (
        "<p>structa.cloud is built in the open. The founder runs the "
        "architecture; each product has a named lead; the libraries are "
        "public on GitHub for anyone to contribute to.</p>"
    ),
    "team": [
        (
            "team",
            {
                "eyebrow": "the team",
                "title": "Who builds what",
                "description": "Every product is a project in the monorepo, and every project has an owner.",
                "members": [
                    {
                        "name": "Mahmoud Ezzat Moustafa",
                        "role": "Founder · full-stack engineer",
                        "bio": "Architect of the monorepo: Django/Wagtail platforms, the AHA landing stack, and the AI libraries. Ships everything as server-rendered documents.",
                        "initials": "ME",
                        "links": [
                            {"platform": "GitHub", "url": "https://github.com/mammhoud"},
                            {"platform": "LinkedIn", "url": "https://linkedin.com/in/mammhoud"},
                            {"platform": "Facebook", "url": "https://facebook.com/mammhoud"},
                            {"platform": "Portfolio", "url": "https://mammhoud.github.io"},
                        ],
                    },
                    {
                        "name": "Formints",
                        "role": "Product lead · point-of-sale",
                        "bio": "The Tauri 2 + Rust desktop POS: SQLite, four editions, one codebase. Community is open source on GitHub.",
                        "initials": "FP",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud/formint-pos"}],
                    },
                    {
                        "name": "Precis LMS",
                        "role": "Product lead · learning platform",
                        "bio": "Courses, enrollments and Stripe payments on django-fusion. The highest-value use case of the CMS.",
                        "initials": "PL",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud"}],
                    },
                    {
                        "name": "Loop CMS",
                        "role": "Product lead · website builder",
                        "bio": "Wagtail StreamField blocks rendered by django-fusion. This very site is built with it.",
                        "initials": "LC",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud/django-fusion"}],
                    },
                    {
                        "name": "Syntara",
                        "role": "Product lead · AI chat",
                        "bio": "Ceptor-ai powered chat embedded into any site. Under development — a preview of what's next.",
                        "initials": "SY",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud/ceptor-ai"}],
                    },
                    {
                        "name": "vResume",
                        "role": "Product lead · cloud resume",
                        "bio": "Create, update and publish professional resumes with custom domains and CI/CD deployments.",
                        "initials": "VR",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud"}],
                    },
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open",
                "subtitle": "Every line of structa.cloud is public on GitHub. Come build with us.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Back to About", "href": "/about/", "style": "outline"},
            },
        )
    ],
}


# About → Founder subpage (child of About, served at /about/founder/).
# The engineer behind structa.cloud — mirrors the Astro founder page: hero,
# story body, tech-stack band (TechStackSectionBlock) and a skills grid
# (FeaturesSectionBlock).
DEFAULT_FOUNDER_SECTIONS = {
    "hero": [
        (
            "hero",
            {
                "title": "Mahmoud Ezzat Moustafa",
                "subtitle": "Full-stack developer, open-source contributor, and the engineer behind structa.cloud. Django, Wagtail, and AI-powered systems.",
                "primary_cta": {"label": "Meet the team", "href": "/about/team/", "style": "secondary"},
                "secondary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "trusted_by": "Python · Django · Wagtail · AI tooling",
            },
        )
    ],
    "body": (
        "<p>Mahmoud Ezzat Moustafa is a full-stack developer specializing in "
        "Python/Django, Wagtail CMS, and AI tooling. He builds server-rendered "
        "platforms that ship as documents — no heavy SPAs, no framework "
        "overhead. Every project in the structa.cloud monorepo carries his "
        "signature: finished HTML in one response.</p>"
        "<p>He works in the open: the libraries, the products, and the "
        "documentation that explains them are all public on GitHub.</p>"
    ),
    "tech": [
        (
            "tech",
            {
                "eyebrow": "the stack",
                "title": "Built on",
                "description": "The tools that ship every product in the monorepo.",
                "items": ["Python", "Django", "Wagtail", "django-fusion", "ceptor-ai", "Astro", "HTMX", "Alpine.js", "Tauri 2", "Rust", "React", "PostgreSQL", "Redis", "Docker", "Traefik", "GitHub Actions"],
            },
        )
    ],
    "features": [
        (
            "features",
            {
                "eyebrow": "skills & values",
                "title": "How the work gets done",
                "description": "The capabilities and principles that show up in every project.",
                "features": [
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "Ships as documents",
                        "description": "Server-rendered HTML in one response — no hydration waterfalls, no 500 KB bundles.",
                    },
                    {
                        "icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z",
                        "title": "Reusable systems",
                        "description": "django-fusion and ceptor-ai extracted from real projects, so every site inherits the patterns.",
                    },
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Bilingual by default",
                        "description": "Arabic and English considered from the first page — direction, content fallbacks, editorial fields.",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "Performance as trust",
                        "description": "A fast first visit gives customers confidence before the first conversation.",
                    },
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open",
                "subtitle": "The full monorepo is public on GitHub. Community editions are free, Pro editions are commercial.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Contact", "href": "/contact/", "style": "outline"},
            },
        )
    ],
}


# About → Startup subpage (child of About, served at /about/startup/).
# The origin story — mirrors the Astro startup page: hero, story body, a
# numbered timeline (ProcessSectionBlock, one step per era) and a stats band.
DEFAULT_STARTUP_SECTIONS = {
    "hero": [
        (
            "hero",
            {
                "title": "The Startup",
                "subtitle": "How structa.cloud grew from freelance Django projects into a monorepo of open-source products, AI tools, and a desktop POS application.",
                "primary_cta": {"label": "See the products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Meet the founder", "href": "/about/founder/", "style": "white"},
                "trusted_by": "2019 · freelance → 2026 · five products",
            },
        )
    ],
    "body": (
        "<p>Structa Cloud started as one developer shipping Wagtail sites. "
        "Each project repeated the same auth patterns, the same blocks, the "
        "same table layouts — until the reusable parts became a library, and "
        "the library became a monorepo of products.</p>"
    ),
    "process": [
        (
            "process",
            {
                "eyebrow": "the timeline",
                "title": "From freelance to five products",
                "description": "A measured path: learn the pattern, extract it, open it, productize it.",
                "steps": [
                    {
                        "title": "2019–2021 · Freelance foundations",
                        "description": "Solo Django developer shipping Wagtail sites. WordPress had the market share; Django had the performance. Auth, CMS, payments, analytics — hand-rolled every time.",
                        "deliverable": "Five client projects",
                    },
                    {
                        "title": "2022 · The reusable library",
                        "description": "After five projects with the same auth, blocks, and tables, django-fusion was extracted — a component system and routing framework every project could share.",
                        "deliverable": "django-fusion v1",
                    },
                    {
                        "title": "2023 · Open source and AI",
                        "description": "Published django-fusion on GitHub, built ceptor-ai (AI chat customizer + MCP server), and started Formints, a desktop POS in Tauri 2 + Rust + React.",
                        "deliverable": "ceptor-ai · Formints",
                    },
                    {
                        "title": "2024 · The AHA stack",
                        "description": "Migrated from heavy React SPAs to Astro + HTMX + Alpine.js — server-rendered HTML with minimal client JS. This landing page is the framework itself.",
                        "deliverable": "Astro + HTMX + Alpine",
                    },
                    {
                        "title": "2025–2026 · Products and scale",
                        "description": "Five products shipping from one monorepo: Formints POS, Precis LMS, Loop CMS, Syntara AI, vResume. Community editions open source, paid editions commercial.",
                        "deliverable": "Five products, one repo",
                    },
                ],
            },
        )
    ],
    "stats": [
        (
            "stats",
            {
                "title": "The story in numbers",
                "stats": [
                    {"value": "5", "suffix": "+", "label": "Years building"},
                    {"value": "5", "suffix": "", "label": "Products shipping"},
                    {"value": "15", "suffix": "+", "label": "Open-source repos"},
                    {"value": "1", "suffix": "", "label": "Monorepo"},
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open, shipped as HTML",
                "subtitle": "Community editions and the core libraries are public on GitHub. Paid editions are commercial.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Read the About page", "href": "/about/", "style": "outline"},
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
            PhasePage,
            PromptPage,
            ProductsPage,
            FeaturesPage,
            BlogPage,
            BrandPage,
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

        # ── Home page (root child) ──────────────────────────────────────
        # Create the owned page before deleting Wagtail's migration-time
        # "Welcome" sibling. Older treebeard versions calculate a new
        # sibling path from the current last child and can return None when
        # the root has just been emptied in a fresh TestCase database.
        home, created = self._get_or_create_child(
            root, HomePage, title="Home", slug="home", **DEFAULT_HOME_CONTENT
        )
        self._created(created, "home")

        # Remove Wagtail's default "Welcome" page and any other non-landing
        # root child now that the root has a valid landing sibling. This keeps
        # the command idempotent while making fresh test databases reliable.
        for child in root.get_children():
            if child.pk != home.pk and child.specific_class not in landing_models:
                self.stdout.write(f"Removing default page: {child.title} (slug={child.slug})")
                child.delete()

        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"port": 8074, "is_default_site": True, "root_page": home},
        )
        site.root_page = home
        site.save()
        self.stdout.write(f"Site root set to {home.title} (http://localhost:{site.port}/)")

        # ── Social auth apps ──────────────────────────────────────────
        self.stdout.write("Seeding social auth apps (GitHub + Google)…")
        from allauth.socialaccount.models import SocialApp

        for provider_id, name, client_id_key, secret_key in (
            ("github", "GitHub", "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"),
            ("google", "Google", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
        ):
            client_id = os.environ.get(client_id_key, "")
            secret = os.environ.get(secret_key, "")
            if client_id and secret:
                app, created = SocialApp.objects.get_or_create(
                    provider=provider_id,
                    defaults={"name": name, "client_id": client_id, "secret": secret},
                )
                if created:
                    app.sites.add(site)
                    self.stdout.write(f"  ✓ {name} SocialApp created")
                else:
                    app.sites.add(site)
                    self.stdout.write(f"  → {name} SocialApp already exists, site added")
            else:
                self.stdout.write(
                    f"  ⚠ {name} skipped — set {client_id_key}/{secret_key} env vars"
                )

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
                    "title": "A clearer path to market",
                    "subtitle": "We connect strategy, design, and delivery for teams building services in Arabic and English.",
                    "primary_cta": {"label": "See how we work", "href": "/services/", "style": "secondary"},
                    "secondary_cta": {"label": "Start a conversation", "href": "/contact/", "style": "white"},
                },
            )
        ],
        body=(
            "<p>Structa Cloud helps teams across the Gulf, Levant, and North Africa turn important ideas into useful digital services.</p>"
            "<p>We start with the customer journey, the content, and the operating reality of your team. Then we choose the simplest technology that can carry the experience well.</p>"
            "<p>Arabic and English content, quick first visits, and clear editorial controls are part of the product brief from the beginning.</p>"
            "<p>The handover matters as much as the launch. Your team gets a system it can understand, update, and improve without a permanent dependency on a development queue.</p>"
        ),
            # About tells the full story — stats, features, testimonials AND
            # the simple transparent pricing stack. The dedicated /pricing/
            # page carries the per-product price sheets on top.
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "about")

        # ── About → Team (subpage, /about/team/) ────────────────────────
        team, created = self._get_or_create_child(
            about,
            TeamPage,
            title="Team",
            slug="team",
            hero=DEFAULT_TEAM_SECTIONS["hero"],
            body=DEFAULT_TEAM_SECTIONS["body"],
            team=DEFAULT_TEAM_SECTIONS["team"],
            cta=DEFAULT_TEAM_SECTIONS["cta"],
        )
        self._created(created, "about:team")

        # ── About → Founder (subpage, /about/founder/) ───────────────────
        founder, created = self._get_or_create_child(
            about,
            FounderPage,
            title="Founder",
            slug="founder",
            hero=DEFAULT_FOUNDER_SECTIONS["hero"],
            body=DEFAULT_FOUNDER_SECTIONS["body"],
            tech=DEFAULT_FOUNDER_SECTIONS["tech"],
            features=DEFAULT_FOUNDER_SECTIONS["features"],
            cta=DEFAULT_FOUNDER_SECTIONS["cta"],
        )
        self._created(created, "about:founder")

        # ── About → Startup (subpage, /about/startup/) ───────────────────
        startup, created = self._get_or_create_child(
            about,
            StartupPage,
            title="Startup",
            slug="startup",
            hero=DEFAULT_STARTUP_SECTIONS["hero"],
            body=DEFAULT_STARTUP_SECTIONS["body"],
            process=DEFAULT_STARTUP_SECTIONS["process"],
            stats=DEFAULT_STARTUP_SECTIONS["stats"],
            cta=DEFAULT_STARTUP_SECTIONS["cta"],
        )
        self._created(created, "about:startup")

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
                "title": "From idea to market",
                "subtitle": "Focused digital services for teams that need a clear customer journey and a dependable launch.",
                "primary_cta": {"label": "Explore products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Start a conversation", "href": "/contact/", "style": "white"},
                "trusted_by": "Arabic-ready · English-ready · built for real teams",
                    },
                )
            ],
    body=(
        "<p>We shape three kinds of work: market-ready websites, digital products, and focused improvements to services that already have customers.</p>"
        "<p>Every engagement balances brand, content, accessibility, and the realities of mobile networks across the region.</p>"
        "<p>We leave teams with a performance budget, bilingual content controls, and a practical handover instead of a black box.</p>"
    ),
            **DEFAULT_SERVICES_SECTIONS,
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "services")

        # ── Services → delivery phases + reusable implementation prompts ──
        phase_seed = [
            {
                "title": "Discover", "slug": "discover", "phase_number": 1,
                "phase_label": "discovery",
                "body": "<p>Turn the brief into a clear document model, visual direction, and measurable first release.</p>",
                "outcomes": "A bounded brief\nA content and route map\nA first-release decision log",
                "prompts": [{
                    "title": "Shape the brief", "slug": "shape-the-brief",
                    "prompt": "Turn this product brief into a focused first release with user, content, route, and success constraints.",
                    "context": "Use this before design or implementation begins.",
                    "output": "A concise scope, assumptions, risks, and acceptance checklist.",
                    "tool": "Wagtail + product discovery",
                }],
            },
            {
                "title": "Build", "slug": "build", "phase_number": 2,
                "phase_label": "build",
                "body": "<p>Build the smallest complete path as server-rendered HTML, then add HTMX and Alpine where they improve the document.</p>",
                "outcomes": "A working content model\nA responsive document route\nProgressive enhancement checks",
                "prompts": [{
                    "title": "Build the first vertical slice", "slug": "build-the-first-vertical-slice",
                    "prompt": "Implement one complete user journey from Wagtail model to accessible HTML, with progressive enhancement only where needed.",
                    "context": "Keep the server-rendered path usable without JavaScript.",
                    "output": "A tested vertical slice with model, API, template, and browser states.",
                    "tool": "Astro + HTMX + Alpine",
                }],
            },
            {
                "title": "Launch", "slug": "launch", "phase_number": 3,
                "phase_label": "launch",
                "body": "<p>Ship a dependable release with content parity, observability, and a handoff the team can own.</p>",
                "outcomes": "SEO and accessibility checks\nDeployment runbook\nEditor handoff",
                "prompts": [{
                    "title": "Prepare the release", "slug": "prepare-the-release",
                    "prompt": "Audit this release for broken routes, missing content, accessibility regressions, and backend/frontend parity before deployment.",
                    "context": "Run the same checklist against the Astro and Django roads.",
                    "output": "A prioritized release report with fixes and explicit sign-off criteria.",
                    "tool": "Django + Astro verification",
                }],
            },
            {
                "title": "Enhance", "slug": "enhance", "phase_number": 4,
                "phase_label": "enhance",
                "body": "<p>Improve the living system through measured content, performance, and interaction enhancements.</p>",
                "outcomes": "A measured improvement backlog\nReusable content patterns\nA safe iteration loop",
                "prompts": [{
                    "title": "Enhance without drift", "slug": "enhance-without-drift",
                    "prompt": "Improve this page while preserving content ownership, render parity, accessibility, and the existing design language.",
                    "context": "Prefer reusable components and Wagtail-managed content over one-off page markup.",
                    "output": "A small change set with regression checks and a documented reason for each change.",
                    "tool": "django-fusion components",
                }],
            },
        ]
        for phase_data in phase_seed:
            prompts = phase_data.pop("prompts")
            phase, phase_created = self._get_or_create_child(services, PhasePage, **phase_data)
            self._created(phase_created, f"services:phase:{phase.slug}")
            for prompt_data in prompts:
                prompt, prompt_created = self._get_or_create_child(phase, PromptPage, **prompt_data)
                self._created(prompt_created, f"services:phase:{phase.slug}:prompt:{prompt.slug}")

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
                        "title": "Most of what we build, shipped as",
                        "subtitle": "The full catalog: products with editions and pricing, plus the projects behind them, from one monorepo.",
                        "primary_cta": {"label": "See the editions", "href": "/products/formint-pos/#editions", "style": "secondary"},
                        "secondary_cta": {"label": "Browse the repo", "href": "https://github.com/mammhoud", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>Every project in the structa.cloud monorepo, one card "
                "each: desktop applications, hosted platforms, and open-source "
                "libraries. Every card links to a reference page with editions "
                "&amp; pricing, tech stack, and snippets/models you can reuse.</p>"
                "<p>The product cards and the repo project grid were merged "
                "into one list — each product IS a project in this repo.</p>"
            ),
            projects=[],
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "products")

        # ── Product pages (children of Products) ─────────────────────────
        # Rename cleanup — the POS product moved from slug ``forge-pos`` to
        # ``formint-pos`` (Formints). Rename in place BEFORE the creation loop
        # so an older page keeps its tree position (the flagship leads the
        # catalog); only delete when the new slug was already created.
        stale_forge = ProductPage.objects.filter(slug="forge-pos").first()
        if stale_forge is not None:
            if ProductPage.objects.filter(slug="formint-pos").exists():
                stale_forge.delete()
                self.stdout.write("Removed stale product page: forge-pos")
            else:
                stale_forge.slug = "formint-pos"
                stale_forge.save()
                self.stdout.write("Renamed product page: forge-pos → formint-pos")

        # Each is a reference document with editions & pricing + snippets.
        for slug, product in DEFAULT_PRODUCT_PAGES.items():
            product_page, created = self._get_or_create_child(
                products,
                ProductPage,
                slug=slug,
                title=product["title"],
                category=product.get("category", "application"),
                tagline=product.get("tagline", ""),
                logo_style=product.get("logo_style", "crest"),
                status=product.get("status", "live"),
                hidden=product.get("hidden", False),
                hero=product.get("hero", []),
                body=product.get("body", ""),
                tech=product.get("tech", []),
                editions=product.get("editions", []),
                comparison=product.get("comparison", []),
                snippets=product.get("snippets", []),
                features=product.get("features", []),
                faq=product.get("faq", []),
                cta=product.get("cta", []),
            )
            self._created(created, f"product:{slug}")

        # Catalog order — product children follow DEFAULT_PRODUCT_PAGES so the
        # flagship (Formints) leads the tree on fresh DBs and after renames.
        desired_order = [slug for slug in DEFAULT_PRODUCT_PAGES]
        current_order = [
            c.slug
            for c in products.get_children().live()
            if isinstance(c.specific, ProductPage)
        ]
        if current_order != desired_order:
            placed = None
            for slug in desired_order:
                node = products.get_children().live().filter(slug=slug).first()
                if node is None:
                    continue
                if placed is None:
                    node.move(products, pos="first-child")
                else:
                    node.move(placed, pos="right")
                placed = node

        # Removed-product cleanup — django-bolt was dropped from the catalog
        # (its capability lives on inside Formints' Pro tier). Any page seeded
        # by an older revision is removed so the tree mirrors the catalog.
        stale_bolt = ProductPage.objects.filter(slug="django-bolt").first()
        if stale_bolt is not None:
            stale_bolt.delete()
            self.stdout.write("Removed removed-product page: django-bolt")

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
                "title": "Ideas from real launches",
                "subtitle": "Practical notes on digital services, performance, and content for teams serving the region.",
                "primary_cta": {"label": "Explore products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Start a conversation", "href": "/contact/", "style": "white"},
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
                        "subtitle": "Simple, transparent pricing. Start free and scale as you grow.",
                        "primary_cta": {"label": "Start Free", "href": "/contact/", "style": "secondary"},
                        "secondary_cta": {"label": "Contact Sales", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            # The tabbed per-product pricing (get_product_pricing) supersedes
            # the old generic tier stack — no tiers seeded here. The generic
            # FAQ moved to the dedicated /faq/ page — no FAQ seeded here.
            pricing=[],
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
                        "subtitle": "The AHA stack, documented. Every capability of Structa Cloud.",
                        "primary_cta": {"label": "Our Products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>The AHA stack is Astro + HTMX + Alpine.js: a server-first "
                "rendering stack that ships finished HTML in one response.</p>"
                "<p>Every capability below exists to keep the page a document: "
                "fast by default, secure by default, editable by editors.</p>"
            ),
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "features")

        # ── Brand (identity system, page + product-tooltip modal) ─────────
        # A real Wagtail page (BrandPage) so editors can toggle display_mode
        # (page / modal / both) in the admin. The identity boards themselves
        # are derived from the catalog + BRAND_SPEC — they can never drift.
        brand, created = self._get_or_create_child(
            home,
            BrandPage,
            title="Brand",
            slug="brand",
            display_mode="both",
            hero=[
                (
                    "hero",
                    {
                        # + Astro accent "five marks"
                        "title": "One family, five marks",
                        "subtitle": "Every product carries its own constructed mark — a symbol built from what it does, not a generic glyph. Same system, five distinct identities.",
                        "primary_cta": {"label": "See the products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Pricing", "href": "/pricing/", "style": "white"},
                    },
                )
            ],
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "brand")

        # ── Projects merged into Products ─────────────────────────────
        # The Projects page was folded into the Products catalog: the product
        # cards ARE the repo project grid (the separate project grid seed was
        # removed) and the legacy /projects/ URL permanently redirects
        # (apps/handlers/urls.py). The ProjectsPage model was removed by
        # migration 0012 so there is nothing to clean up here.

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
                        "topics": [
                            "General inquiry",
                            "Formints POS",
                            "Precis LMS",
                            "Loop CMS",
                            "Syntara",
                            "vResume",
                            "Website building",
                            "Product development",
                            "Enhancements & extensions",
                            "Partnership",
                        ],
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
                        "subtitle": "The honest answers to the questions technical buyers ask.",
                    },
                )
            ],
            faq=DEFAULT_FAQ_SECTIONS["faq"],
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
                "<p>This privacy policy explains how Structa Cloud collects, uses, "
                "and protects your information. We keep data collection minimal "
                "by design: this site is a static-first document, not a data "
                "platform.</p>"
                "<h3>What we collect</h3>"
                "<p>Contact form submissions (name, email, message), account "
                "details for authenticated features, and anonymous usage "
                "patterns. We never sell your personal information to third "
                "parties.</p>"
                "<h3>How we use it</h3>"
                "<p>To respond to inquiries, deliver requested services, "
                "personalize your experience, and improve the platform.</p>"
                "<h3>Cookies and consent</h3>"
                "<p>We only use <strong>essential cookies</strong>: a theme "
                "preference and HTMX navigation state. No tracking, no ads, "
                "no third-party cookies. The cookie banner on first visit asks "
                "for consent; your choice (Accept or Deny) is stored locally in "
                "your browser, and no non-essential cookie is ever set without "
                "it.</p>"
                "<p>When you accept, no additional data is collected — consent "
                "only permits the same essential cookies. When you deny, the "
                "site works identically, minus the persisted theme "
                "preference.</p>"
                "<h3>Your rights</h3>"
                "<p>You can request a copy or deletion of your data at any time "
                "by contacting us, and you can withdraw cookie consent at any "
                "time by clearing your browser storage.</p>"
            ),
        )
        self._created(created, "privacy")

        # ── Social links (Wagtail snippets) ─────────────────────────────
        # Seeded idempotently: existing links are left untouched unless the
        # URL differs from the seed (then the seed wins — the mammhoud handles
        # are the canonical identity).
        try:
            from apps.content.models.settings import SocialLink

            default_links = [
                {"platform": "github", "label": "GitHub", "url": "https://github.com/mammhoud"},
                {"platform": "linkedin", "label": "LinkedIn", "url": "https://linkedin.com/in/mammhoud"},
                {"platform": "facebook", "label": "Facebook", "url": "https://facebook.com/mammhoud"},
                {"platform": "twitter", "label": "X / Twitter", "url": "https://x.com/mammhoud", "is_active": False},
            ]
            for i, link in enumerate(default_links):
                obj, _ = SocialLink.objects.get_or_create(
                    platform=link["platform"],
                    defaults={**link, "sort_order": i},
                )
                if obj.url != link["url"]:
                    obj.url = link["url"]
                    obj.sort_order = i
                    obj.save()
        except Exception:
            self.stdout.write(self.style.WARNING("Social links seed skipped."))

        self._seed_site_languages()
        self._seed_page_translations()
        self.stdout.write(self.style.SUCCESS("✅ Landing pages seeded."))

    def _seed_site_languages(self):
        """Create/update the seeded ``SiteLanguage`` catalog idempotently.

        Existing rows keep their editor changes unless ``--force`` is passed
        (then active/order are refreshed). New languages added to
        ``DEFAULT_SITE_LANGUAGES`` are created; languages removed from the
        default list are left untouched (editors may re-enable them later).
        """
        from apps.content.models.languages import SiteLanguage

        try:
            for entry in DEFAULT_SITE_LANGUAGES:
                code = entry["code"]
                language, created = SiteLanguage.objects.get_or_create(
                    code=code,
                    defaults=entry,
                )
                if not created and self.force:
                    changed = False
                    for field in ("name", "native_name", "direction", "flag"):
                        if getattr(language, field) != entry[field]:
                            setattr(language, field, entry[field])
                            changed = True
                    if language.is_active != entry["is_active"] or language.sort_order != entry["sort_order"]:
                        language.is_active = entry["is_active"]
                        language.sort_order = entry["sort_order"]
                        changed = True
                    if changed:
                        language.save(update_fields=["name", "native_name", "direction", "flag", "is_active", "sort_order"])
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded language {code} ({entry['name']})."))
        except Exception:
            self.stdout.write(self.style.WARNING("Site language seed skipped."))

    def _seed_page_translations(self):
        """Create/update the seeded English/Arabic editorial overlays."""
        for slug, values in DEFAULT_PAGE_TRANSLATIONS.items():
            landing_root = HomePage.objects.first()
            page = (
                landing_root.get_descendants(inclusive=True).live().filter(slug=slug).first()
                if landing_root is not None
                else Page.objects.live().filter(slug=slug).first()
            )
            if page is None:
                continue
            for language in ("en", "ar"):
                # English records are useful as an explicit editorial source;
                # they remain empty until an editor adds an override.
                payload = values if language == "ar" else {}
                translation, created = PageTranslation.objects.get_or_create(
                    page=page,
                    language=language,
                    defaults=payload,
                )
                if not created and payload:
                    changed = False
                    for field in ("title", "search_description", "body", "content"):
                        seeded = payload.get(field, {} if field == "content" else "")
                        if self.force or not getattr(translation, field):
                            setattr(translation, field, seeded)
                            changed = True
                    if changed:
                        translation.save(update_fields=["title", "search_description", "body", "content", "updated_at"])

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
        # Scope the lookup to this exact parent. A depth-only lookup can find
        # an identically-slugged page elsewhere in a fresh test tree, then
        # still attempt to add a duplicate child under the current parent.
        existing_node = parent.get_children().filter(slug=slug).first()
        if existing_node is not None:
            existing = existing_node.specific
            if not isinstance(existing, model):
                # Wagtail's migration fixture can leave a generic Page at the
                # exact slug we now own. Keep it temporarily as a Treebeard
                # sibling while allocating the concrete landing node; deleting
                # the only child first makes older Treebeard releases call
                # _inc_path() on None. The cleanup below removes this renamed
                # placeholder after the concrete page exists.
                placeholder_slug = f"{slug}-placeholder"
                existing_node.slug = placeholder_slug
                existing_node.save(update_fields=["slug"])
            else:
                self._backfill_empty_fields(existing, fields)
                return existing, False
        page = model(**fields)
        parent.add_child(instance=page)
        # If a generic placeholder occupied this exact parent/slug, remove it
        # after the concrete sibling has been allocated safely.
        if existing_node is not None and not isinstance(existing_node.specific, model):
            existing_node.delete()
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
            if name == "slug":
                continue  # slugs anchor the tree; never rewritten
            # Titles are only rewritten for ProductPage (the catalog rename
            # path); every other page keeps its title even under --force so
            # editor-customized About/Blog titles are never clobbered.
            if name == "title" and not isinstance(existing, ProductPage):
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
