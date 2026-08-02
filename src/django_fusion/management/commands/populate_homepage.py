"""
Django management command to populate HomePage with sample demo content.

Run on the remote server::

    docker exec fusion-cms-website python manage.py populate_homepage

Options:
    --reset     Delete existing content and repopulate (default: skip if populated)
    --dry-run   Show what would be added without saving
"""

from importlib import import_module
from django.db import transaction
from django_fusion.management.commands.base import BaseCommand


class Command(BaseCommand):
    help = "Populate the site HomePage with sample demo content"

    home_page_model = ""

    @staticmethod
    def _load_model(path: str):
        module_name, class_name = path.rsplit(".", 1)
        return getattr(import_module(module_name), class_name)

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing content and repopulate from scratch",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be added without saving to the database",
        )

    def handle(self, *args, **options):
        if not self.home_page_model:
            self.stderr.write(self.style.ERROR("populate_homepage requires a site HomePage model"))
            return
        HomePage = self._load_model(self.home_page_model)

        # Find the existing homepage
        homepage = HomePage.objects.live().first()
        if homepage is None:
            self.stderr.write(
                self.style.ERROR(
                    "❌ No live HomePage found. "
                    "Run 'python manage.py setup_wagtail_home' first."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🏠 Found HomePage: {homepage.title} (id={homepage.id})\n"
            )
        )

        # Check if already populated
        has_head = bool(homepage.head)
        has_summary = bool(homepage.summary)
        has_cta = bool(homepage.CTA)

        if any([has_head, has_summary, has_cta]) and not options["reset"]:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  HomePage already has content in one or more sections.\n"
                    "   Use --reset to overwrite existing content."
                )
            )
            self.stdout.write(f"   head has content:    {has_head}")
            self.stdout.write(f"   summary has content: {has_summary}")
            self.stdout.write(f"   CTA has content:     {has_cta}")
            return

        # Build content blocks
        head_blocks = self._build_head()
        summary_blocks = self._build_summary()
        cta_blocks = self._build_cta()
        contact_form_blocks = self._build_contact_form()

        # Dry run — just report
        if options["dry_run"]:
            self.stdout.write(
                self.style.NOTICE(
                    f"   📋 Would add: head={len(head_blocks)} blocks, "
                    f"summary={len(summary_blocks)} blocks, "
                    f"CTA={len(cta_blocks)} blocks, "
                    f"contact_form={len(contact_form_blocks)} blocks"
                )
            )
            self.stdout.write(
                self.style.SUCCESS("\n📋 Dry run complete — no changes written.\n")
            )
            return

        # Assign directly to StreamFields (tuple-based, Wagtail idiom)
        if options["reset"]:
            homepage.head = []
            homepage.summary = []
            homepage.CTA = []
            homepage.contact_form = []

        homepage.head = head_blocks
        homepage.summary = summary_blocks
        homepage.CTA = cta_blocks
        homepage.contact_form = contact_form_blocks

        # Save and publish
        with transaction.atomic():
            revision = homepage.save_revision(log_action=True)
            revision.publish()
            homepage.refresh_from_db()

        self.stdout.write(
            f"   ✅ Added: head={len(head_blocks)} blocks, "
            f"summary={len(summary_blocks)} blocks, "
            f"CTA={len(cta_blocks)} blocks, "
            f"contact_form={len(contact_form_blocks)} blocks"
        )
        self.stdout.write(
            self.style.SUCCESS("\n✅ HomePage populated and published!\n")
        )
        self.stdout.write(
            f"   View at: https://fusion-cms.com/\n"
            f"   Admin:   https://fusion-cms.com/admin/pages/{homepage.id}/edit/\n"
        )

    # ── head: slider + features ───────────────────────────────────────────

    def _build_head(self):
        """Build head StreamField blocks using Wagtail's tuple format."""
        return [
            (
                "slider",
                [
                    (
                        "slide",
                        {
                            "background_image": None,
                            "subtitle": "Professional Training & Consulting",
                            "title": "Empowering Your Workforce with Expert-Led Training",
                            "video_url": "",
                        },
                    ),
                    (
                        "slide",
                        {
                            "background_image": None,
                            "subtitle": "Research & Development",
                            "title": "Innovative Research Solutions for Modern Challenges",
                            "video_url": "",
                        },
                    ),
                    (
                        "slide",
                        {
                            "background_image": None,
                            "subtitle": "Career Growth",
                            "title": "Advance Your Career with Industry-Recognized Certifications",
                            "video_url": "",
                        },
                    ),
                ],
            ),
            (
                "features",
                [
                    (
                        "feature",
                        {
                            "icon_class": "flaticon-happy",
                            "image": None,
                            "title": "Expert Instructors",
                            "description": "Learn from industry professionals with decades of real-world experience.",
                        },
                    ),
                    (
                        "feature",
                        {
                            "icon_class": "flaticon-graduation-cap",
                            "image": None,
                            "title": "Accredited Programs",
                            "description": "Our courses meet international standards and industry certifications.",
                        },
                    ),
                    (
                        "feature",
                        {
                            "icon_class": "flaticon-guarantee",
                            "image": None,
                            "title": "Flexible Learning",
                            "description": "Online, in-person, and hybrid options to fit your schedule.",
                        },
                    ),
                    (
                        "feature",
                        {
                            "icon_class": "flaticon-support",
                            "image": None,
                            "title": "Lifetime Support",
                            "description": "Ongoing mentorship and career guidance after course completion.",
                        },
                    ),
                ],
            ),
        ]

    # ── summary: about ─────────────────────────────────────────────────────

    def _build_summary(self):
        """Build summary StreamField blocks."""
        return [
            (
                "about",
                {
                    "background_image": None,
                    "years_experience": 20,
                    "welcome_text": "Welcome to Fusion CMS",
                    "main_title": "Your Partner in Professional Development & Research",
                    "description": (
                        "<p>At Fusion CMS, we are dedicated to advancing professional "
                        "knowledge through cutting-edge training programs and research "
                        "initiatives. With over two decades of experience, our team of "
                        "experts delivers practical, results-driven solutions tailored to "
                        "your organization's needs.</p>"
                        "<p>We believe in learning that transforms careers and organizations. "
                        "Our programs are designed to bridge the gap between theory and practice, "
                        "ensuring immediate applicability in the workplace.</p>"
                    ),
                    "service_items": [
                        (
                            "service_item",
                            {
                                "icon_class": "flaticon-diploma",
                                "title": "Corporate Training",
                                "description": "Custom training programs designed for your team's specific needs.",
                            },
                        ),
                        (
                            "service_item",
                            {
                                "icon_class": "flaticon-research",
                                "title": "Research Services",
                                "description": "Data-driven research and analysis to inform business decisions.",
                            },
                        ),
                        (
                            "service_item",
                            {
                                "icon_class": "flaticon-certificate",
                                "title": "Certifications",
                                "description": "Industry-recognized certifications to validate your expertise.",
                            },
                        ),
                    ],
                },
            ),
        ]

    # ── CTA: why_choose_us ─────────────────────────────────────────────────

    def _build_cta(self):
        """Build CTA StreamField blocks."""
        return [
            (
                "why_choose_section",
                {
                    "subtitle": "Why Fusion CMS",
                    "title": "What Sets Us Apart",
                    "description": (
                        "We combine academic rigor with practical industry experience "
                        "to deliver training that makes a real difference."
                    ),
                    "highlight_text": "20+ Years of Excellence",
                    "methods": [
                        "Evidence-based curriculum design",
                        "Hands-on practical workshops",
                        "Post-training support & mentoring",
                        "Industry-recognized certifications",
                    ],
                },
            ),
        ]

    # ── contact_form ───────────────────────────────────────────────────────

    def _build_contact_form(self):
        """Build contact_form StreamField blocks."""
        return [
            ("contact_form", {}),
        ]
