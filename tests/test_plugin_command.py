"""Tests for ``manage.py plugin`` and the plugin-description contract.

Three things are asserted here, all named by the owning plan
(``docs/plans/structa-cloud/plugins/product-description-and-attach.md``):

1. **The static reader agrees with the runtime catalog** (G1). The docs gate
   (``scripts/generate_plugin_products.py``) parses ``catalog.py`` with :mod:`ast`
   so it can run without a virtualenv; this command reads the live registry. If
   the two ever disagree, a description could pass the gate and still be wrong at
   runtime — so the agreement is a test, not a comment.
2. **One contract, not two implementations.** Both sides resolve paths and apply
   D1-D3 through :mod:`django_fusion.plugins.descriptions`; a divergence would
   defeat the point of the plan's "a description may only state what the
   repository can prove".
3. **The rules bite** — D1 (capability drift), D2 (a cited path that does not
   exist) and D3 (empty ``limits``) each fail on a deliberately broken fixture,
   which is E2's verification.
"""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from django_fusion.management.commands.plugin import Command
from django_fusion.plugins import attach as editing
from django_fusion.plugins import descriptions as contract
from django_fusion.plugins import plugins
from django_fusion.plugins.catalog import CORE_PLUGINS, PLUGIN_CATALOG

LIBRARY_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LIBRARY_DIR.parent.parent


