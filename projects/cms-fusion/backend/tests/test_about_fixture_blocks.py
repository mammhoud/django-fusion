"""Validate the updated dump-data.json about-page fixture blocks.

The English about page (and every locale variant) must contain the ``about``,
``testimonials`` and ``clients`` blocks so all three sections render in
production, and the ``clients`` blocks must reference Organization snippets
that exist in the fixture.

Both fixture copies (``backend/assets/fixtures`` — mounted by the production
container — and ``assets/fixtures``) are validated and must stay identical.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.conf import settings

from apps.content.models.pages.about import AboutPage

_SITE_DIR = Path(settings.BASE_DIR)
FIXTURE_PATHS = [
    _SITE_DIR / "assets" / "fixtures" / "dump-data.json",
    _SITE_DIR / "backend" / "assets" / "fixtures" / "dump-data.json",
]


@pytest.fixture(scope="module")
def fixture_data():
    contents = [p.read_text(encoding="utf-8") for p in FIXTURE_PATHS]
    assert contents[0] == contents[1], (
        "fixture copies drifted: backend/assets and assets must be identical"
    )
    return json.loads(contents[0])


@pytest.fixture(scope="module")
def org_pks(fixture_data):
    return {
        rec["pk"]
        for rec in fixture_data
        if rec.get("model") == "handlers.organization"
    }


def _about_records(fixture_data):
    return [rec for rec in fixture_data if rec.get("model") == "pages.aboutpage"]


def test_all_about_pages_have_three_blocks(fixture_data):
    """Every locale about page has about + testimonials + clients blocks."""
    assert _about_records(fixture_data), "no aboutpage records found"
    for rec in _about_records(fixture_data):
        facts = json.loads(rec["fields"]["facts"])
        types = [b["type"] for b in facts]
        assert types == ["about", "testimonials", "clients"], (
            f"aboutpage pk={rec['pk']} blocks={types}"
        )


def test_blocks_have_ids(fixture_data):
    """New blocks carry top-level ids like the existing about block."""
    for rec in _about_records(fixture_data):
        facts = json.loads(rec["fields"]["facts"])
        for block in facts:
            assert block.get("id"), (
                f"aboutpage pk={rec['pk']} block {block['type']} missing id"
            )


@pytest.mark.django_db
def test_facts_validate_against_streamfield(fixture_data):
    """Parsing facts through the real AboutPage StreamField succeeds."""
    facts_field = AboutPage._meta.get_field("facts")
    for rec in _about_records(fixture_data):
        facts = json.loads(rec["fields"]["facts"])
        value = facts_field.stream_block.to_python(facts)
        for block in value:
            block.get_prep_value()


@pytest.mark.django_db
def test_records_deserialize(fixture_data):
    """handlers.organization + pages.aboutpage records deserialize cleanly."""
    from django.core import serializers

    models = {"handlers.organization", "pages.aboutpage"}
    filtered = [rec for rec in fixture_data if rec.get("model") in models]
    assert filtered, "no target records in fixture"
    # Deserialize (without saving) — exercises UUID pk + JSON-string fields.
    list(serializers.deserialize("json", json.dumps(filtered)))


def test_testimonials_have_content(fixture_data):
    """Each testimonials block carries at least one testimonial with text."""
    for rec in _about_records(fixture_data):
        facts = json.loads(rec["fields"]["facts"])
        for block in facts:
            if block["type"] != "testimonials":
                continue
            items = block["value"]["testimonials"]
            assert items, f"aboutpage pk={rec['pk']} has empty testimonials"
            for item in items:
                assert item["value"]["content"].strip(), (
                    f"aboutpage pk={rec['pk']} testimonial has no content"
                )
                assert item["value"]["client_name"].strip()


def test_clients_reference_existing_organizations(fixture_data, org_pks):
    """Every clients block references an Organization present in the fixture."""
    assert len(org_pks) >= 4, f"expected organizations, got {len(org_pks)}"
    for rec in _about_records(fixture_data):
        facts = json.loads(rec["fields"]["facts"])
        for block in facts:
            if block["type"] != "clients":
                continue
            refs = [c["value"]["organization"] for c in block["value"]]
            assert refs, f"aboutpage pk={rec['pk']} clients block is empty"
            for ref in refs:
                assert ref in org_pks, (
                    f"aboutpage pk={rec['pk']} references missing org {ref}"
                )
