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

    def handle(self, *args, **options):
        """Execute the command."""
        verbose = options.get("verbose", False)
        dry_run = options.get("dry_run", False)

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
                for fixture_name in self.fixture_names:
                    fixture_path = self.fixture_dir / fixture_name
                    self.stdout.write(f"Loading {fixture_name}...")
                    call_command(
                        "loaddata",
                        str(fixture_path),
                        verbosity=2 if verbose else 0,
                    )
                    self.stdout.write(self.style.SUCCESS(f"✓ {fixture_name} loaded\n"))

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
        from apps.pages.lms.models import Course, CourseTag, Specialization
        
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