@pytest.fixture(scope="module")
def gate_script():
    """The docs gate, loaded by path — ``scripts/`` is not an importable package."""
    path = LIBRARY_DIR / "scripts" / "generate_plugin_products.py"
    spec = importlib.util.spec_from_file_location("_gate_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args: str) -> tuple[int, str]:
    """Run ``plugin`` with *args*, returning ``(exit_code, stdout)``.

    The command is instantiated directly rather than looked up by name: Django
    discovers commands through ``apps.get_app_configs()``, and these settings
    install ``django_fusion.comp`` (the sub-app) rather than the root package, so
    discovery would not find a framework-level command. Calling the class is also
    what makes this test independent of the site's ``INSTALLED_APPS``.
    """
    out = io.StringIO()
    code = 0
    try:
        call_command(Command(), *args, stdout=out, stderr=out)
    except SystemExit as exc:  # the command signals failure with an exit code
        code = int(exc.code or 0)
    except CommandError as exc:  # argparse rejected the invocation
        out.write(str(exc))
        code = 2
    return code, out.getvalue()


class TestStaticReaderAgreesWithRuntime:
    """The gate's ``ast`` view must equal what the registry reports."""

    def test_catalog_names_match(self, gate_script):
        static, core = gate_script.read_catalog()
        assert set(static) == {spec.name for spec in plugins.catalog()}
        assert set(core) == set(CORE_PLUGINS)

    @pytest.mark.parametrize("name", sorted(PLUGIN_CATALOG))
    def test_capabilities_signals_and_description_match(self, gate_script, name):
        static, _ = gate_script.read_catalog()
        spec = plugins.get(name)
        assert spec is not None
        assert static[name]["capabilities"] == set(spec.capabilities)
        assert static[name]["signals"] == set(spec.signals)
        assert static[name]["description"] == spec.description
        assert static[name]["core"] == spec.core

    def test_core_flag_agrees_with_the_core_plugins_tuple(self):
        for name, spec in PLUGIN_CATALOG.items():
            assert spec.core is (name in CORE_PLUGINS), f"{name} disagrees with CORE_PLUGINS"


class TestOneSharedContract:
    """Both readers must use the same resolution and the same rules."""

    def test_product_path_resolution_is_identical(self, gate_script):
        for name in PLUGIN_CATALOG:
            assert gate_script.expected_product_path(name) == contract.expected_product_path(name)

    def test_repo_root_resolution_points_at_the_repository(self):
        assert contract.default_repo_root() == REPO_ROOT

    def test_every_catalog_spec_has_a_description(self):
        missing = [
            spec.name
            for spec in plugins.catalog()
            if (path := contract.expected_product_path(spec.name)) is None or not path.exists()
        ]
        assert missing == [], f"plugins without a PRODUCT.md: {missing}"

    def test_every_description_passes_the_contract(self):
        failures = []
        for spec in plugins.catalog():
            spec_failures, _ = contract.check_product_for_spec(spec)
            failures += spec_failures
        assert failures == []


class TestRulesBite:
    """D1/D2/D3 must fail on a broken fixture — otherwise the gate is decoration."""

    @staticmethod
    def _write(tmp_path: Path, *, body: str = "---\n---\n\n# x\n") -> Path:
        path = tmp_path / "PRODUCT.md"
        path.write_text(body, encoding="utf-8")
        return path

    def _frontmatter(self, **overrides) -> str:
        fields = {
            "id": "plugin.htmx",
            "title": "HTMX",
            "summary": "htmx detection and fragment helpers",
            "capabilities": "[htmx, fragments]",
            "signals": "[htmx-request]",
            "limits": None,
            "evidence": None,
        }
        fields.update(overrides)
        lines = ["---"]
        for key, value in fields.items():
            if value is None and key == "limits":
                lines.append('limits:\n  - "does not bundle htmx."')
            elif value is None and key == "evidence":
                lines.append("evidence:\n  - path: REAL_FILE\n    what: proves it")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines) + "\n\n# HTMX\n"

    def test_missing_capability_fails_d1(self, tmp_path):
        path = self._write(tmp_path, body=self._frontmatter().replace("REAL_FILE", "pyproject.toml"))
        failures, _ = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments", "sse"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR,
        )
        assert any("omits 'sse'" in message for message in failures)

    def test_invented_capability_fails_d1(self, tmp_path):
        path = self._write(
            tmp_path,
            body=self._frontmatter(capabilities="[htmx, fragments, teleportation]").replace(
                "REAL_FILE", "pyproject.toml"
            ),
        )
        failures, _ = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR,
        )
        assert any("claims 'teleportation'" in message for message in failures)

    def test_nonexistent_evidence_path_fails_d2(self, tmp_path):
        path = self._write(tmp_path, body=self._frontmatter())  # REAL_FILE is not a real path
        failures, _ = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR,
        )
        assert any("evidence path does not exist" in message for message in failures)

    def test_empty_limits_fails_d3(self, tmp_path):
        path = self._write(
            tmp_path,
            body=self._frontmatter().replace(
                'limits:\n  - "does not bundle htmx."', "limits: []"
            ).replace("REAL_FILE", "pyproject.toml"),
        )
        failures, _ = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR,
        )
        assert any("[D3]" in message for message in failures)

    def test_commercial_claim_without_a_register_entry_fails_d4(self, tmp_path):
        path = self._write(
            tmp_path,
            body=self._frontmatter(summary="the world-class htmx layer").replace(
                "REAL_FILE", "pyproject.toml"
            ),
        )
        failures, _ = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR, claims_text="",
        )
        assert any("[D4]" in message and "world-class" in message for message in failures)

    def test_commercial_claim_backed_by_a_register_entry_passes(self, tmp_path):
        path = self._write(
            tmp_path,
            body=self._frontmatter(summary="the world-class htmx layer").replace(
                "REAL_FILE", "pyproject.toml"
            ),
        )
        failures, _ = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR, claims_text="world-class — measured against X",
        )
        assert not any("[D4]" in message for message in failures)

    def test_no_description_states_a_commercial_claim(self):
        """The register is empty of plugin claims because none are made."""
        claims = contract.load_claims(REPO_ROOT)
        offenders = {}
        for spec in plugins.catalog():
            path = contract.expected_product_path(spec.name)
            if path is None or not path.exists():
                continue
            terms = contract.uncovered_claims(
                contract.find_commercial_claims(path.read_text(encoding="utf-8")), claims
            )
            if terms:
                offenders[spec.short_name] = terms
        assert offenders == {}

    def test_a_clean_fixture_passes(self, tmp_path):
        path = self._write(
            tmp_path,
            body=self._frontmatter().replace("REAL_FILE", "pyproject.toml"),
        )
        failures, warnings = contract.check_product(
            path, name="django_fusion.plugins.htmx",
            capabilities={"htmx", "fragments"}, signals={"htmx-request"},
            repo_root=LIBRARY_DIR,
        )
        assert failures == []


