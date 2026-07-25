"""
Shared static page content definitions for the LMS.

Moved from ``www.api.pages`` to a reusable plugin module so that both the
API views and the django-fusion fragment components can import the same
canonical page data without circular imports.

Query priority (Wagtail CMS-first):
    ``get_page_for_language()`` queries Wagtail ``Page.objects.live()``
    first, converting results to the frontend contract via
    ``page_to_dict()``.  When no Wagtail page exists for a slug it falls
    back to the hardcoded ``STATIC_PAGES`` dict (demo / development data).

Language support:
    ``STATIC_PAGES`` holds the canonical English content.  Per-language
    overrides live in ``STATIC_PAGE_TRANSLATIONS`` — a dict of dicts
    keyed first by language code then by page slug.  Any field present
    in the translation dict replaces the matching field in the
    English page data (deep merge for blocks).

    To add a new language, add entries to ``STATIC_PAGE_TRANSLATIONS``
    and ensure the language code appears in ``settings.LANGUAGES``.
"""

import logging

logger = logging.getLogger(__name__)

# ── Wagtail CMS imports (optional — the module works without Wagtail) ──
try:
    from wagtail.models import Page
    from www.content.models.pages import page_to_dict

    _WAGTAIL_AVAILABLE = True
except ImportError:
    _WAGTAIL_AVAILABLE = False
    Page = None  # type: ignore[assignment]
    page_to_dict = None  # type: ignore[assignment]
    logger.warning("Wagtail not available — STATIC_PAGES fallback only")


def cta(label, href, variant="primary"):
    return {"label": label, "href": href, "variant": variant}


