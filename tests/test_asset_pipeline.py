"""Regression tests for the unified django-fusion asset pipeline."""

from __future__ import annotations

import json

from django.test import override_settings


def _pipeline_settings(stats_file, *, configured=None):
    return {
        "STATIC_URL": "/static/",
        "STATIC_ROOT": "/tmp/fusion-staticfiles",
        "WEBPACK_LOADER": {
            "DEFAULT": {
                "STATS_FILE": str(stats_file),
                "BUNDLE_DIR_NAME": "bundles/cms-fusion/",
            }
        },
        "FUSION_PIPELINE": {
            "enabled": True,
            "webpack": {
                "enabled": True,
                "stats_file": str(stats_file),
                "bundle_dir": "bundles/cms-fusion/",
            },
            "components": {"enabled": False},
        },
        "FUSION_ASSETS": configured or {
            "top": {"css": ["/static/css/fusion.css"]},
            "bottom": {"js": ["/static/js/fusion-bridge.js"]},
        },
    }


def test_asset_pipeline_options_derive_manifest_from_static_root(tmp_path):
    """The component manifest follows a customized STATIC_ROOT."""
    stats_file = tmp_path / "bundles.json"
    static_root = tmp_path / "collected"

    settings = _pipeline_settings(stats_file)
    settings.update(
        STATIC_ROOT=str(static_root),
        FUSION_PIPELINE={
            "webpack": {"enabled": False},
            "components": {"enabled": True},
        },
    )

    with override_settings(**settings):
        from django_fusion.config.assets import get_asset_pipeline_options

        options = get_asset_pipeline_options()

    assert options.component_manifest_path == static_root / "components" / "manifest.json"


def test_asset_pipeline_options_resolve_webpack_defaults(tmp_path):
    """Pipeline options honor explicit settings and webpack fallback values."""
    stats_file = tmp_path / "bundles.json"
    settings = _pipeline_settings(stats_file)

    with override_settings(**settings):
        from django_fusion.config.assets import get_asset_pipeline_options

        options = get_asset_pipeline_options()

    assert options.webpack_enabled is True
    assert options.webpack_stats_file == stats_file
    assert options.webpack_bundle_dir == "bundles/cms-fusion/"
    assert options.public_url("bundles/cms-fusion/app.js") == "/static/bundles/cms-fusion/app.js"


def test_pipeline_accepts_legacy_setting_name(tmp_path):
    """Projects still setting ``FUSION_ASSET_PIPELINE`` keep working."""
    stats_file = tmp_path / "bundles.json"
    settings = _pipeline_settings(stats_file)
    settings["FUSION_ASSET_PIPELINE"] = settings.pop("FUSION_PIPELINE")

    with override_settings(**settings):
        from django_fusion.config.assets import get_asset_pipeline_options

        options = get_asset_pipeline_options()

    assert options.enabled is True
    assert options.webpack_stats_file == stats_file


def test_pipeline_options_expose_render_first_flag(tmp_path):
    """The effective render-first flag rides on the pipeline options."""
    stats_file = tmp_path / "bundles.json"
    settings = _pipeline_settings(stats_file)
    settings.update(FUSION_RENDER_FIRST=True)

    with override_settings(**settings):
        from django_fusion.config.assets import get_asset_pipeline_options

        options = get_asset_pipeline_options()

    assert options.fusion_render_first is True
    assert options.render_first is True


def test_pipeline_options_fall_back_to_legacy_render_first_name(tmp_path):
    """Legacy render-first setting names still resolve when the new one is unset."""
    stats_file = tmp_path / "bundles.json"
    settings = _pipeline_settings(stats_file)
    settings.update(FUSION_RENDER_FIRST_DEFAULT=True)
    settings.pop("FUSION_RENDER_FIRST", None)

    with override_settings(**settings):
        from django_fusion.config.assets import get_asset_pipeline_options

        options = get_asset_pipeline_options()

    assert options.fusion_render_first is True


