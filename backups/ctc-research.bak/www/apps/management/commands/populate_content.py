"""
populate_content management command
=====================================
Populate Wagtail pages with multilingual content from a markdown file.

Supports page models: HomePage, AboutPage, ContactPage, TeamPage,
CoursesPage, EventPage, ServicesPage.

Usage:
    uv run python manage.py populate_content --content-file docs/content.md
    uv run python manage.py populate_content --content-file docs/content.md --locale en
"""

import re
import sys
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django_fusion.site.management.commands.base import BaseCommand

# NOTE: Wagtail imports are deferred inside handle() to allow this module
# to be imported/patched in tests before Django's app registry is fully ready.


# ---------------------------------------------------------------------------
# Helpers (ported from base-dir populate_content.py)
# ---------------------------------------------------------------------------

ALL_LOCALE_CODES = ["en", "ar", "de", "fr", "es", "pt-br"]


def _get_or_create_locale(code: str):
    from wagtail_localize.models import Locale  # deferred — safe after app ready
    locale, _ = Locale.objects.get_or_create(language_code=code)
    return locale


def _parse_md_to_dict(text: str) -> dict[str, str]:
    """Split markdown into per-page sections keyed by model name."""
    pages: dict[str, str] = {}
    sections = re.split(r"## \d+\. (.*?) PAGE \((.*?)\)", text)
    for i in range(1, len(sections), 3):
        title = sections[i].strip()  # noqa: F841
        model_name = sections[i + 1].strip()
        pages[model_name] = sections[i + 2]
    return pages


def _extract_field_trans(content: str) -> dict:
    """Extract multilingual field values from a page section."""
    results: dict = {}
    LANG_CODES = {"en", "ar", "de", "fr", "es", "pt-br"}

    def _save(k, v):
        if k in results:
            if not isinstance(results[k], list):
                results[k] = [results[k]]
            results[k].append(v)
        else:
            results[k] = v

    current_key = None
    current_langs: dict = {}

    for line in content.split("\n"):
        match = re.match(r"^[ \t]*-+[ \t]*\*\*([^*:\n]+):\*\*[ \t]*(.*)", line)
        if match:
            k = match.group(1).strip()
            v = match.group(2).strip()
            if k.lower() in LANG_CODES:
                current_langs[k.lower()] = v
            else:
                if current_key and current_langs:
                    _save(current_key, current_langs)
                current_key = k
                if v:
                    _save(k, v)
                    current_key = None
                    current_langs = {}
                else:
                    current_langs = {}
            continue

        match_inner = re.match(r"^[ \t]+-+[ \t]*\*\*([^*:\n]+):\*\*[ \t]*(.*)", line)
        if match_inner:
            k = match_inner.group(1).strip()
            v = match_inner.group(2).strip()
            if k.lower() in LANG_CODES:
                current_langs[k.lower()] = v
                continue

        if (
            current_langs
            and line.strip()
            and (
                line.startswith("    ")
                or line.startswith("  ")
                or line.startswith("\t")
            )
        ):
            last_code = list(current_langs.keys())[-1]
            current_langs[last_code] += "\n" + line.strip()

    if current_key and current_langs:
        _save(current_key, current_langs)

    return results


def _get_trans(trans_map: dict, key: str, code: str, index: int | None = None):
    if key not in trans_map:
        return None
    val = trans_map[key]
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        if index is not None and index < len(val):
            item = val[index]
            return item.get(code) if isinstance(item, dict) else item
        item = val[0]
        return item.get(code) if isinstance(item, dict) else item
    return val.get(code) if isinstance(val, dict) else val


def _rt(val):
    """Wrap a string in RichText, or return None."""
    if val is None:
        return None
    from wagtail.rich_text import RichText  # deferred — safe to call after app ready
    return RichText(val)


# ---------------------------------------------------------------------------
# Per-model population helpers
# ---------------------------------------------------------------------------

