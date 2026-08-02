"""Contract tests for the canonical CMS Fusion asset tree.

The project keeps design sources, Django static sources, fixture data, and
runtime uploads under one project-owned ``assets/`` directory. These tests are
intentionally filesystem-only so they catch path drift before Django or the
frontend build starts.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = PROJECT_ROOT / "assets"


REQUIRED_ASSET_DIRECTORIES = (
    "styles",
    "static/js",
    "static/styles",
    "fixtures",
    "media",
)


def test_canonical_asset_directories_exist_and_are_populated():
    """All canonical CMS Fusion asset process directories contain files."""
    for relative_path in REQUIRED_ASSET_DIRECTORIES:
        directory = ASSETS_ROOT / relative_path
        assert directory.is_dir(), f"Missing asset directory: {relative_path}"
        assert any(directory.iterdir()), f"Empty asset directory: {relative_path}"


def test_fixture_sources_are_valid_json():
    """Every CMS Fusion JSON fixture can be parsed before it is loaded."""
    fixture_files = sorted((ASSETS_ROOT / "fixtures").rglob("*.json"))
    assert fixture_files, "The canonical fixture tree must contain JSON fixtures"

    for fixture_file in fixture_files:
        with fixture_file.open(encoding="utf-8") as stream:
            json.load(stream)


def test_generated_outputs_are_not_asset_sources():
    """Build outputs remain siblings of, rather than nested in, sources."""
    generated_root = ASSETS_ROOT / "staticfiles"
    source_roots = tuple(ASSETS_ROOT / path for path in REQUIRED_ASSET_DIRECTORIES)

    assert generated_root.parent == ASSETS_ROOT
    assert all(not source.is_relative_to(generated_root) for source in source_roots)
    assert not (ASSETS_ROOT / "styles" / "static").exists()


def test_assets_config_declares_canonical_path_settings():
    """The Django asset config declares the canonical project path settings."""
    config_file = PROJECT_ROOT / "configs" / "base" / "assets.py"
    tree = ast.parse(config_file.read_text(encoding="utf-8"))

    assignments = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        assignments.update(
            target.id for target in targets if isinstance(target, ast.Name)
        )

    assert {
        "ASSETS_DIR",
        "STATIC_DIR",
        "MEDIA_DIR",
        "FIXTURES_DIR",
        "STATIC_ROOT",
        "MEDIA_ROOT",
        "STATICFILES_DIRS",
        "FIXTURE_DIRS",
        "FUSION_ASSET_PIPELINE",
    }.issubset(assignments)


def test_fixture_loader_uses_project_asset_root():
    """The management command resolves fixtures from this project's assets."""
    from apps.core.management.commands.load_fusion_fixtures import FIXTURE_DIR

    assert FIXTURE_DIR == ASSETS_ROOT / "fixtures"


def test_container_setup_always_collects_static_and_generates_manifest():
    """Prebuilt/disabled webpack paths still refresh collected asset metadata."""
    entrypoint = (PROJECT_ROOT / "compose" / "entrypoint").read_text(encoding="utf-8")
    build_block = entrypoint.index('if [ "$SHOULD_BUILD_ASSETS" = "true" ]; then')
    collect_marker = '\n    echo "[SETUP] Collecting static files and generating component manifest..."'
    collect_block = entrypoint.index(collect_marker)
    build_end = entrypoint.rfind('\n    fi', build_block, collect_block) + len('\n    fi')

    assert build_end > build_block
    assert build_end < collect_block
    assert 'collectstatic python manage.py --site "$SITE_NAME" collectstatic --noinput' in entrypoint
    assert 'generate_asset_manifest python manage.py --site "$SITE_NAME" generate_asset_manifest' in entrypoint