def test_merged_manifest_adds_webpack_links_and_deduplicates(tmp_path):
    """Webpack CSS/JS links merge with configured links without duplicates."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps(
            {
                "chunks": {
                    "main": [
                        "app.css",
                        "app.js",
                        "app.js",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    settings = _pipeline_settings(
        stats_file,
        configured={
            "top": {"css": ["/static/bundles/cms-fusion/app.css"]},
            "bottom": {"js": ["/static/bundles/cms-fusion/app.js"]},
        },
    )

    with override_settings(**settings):
        from django_fusion.config.manifest import load_merged_asset_manifest

        manifest = load_merged_asset_manifest()

    assert manifest["top"]["css"] == ["/static/bundles/cms-fusion/app.css"]
    assert manifest["bottom"]["js"] == ["/static/bundles/cms-fusion/app.js"]
    assert manifest["webpack"]["enabled"] is True
    assert "fusion_render_first" in manifest


def test_render_first_gate_trims_webpack_links_in_data_mode(tmp_path):
    """With the gate on and render-first off, webpack links are not served."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps({"chunks": {"main": ["main.css", "main.js"]}}),
        encoding="utf-8",
    )
    settings = _pipeline_settings(stats_file)
    settings.update(
        FUSION_RENDER_FIRST=False,
        FUSION_PIPELINE={
            "enabled": True,
            "render_first_gates_assets": True,
            "webpack": {
                "enabled": True,
                "stats_file": str(stats_file),
                "bundle_dir": "bundles/cms-fusion/",
            },
            "components": {"enabled": False},
        },
    )

    with override_settings(**settings):
        from django_fusion.config.manifest import load_merged_asset_manifest

        manifest = load_merged_asset_manifest()

    assert manifest["fusion_render_first"] is False
    assert "/static/bundles/cms-fusion/main.css" not in manifest["top"]["css"]
    assert "/static/bundles/cms-fusion/main.js" not in manifest["bottom"]["js"]
    assert manifest["webpack"]["enabled"] is False
    # Core configured assets are still served.
    assert "/static/css/fusion.css" in manifest["top"]["css"]


def test_render_first_gate_keeps_webpack_links_in_render_first_mode(tmp_path):
    """With the gate on and render-first active, webpack links stay served."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps({"chunks": {"main": ["main.css", "main.js"]}}),
        encoding="utf-8",
    )
    settings = _pipeline_settings(stats_file)
    settings.update(
        FUSION_RENDER_FIRST=True,
        FUSION_PIPELINE={
            "enabled": True,
            "render_first_gates_assets": True,
            "webpack": {
                "enabled": True,
                "stats_file": str(stats_file),
                "bundle_dir": "bundles/cms-fusion/",
            },
            "components": {"enabled": False},
        },
    )

    with override_settings(**settings):
        from django_fusion.config.manifest import load_merged_asset_manifest

        manifest = load_merged_asset_manifest()

    assert manifest["fusion_render_first"] is True
    assert "/static/bundles/cms-fusion/main.css" in manifest["top"]["css"]
    assert manifest["webpack"]["enabled"] is True


def test_component_manifest_cache_tracks_path_and_file_changes(tmp_path):
    """Different manifest files and rewrites never reuse stale data."""
    from django_fusion.config.manifest import clear_asset_manifest_cache, load_asset_manifest

    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps({"first.html": ["one"]}), encoding="utf-8")
    second.write_text(json.dumps({"second.html": ["two"]}), encoding="utf-8")

    with override_settings(
        STATIC_ROOT=str(tmp_path),
        FUSION_PIPELINE={"components": {"manifest_path": str(first)}},
    ):
        clear_asset_manifest_cache()
        assert load_asset_manifest() == {"first.html": ["one"]}

    with override_settings(
        STATIC_ROOT=str(tmp_path),
        FUSION_PIPELINE={"components": {"manifest_path": str(second)}},
    ):
        assert load_asset_manifest() == {"second.html": ["two"]}

    first.write_text(json.dumps({"first.html": ["updated"]}), encoding="utf-8")
    with override_settings(
        STATIC_ROOT=str(tmp_path),
        FUSION_PIPELINE={"components": {"manifest_path": str(first)}},
    ):
        assert load_asset_manifest() == {"first.html": ["updated"]}


def test_merged_manifest_supports_legacy_assets_map(tmp_path):
    """Older webpack stats with an ``assets`` map remain link-compatible."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps({"status": "done", "assets": {"legacy.css": {}, "legacy.js": {}}}),
        encoding="utf-8",
    )

    with override_settings(**_pipeline_settings(stats_file)):
        from django_fusion.config.manifest import load_merged_asset_manifest

        manifest = load_merged_asset_manifest()

    assert "/static/bundles/cms-fusion/legacy.css" in manifest["top"]["css"]
    assert "/static/bundles/cms-fusion/legacy.js" in manifest["bottom"]["js"]