def _populate_home(translation, trans_map: dict, code: str) -> None:
    # Head
    nh = []
    for b in translation.head:
        v = b.value
        if b.block_type == "slider":
            for i, s in enumerate(v or []):
                s.value["subtitle"] = _get_trans(trans_map, "Subtitle", code, i) or s.value.get("subtitle")
                s.value["title"] = _get_trans(trans_map, "Title", code, i) or s.value.get("title")
        elif b.block_type == "features":
            for i, f in enumerate(v or []):
                f.value["title"] = _get_trans(trans_map, "Title", code, i + 2) or f.value.get("title")
                f.value["description"] = _get_trans(trans_map, "Description", code, i) or f.value.get("description")
        nh.append((b.block_type, v))
    translation.head = nh

    # Summary
    ns = []
    has_about = False
    for b in translation.summary:
        v = b.value
        if b.block_type == "about":
            has_about = True
            v["welcome_text"] = _get_trans(trans_map, "Welcome Text", code, 0) or v.get("welcome_text")
            v["main_title"] = _get_trans(trans_map, "Main Title", code, 0) or v.get("main_title")
            v["description"] = _rt(_get_trans(trans_map, "Description", code, 3)) or v.get("description")
        elif b.block_type == "listing_section":
            v["subtitle"] = _get_trans(trans_map, "Subtitle", code, 2) or v.get("subtitle")
            v["title"] = _get_trans(trans_map, "Title", code, 5) or v.get("title")
        ns.append((b.block_type, v))

    if not has_about:
        ns.insert(0, ("about", {
            "welcome_text": _get_trans(trans_map, "Welcome Text", code, 0),
            "main_title": _get_trans(trans_map, "Main Title", code, 0),
            "description": _rt(_get_trans(trans_map, "Description", code, 3)),
        }))

    # Ensure clients section
    clients_exists = any(
        (b[0] if isinstance(b, tuple) else b.block_type) == "clients" for b in ns
    )
    if not clients_exists:
        from www.apps.models.manage.company import Organization
        orgs = Organization.objects.all()[:5]
        client_blocks = [("client", {"organization": org}) for org in orgs]
        ns.append(("clients", client_blocks))

    translation.summary = ns

    # CTA
    nc = []
    for b in translation.CTA:
        v = b.value
        if b.block_type == "why_choose_section":
            v["subtitle"] = _get_trans(trans_map, "Subtitle", code, 3) or v.get("subtitle")
            v["title"] = _get_trans(trans_map, "Title", code, 7) or v.get("title")
            v["description"] = _get_trans(trans_map, "Description", code, 4) or v.get("description")
            v["highlight_text"] = _get_trans(trans_map, "Highlight Text", code, 0) or v.get("highlight_text")
            methods = _get_trans(trans_map, "Methods (List)", code)
            if methods:
                v["methods"] = [m.strip() for m in methods.split(",")]
        nc.append((b.block_type, v))
    translation.CTA = nc

    if not translation.contact_form:
        translation.contact_form = [("contact_form", {"form_id": "homepage-contact-form"})]

    translation.form_title = _get_trans(trans_map, "Form Title", code) or translation.form_title
    translation.form_intro = _rt(_get_trans(trans_map, "Form Intro", code)) or translation.form_intro
    translation.button_text = _get_trans(trans_map, "Button Text", code) or translation.button_text
    translation.success_message = _rt(_get_trans(trans_map, "Success Message", code)) or translation.success_message


