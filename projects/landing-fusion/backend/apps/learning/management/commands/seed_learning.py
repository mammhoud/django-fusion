"""Seed the public Structa Cloud learning catalog.

Usage::

    python manage.py seed_learning

The command is intentionally idempotent: editors can continue changing the
course in Wagtail without a later seed replacing their description or lessons.
Only missing records and the stable YouTube channel metadata are backfilled.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.html import format_html

from apps.learning.models import Course, Lesson, Module


YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@mammhoud"
COURSE_SLUG = "ship-django-products"


MODULES = [
    {
        "order": 1,
        "title": "The document-first foundation",
        "description": "Start with the customer journey, finished HTML, and an editorial model your team can own.",
        "lessons": [
            ("A page is a product surface", "Choose the smallest useful journey and turn it into a clear document.", 18, True),
            ("Model content around decisions", "Shape Wagtail fields and reusable sections around the questions customers ask.", 24, True),
            ("Build a fast first response", "Keep the critical path small, readable, and measurable on real regional networks.", 22, False),
        ],
    },
    {
        "order": 2,
        "title": "HTMX interactions without a SPA",
        "description": "Add useful interaction while keeping the server response as the source of truth.",
        "lessons": [
            ("Fragments as a UI contract", "Return the exact HTML region that changes and let the browser swap it in.", 20, False),
            ("Forms, validation, and CSRF", "Handle success and failure states with progressive enhancement and safe defaults.", 27, False),
            ("Loading, empty, and error states", "Make the slow path feel intentional instead of hiding it behind a spinner.", 19, False),
        ],
    },
    {
        "order": 3,
        "title": "Alpine for the small moments",
        "description": "Use a small amount of declarative state for menus, accordions, and learner progress.",
        "lessons": [
            ("State at the edge", "Keep Alpine state local and avoid rebuilding the page in the browser.", 21, False),
            ("Accessible accordions and menus", "Pair transitions with keyboard behavior, labels, and escape paths.", 26, False),
            ("Course progress that stays honest", "Update progress from completed lessons and keep certificates derived from evidence.", 23, False),
        ],
    },
    {
        "order": 4,
        "title": "Test, ship, and hand over",
        "description": "Finish with checks that protect the critical path and a deployment your team can understand.",
        "lessons": [
            ("Test the real route", "Verify HTML, API contracts, links, assets, and the browser console before release.", 25, False),
            ("Performance as a launch feature", "Set budgets for first paint, images, JavaScript, and server response time.", 18, False),
            ("A calm production handoff", "Document the content model, environment variables, logs, and rollback path.", 24, False),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the public Structa Cloud course catalog."

    def handle(self, *args, **options):
        User = get_user_model()
        instructor, created = User.objects.get_or_create(
            username="mammhoud",
            defaults={
                "email": "mammhoud@structa.cloud",
                "first_name": "Mahmoud",
                "last_name": "Ezzat",
            },
        )
        if created:
            instructor.set_unusable_password()
            instructor.save(update_fields=["password"])

        description = format_html(
            "<p>Build a useful digital service with the AHA stack: Astro for documents, "
            "HTMX for server-rendered interactions, and Alpine for small moments of state.</p>"
            "<p>This practical path is for founders, product teams, and developers who want "
            "fast pages that remain editable, testable, and easy to hand over. You will "
            "finish with a working course-sized product slice and a release checklist.</p>"
            "<h2>What you will be able to do</h2>"
            "<ul><li>Design content and routes around real customer decisions</li>"
            "<li>Build search, forms, menus, and progress with progressive enhancement</li>"
            "<li>Protect the critical path with backend, static, and browser checks</li>"
            "<li>Ship a maintainable handoff instead of a fragile demo</li></ul>"
        )
        course, course_created = Course.objects.get_or_create(
            slug=COURSE_SLUG,
            defaults={
                "title": "Ship Django Products with HTMX and Alpine",
                "short_description": "A practical, document-first course for building fast, content-driven products that teams can own.",
                "description": description,
                "instructor": instructor,
                "language": "en",
                "difficulty": "intermediate",
                "duration_hours": "6.5",
                "price": "0.00",
                "is_published": True,
                "is_featured": True,
                "has_certificate": True,
                "youtube_channel_url": YOUTUBE_CHANNEL_URL,
                "youtube_channel_name": "Mahmoud Ezzat · @mammhoud",
            },
        )
        changed = []
        if course.instructor_id != instructor.pk:
            course.instructor = instructor
            changed.append("instructor")
        if not course.youtube_channel_url:
            course.youtube_channel_url = YOUTUBE_CHANNEL_URL
            changed.append("youtube_channel_url")
        if not course.youtube_channel_name:
            course.youtube_channel_name = "Mahmoud Ezzat · @mammhoud"
            changed.append("youtube_channel_name")
        if not course.is_published:
            course.is_published = True
            changed.append("is_published")
        if not course.is_featured:
            course.is_featured = True
            changed.append("is_featured")
        if not course.has_certificate:
            course.has_certificate = True
            changed.append("has_certificate")
        if changed:
            course.save(update_fields=[*changed, "updated_at"])

        for module_data in MODULES:
            module, _ = Module.objects.get_or_create(
                course=course,
                order=module_data["order"],
                defaults={
                    "title": module_data["title"],
                    "description": module_data["description"],
                },
            )
            for lesson_order, lesson_data in enumerate(module_data["lessons"], start=1):
                Lesson.objects.get_or_create(
                    module=module,
                    order=lesson_order,
                    defaults={
                        "title": lesson_data[0],
                        "description": lesson_data[1],
                        "duration_minutes": lesson_data[2],
                        "is_preview": lesson_data[3],
                        "is_active": True,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Created' if course_created else 'Found'} course '{course.slug}' "
                f"with {course.modules.count()} modules and channel {YOUTUBE_CHANNEL_URL}"
            )
        )