class TestMarkerRegionEditing:
    """The pure edit machinery — what it refuses matters as much as what it writes."""

    @staticmethod
    def _wrap(listing: str, tail: str) -> str:
        newline = chr(10)
        return (
            "import os"
            + newline * 2
            + editing.MARKER_BEGIN
            + newline
            + listing
            + newline
            + editing.MARKER_END
            + newline * 2
            + tail
            + newline
        )

    @classmethod
    def region(cls, *apps: str) -> str:
        """A region exactly as the tool renders it — the round-trip fixture.

        The interior is tool-owned: the command regenerates it (including its note
        line), which ``--dry-run`` shows before anything is written.
        """
        return cls._wrap(editing.render_plugin_apps(list(apps)), "INSTALLED_APPS = PLUGIN_APPS")

    @classmethod
    def map_region(cls, **entries: str) -> str:
        return cls._wrap(editing.render_optional_map(dict(entries)), "INSTALLED_APPS = []")

    def test_region_bounds_are_found(self):
        lines = self.region().splitlines()
        bounds = editing.region_bounds(self.region())
        assert bounds is not None
        begin, end = bounds
        assert lines[begin] == editing.MARKER_BEGIN
        assert lines[end] == editing.MARKER_END
        assert end > begin

    def test_no_region_is_reported_not_guessed(self):
        assert editing.region_bounds("INSTALLED_APPS = []" + chr(10)) is None

    def test_add_then_remove_restores_the_original_bytes(self):
        original = self.region()
        attached = editing.with_app(original, "plugins.learning", add=True)
        assert "plugins.learning" in attached
        assert attached != original
        assert editing.with_app(attached, "plugins.learning", add=False) == original

    def test_attaching_twice_is_a_no_op(self):
        once = editing.with_app(self.region(), "plugins.learning", add=True)
        assert editing.with_app(once, "plugins.learning", add=True) == once

    def test_detaching_something_absent_is_a_no_op(self):
        original = self.region()
        assert editing.with_app(original, "plugins.learning", add=False) == original

    def test_a_file_without_markers_is_refused(self):
        with pytest.raises(editing.RegionMissing):
            editing.with_app("INSTALLED_APPS = []" + chr(10), "plugins.learning", add=True)

    def test_entries_are_sorted_and_deduplicated(self):
        text = self.region("plugins.blog", "plugins.blog", "plugins.learning")
        assert editing.read_plugin_apps(text) == ["plugins.blog", "plugins.learning"]

    def test_a_non_literal_app_list_is_refused(self):
        broken = self.region().replace("PLUGIN_APPS: list[str] = []", "PLUGIN_APPS = list(OTHER)")
        with pytest.raises(editing.RegionMissing):
            editing.read_plugin_apps(broken)

    def test_optional_map_round_trip(self):
        original = self.map_region()
        added = editing.with_optional_app(original, "plugins.shop", "ecommerce", add=True)
        assert editing.read_optional_map(added) == {"plugins.shop": "ecommerce"}
        assert editing.with_optional_app(added, "plugins.shop", "ecommerce", add=False) == original

    def test_diff_is_reviewable(self):
        after = editing.with_app(self.region(), "plugins.learning", add=True)
        assert "+    \"plugins.learning\"," in editing.unified_diff(self.region(), after, "settings.py")


