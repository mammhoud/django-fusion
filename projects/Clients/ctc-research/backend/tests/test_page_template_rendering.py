"""Regression tests for the services and events page templates.

Locks in the recreated ``services/includes/*`` and ``events/*`` component
templates (see CHANGELOG 2026-08-02 — the components were missing after the
template-tree consolidation and caused 500s in production). A missing or
renamed component now fails the suite instead of silently 500ing at runtime.

Pages are rendered through the real WagtailPageMixin pipeline
(``page.serve(request)``), so the ``{% comp %}`` resolution of every
``services/includes/*`` and ``events/includes/*`` template is exercised.
"""
from __future__ import annotations

import base64
from pathlib import Path

from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import RequestFactory, TestCase, override_settings
from wagtail.images.models import Image
from wagtail.models import Collection, Locale, Page, Site

from apps.content.models.pages.about import AboutPage
from apps.content.models.pages.events import EventPage
from apps.content.models.pages.services import ServicesPage
from apps.pages.accounts.models import Event

User = get_user_model()

# On the host, ``active_site_dir()`` resolves to the project folder
# (``projects/precis-lms``) rather than the Django root (``backend/``), so the
# site templates are not on the default search path. Prepending the backend
# template dirs replicates the container layout where the backend is mounted
# directly at the site root.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_EXTRA_TEMPLATE_DIRS = [
    str(_BACKEND_DIR / "templates"),
    str(_BACKEND_DIR / "apps" / "templates"),
]


def _templates_override():
    """Copy the active TEMPLATES config with the backend dirs prepended."""
    template_cfg = dict(dj_settings.TEMPLATES[0])
    dirs = list(template_cfg.get("DIRS", []))
    for extra in reversed(_EXTRA_TEMPLATE_DIRS):
        if extra not in dirs:
            dirs.insert(0, extra)
    template_cfg["DIRS"] = dirs
    return [template_cfg]


TEMPLATES_OVERRIDE = _templates_override()