STATIC_PAGES = {
    "home": {
        "slug": "home",
        "title": "Learn Without Limits",
        "seo": {
            "title": "LMS Platform | Learn Without Limits",
            "description": "Master new skills with expert-led courses, interactive content, and a community of learners.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Learn Without Limits",
                "intro": "Master new skills with expert-led courses, interactive content, and a community of learners.",
                "ctas": [
                    cta("Explore Courses", "/courses"),
                    cta("Get Started Free", "/registration", "secondary"),
                ],
            },
            {
                "type": "stats",
                "items": [
                    {"label": "Students", "value": "5K+"},
                    {"label": "Reviews", "value": "12K+"},
                ],
            },
            {
                "type": "section_header",
                "key": "featured_courses",
                "heading": "Featured Courses",
                "intro": "Most popular courses picked for you",
                "cta": cta("View All", "/courses", "link"),
            },
            {
                "type": "cta",
                "heading": "Start Learning Today",
                "intro": "Join thousands of students building skills for their next opportunity.",
                "ctas": [cta("Create Free Account", "/registration")],
            },
        ],
    },
    "about-us": {
        "slug": "about-us",
        "title": "About LMS Platform",
        "seo": {
            "title": "About LMS Platform",
            "description": "Empowering learners worldwide with quality education and expert-led courses.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "About LMS Platform",
                "intro": "Empowering learners worldwide with quality education and expert-led courses.",
            },
            {
                "type": "stats",
                "items": [
                    {
                        "label": "Students",
                        "value": "5K+",
                        "description": "Active learners worldwide",
                    },
                    {
                        "label": "Countries",
                        "value": "50+",
                        "description": "Global reach",
                    },
                ],
            },
            {
                "type": "rich_section",
                "heading": "Our Mission",
                "html": "<p>We believe quality education should be accessible to everyone. Our platform connects passionate instructors with eager learners, creating a community where knowledge knows no boundaries.</p>",
                "items": [
                    {
                        "heading": "Quality Content",
                        "text": "Courses crafted by industry experts with real-world experience",
                    },
                    {
                        "heading": "Flexible Learning",
                        "text": "Learn at your own pace with lifetime access to all materials",
                    },
                    {
                        "heading": "Community Driven",
                        "text": "Join a global community of learners and instructors",
                    },
                ],
            },
            {
                "type": "cta",
                "heading": "Ready to Get Started?",
                "intro": "Join our community and start learning today.",
                "ctas": [cta("Create Free Account", "/registration")],
            },
        ],
    },
    "privacy": {
        "slug": "privacy",
        "title": "Privacy Policy",
        "seo": {
            "title": "Privacy Policy",
            "description": "How LMS Platform collects, uses, discloses, and safeguards user information.",
        },
        "last_updated": "January 1, 2026",
        "blocks": [
            {
                "type": "rich_section",
                "heading": "1. Introduction",
                "html": "<p>Welcome to LMS Platform. We respect your privacy and are committed to protecting your personal data. This privacy policy explains how we collect, use, disclose, and safeguard your information when you visit our platform.</p>",
            },
            {
                "type": "rich_section",
                "heading": "2. Information We Collect",
                "html": "<p>We may collect account, profile, learning, payment, and technical data needed to operate the platform.</p>",
            },
            {
                "type": "rich_section",
                "heading": "3. How We Use Your Information",
                "html": "<p>We use your information to provide courses, process enrollments, personalize learning, communicate updates, issue certificates, prevent fraud, and comply with legal obligations.</p>",
            },
            {
                "type": "rich_section",
                "heading": "4. Data Sharing and Disclosure",
                "html": "<p>We do not sell personal information. We may share data with service providers, instructors for enrolled courses, and legal authorities when required.</p>",
            },
            {
                "type": "rich_section",
                "heading": "5. Data Security",
                "html": "<p>We use technical and organizational measures including encryption in transit, secure data centers, and access controls.</p>",
            },
            {
                "type": "rich_section",
                "heading": "6. Your Rights",
                "html": "<p>You may request access, correction, erasure, portability, or object to marketing-related processing.</p>",
            },
            {
                "type": "rich_section",
                "heading": "7. Cookies",
                "html": "<p>We use cookies and similar technologies to improve browsing, analyze traffic, and understand user journeys.</p>",
            },
            {
                "type": "rich_section",
                "heading": "8. Third-Party Links",
                "html": "<p>Our platform may link to third-party websites with their own privacy practices.</p>",
            },
            {
                "type": "rich_section",
                "heading": "9. Changes to This Policy",
                "html": "<p>We may update this privacy policy and will post the updated date on this page.</p>",
            },
            {
                "type": "rich_section",
                "heading": "10. Contact Us",
                "html": "<p>If you have questions about this policy, contact privacy@lmsplatform.com.</p>",
            },
        ],
    },
    "faq": {
        "slug": "faq",
        "title": "Frequently Asked Questions",
        "seo": {
            "title": "Frequently Asked Questions",
            "description": "Answers to common questions about LMS Platform.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Frequently Asked Questions",
                "intro": "Find answers to common questions about our platform",
            },
            {
                "type": "faq_groups",
                "groups": [
                    {
                        "title": "Getting Started",
                        "items": [
                            {
                                "question": "How do I create an account?",
                                "answer": "Click the Sign Up button, fill in your details, choose your role, and verify your email address.",
                            },
                            {
                                "question": "Is there a free trial?",
                                "answer": "Yes. New students can start with a 7-day free trial and no credit card is required.",
                            },
                            {
                                "question": "How do I enroll in a course?",
                                "answer": "Browse the course catalog, select a course, and click Enroll Now.",
                            },
                            {
                                "question": "Can I access courses on mobile?",
                                "answer": "Yes. The platform is responsive across phones, tablets, and desktops.",
                            },
                        ],
                    },
                    {
                        "title": "Account & Billing",
                        "items": [
                            {
                                "question": "What payment methods do you accept?",
                                "answer": "We accept major credit cards, PayPal, and selected local payment methods.",
                            },
                            {
                                "question": "Can I get a refund?",
                                "answer": "We offer a 30-day money-back guarantee for eligible course purchases.",
                            },
                        ],
                    },
                    {
                        "title": "Learning Experience",
                        "items": [
                            {
                                "question": "How are courses structured?",
                                "answer": "Courses are organized into modules and lessons with videos, readings, exercises, quizzes, and projects.",
                            },
                            {
                                "question": "Do I get a certificate?",
                                "answer": "Yes. Completed courses include a verifiable certificate.",
                            },
                        ],
                    },
                    {
                        "title": "For Instructors",
                        "items": [
                            {
                                "question": "How do I become an instructor?",
                                "answer": "Register as an instructor, complete your profile, and submit your course for review.",
                            }
                        ],
                    },
                    {
                        "title": "Technical Support",
                        "items": [
                            {
                                "question": "What browsers are supported?",
                                "answer": "Current versions of Chrome, Firefox, Safari, and Edge are supported.",
                            },
                            {
                                "question": "How do I reset my password?",
                                "answer": "Use Forgot Password on the login page and follow the emailed reset link.",
                            },
                        ],
                    },
                ],
            },
            {
                "type": "cta",
                "heading": "Still have questions?",
                "intro": "Can't find the answer you're looking for? We're here to help.",
                "ctas": [cta("Contact Support", "/contact")],
            },
        ],
    },
    "contact": {
        "slug": "contact",
        "title": "Contact Us",
        "seo": {
            "title": "Contact Us",
            "description": "Contact LMS Platform support and sales.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Contact Us",
                "intro": "We'd love to hear from you",
            },
            {
                "type": "contact_methods",
                "items": [
                    {
                        "type": "email",
                        "label": "Email",
                        "value": "support@lmsplatform.com",
                        "href": "mailto:support@lmsplatform.com",
                    },
                    {
                        "type": "phone",
                        "label": "Phone",
                        "value": "+1 (555) 123-4567",
                        "href": "tel:+15551234567",
                    },
                    {
                        "type": "address",
                        "label": "Address",
                        "value": "123 Learning St, Education City, EC 10001",
                    },
                    {
                        "type": "hours",
                        "label": "Hours",
                        "value": "Mon-Fri 9:00 AM - 6:00 PM EST",
                    },
                ],
            },
            {"type": "form", "heading": "Send us a message"},
        ],
    },
    "dashboard": {
        "slug": "dashboard",
        "title": "Dashboard",
        "seo": {
            "title": "Dashboard",
            "description": "Your learning dashboard",
        },
        "blocks": [
            {
                "type": "dashboard_welcome",
                "heading": "Welcome back!",
                "intro": "Here's your learning progress at a glance.",
            },
            {
                "type": "dashboard_quick_links",
                "heading": "Quick Links",
                "links": [
                    {"label": "My Courses", "href": "/dashboard/courses", "icon_class": "HiBookOpen"},
                    {"label": "Quizzes", "href": "/dashboard/quiz", "icon_class": "HiChartBar"},
                    {"label": "Announcements", "href": "/dashboard/announcement", "icon_class": "HiSpeakerphone"},
                ],
            },
            {
                "type": "dashboard_tip",
                "heading": "Pro Tip",
                "content": "Complete your profile to get personalized course recommendations.",
            },
        ],
    },
}


