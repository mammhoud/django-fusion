"""Management command to load course fixtures."""

import logging
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django_fusion.management.commands.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Load the canonical LMS and medical-research course fixtures."""

    help = "Load LMS and CTC medical-research course fixtures."

    fixture_dir = Path(__file__).resolve().parents[2] / "fixtures"
    fixture_names = (
        "specializations.json",
        "course_tags.json",
        "courses.json",
        "medical_research_catalog.json",
        "medical_research_curriculum.json",
        "events.json",
    )

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed loading information",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate fixture files without loading data.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help=(
                "Delete fixture-owned rows (courses, specializations, tags, "
                "modules, lessons, events, event translations) before loading. "
                "Omit for a non-destructive load that only adds missing rows."
            ),
        )

    def handle(self, *args, **options):
        """Execute the command."""
        verbose = options.get("verbose", False)
        dry_run = options.get("dry_run", False)
        replace = options.get("replace", False)

        missing = [
            name for name in self.fixture_names
            if not (self.fixture_dir / name).exists()
        ]
        if missing:
            raise CommandError(
                "Missing course fixture(s): " + ", ".join(missing)
            )
        if dry_run:
            for fixture_name in self.fixture_names:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {fixture_name} found ({self.fixture_dir / fixture_name})"
                    )
                )
            self.stdout.write(self.style.SUCCESS("\nDry run complete; no data loaded.\n"))
            return

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('📚 LOADING COURSE FIXTURES'))
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
        
        # Ensure we have an instructor user
        self._ensure_instructor_user()

        try:
            with transaction.atomic():
                if replace:
                    self._wipe_fixture_owned_rows()

                for fixture_name in self.fixture_names:
                    fixture_path = self.fixture_dir / fixture_name
                    self.stdout.write(f"Loading {fixture_name}...")
                    call_command(
                        "loaddata",
                        str(fixture_path),
                        verbosity=2 if verbose else 0,
                    )
                    self.stdout.write(self.style.SUCCESS(f"✓ {fixture_name} loaded\n"))

            # EventTranslation carries explicit integer PKs in events.json;
            # advance its sequence so later admin creates never collide.
            self._reset_event_translation_sequence()

            # Course API responses are cached by Django's shared production
            # middleware. Clear it after fixture reload so public consumers do
            # not receive the pre-reload response schema or catalog.
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✓ Shared API cache cleared\n"))

            # Show summary
            self._show_summary()
            
            self.stdout.write(self.style.SUCCESS('\n✅ All fixtures loaded successfully!\n'))
            self.stdout.write('🌐 Visit http://localhost:8000/courses/ to see courses\n')
            self.stdout.write('📊 Admin: http://localhost:8000/admin/\n')
            self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
            
        except Exception as exc:
            logger.exception("course fixture load failed")
            self.stdout.write(self.style.ERROR(f"\n❌ Error loading fixtures: {exc}\n"))
            raise CommandError("Unable to load course fixtures") from exc

    def _wipe_fixture_owned_rows(self):
        """Delete fixture-owned LMS rows before a replace load.

        ``loaddata`` inserts rows with explicit primary keys but the LMS
        models carry unique constraints (``lms.Course.title``/``slug``), so a
        re-run without wiping first aborts on ``IntegrityError``.  Children
        are deleted before parents so FK cascades stay deterministic.
        """
        from apps.handlers.models import Event, EventTranslation
        from apps.learning.models import (
            Course,
            CourseTag,
            Lesson,
            Module,
            Specialization,
        )

        # Handlers events first: EventTranslation references Event.
        deleted_translations = EventTranslation.objects.all().delete()[0]
        deleted_events = self._delete_events(Event)

        # Lesson → Module → Course: children reference their parents via
        # ParentalKey with CASCADE, so explicit order is just defensive.
        deleted_lessons = Lesson.objects.all().delete()[0]
        deleted_modules = Module.objects.all().delete()[0]
        deleted_courses = Course.objects.all().delete()[0]
        deleted_specializations = Specialization.objects.all().delete()[0]
        deleted_tags = CourseTag.objects.all().delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Removed existing rows "
                f"(courses={deleted_courses}, modules={deleted_modules}, "
                f"lessons={deleted_lessons}, specializations={deleted_specializations}, "
                f"tags={deleted_tags}, events={deleted_events}, "
                f"event_translations={deleted_translations})\n"
            )
        )

    @staticmethod
    def _delete_events(Event):
        """Delete all Event rows without tripping taggit's int object_id.

        ``Event`` uses a UUID primary key but ``TaggableManager`` stores its
        generic relation in ``TaggedItem.object_id`` (PositiveIntegerField).
        The cascade collector converts each UUID to a 128-bit int via
        ``int(uuid)``, which overflows SQLite/Postgres integer columns.  Clear
        the taggit rows by content type (an int filter — safe), then delete
        the events with raw SQL so the collector never builds an ``object_id
        IN (uuid, …)`` query.
        """
        from django.contrib.contenttypes.models import ContentType
        from django.db import connection
        from taggit.models import TaggedItem

        deleted_events = Event.objects.count()
        content_type = ContentType.objects.get_for_model(Event)
        TaggedItem.objects.filter(content_type=content_type).delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM %s" % Event._meta.db_table)
        return deleted_events

    @staticmethod
    def _reset_event_translation_sequence():
        """Advance the EventTranslation id sequence past explicit fixture PKs."""
        from django.db import connection

        if connection.vendor != "postgresql":
            return
        table = "handlers_eventtranslation"
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT setval("
                    "pg_get_serial_sequence(%s, 'id'), "
                    "(SELECT COALESCE(MAX(id), 1) FROM %s), true"
                    ") ",
                    [table, table],
                )
        except Exception:
            # Table may not exist in this checkout — best-effort only.
            pass

    def _ensure_instructor_user(self):
        """Ensure instructor user exists."""
        User = get_user_model()
        instructor = User.objects.filter(username="instructor").first()
        if instructor:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Using existing instructor user (ID: {instructor.id})\n"
                )
            )
            return

        password = os.environ.get("INSTRUCTOR_PASSWORD")
        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "⚠ No instructor user found; course fixtures require instructor "
                    "ID 1. Set INSTRUCTOR_PASSWORD to create it.\n"
                )
            )
            return

        instructor = User.objects.create_user(
            "instructor",
            os.environ.get("INSTRUCTOR_EMAIL", "instructor@example.com"),
            password,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created instructor user (ID: {instructor.id})\n"
            )
        )

    def _show_summary(self):
        """Show a summary of loaded data."""
        from apps.learning.models import Course, CourseTag, Specialization
        
        courses_count = Course.objects.count()
        tags_count = CourseTag.objects.count()
        specialization_count = Specialization.objects.count()
        published_courses = Course.objects.filter(is_published=True, is_active=True).count()
        featured_courses = Course.objects.filter(is_featured=True).count()
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📊 FIXTURE SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Total Courses:         {courses_count}')
        self.stdout.write(f'Published Courses:     {published_courses}')
        self.stdout.write(f'Featured Courses:      {featured_courses}')
        self.stdout.write(f'Course Tags:           {tags_count}')
        self.stdout.write(f'Specializations:       {specialization_count}')
        self.stdout.write('=' * 60 + '\n')
