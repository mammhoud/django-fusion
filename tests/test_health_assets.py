"""Regression tests for the canonical asset and health APIs."""

from __future__ import annotations

import json

from django.test import override_settings


def test_health_api_exports_shared_checks():
    """The health package exposes both callable and class-based contracts."""
    from django_fusion.core.health import (
        AssetHealthView,
        AssetsHealthView,
        MediaHealthView,
        asset_health_check,
        media_health_check,
    )

    assert AssetsHealthView is AssetHealthView
    assert callable(asset_health_check)
    assert callable(media_health_check)
    assert MediaHealthView.as_view()


@override_settings(MEDIA_ROOT="/path/that/does/not/exist")
def test_media_health_preserves_degraded_response_contract():
    """A missing media mount is degraded but remains probe-friendly (HTTP 200)."""
    from django_fusion.core.health import media_health_check

    response = media_health_check(None)
    payload = json.loads(response.content)

    assert response.status_code == 200
    assert payload["status"] == "degraded"
    assert "media_root" in payload["checks"]
    assert payload["warnings"]


def test_asset_health_reads_webpack_stats(tmp_path):
    """The shared asset check validates the configured stats file."""
    from django_fusion.core.health import asset_health_check

    static_root = tmp_path / "staticfiles"
    static_root.mkdir()
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / "app.js").write_text("bundle", encoding="utf-8")
    stats_file = tmp_path / "webpack-stats.json"
    stats_file.write_text(json.dumps({"assets": {"app.js": {}}}), encoding="utf-8")

    with override_settings(
        STATIC_ROOT=str(static_root),
        MEDIA_ROOT=str(tmp_path / "media"),
        WEBPACK_LOADER={"DEFAULT": {"STATS_FILE": str(stats_file)}},
    ):
        response = asset_health_check(None)

    payload = json.loads(response.content)
    assert response.status_code == 200
    assert payload["checks"]["webpack_bundles"]["asset_count"] == 1
    assert payload["checks"]["bundle_files"]["file_count"] == 1
