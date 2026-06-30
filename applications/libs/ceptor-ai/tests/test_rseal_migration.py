from pathlib import Path

from ceptor_ai import classify_import, migration_plan


def test_classifies_ai_import_for_ceptor_ai() -> None:
    rule = classify_import("ceptor_ai.ai.integrations")
    assert rule is not None
    assert rule.target == "ceptor_ai.ai"
    assert rule.status == "move-to-ceptor-ai"


def test_keeps_wagtail_blocks_in_ceptor_ai_rseal() -> None:
    rule = classify_import("ceptor_ai.blocks.contact.contact_card")
    assert rule is not None
    assert rule.target == "ceptor_ai.blocks"
    assert rule.status == "keep-in-ceptor-ai"


def test_migration_plan_finds_imports(tmp_path: Path) -> None:
    module = tmp_path / "sample.py"
    module.write_text(
        "from ceptor_ai.ai.integrations import OpenAIIntegration\n"
        "from ceptor_ai.blocks.contact.contact_card import ContactCardBlock\n",
        encoding="utf-8",
    )

    items = migration_plan(tmp_path)

    assert [item.status for item in items] == [
        "move-to-ceptor-ai",
        "keep-in-ceptor-ai",
    ]
