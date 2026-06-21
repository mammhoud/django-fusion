from pathlib import Path

from crafts_ai.rseal import classify_import, migration_plan


def test_classifies_ai_import_for_crafts_ai() -> None:
    rule = classify_import("django_rseal.ai.integrations")
    assert rule is not None
    assert rule.target == "crafts_ai.ai"
    assert rule.status == "move-to-crafts-ai"


def test_keeps_wagtail_blocks_in_django_rseal() -> None:
    rule = classify_import("django_rseal.blocks.contact.contact_card")
    assert rule is not None
    assert rule.target == "django_rseal.blocks"
    assert rule.status == "keep-in-django-rseal"


def test_migration_plan_finds_imports(tmp_path: Path) -> None:
    module = tmp_path / "sample.py"
    module.write_text(
        "from django_rseal.ai.integrations import OpenAIIntegration\n"
        "from django_rseal.blocks.contact.contact_card import ContactCardBlock\n",
        encoding="utf-8",
    )

    items = migration_plan(tmp_path)

    assert [item.status for item in items] == [
        "move-to-crafts-ai",
        "keep-in-django-rseal",
    ]