def test_webpack_links_do_not_duplicate_bundle_directory(tmp_path):
    """Stats URLs already prefixed with the bundle directory remain stable."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps({"chunks": {"main": ["bundles/cms-fusion/main.js"]}}),
        encoding="utf-8",
    )

    with override_settings(**_pipeline_settings(stats_file)):
        from django_fusion.config.manifest import load_merged_asset_manifest

        manifest = load_merged_asset_manifest()

    assert manifest["bottom"]["js"] == [
        "/static/js/fusion-bridge.js",
        "/static/bundles/cms-fusion/main.js",
    ]
    assert manifest["bottom"]["js"].count("/static/bundles/cms-fusion/main.js") == 1


def test_root_relative_webpack_links_use_static_url(tmp_path):
    """Root-relative bundle paths are still served below STATIC_URL."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps({"chunks": {"main": ["/bundles/cms-fusion/main.js"]}}),
        encoding="utf-8",
    )

    with override_settings(**_pipeline_settings(stats_file)):
        from django_fusion.config.manifest import load_merged_asset_manifest

        manifest = load_merged_asset_manifest()

    assert "/static/bundles/cms-fusion/main.js" in manifest["bottom"]["js"]


def test_manifest_command_uses_configured_path_then_standalone_fallback(tmp_path, monkeypatch):
    """The command honors pipeline paths and preserves standalone fallback behavior."""
    import django_fusion.management.commands.generate_asset_manifest as command_module

    output_paths = []
    monkeypatch.setattr(command_module, "generate_asset_manifest", lambda: {"page.html": ["card"]})
    monkeypatch.setattr(
        command_module,
        "save_asset_manifest",
        lambda manifest, path: output_paths.append((manifest, path)),
    )

    configured = tmp_path / "configured.json"
    fallback = tmp_path / "fallback.json"
    monkeypatch.setattr(command_module, "default_manifest_path", lambda: fallback)

    with override_settings(
        STATIC_ROOT="",
        FUSION_PIPELINE={"components": {"manifest_path": str(configured)}},
    ):
        command_module.Command().handle(output=None)

    with override_settings(STATIC_ROOT="", FUSION_PIPELINE={}):
        command_module.Command().handle(output=None)

    assert output_paths == [
        ({"page.html": ["card"]}, configured),
        ({"page.html": ["card"]}, fallback),
    ]


def test_asset_api_and_template_tags_share_merged_links(tmp_path):
    """API and server-rendered tags expose the same merged CSS/JS links."""
    stats_file = tmp_path / "bundles.json"
    stats_file.write_text(
        json.dumps({"chunks": {"main": ["main.css", "main.js"]}}),
        encoding="utf-8",
    )

    with override_settings(**_pipeline_settings(stats_file)):
        from django_fusion.comp.tags.fusion_assets import (
            fusion_bottom_assets,
            fusion_top_assets,
        )
        from django_fusion.core.assets.views import _get_assets_config

        config = _get_assets_config()
        top_html = str(fusion_top_assets())
        bottom_html = str(fusion_bottom_assets())

    assert config["top"]["css"] == ["/static/css/fusion.css", "/static/bundles/cms-fusion/main.css"]
    assert config["bottom"]["js"] == ["/static/js/fusion-bridge.js", "/static/bundles/cms-fusion/main.js"]
    assert "/static/bundles/cms-fusion/main.css" in top_html
    assert "/static/bundles/cms-fusion/main.js" in bottom_html