def normalize_slug(slug: str) -> str:
    """Normalize a URL slug to the keys used in ``STATIC_PAGES``."""
    return "home" if slug in ("", "home", "index") else slug.strip("/")


# ── Per-language overrides ──────────────────────────────────────────
#
# Keys: STATIC_PAGE_TRANSLATIONS[language_code][page_slug] = { ... }
# The overrides are shallow-merged on top of the English page.  Lists
# (e.g. ``blocks``) are replaced whole when present, so you must
# provide the complete block list for the translated page.

STATIC_PAGE_TRANSLATIONS: dict = {
    "fr": {
        "home": {
            "title": "Apprendre Sans Limites",
            "seo": {
                "title": "Plateforme LMS | Apprendre Sans Limites",
                "description": "Maîtrisez de nouvelles compétences avec des cours dirigés par des experts.",
            },
            "blocks": [
                {
                    "type": "hero",
                    "heading": "Apprendre Sans Limites",
                    "intro": "Maîtrisez de nouvelles compétences avec des cours dirigés par des experts, du contenu interactif et une communauté d'apprenants.",
                    "ctas": [
                        cta("Explorer les Cours", "/courses"),
                        cta("Essai Gratuit", "/registration", "secondary"),
                    ],
                },
                {
                    "type": "section_header",
                    "key": "featured_courses",
                    "heading": "Cours en Vedette",
                    "intro": "Les cours les plus populaires sélectionnés pour vous",
                    "cta": cta("Voir Tout", "/courses", "link"),
                },
                {
                    "type": "cta",
                    "heading": "Commencez à Apprendre Aujourd'hui",
                    "intro": "Rejoignez des milliers d'étudiants qui développent leurs compétences.",
                    "ctas": [cta("Créer un Compte Gratuit", "/registration")],
                },
            ],
        },
        "about-us": {
            "title": "À Propos de la Plateforme LMS",
            "blocks": [
                {
                    "type": "hero",
                    "heading": "À Propos de la Plateforme LMS",
                    "intro": "Donner aux apprenants du monde entier les moyens d'accéder à une éducation de qualité.",
                },
                {
                    "type": "rich_section",
                    "heading": "Notre Mission",
                    "html": "<p>Nous croyons que l'éducation de qualité doit être accessible à tous.</p>",
                    "items": [
                        {"heading": "Contenu de Qualité", "text": "Cours conçus par des experts du secteur"},
                        {"heading": "Apprentissage Flexible", "text": "Apprenez à votre rythme avec un accès illimité"},
                        {"heading": "Communauté", "text": "Rejoignez une communauté mondiale d'apprenants"},
                    ],
                },
                {
                    "type": "cta",
                    "heading": "Prêt à Commencer ?",
                    "intro": "Rejoignez notre communauté et commencez à apprendre.",
                    "ctas": [cta("Créer un Compte Gratuit", "/registration")],
                },
            ],
        },
        "contact": {
            "title": "Contactez-Nous",
            "blocks": [
                {
                    "type": "hero",
                    "heading": "Contactez-Nous",
                    "intro": "Nous serions ravis de vous entendre",
                },
            ],
        },
    },
    "es": {
        "home": {
            "title": "Aprende Sin Límites",
            "seo": {
                "title": "Plataforma LMS | Aprende Sin Límites",
                "description": "Domina nuevas habilidades con cursos dirigidos por expertos.",
            },
            "blocks": [
                {
                    "type": "hero",
                    "heading": "Aprende Sin Límites",
                    "intro": "Domina nuevas habilidades con cursos dirigidos por expertos, contenido interactivo y una comunidad de aprendizaje.",
                    "ctas": [
                        cta("Explorar Cursos", "/courses"),
                        cta("Prueba Gratis", "/registration", "secondary"),
                    ],
                },
                {
                    "type": "section_header",
                    "key": "featured_courses",
                    "heading": "Cursos Destacados",
                    "intro": "Los cursos más populares seleccionados para ti",
                    "cta": cta("Ver Todos", "/courses", "link"),
                },
                {
                    "type": "cta",
                    "heading": "Empieza a Aprender Hoy",
                    "intro": "Únete a miles de estudiantes desarrollando sus habilidades.",
                    "ctas": [cta("Crear Cuenta Gratis", "/registration")],
                },
            ],
        },
        "about-us": {
            "title": "Acerca de la Plataforma LMS",
            "blocks": [
                {
                    "type": "hero",
                    "heading": "Acerca de la Plataforma LMS",
                    "intro": "Empoderando a estudiantes de todo el mundo con educación de calidad.",
                },
                {
                    "type": "cta",
                    "heading": "¿Listo para Empezar?",
                    "intro": "Únete a nuestra comunidad y comienza a aprender.",
                    "ctas": [cta("Crear Cuenta Gratis", "/registration")],
                },
            ],
        },
    },
    "de": {
        "home": {
            "title": "Grenzenlos Lernen",
            "seo": {
                "title": "LMS-Plattform | Grenzenlos Lernen",
                "description": "Meistern Sie neue Fähigkeiten mit von Experten geleiteten Kursen.",
            },
            "blocks": [
                {
                    "type": "hero",
                    "heading": "Grenzenlos Lernen",
                    "intro": "Meistern Sie neue Fähigkeiten mit von Experten geleiteten Kursen, interaktiven Inhalten und einer Lerngemeinschaft.",
                    "ctas": [
                        cta("Kurse Entdecken", "/courses"),
                        cta("Kostenlos Testen", "/registration", "secondary"),
                    ],
                },
                {
                    "type": "cta",
                    "heading": "Beginnen Sie Heute zu Lernen",
                    "intro": "Werden Sie Teil tausender Studenten, die ihre Fähigkeiten ausbauen.",
                    "ctas": [cta("Kostenloses Konto", "/registration")],
                },
            ],
        },
    },
    "ar": {
        "home": {
            "title": "تعلم بلا حدود",
            "seo": {
                "title": "منصة LMS | تعلم بلا حدود",
                "description": "أتقن مهارات جديدة مع دورات يقودها خبراء ومحتوى تفاعلي.",
            },
            "blocks": [
                {
                    "type": "hero",
                    "heading": "تعلم بلا حدود",
                    "intro": "أتقن مهارات جديدة مع دورات يقودها خبراء ومحتوى تفاعلي ومجتمع من المتعلمين.",
                    "ctas": [
                        cta("استكشف الدورات", "/courses"),
                        cta("جرب مجاناً", "/registration", "secondary"),
                    ],
                },
                {
                    "type": "cta",
                    "heading": "ابدأ التعلم اليوم",
                    "intro": "انضم إلى آلاف الطلاب الذين يطورون مهاراتهم.",
                    "ctas": [cta("أنشئ حساباً مجانياً", "/registration")],
                },
            ],
        },
    },
}