class TestPluginCommand:
    def test_list_reports_every_spec(self):
        code, out = run("list", "--json")
        assert code == 0
        payload = json.loads(out)
        assert payload["total"] == len(PLUGIN_CATALOG)
        assert {row["name"] for row in payload["plugins"]} == set(PLUGIN_CATALOG)
        assert all(row["described"] for row in payload["plugins"])

    def test_describe_renders_a_description(self):
        code, out = run("describe", "htmx")
        assert code == 0
        assert "HTMX" in out
        assert "capabilities" in out
        assert "What it does not do" in out

    def test_describe_accepts_the_full_dotted_name(self):
        code, out = run("describe", "django_fusion.plugins.htmx", "--json")
        assert code == 0
        payload = json.loads(out)
        assert payload["frontmatter"]["id"] == "plugin.htmx"
        assert payload["failures"] == []

    def test_describe_unknown_plugin_refuses(self):
        code, out = run("describe", "not-a-plugin")
        assert code == 2
        assert "unknown plugin" in out

    def test_describe_without_a_name_refuses(self):
        code, out = run("describe")
        assert code == 2
        assert "needs a plugin name" in out

    def test_check_is_clean_in_this_repository(self):
        code, out = run("check")
        assert code == 0, out
        assert "gate clean" in out

    def test_doctor_reports_no_drift(self):
        code, out = run("doctor")
        assert code == 0
        assert "no drift" in out

    def test_check_rejects_a_described_plugin_with_no_catalog_spec(self, tmp_path):
        """A description the registry cannot describe would be a listing with no spec."""
        described = tmp_path / "plugins" / "learning"
        described.mkdir(parents=True)
        (described / "PRODUCT.md").write_text("---\nid: plugin.learning\n---\n", encoding="utf-8")
        code, out = run("check", "--root", str(tmp_path / "plugins"))
        assert code == 1
        assert "no catalog spec" in out

    def test_a_helper_directory_is_skipped_not_guessed_at(self, tmp_path):
        """``plugins/workers`` holds task actors, not a plugin — no invented failure.

        The skip is reported so a narrowed scope stays visible.
        """
        (tmp_path / "plugins" / "workers").mkdir(parents=True)
        (tmp_path / "plugins" / "workers" / "content_tasks.py").write_text("", encoding="utf-8")
        code, out = run("check", "--root", str(tmp_path / "plugins"))
        assert code == 0, out
        assert "skipped" in out

    def test_missing_root_is_reported(self, tmp_path):
        code, out = run("check", "--root", str(tmp_path / "nope"))
        assert code == 1
        assert "not a directory" in out

    def test_attach_unknown_plugin_refuses_with_capability_hints(self):
        code, out = run("attach", "not-a-plugin")
        assert code == 2
        assert "unknown plugin" in out
        assert "capability" in out

    def test_attach_needs_a_name(self):
        code, out = run("attach")
        assert code == 2
        assert "needs a plugin name" in out

    def test_attach_refuses_a_plugin_that_is_not_an_app(self):
        """htmx has no apps.py, so an app-list entry would do nothing."""
        code, out = run("attach", "htmx")
        assert code == 1
        assert "not an app-shaped plugin" in out

    def test_attach_refuses_when_the_marker_region_is_absent(self, tmp_path, monkeypatch):
        """A2: fail loudly rather than guess where an app list ends."""
        site = tmp_path / "settings.py"
        site.write_text("INSTALLED_APPS = ['django_fusion']\n", encoding="utf-8")
        monkeypatch.setattr(Command, "_site_settings_path", lambda self: site, raising=True)
        monkeypatch.setattr(Command, "_is_app_plugin", staticmethod(lambda name: True))
        code, out = run("attach", "django_fusion.plugins.apis", "--apply")
        assert code == 1
        assert "region" in out

    def test_optional_attach_and_detach_round_trip(self, tmp_path):
        """The mutating path end-to-end: write, verify with `check`, then remove."""
        map_file = tmp_path / "apps.py"
        map_file.write_text(TestMarkerRegionEditing.map_region(), encoding="utf-8")
        original = map_file.read_text(encoding="utf-8")

        # Preview writes nothing.
        code, out = run("attach", "htmx", "--optional", "--optional-map", str(map_file))
        assert code == 0
        assert "preview only" in out
        assert map_file.read_text(encoding="utf-8") == original

        # --apply writes the entry, naming the capability that justifies it.
        code, out = run(
            "attach", "htmx", "--optional", "--optional-map", str(map_file), "--apply"
        )
        assert code == 0, out
        assert '"django_fusion.plugins.htmx": "htmx"' in map_file.read_text(encoding="utf-8")

        # Re-running is a no-op, not a duplicate entry.
        code, out = run(
            "attach", "htmx", "--optional", "--optional-map", str(map_file), "--apply"
        )
        assert "nothing to do" in out

        # detach restores the original bytes exactly (A1/A3).
        code, out = run(
            "detach", "htmx", "--optional", "--optional-map", str(map_file), "--apply"
        )
        assert code == 0, out
        assert map_file.read_text(encoding="utf-8") == original

    def test_a_failed_check_rolls_the_write_back(self, tmp_path, monkeypatch):
        """A3: a half-attached site never survives the command."""
        map_file = tmp_path / "apps.py"
        map_file.write_text(TestMarkerRegionEditing.map_region(), encoding="utf-8")
        original = map_file.read_text(encoding="utf-8")
        monkeypatch.setattr(
            Command, "_run_check", lambda self: "SystemCheckError: boom", raising=True
        )
        code, out = run(
            "attach", "htmx", "--optional", "--optional-map", str(map_file), "--apply"
        )
        assert code == 1
        assert "rolled back" in out
        assert map_file.read_text(encoding="utf-8") == original

    def test_the_optional_map_in_this_repository_is_writable(self):
        """The site-side marker region exists, so --optional is usable today."""
        from django_fusion.plugins import attach as editing

        from django_fusion.management.commands.plugin import DEFAULT_OPTIONAL_MAP

        path = REPO_ROOT / DEFAULT_OPTIONAL_MAP
        assert path.exists(), path
        assert editing.region_bounds(path.read_text(encoding="utf-8")) is not None

    def test_optional_plugins_are_reported_not_failed(self):
        """A missing optional dependency is the environment's business, not drift.

        ``django_fusion.plugins.robyn`` ships with no declared extra, so it is
        routinely absent; the gate must stay green anyway (hence a warning).
        """
        code, out = run("doctor")
        assert code == 0
        assert "not importable here" in out or "no drift" in out

    @pytest.mark.parametrize(
        ("module", "expected"),
        [
            ("django_fusion.plugins.robyn", "external"),
            ("django_fusion.plugins.no_such_module", "broken"),
        ],
    )
    def test_import_problem_classification(self, module, expected):
        from django_fusion.management.commands.plugin import _import_problem

        assert _import_problem(module) == expected