def _populate_about(translation, trans_map: dict, code: str) -> None:
    for b in translation.head:
        if b.block_type == "page_title":
            b.value["page_title"] = _get_trans(trans_map, "Page Title", code) or b.value.get("page_title")
            b.value["breadcrumb_home_text"] = _get_trans(trans_map, "Breadcrumb Home Text", code) or b.value.get("breadcrumb_home_text")

    nf = []
    has_about_block = False
    has_testimonials = False
    has_clients = False

    for b in translation.facts:
        v = b.value
        if b.block_type == "about":
            has_about_block = True
            v["welcome_text"] = _get_trans(trans_map, "Welcome Text", code) or v.get("welcome_text")
            v["main_title"] = _get_trans(trans_map, "Main Title", code) or v.get("main_title")
            v["description"] = _get_trans(trans_map, "Description", code) or v.get("description")
            v["experience_description"] = _rt(_get_trans(trans_map, "Experience Description", code)) or v.get("experience_description")
        elif b.block_type == "testimonials":
            has_testimonials = True
            v["subtitle"] = _get_trans(trans_map, "Subtitle", code) or v.get("subtitle")
            v["title"] = _get_trans(trans_map, "Title", code, 1) or v.get("title")
        elif b.block_type == "clients":
            has_clients = True
        nf.append((b.block_type, v))

    if not has_about_block:
        nf.insert(0, ("about", {
            "welcome_text": _get_trans(trans_map, "Welcome Text", code),
            "main_title": _get_trans(trans_map, "Main Title", code),
            "description": _get_trans(trans_map, "Description", code),
            "experience_description": _rt(_get_trans(trans_map, "Experience Description", code)),
        }))

    if not has_testimonials:
        nf.append(("testimonials", {
            "subtitle": _get_trans(trans_map, "Subtitle", code),
            "title": _get_trans(trans_map, "Title", code, 1),
            "testimonials": [],
        }))

    if not has_clients:
        from www.apps.models.manage.company import Organization
        orgs = Organization.objects.all()[:5]
        client_blocks = [("client", {"organization": org}) for org in orgs]
        nf.append(("clients", client_blocks))

    translation.facts = nf


def _populate_contact(translation, trans_map: dict, code: str) -> None:
    for b in translation.head:
        if b.block_type == "page_title":
            b.value["page_title"] = _get_trans(trans_map, "Page Title", code) or b.value.get("page_title")
            b.value["breadcrumb_home_text"] = _get_trans(trans_map, "Breadcrumb Home Text", code) or b.value.get("breadcrumb_home_text")

    for b in translation.contact_info:
        if b.block_type == "contact_info":
            v = b.value
            v["subtitle"] = _get_trans(trans_map, "Subtitle", code) or v.get("subtitle")
            v["title"] = _get_trans(trans_map, "Title", code) or v.get("title")
            v["description"] = _get_trans(trans_map, "Description", code) or v.get("description")

    for b in translation.contact_details:
        v = b.value
        if b.block_type == "address":
            v["title"] = _get_trans(trans_map, "Title", code, 1) or v.get("title")
        elif b.block_type == "phone":
            v["title"] = _get_trans(trans_map, "Title", code, 2) or v.get("title")
        elif b.block_type == "email":
            v["title"] = _get_trans(trans_map, "Title", code, 3) or v.get("title")

    if not translation.contact_form:
        translation.contact_form = [("contact_form", {"form_id": "contact-page-form"})]


def _populate_team(translation, trans_map: dict, code: str, team_photos: dict) -> None:
    for b in translation.head:
        if b.block_type == "page_title":
            b.value["page_title"] = _get_trans(trans_map, "Page Title", code) or b.value.get("page_title")

    new_body = []
    has_team_section = any(b.block_type == "team_section" for b in translation.body)
    body_blocks = list(translation.body)
    if not has_team_section:
        body_blocks.append(("team_section", {"title": "", "subtitle": "", "team_members": []}))

    for block in body_blocks:
        if isinstance(block, tuple):
            block_type, val = block
        else:
            block_type = block.block_type
            val = block.value

        if block_type == "team_section":
            val["title"] = _get_trans(trans_map, "Title", code) or val.get("title")
            val["subtitle"] = _get_trans(trans_map, "Subtitle", code) or val.get("subtitle")

            names = trans_map.get("Name", [])
            if isinstance(names, dict):
                names = [names]
            count = len(names)
            new_members = []
            for i in range(count):
                en_name = _get_trans(trans_map, "Name", "en", i)
                photo = team_photos.get(en_name)
                m_name = _get_trans(trans_map, "Name", code, i)
                m_pos = _get_trans(trans_map, "Position", code, i)
                m_bio = _get_trans(trans_map, "Bio", code, i)

                skills = []
                for s_idx in range(1, 4):
                    s_name = _get_trans(trans_map, f"Skill {s_idx}", code, i)
                    if s_name:
                        skills.append({"name": s_name, "percentage": 95 - (s_idx * 5)})

                new_members.append({
                    "name": m_name,
                    "position": m_pos,
                    "bio": m_bio,
                    "photo": photo,
                    "skills": skills,
                    "order": i + 1,
                })
            val["team_members"] = new_members
            new_body.append(("team_section", val))
        else:
            new_body.append((block_type, val))

    translation.body = new_body