def get_page_for_language(slug: str, language_code: str) -> dict | None:
    """Return the page content for *slug* translated into *language_code*.

    Query priority:
    1. Wagtail ``Page.objects.live()`` — CMS-managed content
    2. ``STATIC_PAGES`` + ``STATIC_PAGE_TRANSLATIONS`` — demo fallback

    Returns ``None`` when the slug is unknown in both sources.
    """
    normalized = normalize_slug(slug)

    # 1. Try Wagtail CMS first
    if _WAGTAIL_AVAILABLE:
        try:
            page = Page.objects.live().filter(slug=normalized).first()
            # Only match our custom content pages (which have a ``body``
            # StreamField), not the default Wagtail root/welcome pages.
            if page is not None and hasattr(page.specific, "body"):
                return page_to_dict(page.specific)
        except Exception:
            logger.debug("Wagtail page query failed for slug=%r — using static fallback", slug)

    # 2. Fall back to hardcoded STATIC_PAGES (demo / development data)
    page = STATIC_PAGES.get(normalized)
    if page is None:
        return None

    if language_code == "en" or not language_code:
        return page

    # Check for a translation override
    lang_overrides = STATIC_PAGE_TRANSLATIONS.get(language_code, {})
    override = lang_overrides.get(normalized)
    if override is None:
        return page

    # Shallow-merge the override on top of the English page
    merged: dict = {**page, **override}
    merged["slug"] = page["slug"]
    return merged
