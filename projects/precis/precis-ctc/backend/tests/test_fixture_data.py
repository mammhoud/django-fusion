"""
Real-fixture integration tests for precis-lms.

Loads the actual ``assets/fixtures/dump-data.json`` fixture into the test
database and verifies:

1. Fixture data loads cleanly (locales, pages, images, site, subscriptions).
2. The English home page is initialised at root (depth=2) with the ``en`` locale.
3. All six locale home pages exist (en, fr, de, es, ar, pt-br).
4. Child pages (about, contact, team, all-courses, events, services) exist
   under the English home page.
5. The default site's root page points to the English home page.
6. StreamField blocks deserialize on the real Wagtail models (the
   "components fit with fixture dynamic content" guarantee).
7. API endpoints (pages list, page data, page fragment, courses) return
   fixture-backed content.

The fixture references an ``admin`` user (page owner / subscriptions) and the
Wagtail ``Root > Media > Main Photos (assets)`` collection tree, so those are
created before ``loaddata``.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.shortcuts import render
from django.test import Client, RequestFactory, TestCase, override_settings
from wagtail.models import Collection, Locale, Page, Site

User = get_user_model()

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets" / "fixtures" / "dump-data.json"
)

# Locale codes present in dump-data.json (locale PKs 1..6)
EXPECTED_LOCALES = ["en", "fr", "de", "es", "ar", "pt-br"]

# Home page slugs per locale (depth=2)
HOME_SLUGS = {
    "en": "home",
    "fr": "home-fr",
    "de": "home-de",
    "es": "home-es",
    "ar": "home-ar",
    "pt-br": "home-pt-br",
}

# Every translated page family represented in dump-data.json.  The Arabic
# slugs are intentionally explicit because they are part of the public URL
# contract and cannot be inferred from the English slug.
TRANSLATED_PAGE_SLUGS = {
    "home": HOME_SLUGS,
    "about": {
        "en": "about",
        "fr": "about",
        "de": "about",
        "es": "about",
        "ar": "عن-سي-تي-سي-للبحث-العلمي",
        "pt-br": "about",
    },
    "contact": {code: "contact" for code in EXPECTED_LOCALES},
    "team": {
        "en": "team",
        "fr": "team",
        "de": "team",
        "es": "team",
        "ar": "فريقنا",
        "pt-br": "team",
    },
    "all-courses": {code: "all-courses" for code in EXPECTED_LOCALES},
    "events": {code: "events" for code in EXPECTED_LOCALES},
    "services": {code: "services" for code in EXPECTED_LOCALES},
}

# English child pages under /home/
EN_CHILD_SLUGS = ["about", "contact", "team", "all-courses", "events", "services"]

# Titles from the fixture (English locale)
EXPECTED_TITLES = {
    "home": "Home Page",
    "about": "About",
    "contact": "Contact",
    "team": "Our Team",
    "all-courses": "Courses",
    "events": "Upcoming Events",
    "services": "Our Capabilities",
}

# Localized home-page titles per locale (depth=2) from dump-data.json
EXPECTED_HOME_TITLES = {
    "en": "Home Page",
    "fr": "Page d'accueil",
    "de": "Startseite",
    "es": "Página de inicio",
    "ar": "الصفحة الرئيسية",
    "pt-br": "Página inicial",
}

# LMS app fixtures loaded on top of dump-data.json (courses/events)
LMS_FIXTURES = [
    "specializations.json",
    "course_tags.json",
    "courses.json",
    "medical_research_catalog.json",
    "medical_research_curriculum.json",
    "events.json",
]
LMS_FIXTURE_DIR = (
    Path(__file__).resolve().parent.parent
    / "apps" / "learning" / "fixtures"
)
RESEARCH_FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets" / "fixtures" / "research_publications.json"
)

# Expected LMS fixture content (spot checks — actual titles in courses.json)
EXPECTED_COURSES = {
    "Python Basics",
    "Data Science with Python",
    "Clinical Trial Design & Protocol Development",
    "Biostatistics for Clinical Research",
    "Systematic Reviews & Evidence Synthesis",
    "Medical AI & Clinical Data Analytics",
    "Scientific & Medical Manuscript Writing",
    "Research Ethics, GCP & Publication Integrity",
}
EXPECTED_MEDICAL_COURSE_SLUGS = {
    "clinical-trial-design-protocol-development",
    "biostatistics-clinical-research",
    "systematic-reviews-evidence-synthesis",
    "medical-ai-clinical-data-analytics",
    "scientific-medical-manuscript-writing",
    "research-ethics-gcp-publication-integrity",
}
EXPECTED_EVENTS = {"AI in Medical Writing Workshop"}

# StreamField block keys present on the fixture HomePage records
HOME_BLOCK_TYPES = {"slider", "features"}   # head
SUMMARY_BLOCK_TYPES = {"about", "listing_section"}  # summary
CTA_BLOCK_TYPES = {"contact_section", "why_choose_section", "clients"}  # CTA


@override_settings(ROOT_URLCONF="tests.urls")
class TestFixtureData(TestCase):
    """Load the real dump-data.json fixture and verify pages + APIs."""

    @classmethod
    def setUpTestData(cls):
        # ── 1. Content types (fixture uses natural keys) ────────────
        for app_config in apps.get_app_configs():
            try:
                create_contenttypes(app_config, interactive=False, verbosity=0)
            except Exception:
                pass

        # ── 2. Admin user (page owner / page subscriptions) ──────────
        User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True},
        )

        # ── 3. Wagtail collection tree (image FK targets) ────────────
        cls._ensure_collections()

        # ── 3.5 Purge auto-created initial site/pages ────────────────
        # Wagtail's post-migrate hook creates a "Welcome to your new
        # Wagtail site!" page at url_path "/home/" (path 00010001), which
        # collides with the fixture's own home page during natural-key
        # resolution of the site record ("get() returned more than one
        # Page"). Delete the auto-created site + non-root pages so the
        # fixture tree installs cleanly. (Same pattern as
        # test_setup_wagtail_home_creates_home_when_missing.)
        Site.objects.all().delete()
        for page in Page.objects.exclude(depth=1):
            page.delete()

        # ── 4. Load the fixture ──────────────────────────────────────
        call_command("loaddata", str(FIXTURE_PATH), verbosity=0)

        # ── 5. Load LMS app fixtures (courses, events, …) ─────────────
        # Fail loudly so a broken LMS fixture surfaces as a clear setup
        # error instead of a confusing empty-data assertion downstream.
        for name in LMS_FIXTURES:
            path = LMS_FIXTURE_DIR / name
            assert path.exists(), f"missing LMS fixture: {path}"
            call_command("loaddata", str(path), verbosity=0)

        assert RESEARCH_FIXTURE_PATH.exists(), f"missing research fixture: {RESEARCH_FIXTURE_PATH}"
        call_command("loaddata", str(RESEARCH_FIXTURE_PATH), verbosity=0)

        cls.client = Client()

    @staticmethod
    def _ensure_collections():
        """Create the collection tree referenced by fixture images."""
        root = Collection.objects.filter(name="Root").first()
        if root is None:
            root = Collection.add_root(name="Root")
        media = root.get_children().filter(name="Media").first()
        if media is None:
            media = root.add_child(name="Media")
        if not media.get_children().filter(name="Main Photos (assets)").exists():
            media.add_child(name="Main Photos (assets)")

    # ── Fixture integrity ──────────────────────────────────────────

    def test_locales_loaded(self):
        codes = set(Locale.objects.values_list("language_code", flat=True))
        for code in EXPECTED_LOCALES:
            assert code in codes, f"missing locale {code}"

    def test_fixture_pages_loaded(self):
        # Root + 6 locale home pages + 36 translated child pages.
        assert Page.objects.filter(live=True).count() >= 43

    def test_expected_page_slugs_present(self):
        slugs = set(Page.objects.filter(live=True).values_list("slug", flat=True))
        expected = {"root"} | set(HOME_SLUGS.values()) | set(EN_CHILD_SLUGS)
        assert expected.issubset(slugs), expected - slugs

    def test_admin_user_created(self):
        assert User.objects.filter(username="admin").exists()

    # ── Home page init at root (English) ───────────────────────────

    def test_english_home_page_at_root(self):
        home = Page.objects.get(depth=2, live=True, slug="home")
        assert home.title == "Home Page"
        assert home.locale.language_code == "en"
        assert home.get_parent().depth == 1

    def test_all_locale_home_pages(self):
        for locale_code, slug in HOME_SLUGS.items():
            home = Page.objects.filter(
                depth=2, live=True, slug=slug, locale__language_code=locale_code
            ).first()
            assert home is not None, (
                f"missing {locale_code} home page slug={slug}"
            )

    def test_every_page_family_is_seeded_for_every_locale(self):
        """Every archived page family has a live page in all six locales."""
        translation_keys = set()

        for family, slugs_by_locale in TRANSLATED_PAGE_SLUGS.items():
            family_keys = set()
            for locale_code in EXPECTED_LOCALES:
                slug = slugs_by_locale[locale_code]
                pages = Page.objects.filter(
                    live=True,
                    slug=slug,
                    locale__language_code=locale_code,
                )
                assert pages.count() == 1, (
                    f"expected one {family} page for {locale_code}: {slug}; "
                    f"found {pages.count()}"
                )
                page = pages.get()

                expected_depth = 2 if family == "home" else 3
                assert page.depth == expected_depth
                if family != "home":
                    parent = page.get_parent()
                    assert parent.slug == HOME_SLUGS[locale_code]
                    assert parent.locale.language_code == locale_code

                family_keys.add(page.translation_key)

            assert len(family_keys) == 1, (
                f"{family} pages are not linked by one translation key: {family_keys}"
            )
            translation_keys.update(family_keys)

        assert len(translation_keys) == len(TRANSLATED_PAGE_SLUGS)

    def test_all_locale_home_titles_match_fixture(self):
        """Every locale's home page title matches dump-data.json exactly."""
        for locale_code, expected in EXPECTED_HOME_TITLES.items():
            slug = HOME_SLUGS[locale_code]
            home = Page.objects.filter(
                depth=2, live=True, slug=slug, locale__language_code=locale_code
            ).first()
            assert home is not None, f"missing {locale_code} home {slug}"
            assert home.title == expected, (
                f"{locale_code} home title {home.title!r} != {expected!r}"
            )

    def test_english_child_pages(self):
        home = Page.objects.get(depth=2, live=True, slug="home")
        child_slugs = {c.slug for c in home.get_children().live()}
        for slug in EN_CHILD_SLUGS:
            assert slug in child_slugs, f"missing child page {slug}"

    def test_default_site_points_to_home(self):
        site = Site.objects.filter(is_default_site=True).first()
        assert site is not None
        assert site.root_page.slug == "home"
        assert site.root_page.locale.language_code == "en"

    # ── Home page init at root (setup_wagtail_home) ────────────────

    def test_setup_wagtail_home_keeps_fixture_root(self):
        """setup_wagtail_home keeps the fixture home as the site root (English)."""
        from django.core.management import call_command

        out, err = io.StringIO(), io.StringIO()
        call_command("setup_wagtail_home", stdout=out, stderr=err)
        assert "skipped" not in out.getvalue() + err.getvalue(), (
            out.getvalue() + err.getvalue()
        )
        site = Site.objects.filter(is_default_site=True).first()
        assert site is not None
        assert site.root_page.slug == "home"
        assert site.root_page.locale.language_code == "en"

    def test_setup_wagtail_home_keeps_root_on_second_run(self):
        """Running setup_wagtail_home twice does not change the site root."""
        from django.core.management import call_command

        site = Site.objects.filter(is_default_site=True).first()
        assert site is not None
        root_page_id_before = site.root_page_id

        call_command("setup_wagtail_home", stdout=io.StringIO(), stderr=io.StringIO())
        site.refresh_from_db()
        assert site.root_page_id == root_page_id_before

    def test_setup_wagtail_home_creates_home_when_missing(self):
        """setup_wagtail_home creates a HomePage under root when none exists."""
        from django.core.management import call_command

        from apps.content.models.pages.home import HomePage

        # Delete the default site FIRST — Wagtail PROTECTs pages that are a
        # Site.root_page, so deleting the English home while it is still the
        # site root would raise a ProtectedError.
        Site.objects.all().delete()
        for page in Page.objects.filter(
            depth=2, content_type__model="homepage"
        ):
            page.delete()

        # Capture stdout/stderr so silent command failures surface here.
        out, err = io.StringIO(), io.StringIO()
        call_command("setup_wagtail_home", stdout=out, stderr=err)
        assert "skipped" not in out.getvalue() + err.getvalue(), (
            out.getvalue() + err.getvalue()
        )

        home = HomePage.objects.filter(live=True, depth=2).first()
        assert home is not None
        assert home.slug == "home"
        assert home.locale.language_code == "en"
        site = Site.objects.filter(is_default_site=True).first()
        assert site is not None
        assert site.root_page_id == home.pk

    # ── StreamField block deserialization (components fit fixtures) ─

    def test_home_page_blocks_deserialize(self):
        """Fixture StreamField content loads on the real HomePage model."""
        from apps.content.models.pages.home import HomePage

        home = HomePage.objects.get(depth=2, live=True, slug="home")
        assert home.head, "head StreamField should not be empty"
        assert home.summary, "summary StreamField should not be empty"
        assert home.CTA, "CTA StreamField should not be empty"

        head_types = {b.block_type for b in home.head}
        assert head_types, "head should contain blocks"
        assert head_types & HOME_BLOCK_TYPES, (
            f"head blocks {head_types} should include {HOME_BLOCK_TYPES}"
        )

        summary_types = {b.block_type for b in home.summary}
        assert summary_types & SUMMARY_BLOCK_TYPES, (
            f"summary blocks {summary_types} should include {SUMMARY_BLOCK_TYPES}"
        )

        cta_types = {b.block_type for b in home.CTA}
        assert cta_types & CTA_BLOCK_TYPES, (
            f"CTA blocks {cta_types} should include {CTA_BLOCK_TYPES}"
        )

    def test_all_home_pages_blocks_deserialize(self):
        """Every locale home page's StreamFields deserialize without errors."""
        from apps.content.models.pages.home import HomePage

        for locale_code, slug in HOME_SLUGS.items():
            home = HomePage.objects.filter(
                live=True, slug=slug, locale__language_code=locale_code
            ).first()
            assert home is not None, f"missing {locale_code} home {slug}"
            # Accessing these properties forces block deserialization.
            # 'slider' and 'features' are nested StreamBlocks — force
            # iteration so nested block values deserialize too.
            for stream in (home.head, home.summary, home.CTA):
                for block in stream:
                    if block.block_type in ("slider", "features"):
                        list(block.value)

    # ── API — pages list ───────────────────────────────────────────

    def test_pages_api_returns_fixture_pages(self):
        response = self.client.get("/api/pages/")
        assert response.status_code == 200
        data = json.loads(response.content)
        slugs = {p["slug"] for p in data.get("pages", [])}
        assert "home" in slugs
        for slug in EN_CHILD_SLUGS:
            assert slug in slugs, f"API missing page {slug}"

    # ── API — page data ────────────────────────────────────────────

    def test_navigation_uses_short_page_labels(self):
        """Editorial page titles must not make the public header verbose."""
        response = self.client.get("/apis/navigation/")
        assert response.status_code == 200
        labels = {item["href"]: item["label"] for item in response.json()["nav_items"]}
        assert labels["/contact/"] == "Contact"
        assert labels["/courses/"] == "Courses"

    def test_about_navigation_children_feed_dropdown(self):
        """The About nav item carries its curated dropdown (founder/research/
        education/services), matching the Precis Landing organization contract.

        ``Team`` is deliberately absent from the dropdown: it is already a
        first-class top-level nav item (``/team/``), so including it here would
        render the label twice in the header.
        """
        response = self.client.get("/apis/navigation/")
        assert response.status_code == 200
        by_href = {item["href"]: item for item in response.json()["nav_items"]}
        about = by_href["/about/"]
        assert [child["href"] for child in about["children"]] == [
            "/about/founder/",
            "/about/research/",
            "/about/education/",
            "/services/",
        ]
        assert about["children"][0]["label"] == "Founder"
        # Team remains a top-level nav item exactly once in the header.
        team_slugs = [
            item["href"] for item in response.json()["nav_items"] if item["href"] == "/team/"
        ]
        assert team_slugs == ["/team/"]
        # Leaf items carry an empty children list for the shared header contract.
        assert by_href["/courses/"]["children"] == []

    def test_home_page_data(self):
        response = self.client.get("/api/pages/home/data/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["data"]["slug"] == "home"
        assert body["data"]["title"] == "Home Page"

    def test_about_page_data(self):
        response = self.client.get("/api/pages/about/data/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["data"]["slug"] == "about"
        assert body["data"]["title"] == "About"

    def test_unknown_page_data_returns_404(self):
        response = self.client.get("/api/pages/does-not-exist/data/")
        assert response.status_code == 404

    # ── API — locale-specific home slugs ───────────────────────────

    def test_locale_home_slugs_resolve(self):
        for locale_code, slug in HOME_SLUGS.items():
            response = self.client.get(f"/api/pages/{slug}/data/")
            assert response.status_code == 200, (
                f"{locale_code}: {slug} -> {response.status_code}"
            )
            body = json.loads(response.content)
            assert body["data"]["slug"] == slug
            assert len(body["data"].get("title") or "") > 3

    # ── API — Arabic Unicode slugs (mirrors language-switcher e2e) ─

    def test_arabic_team_slug_resolves(self):
        """Arabic team page resolves via Unicode slug فريقنا.

        The Django test client quotes the Unicode path for WSGI and the URL
        resolver unquotes it before matching (mirrors the e2e spec's
        encodeURIComponent usage).
        """
        response = self.client.get("/api/pages/فريقنا/data/")
        assert response.status_code == 200, response.status_code
        body = json.loads(response.content)
        assert "فريقنا" in body["data"]["title"]

    def test_arabic_about_slug_resolves(self):
        """Arabic about page resolves via Unicode slug عن-سي-تي-سي-للبحث-العلمي."""
        response = self.client.get("/api/pages/عن-سي-تي-سي-للبحث-العلمي/data/")
        assert response.status_code == 200, response.status_code
        body = json.loads(response.content)
        assert "سي تي سي" in body["data"]["title"]

    # ── API — page fragment pointers ───────────────────────────────

    def test_home_fragment_pointer(self):
        response = self.client.get("/api/pages/home/fragment/")
        assert response.status_code == 200
        body = json.loads(response.content)
        data = body["data"]
        # fusion_response() payload: component, fragment_name, fragment_url,
        # fusion_render_first + extra keys (page_slug, title, layout).
        assert data["fragment_name"].startswith("pages.")
        assert data["page_slug"] == "home"
        assert "fragment_url" in data
        assert isinstance(data["fusion_render_first"], bool)

    def test_home_fragment_page_route_renders_html(self):
        """GET /fragment/pages/home/ renders the content-only HTML fragment.

        This is the frontend's RenderModeSwitch/LiveFragment HTML road — it
        must return HTML (not the JSON pointer from /api/pages/<slug>/fragment/)
        and must never embed the full layout or the learning teaser.
        """
        response = self.client.get("/fragment/pages/home/", HTTP_HX_REQUEST="true")
        assert response.status_code == 200, response.status_code
        assert response["Content-Type"].startswith("text/html")
        body = response.content.decode()
        assert "<html" not in body.lower(), "fragment must not embed the document shell"
        assert "[ LEARNING / PREVIEW ]" not in body, (
            "home fragment must not carry the learning teaser"
        )

    def test_fragment_page_route_unknown_slug_returns_404(self):
        response = self.client.get("/fragment/pages/does-not-exist/", HTTP_HX_REQUEST="true")
        assert response.status_code == 404

    # ── Home learning section — single distinct teaser (once-only) ──

    def test_home_renders_single_distinct_learning_teaser(self):
        """The home page renders exactly ONE [ LEARNING / PREVIEW ] teaser.

        Never the catalog's [ LEARNING / PUBLIC CATALOG ] marker, never the
        old duplicated section markers, and never more than once per
        document (main.html is the only template that carries it).
        """
        from apps.content.models.pages.home import HomePage

        home = HomePage.objects.get(depth=2, live=True, slug="home")
        request = RequestFactory().get("/")
        html = render(request, "home/main.html", {"page": home}).content.decode()

        preview_count = html.count("[ LEARNING / PREVIEW ]")
        assert preview_count == 1, (
            "home must render exactly one distinct learning teaser; "
            f"found {preview_count}"
        )
        assert "PUBLIC CATALOG" not in html, (
            "the catalog marker must never appear on the home page"
        )
        # The teaser CTA must point at the seeded Wagtail catalog page
        # (slug `all-courses`). A bare /courses/ href 404s on the Django
        # road, silently killing the home's primary learning CTA.
        assert 'href="/all-courses/"' in html, (
            "teaser CTA must link to the seeded /all-courses/ catalog page"
        )
        assert "Learn by shipping." not in html, (
            "the old duplicated learning section marker must stay absent"
        )

    def test_home_fragment_never_contains_learning_teaser(self):
        """The HTMX home fragment omits the teaser so a swap can never
        render the learning section twice on the home page."""
        from apps.content.models.pages.home import HomePage

        home = HomePage.objects.get(depth=2, live=True, slug="home")
        request = RequestFactory().get("/")
        html = render(request, "home/fragment.html", {"page": home}).content.decode()

        assert "[ LEARNING / PREVIEW ]" not in html, (
            "fragment must not carry the teaser; snippet: "
            f"{html[max(0, html.find('LEARNING') - 60): html.find('LEARNING') + 120] if 'LEARNING' in html else 'none'}"
        )

    def test_learning_teaser_localized_per_locale(self):
        """The teaser copy follows the seeded-language gettext catalogs.

        Every seeded locale (ar, sv, fr, de, es, pt-br) must resolve its own
        title/intro/CTA from assets/locale catalogs, keeping the Django road
        in parity with the Astro road's teaser-translations map.
        """
        from django.utils import translation

        from apps.content.models.pages.home import HomePage

        home = HomePage.objects.get(depth=2, live=True, slug="home")
        request = RequestFactory().get("/")
        expectations = {
            "ar": "دورات تقدّم واضح",
            "sv": "Kurser med synliga framsteg",
            "fr": "Des cours avec une progression visible",
            "de": "Kurse mit sichtbarem Fortschritt",
            "es": "Cursos con progreso visible",
            "pt-br": "Cursos com progresso visível",
        }
        for lang, expected in expectations.items():
            with translation.override(lang):
                html = render(request, "home/main.html", {"page": home}).content.decode()
            assert expected in html, (
                f"{lang} teaser title missing from rendered home page"
            )
            # The English source copy must not leak into a localized render.
            assert "Courses with visible progress" not in html, (
                f"English teaser leaked into {lang} render"
            )

    # ── API — courses (LMS fixtures) ───────────────────────────────

    def test_courses_api_returns_200(self):
        response = self.client.get("/api/courses/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "data" in data

    def test_courses_api_returns_fixture_courses(self):
        """Courses endpoint surfaces generic and medical research fixtures."""
        response = self.client.get("/api/courses/?per_page=50")
        assert response.status_code == 200
        data = json.loads(response.content)
        titles = {c.get("title") for c in data.get("data", [])}
        slugs = {c.get("slug") for c in data.get("data", [])}
        for expected in EXPECTED_COURSES:
            assert expected in titles, (
                f"courses API missing fixture course {expected!r}; got {titles}"
            )
        assert EXPECTED_MEDICAL_COURSE_SLUGS.issubset(slugs)
        assert data["pagination"]["total"] >= len(EXPECTED_COURSES)

    def test_medical_research_courses_have_complete_learning_metadata(self):
        """Medical courses are published and contain usable research metadata."""
        from apps.learning.models import Course

        courses = Course.objects.filter(slug__in=EXPECTED_MEDICAL_COURSE_SLUGS)
        assert courses.count() == len(EXPECTED_MEDICAL_COURSE_SLUGS)
        for course in courses:
            assert course.is_published and course.is_active
            assert course.short_description
            assert course.objectives
            assert course.requirements
            assert course.target_audience
            assert course.duration > 0

    def test_medical_curriculum_has_rich_text_without_code_blocks(self):
        """Every seeded medical course has two modules and four rich-text lessons."""
        from apps.learning.models import Course

        courses = Course.objects.filter(slug__in=EXPECTED_MEDICAL_COURSE_SLUGS)
        assert courses.count() == len(EXPECTED_MEDICAL_COURSE_SLUGS)
        for course in courses:
            modules = list(course.modules.all())
            assert len(modules) == 2, course.slug
            lessons = [lesson for module in modules for lesson in module.lessons.all()]
            assert len(lessons) == 4, course.slug
            for lesson in lessons:
                block_types = {block.block_type for block in lesson.content}
                assert "rich_text" in block_types, lesson.slug
                assert "code" not in block_types, lesson.slug

    def test_medical_course_detail_api_returns_all_learning_content(self):
        """Course detail API exposes all seeded medical learning fields."""
        response = self.client.get(
            "/api/courses/medical-ai-clinical-data-analytics/"
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "medical-ai-clinical-data-analytics"
        assert data["objectives"]
        assert data["target_audience"]
        assert data["requirements"]
        assert "Medical AI & Digital Health" in data["specializations"]
        assert "Clinical Data" in data["tags"]
        assert isinstance(data["overview"], (str, list))
        # The learning path must surface the seeded modules and their lessons
        # (regression: the API used to filter a nonexistent `is_published`
        # field, silently returning an empty syllabus).
        assert data["modules"], "course detail API must expose modules"
        assert all(
            isinstance(m.get("lessons"), list) and m["lessons"] for m in data["modules"]
        ), "every module must expose at least one lesson"

    def test_courses_filters_api(self):
        response = self.client.get("/api/courses/filters/")
        assert response.status_code == 200

    def test_events_api_returns_fixture_events(self):
        """Events endpoint surfaces the events.json fixture records."""
        response = self.client.get("/api/events/")
        assert response.status_code == 200
        data = json.loads(response.content)
        titles = {e.get("title") for e in data.get("results", [])}
        for expected in EXPECTED_EVENTS:
            assert expected in titles, (
                f"events API missing fixture event {expected!r}; got {titles}"
            )

    def test_events_api_paginated_shape(self):
        """Events API returns DRF-style {results, count, next, previous}."""
        response = self.client.get("/api/events/")
        data = json.loads(response.content)
        assert "results" in data and "count" in data
        assert data["count"] >= 1
        assert "next" in data and "previous" in data

    def test_events_upcoming_api(self):
        """Upcoming events endpoint returns a raw array of future events."""
        from django.utils import timezone

        from apps.handlers.models.manage.event import Event

        response = self.client.get("/api/events/upcoming/")
        assert response.status_code == 200
        data = json.loads(response.content)
        # Frontend contract: raw list (not paginated dict)
        assert isinstance(data, list)
        # Dynamic expectation: every visible+active future event appears.
        # Mirror the endpoint contract exactly: it slices to the first 6
        # upcoming events, so only compare against that same bounded slice.
        expected_titles = set(
            Event.objects.filter(
                is_visible=True, is_active=True, start_date__gte=timezone.now()
            ).order_by("start_date").values_list("title", flat=True)[:6]
        )
        returned_titles = {e.get("title") for e in data}
        assert expected_titles.issubset(returned_titles), (
            expected_titles - returned_titles
        )
        assert len(data) <= 6

    def test_event_detail_api(self):
        """Event detail resolves via the UUID pk from events.json."""
        from apps.handlers.models.manage.event import Event

        event = Event.objects.filter(
            title="AI in Medical Writing Workshop"
        ).first()
        assert event is not None
        response = self.client.get(f"/api/events/{event.pk}/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["title"] == "AI in Medical Writing Workshop"

    def test_event_detail_unknown_uuid_404(self):
        """Unknown event UUID returns 404 (not 500)."""
        response = self.client.get(
            "/api/events/00000000-0000-0000-0000-000000000000/"
        )
        assert response.status_code == 404

    # ── Event translations (EventTranslation overlay) ─────────────

    def test_events_api_serves_localized_titles(self):
        """?lang= resolves the EventTranslation overlay for list rows."""
        response = self.client.get("/api/events/?lang=fr")
        assert response.status_code == 200
        data = json.loads(response.content)
        titles = {e.get("title") for e in data.get("results", [])}
        assert "Atelier : l'IA dans la rédaction médicale" in titles
        assert "AI in Medical Writing Workshop" not in titles

    def test_events_api_serves_localized_location(self):
        """The overlay location replaces the canonical venue."""
        response = self.client.get("/api/events/?lang=de")
        data = json.loads(response.content)
        rows = {e.get("title"): e.get("location") for e in data.get("results", [])}
        assert any("Online" in loc for loc in rows.values())

    def test_events_page_api_serves_localized_events(self):
        """The /apis/pages/events/ road also merges the overlay."""
        response = self.client.get("/apis/pages/events/?lang=es")
        assert response.status_code == 200
        data = json.loads(response.content)
        titles = {e.get("title") for e in data.get("events", [])}
        assert "Conferencia anual de IA médica 2026" in titles

    def test_events_page_hero_subtitle_is_localized(self):
        """EventPage intro_text feeds the localized hero subtitle."""
        response = self.client.get("/apis/pages/events/?lang=sv")
        assert response.status_code == 200
        data = json.loads(response.content)
        subtitle = data.get("hero", {}).get("subtitle", "")
        assert "Workshops, symposier och akademiska skrivsessioner" in subtitle

    # ── Arabic RTL overlay coverage (EventTranslation) ─────────────

    # The four seeded events that are visible + active; the fifth
    # (Medical Writers Meetup) is seeded inactive and must stay off the
    # public roads (see test_arabic_overlay_covers_inactive_event_below).
    AR_EVENT_TITLES = {
        "ورشة عمل الذكاء الاصطناعي في الكتابة الطبية",
        "ندوة البحث السريري المدفوع بالبيانات",
        "المؤتمر السنوي للذكاء الاصطناعي الطبي 2026",
        "ندوة عبر الإنترنت حول أفضل ممارسات مراجعة الأقران",
    }
    AR_EVENT_LOCATIONS = {
        "افتراضي - عبر زوم",
        "قاعة المؤتمرات A، المبنى 3",
        "مركز المؤتمرات الكبير",
        "عبر الإنترنت",
    }

    def test_events_api_serves_arabic_overlay_titles(self):
        """?lang=ar resolves the Arabic EventTranslation overlay (no English fallback)."""
        response = self.client.get("/api/events/?lang=ar")
        assert response.status_code == 200
        data = json.loads(response.content)
        titles = {e.get("title") for e in data.get("results", [])}
        assert titles == self.AR_EVENT_TITLES, titles
        # Every Arabic title is RTL content — none of the canonical English
        # titles may leak through the overlay merge.
        assert "AI in Medical Writing Workshop" not in titles

    def test_events_api_serves_arabic_overlay_locations(self):
        """The Arabic overlay replaces the canonical venue with RTL text."""
        response = self.client.get("/api/events/?lang=ar")
        assert response.status_code == 200
        data = json.loads(response.content)
        locations = {e.get("location") for e in data.get("results", [])}
        assert locations == self.AR_EVENT_LOCATIONS, locations
        assert "Virtual - Zoom" not in locations

    def test_events_page_api_serves_arabic_overlay(self):
        """The /apis/pages/events/ road also merges the Arabic overlay."""
        response = self.client.get("/apis/pages/events/?lang=ar")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data.get("language") == "ar"
        titles = {e.get("title") for e in data.get("events", [])}
        assert titles == self.AR_EVENT_TITLES, titles
        locations = {e.get("location") for e in data.get("events", [])}
        assert locations == self.AR_EVENT_LOCATIONS, locations

    def test_events_arabic_hero_subtitle_is_localized(self):
        """The Arabic EventPage intro_text feeds the localized hero subtitle."""
        response = self.client.get("/apis/pages/events/?lang=ar")
        assert response.status_code == 200
        data = json.loads(response.content)
        subtitle = data.get("hero", {}).get("subtitle", "")
        assert "ورش عمل وندوات وجلسات كتابة أكاديمية" in subtitle

    def test_arabic_overlay_covers_inactive_event(self):
        """The seeded inactive event still carries its Arabic overlay.

        The fifth event (Medical Writers Meetup) is seeded with
        ``is_active=False`` so it is filtered from both public roads, but its
        Arabic overlay must still exist in the DB — the full seed translated
        all five events, and toggling the event live later must surface RTL
        content immediately.
        """
        from apps.handlers.models import Event, EventTranslation

        event = Event.objects.get(title="Medical Writers Meetup")
        translation = EventTranslation.objects.filter(
            event=event, language="ar"
        ).first()
        assert translation is not None
        assert translation.title == "لقاء الكتاب الطبيين"
        assert translation.location == "صالة الكتاب، وسط المدينة"

        # Inactive → excluded from the list and page roads.
        for url in ("/api/events/?lang=ar", "/apis/pages/events/?lang=ar"):
            data = json.loads(self.client.get(url).content)
            rows = data.get("results", data.get("events", []))
            assert "لقاء الكتاب الطبيين" not in {e.get("title") for e in rows}

    def test_language_catalog_exposes_arabic_as_rtl(self):
        """The language catalog marks ar as RTL for the frontend layout switch."""
        response = self.client.get("/apis/content/languages/")
        assert response.status_code == 200
        data = json.loads(response.content)
        languages = {item["code"]: item for item in data.get("languages", [])}
        assert "ar" in languages
        assert languages["ar"]["dir"] == "rtl"
        assert all(
            item["dir"] == "ltr" for code, item in languages.items() if code != "ar"
        )

    # ── LMS fixture reload idempotency ────────────────────────────

    def test_load_course_fixtures_replace_is_idempotent(self):
        """A second ``load_course_fixtures --replace`` run must not raise.

        Regression: the LMS tables carry unique constraints (Course.title /
        slug), so re-running the loader on an already-populated database
        aborted with ``duplicate key value violates unique constraint
        "lms_course_title_key"``.  ``--replace`` wipes fixture-owned rows
        first, making the load re-runnable inside the ``load_data`` flow.
        """
        from apps.handlers.models import Event, EventTranslation
        from apps.learning.models import Course, CourseTag, Module, Specialization

        # First run already happened in setUpTestData — assert populated.
        assert Course.objects.filter(title="Clinical Trial Design & Protocol Development").exists()
        assert Event.objects.count() == 5
        assert EventTranslation.objects.count() == 30
        assert Specialization.objects.count() >= 5
        assert CourseTag.objects.count() >= 12
        assert Module.objects.exists()

        # Second run with --replace must complete without IntegrityError.
        call_command("load_course_fixtures", verbosity=0, replace=True)

        # Data is reloaded, not accumulated.
        assert Course.objects.filter(title="Clinical Trial Design & Protocol Development").exists()
        assert Course.objects.count() == 14
        assert Event.objects.count() == 5
        assert EventTranslation.objects.count() == 30

    def test_load_course_fixtures_without_replace_is_non_destructive(self):
        """Plain ``load_course_fixtures`` (no --replace) only adds missing rows."""
        from apps.handlers.models import Event

        before = Event.objects.count()
        call_command("load_course_fixtures", verbosity=0)
        # Events already exist, so a non-destructive load leaves them alone.
        assert Event.objects.count() == before

    # ── Team page completeness (full 10-member roster, no fallbacks) ─

    def test_team_pages_carry_full_roster_per_locale(self):
        """Every locale team page exposes the full translated roster."""
        from apps.content.models.pages.team import TeamPage

        team_pages = TeamPage.objects.all()
        assert team_pages.count() == 7  # en, ar, de, es, fr, pt-br, sv
        for page in team_pages:
            block = page.body[0].value if page.body else {}
            members = block.get("team_members", []) if isinstance(block, dict) else []
            assert len(members) == 10, (
                f"{page.locale.language_code} team page has {len(members)} members"
            )
            assert all(m.get("bio") for m in members), (
                f"{page.locale.language_code} team page has empty bios"
            )

    def test_team_api_serves_localized_roster(self):
        """The Astro team road returns localized member bios."""
        response = self.client.get("/apis/pages/team/?lang=de")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data.get("team_title") == "Lernen Sie die Innovatoren kennen"
        members = data.get("team_members", [])
        assert len(members) == 10
        assert all(m.get("bio") for m in members)

    def test_sv_team_page_served_without_fallback(self):
        """sv resolves its own team page (no English fallback)."""
        response = self.client.get("/apis/pages/team/?lang=sv")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data.get("team_title") == "Möt innovatörerna"
        assert len(data.get("team_members", [])) == 10

    # ── About mission/skills/faq translations ─────────────────────

    def test_about_mission_blocks_localized(self):
        """Non-English about pages expose translated mission/skills/faq."""
        for lang, expected in (("de", "Warum CTC Research"), ("es", "Por qué CTC Research")):
            response = self.client.get(f"/apis/pages/about/?lang={lang}")
            assert response.status_code == 200
            data = json.loads(response.content)
            assert data.get("mission_title") == expected, lang
            assert data.get("skills_title"), lang
            assert data.get("faq"), lang

    def test_sv_about_page_localized(self):
        """sv about page exposes the Swedish mission copy."""
        response = self.client.get("/apis/pages/about/?lang=sv")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data.get("mission_title") == "Varför CTC Research"

    # ── API — research documents ──────────────────────────────────

    def test_research_documents_are_localized_wagtail_snippets(self):
        response = self.client.get("/apis/research/publications/?lang=en")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        assert body["documents"][0]["language"] == "en"
        assert body["guidance"]["steps"]

        arabic = self.client.get("/apis/research/publications/?lang=ar")
        assert arabic.status_code == 200
        assert arabic.json()["documents"][0]["language"] == "ar"

    # ── API — health & branding ────────────────────────────────────

    def test_health(self):
        response = self.client.get("/api/health/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == 200
        assert "fusion_render_first" in data["data"]

    def test_branding(self):
        response = self.client.get("/api/branding/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "site_name" in data