def _populate_courses(translation, trans_map: dict, code: str) -> None:
    for b in translation.head:
        if b.block_type == "page_title":
            b.value["page_title"] = _get_trans(trans_map, "Page Title", code) or b.value.get("page_title")
            b.value["breadcrumb_home_text"] = _get_trans(trans_map, "Breadcrumb Home Text", code) or b.value.get("breadcrumb_home_text")
    translation.introduction = _get_trans(trans_map, "Intro Text", code) or translation.introduction


def _populate_event_or_services(translation, trans_map: dict, code: str) -> None:
    nh = []
    for b in translation.header_section:
        v = b.value
        if b.block_type == "hero":
            v["subtitle"] = _get_trans(trans_map, "Subtitle", code) or v.get("subtitle")
            v["title"] = _get_trans(trans_map, "Title", code) or v.get("title")
            v["intro_text"] = _rt(_get_trans(trans_map, "Intro Text", code)) or v.get("intro_text")
        nh.append((b.block_type, v))
    translation.header_section = nh

    nc = []
    for b in translation.cta_section:
        v = b.value
        if b.block_type == "cta":
            v["title"] = _get_trans(trans_map, "Title", code, 1) or v.get("title")
            v["subtitle"] = _get_trans(trans_map, "Subtitle", code, 1) or v.get("subtitle")
            v["button_text"] = _get_trans(trans_map, "Button Text", code) or v.get("button_text")
        nc.append((b.block_type, v))
    translation.cta_section = nc

    translation.intro_text = _rt(_get_trans(trans_map, "Intro Text", code)) or translation.intro_text
    ipp = _get_trans(trans_map, "Items per Page", code)
    if ipp:
        try:
            translation.items_per_page = int(re.search(r"\d+", str(ipp)).group())
        except (AttributeError, ValueError):
            pass


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Populate Wagtail pages with multilingual content from a markdown file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--content-file",
            required=True,
            help="Path to content markdown file",
        )
        parser.add_argument(
            "--locale",
            default=None,
            help="Limit to a single locale code (e.g. 'en'). Default: all locales.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Deferred Wagtail imports — must be inside handle() so the module can
        # be imported and patched in tests before the app registry is ready.

        from plugins.lms.models.courses.index import CoursesPage

        from www.core.content.models.pages.about import AboutPage
        from www.core.content.models.pages.contact import ContactPage
        from www.core.content.models.pages.events import EventPage
        from www.core.content.models.pages.home import HomePage
        from www.core.content.models.pages.services import ServicesPage
        from www.core.content.models.pages.team import TeamPage

        MODEL_MAP = {
            "HomePage": HomePage,
            "AboutPage": AboutPage,
            "ContactPage": ContactPage,
            "TeamPage": TeamPage,
            "CoursesPage": CoursesPage,
            "EventPage": EventPage,
            "ServicesPage": ServicesPage,
        }

        content_file = Path(options["content_file"])
        locale_filter: str | None = options["locale"]

        # Validate content file
        if not content_file.exists():
            raise CommandError(
                f"Content file not found: {content_file}. "
                "Pass the correct path via --content-file."
            )

        # Determine which locale codes to process
        if locale_filter:
            if locale_filter not in ALL_LOCALE_CODES:
                raise CommandError(
                    f"Unknown locale code '{locale_filter}'. "
                    f"Supported codes: {', '.join(ALL_LOCALE_CODES)}"
                )
            codes = [locale_filter]
        else:
            codes = ALL_LOCALE_CODES

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\n🚀 Populating content from {content_file} "
                f"(locales: {', '.join(codes)})...\n"
            )
        )

        try:
            text = content_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandError(f"Could not read content file: {exc}") from exc

        page_data = _parse_md_to_dict(text)
        locales = {c: _get_or_create_locale(c) for c in codes}

        # Pre-extract team photos from the English TeamPage (needed for all locales)
        team_photos: dict = {}
        en_locale = _get_or_create_locale("en")
        en_team = TeamPage.objects.filter(locale=en_locale).specific().first()
        if en_team:
            for b in en_team.body:
                if b.block_type == "team_section":
                    for m in b.value.get("team_members", []):
                        mv = m.value if hasattr(m, "value") else m
                        name = mv.get("name")
                        photo = mv.get("photo")
                        if name and photo:
                            team_photos[name] = photo
        self.stdout.write(f"📸 Found {len(team_photos)} photos in English Team Page")

        en_home = (
            HomePage.objects.filter(locale=en_locale).first()
            or HomePage.objects.first()
        )
        if not en_home:
            raise CommandError(
                "No HomePage found in the database. "
                "Ensure the site tree is initialised before running this command."
            )

        errors: list[str] = []

        for model_name, model in MODEL_MAP.items():
            if model_name not in page_data:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠  No section found for {model_name} — skipping.")
                )
                continue

            self.stdout.write(f"📦 {model_name}")

            en_root = model.objects.filter(locale=en_locale).first()
            if not en_root:
                self.stdout.write(f"    ✨ Creating missing English page for {model_name}")
                slug = model_name.lower().replace("page", "")
                if model_name == "CoursesPage":
                    slug = "all-courses"
                elif model_name == "EventPage":
                    slug = "events"
                elif model_name == "ServicesPage":
                    slug = "services"

                en_root = model(
                    title=f"{model_name} (EN)",
                    slug=slug,
                    locale=en_locale,
                )
                en_home.add_child(instance=en_root)
                en_root.save_revision().publish()

            trans_map = _extract_field_trans(page_data[model_name])

            for code in codes:
                locale = locales[code]
                translation = en_root.get_translation_or_none(locale)
                if not translation:
                    if code == "en":
                        translation = en_root
                    else:
                        self.stdout.write(f"    ➕ Creating translation for {code}")
                        translation = en_root.copy_for_translation(locale)

                # Common fields
                p_title = _get_trans(trans_map, "Page Title", code)
                if p_title:
                    translation.title = p_title
                translation.seo_title = (
                    _get_trans(trans_map, "Meta Title", code) or p_title or translation.seo_title
                )
                translation.search_description = (
                    _get_trans(trans_map, "Meta Description", code) or translation.search_description
                )

                try:
                    if model_name == "HomePage":
                        _populate_home(translation, trans_map, code)
                    elif model_name == "AboutPage":
                        _populate_about(translation, trans_map, code)
                    elif model_name == "ContactPage":
                        _populate_contact(translation, trans_map, code)
                    elif model_name == "TeamPage":
                        _populate_team(translation, trans_map, code, team_photos)
                    elif model_name == "CoursesPage":
                        _populate_courses(translation, trans_map, code)
                    elif model_name in ("EventPage", "ServicesPage"):
                        _populate_event_or_services(translation, trans_map, code)

                    translation.save_revision().publish()
                    self.stdout.write(
                        self.style.SUCCESS(f"    ✅ Published {code}: {translation.title}")
                    )
                except Exception as exc:  # noqa: BLE001
                    msg = f"    ✗  Failed to publish {model_name} [{code}]: {exc}"
                    self.stderr.write(self.style.ERROR(msg))
                    errors.append(msg)

        if errors:
            self.stderr.write(
                self.style.ERROR(
                    f"\n{len(errors)} error(s) occurred during content population. "
                    "Review the messages above."
                )
            )
            sys.exit(1)

        self.stdout.write(
            self.style.SUCCESS("\n✨ Global content population complete.")
        )