@override_settings(ROOT_URLCONF="tests.urls", TEMPLATES=TEMPLATES_OVERRIDE)
class TestPageTemplateRendering(TestCase):
    """ServicesPage and EventPage render through the new component templates."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(username="tpltest", password="x")

        # Migrations are disabled in tests, so the default 'en' locale row is
        # not seeded — create it before saving any page.
        cls.en, _ = Locale.objects.get_or_create(language_code="en")

        root = Page.get_first_root_node()
        if root is None:
            root = Page.add_root(
                instance=Page(title="Root", slug="root", live=True)
            )
        cls.root = root

        cls.services = cls.root.add_child(
            instance=ServicesPage(
                title="Services",
                slug="services",
                live=True,
                intro_text="Our services overview.",
                owner=cls.user,
            )
        )
        cls.events = cls.root.add_child(
            instance=EventPage(
                title="Events",
                slug="events",
                live=True,
                intro_text="Upcoming events.",
                owner=cls.user,
            )
        )
        Site.objects.update_or_create(
            hostname="testserver",
            port=80,
            defaults={
                "root_page": cls.root,
                "is_default_site": True,
                "site_name": "CTC Research Test",
            },
        )

        # One active event so the grid renders real backend data.
        cls.event = Event.objects.create(
            title="Test Workshop",
            description="Hands-on session",
            event_type=Event.EventType.WORKSHOP,
            location="Online",
        )

    def _render(self, page):
        """Render a page through the real serve() pipeline."""
        request = self.factory.get(page.url_path)
        request.user = self.user
        response = page.serve(request)
        response.render()
        return response

    def test_services_page_renders_new_components(self):
        """services/main.html + services/includes/page_title.html render."""
        response = self._render(self.services)
        assert response.status_code == 200, response.content[:500]
        content = response.content.decode()
        # services/includes/page_title.html hero section
        assert "page-title" in content
        # dynamic page title + intro text from the backend model
        assert "Services" in content
        assert "Our services overview" in content

    def test_events_page_renders_new_components(self):
        """events/main.html + events/includes/events_grid.html render."""
        response = self._render(self.events)
        assert response.status_code == 200, response.content[:500]
        content = response.content.decode()
        # events/main.html wrapper class
        assert "events-page" in content
        # events/includes/events_grid.html card markup
        assert "event-card" in content
        # dynamic event data from the DB appears in the rendered grid
        assert "Test Workshop" in content
        assert "Online" in content

    def test_events_grid_shows_paginated_items(self):
        """BaseIndexPage pagination feeds page_items into the grid."""
        response = self._render(self.events)
        assert response.status_code == 200
        content = response.content.decode()
        # The single active event is listed exactly once as a card.
        assert content.count("event-card__title") == 1

    def test_about_page_renders_sections(self):
        """about/main.html + about/sections/{about,testimonials,clients}.html render.

        Locks in the about sections that were missing after the template-tree
        consolidation and caused HTTP 500s on /about/ (they now render through
        the real WagtailPageMixin pipeline with backend block data).
        """
        about = self.root.add_child(
            instance=AboutPage(
                title="About",
                slug="about",
                live=True,
                owner=self.user,
                head=[("page_title", {"page_title": "About Us", "breadcrumb_home_text": "Home"})],
                facts=[
                    ("about", {
                        "welcome_text": "Welcome to CTC Research",
                        "main_title": "Who We Are",
                        "description": "Built on CTC Research.",
                        "years_experience": 20,
                    }),
                    ("testimonials", {
                        "subtitle": "Feedback",
                        "title": "What Clients Say",
                        "testimonials": [
                            ("testimonial", {
                                "content": "Outstanding platform.",
                                "client_name": "Jane Doe",
                                "client_position": "CEO",
                            }),
                        ],
                    }),
                    ("clients", []),
                ],
            )
        )
        response = self._render(about)
        assert response.status_code == 200, response.content[:500]
        content = response.content.decode()
        # about/main.html + content.page_title component hero
        assert "page-title" in content
        # dynamic backend block data rendered through about/sections/about.html
        assert "Who We Are" in content
        assert "Welcome to CTC Research" in content
        # about/sections/testimonials.html renders the block's client data
        assert "What Clients Say" in content
        assert "Outstanding platform." in content
        assert "Jane Doe" in content

    def test_about_page_renders_gallery_counters_and_video(self):
        """The media gallery, counters, experience, and video blocks render.

        Locks in the StreamBlock → ListBlock migration: the gallery renders via
        ``{% include_block %}`` (Wagtail block rendering) instead of the legacy
        ``{% comp %}`` wrapper, and its items render through
        ``blocks/media/gallery_item.html`` with the ``self``/``value`` contract.
        """
        root_collection = Collection.get_first_root_node()
        if root_collection is None:
            root_collection = Collection.add_root(name="Root")
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
            "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        image = Image.objects.create(
            title="Gallery Test",
            file=ContentFile(png, name="gallery.png"),
            collection=root_collection,
        )

        about = self.root.add_child(
            instance=AboutPage(
                title="About Gallery",
                slug="about-gallery",
                live=True,
                owner=self.user,
                head=[("page_title", {"page_title": "About Us", "breadcrumb_home_text": "Home"})],
                facts=[
                    ("about", {
                        "welcome_text": "Welcome",
                        "main_title": "Our Story",
                        "description": "About the center.",
                        "years_experience": 20,
                        "experience_description": "<p>Two decades of research.</p>",
                        "video_link": "https://www.youtube.com/watch?v=abc",
                        "counters": [
                            ("counter", {"icon_class": "fas fa-flask", "number": 120, "label": "Projects"}),
                        ],
                        "gallery": {
                            "gallery_title": "Media",
                            "gallery_description": "",
                            "lightbox_enabled": True,
                            "lazy_loading": True,
                            "media_items": [
                                {
                                    "media_type": "image",
                                    "image": {"image": image, "alternative_text": "Lab photo", "lazy_loading": True},
                                    "video": {"embed_url": ""},
                                    "caption": "<p>Our lab</p>",
                                    "category": "research",
                                    "featured": False,
                                },
                                {
                                    "media_type": "video",
                                    "image": {},
                                    "video": {"embed_url": "https://www.youtube.com/watch?v=xyz"},
                                    "caption": "",
                                    "category": "",
                                    "featured": False,
                                },
                            ],
                        },
                    }),
                ],
            )
        )
        response = self._render(about)
        assert response.status_code == 200, response.content[:500]
        content = response.content.decode()
        # gallery wrapper + items (image alt text + video placeholder)
        assert "media-gallery" in content
        assert "media-item" in content
        assert "Lab photo" in content
        assert "bi-play-circle" in content
        # counters
        assert ">120<" in content
        assert "Projects" in content
        # experience + video link
        assert "Two decades of research" in content
        assert "Watch Video" in content
