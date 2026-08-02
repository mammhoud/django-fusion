"""
Django management command to populate Courses and Events pages with sample content.

Run on the remote server::

    docker exec fusion-cms-website python manage.py populate_courses
    docker exec fusion-cms-website python manage.py populate_courses --dry-run

Options:
    --courses-only    Only populate course data (skip events)
    --events-only     Only populate event data (skip courses)
    --dry-run         Show what would be done without saving
"""

from importlib import import_module
from pathlib import Path

from django.core.management.base import CommandError
from django_fusion.management.commands.base import BaseCommand


class Command(BaseCommand):
    help = "Populate site Courses and Events pages with sample content"

    courses_page_model = ""
    course_model = ""
    home_page_model = ""
    event_page_model = ""
    course_fixtures_dir: Path | None = None
    events_fixture: Path | None = None

    @staticmethod
    def _load_model(path: str):
        module_name, class_name = path.rsplit(".", 1)
        return getattr(import_module(module_name), class_name)

    def _model(self, path: str):
        if not path:
            raise CommandError("populate_courses requires site model configuration")
        return self._load_model(path)

    def add_arguments(self, parser):
        parser.add_argument(
            "--courses-only",
            action="store_true",
            help="Only populate course data (skip events)",
        )
        parser.add_argument(
            "--events-only",
            action="store_true",
            help="Only populate event data (skip courses)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without saving",
        )

    def handle(self, *args, **options):
        if not options.get("events_only"):
            self._handle_courses(options)
        if not options.get("courses_only"):
            self._handle_events(options)

    # ── Courses ────────────────────────────────────────────────────────────

    def _handle_courses(self, options):
        from django.core.management import call_command

        self.stdout.write(self.style.SUCCESS("\n📚 Courses Setup\n"))

        # Step 1: Load course fixtures from plugin directory
        if self.course_fixtures_dir is None:
            raise CommandError("populate_courses requires a course fixtures directory")
        lms_fixtures = self.course_fixtures_dir
        for name in ("specializations.json", "course_tags.json", "courses.json"):
            path = lms_fixtures / name
            if not path.exists():
                self.stdout.write(f"   ⚠️  Fixture not found: {path}")
                continue
            if options["dry_run"]:
                self.stdout.write(f"   📋 Would load: {name}")
            else:
                try:
                    call_command("loaddata", str(path), verbosity=0)
                    self.stdout.write(f"   ✅ Loaded: {name}")
                except Exception as e:
                    self.stdout.write(f"   ⏭️  Skipped: {name} ({e})")

        # Step 2: Find or create CoursesPage
        courses_page = self._get_or_create_courses_page(options)
        if courses_page is None:
            self.stderr.write(self.style.ERROR(
                "❌ Could not find or create CoursesPage."
            ))
            return

        # Step 3: Populate CoursesPage header if empty
        self._populate_courses_header(courses_page, options)

        # Step 4: Link published courses
        self._link_courses(courses_page, options)

        # Step 5: Save and publish
        if not options["dry_run"]:
            import django.db.transaction as transaction
            with transaction.atomic():
                revision = courses_page.save_revision(log_action=True)
                revision.publish()
                courses_page.refresh_from_db()

            self.stdout.write(self.style.SUCCESS(
                "\n✅ CoursesPage populated and published!\n"
                "   View at: https://fusion-cms.com/home/all-courses/\n"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\n📋 Dry run complete — no changes written.\n"
            ))

    def _get_or_create_courses_page(self, options):
        """Find the existing CoursesPage or create one under the HomePage."""
        from wagtail.models import Page

        CoursesPage = self._model(self.courses_page_model)
        page = CoursesPage.objects.live().first()
        if page:
            if options["dry_run"]:
                self.stdout.write(f"   📋 Would use existing CoursesPage (id={page.id})")
            else:
                self.stdout.write(f"   🧭 Found CoursesPage: {page.title} (id={page.id})")
            return page

        # Find the configured HomePage to create CoursesPage under it.
        HomePage = self._model(self.home_page_model)
        home = HomePage.objects.live().first()
        if home is None:
            # Fallback: find any depth=2 live page
            home = Page.objects.live().filter(depth=2).first()
        if home is None:
            return None

        if options["dry_run"]:
            self.stdout.write("   📋 Would create new CoursesPage under HomePage")
            return None

        self.stdout.write("   🆕 Creating CoursesPage...")
        page = CoursesPage(
            title="All Courses",
            slug="all-courses",
            introduction=(
                "Explore our comprehensive catalog of professional courses "
                "designed to advance your career and skills."
            ),
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(f"   ✅ Created CoursesPage (id={page.id})")
        return page

    def _populate_courses_header(self, page, options):
        """Add a page_title header block to the courses page."""
        if page.head.raw_data:
            if options["dry_run"]:
                self.stdout.write("   📋 Header already populated, skipping")
            else:
                self.stdout.write("   ⏭️  Header already populated, skipping")
            return

        header_data = {
            "type": "page_title",
            "value": {
                "page_title_background": None,
                "page_title": "Our Courses",
                "breadcrumb_home_text": "Home",
            },
            "id": "courses-header-1",
        }

        if options["dry_run"]:
            self.stdout.write("   📋 Would add header: 'Our Courses'")
        else:
            page.head.raw_data = [header_data]
            self.stdout.write("   ✅ Header populated")

    def _link_courses(self, page, options):
        """Link all published, active courses to the CoursesPage."""
        Course = self._model(self.course_model)
        courses = Course.objects.filter(is_active=True, is_published=True)
        count = courses.count()

        if count == 0:
            if options["dry_run"]:
                self.stdout.write("   📋 No published courses found")
            else:
                self.stdout.write("   ⚠️  No published courses found. Load courses.json first.")
            return

        if options["dry_run"]:
            self.stdout.write(f"   📋 Would link {count} courses")
            return

        page.selected_courses.set(courses)
        page.introduction = (
            f"Explore our catalog of {count} professional courses designed "
            "to advance your career. Filter by difficulty, topic, or search "
            "for exactly what you need."
        )
        self.stdout.write(f"   ✅ Linked {count} courses")

    # ── Events ─────────────────────────────────────────────────────────────

    def _handle_events(self, options):
        from django.core.management import call_command
        from django.db import transaction

        self.stdout.write(self.style.SUCCESS("\n📅 Events Setup\n"))

        # Step 1: Load events fixture
        if self.events_fixture is None:
            self.stdout.write("   ℹ️  No events fixture configured")
            return
        events_fixture = self.events_fixture
        if events_fixture.exists():
            if options["dry_run"]:
                self.stdout.write("   📋 Would load: events.json")
            else:
                try:
                    call_command("loaddata", str(events_fixture), verbosity=0)
                    self.stdout.write("   ✅ Loaded: events.json")
                except Exception as e:
                    self.stdout.write(f"   ⏭️  Skipped events.json ({e})")
        else:
            self.stdout.write("   ℹ️  No events fixture found")

        # Step 2: Find or create EventPage
        event_page = self._get_or_create_event_page(options)
        if event_page is None:
            return

        # Step 3: Populate header_section if empty
        self._populate_event_header(event_page, options)

        # Step 4: Save and publish
        if not options["dry_run"]:
            with transaction.atomic():
                revision = event_page.save_revision(log_action=True)
                revision.publish()
            self.stdout.write(self.style.SUCCESS(
                "\n✅ EventPage populated and published!\n"
                "   View at: https://fusion-cms.com/events/\n"
            ))

    def _get_or_create_event_page(self, options):
        """Find the existing EventPage or create one under the HomePage."""
        EventPage = self._model(self.event_page_model)
        page = EventPage.objects.live().first()
        if page:
            if options["dry_run"]:
                self.stdout.write(f"   📋 Would use existing EventPage (id={page.id})")
            else:
                self.stdout.write(f"   🧭 Found EventPage: {page.title} (id={page.id})")
            return page

        # Create EventPage under the configured HomePage.
        HomePage = self._model(self.home_page_model)
        home = HomePage.objects.live().first()
        if home is None:
            self.stderr.write(self.style.ERROR(
                "   ❌ No HomePage found — cannot create EventPage."
            ))
            return None

        if options["dry_run"]:
            self.stdout.write("   📋 Would create new EventPage under HomePage")
            return None

        self.stdout.write("   🆕 Creating EventPage...")
        page = EventPage(
            title="Events",
            slug="events",
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(f"   ✅ Created EventPage (id={page.id})")
        return page

    def _populate_event_header(self, page, options):
        """Populate the header_section StreamField with a hero block."""
        if page.header_section:
            if options["dry_run"]:
                self.stdout.write("   📋 Header already populated, skipping")
            else:
                self.stdout.write("   ⏭️  Header already populated, skipping")
            return

        if options["dry_run"]:
            self.stdout.write("   📋 Would add hero header")
            return

        page.header_section = [
            (
                "hero",
                {
                    "background_image": None,
                    "subtitle": "Stay Updated",
                    "title": "Upcoming Events & Workshops",
                    "intro_text": (
                        "<p>Join our workshops, seminars, and conferences. "
                        "Connect with industry experts and enhance your professional skills.</p>"
                    ),
                },
            ),
        ]
        self.stdout.write("   ✅ Header populated")
