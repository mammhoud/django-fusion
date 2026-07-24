"""Tests for ``django_fusion.fragments.analyzer.views``.

Covers two distinct surfaces:

* **Pure-Python coercion helpers** (``_coerce_depth``, ``_coerce_bool``,
  ``_coerce_filters``) -- no Django setup needed.
* **The ``AnalyzeView`` HTTP POST contract** -- requires a Django
  request lifecycle, configured lazily via a class autouse fixture
  that runs an inline ``settings.configure()`` when no conftest /
  pytest-django has already done so.

**Real customizer fragment fixture**.

``customizer_fragment`` is loaded from disk (via ``customizer_fragment_path``
which walks up from this test file to find the real
``page_card_grid.html``). It is used by
``TestAnalyzeViewEndToEnd`` to feed the analyzer with bytes from the
actual customizer UI rather than a synthetic snippet -- this catches
future regressions where the view pipeline changes shape against the
real downstream consumer.

Like ``tests/analyzer/test_parser.py``, ``pytest.skip`` is invoked
when the real fragment isn't reachable from this test's location
(e.g. ``django-fusion`` installed as a wheel outside the repo).
"""

from __future__ import annotations

import json as jsonlib
from pathlib import Path

import pytest


# ────────────────────────────────────────────────────────────────────
# Module-scoped real customizer fragment fixture
# ────────────────────────────────────────────────────────────────────
# Walks up from this test file looking for a directory that contains
# ``customizer/templates/fragments/page_card_grid.html``. Robust to
# renaming the test file's parent directories or repo relocation.

@pytest.fixture(scope="module")
def customizer_fragment_path() -> Path:
    here = Path(__file__).resolve().parent
    for ancestor in [here, *here.parents]:
        candidate = (
            ancestor
            / "customizer"
            / "templates"
            / "fragments"
            / "page_card_grid.html"
        )
        if candidate.exists():
            return candidate
    pytest.skip(
        f"customizer fragment not reachable from {here} "
        "(test must be inside the repo to read the real file from disk)"
    )


@pytest.fixture(scope="module")
def customizer_fragment(customizer_fragment_path: Path) -> str:
    """Byte-for-byte content of
    ``customizer/templates/fragments/page_card_grid.html``. Loaded
    once per module so the end-to-end test runs cheaply.
    """
    return customizer_fragment_path.read_text(encoding="utf-8")


# ────────────────────────────────────────────────────────────────────
# Django setup helper (kept as a function so per-class autouse
# fixtures can take it as a parameter without coupling to a Django
# session lifecycle).
# ────────────────────────────────────────────────────────────────────

def _ensure_django(tmp_path: Path) -> None:
    """Configure a minimal Django settings module + TEMPLATES_DIRS =
    ``tmp_path``, but only if no conftest/pytest-django has already
    configured it.

    Also FORCES the live template engine's cached ``dirs`` to track
    ``tmp_path`` on every call. Django caches ``engine.dirs`` at
    ``django.setup()`` time; subsequent ``settings.TEMPLATES``
    mutations don't propagate to existing engines. Without this
    manual sync, ``scanner._resolve_template_dirs`` returns the
    first-ever ``tmp_path`` the test suite configured Django with,
    regardless of which caller's ``tmp_path`` is current.
    """
    import django
    from django.conf import settings as dj_settings
    from django.template import engines

    if not dj_settings.configured:
        django.conf.settings.configure(
            DEBUG=False,
            DATABASES={},
            INSTALLED_APPS=[],
            TEMPLATES=[{
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [str(tmp_path)],
                "APP_DIRS": False,
                "OPTIONS": {},
            }],
            USE_TZ=True,
        )
        django.setup()

    # Sync settings.TEMPLATES[0]['DIRS'] with tmp_path and invalidate the
    # engines cache. Both steps are required because:
    # - settings.TEMPLATES mutation alone is ignored by a CACHED engine
    #   (Django's engines registry caches the engine on first lookup;
    #   later TEMPLATES edits don't reach it -- this is the well-known
    #   engine.dirs cache quirk).
    # - engines._engines cache invalidation alone doesn't update
    #   settings.TEMPLATES (which is where new test callers will later
    #   re-read DIRS from).
    # Together they force ``engines["django"]`` to rebuild against
    # ``tmp_path`` on every call, which is critical under pytest-django's
    # session-pre-configured Django where the cached engine's DIRS may
    # otherwise point at tests/settings.py's <tests>/assets/templates
    # rather than the per-test tmp_path.
    if not isinstance(getattr(dj_settings, "TEMPLATES", None), list) or not dj_settings.TEMPLATES:
        dj_settings.TEMPLATES = [{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(tmp_path)],
            "APP_DIRS": False,
            "OPTIONS": {},
        }]
    else:
        entry = dict(dj_settings.TEMPLATES[0])
        entry["DIRS"] = [str(tmp_path)]
        entry.setdefault("BACKEND", "django.template.backends.django.DjangoTemplates")
        dj_settings.TEMPLATES[0] = entry
    engines._engines.clear()

    # Doubly-cover: force the LIVE engine's dirs to [tmp_path] even when
    # the cache clear somehow no-ops. The analyzer's _resolve_template_dirs
    # reads through django.template.engines["django"].engine.dirs, so this
    # is the line that the call-site ultimately depends on.
    try:
        eng = engines["django"]
        if hasattr(eng, "engine"):
            eng.engine.dirs = [str(tmp_path)]
    except (KeyError, AttributeError):
        pass


# ────────────────────────────────────────────────────────────────────
# Coercion helpers (pure-Python -- no Django required)
# ────────────────────────────────────────────────────────────────────
# Class pattern matches the rest of the suite: import once via an
# autouse fixture, store on ``self`` to keep the test bodies focused
# on the contract under test.

class TestCoerceDepth:
    @pytest.fixture(autouse=True)
    def _import(self):
        from django_fusion.fragments.analyzer.views import MAX_DEPTH, _coerce_depth
        self._fn = _coerce_depth
        self._max = MAX_DEPTH

    def test_int_in_range_preserved(self):
        assert self._fn(3) == 3
        assert self._fn(5) == 5

    def test_int_above_max_clamped(self):
        assert self._fn(99999) == self._max

    def test_int_below_one_floored(self):
        assert self._fn(0) == 1
        assert self._fn(-5) == 1

    def test_string_int_parsed(self):
        assert self._fn("5") == 5

    def test_string_garbage_falls_back_to_default(self):
        assert self._fn("abc") == 3

    def test_none_falls_back_to_default(self):
        assert self._fn(None) == 3

    def test_object_falls_back_to_default(self):
        assert self._fn(object()) == 3


class TestCoerceBool:
    @pytest.fixture(autouse=True)
    def _import(self):
        from django_fusion.fragments.analyzer.views import _coerce_bool
        self._fn = _coerce_bool

    def test_real_bool_preserved(self):
        assert self._fn(True, False) is True
        assert self._fn(False, True) is False

    def test_truthy_string_recognized(self):
        for s in ("true", "True", "1", "yes", "on", "  yes  "):
            assert self._fn(s, False) is True

    def test_falsy_string_returns_default(self):
        # strings not in the truthy set fall back to default
        assert self._fn("false", True) is True
        assert self._fn("0", True) is True

    def test_other_types_follow_truthy_semantics_when_default_false(self):
        assert self._fn(1, False) is True
        assert self._fn(0, False) is False
        assert self._fn([], False) is False
        assert self._fn("any", False) is True

    def test_other_types_use_default_when_default_truthy(self):
        assert self._fn(0, True) is True
        assert self._fn([], True) is True
        assert self._fn(42, True) is True


class TestCoerceFilters:
    @pytest.fixture(autouse=True)
    def _import(self):
        from django_fusion.fragments.analyzer.views import _coerce_filters
        self._fn = _coerce_filters

    def test_non_dict_returns_empty(self):
        assert self._fn("not a dict") == {}
        assert self._fn(None) == {}
        assert self._fn([1, 2]) == {}

    def test_filters_stringifies_ints_drops_none(self):
        out = self._fn({"exclude_patterns": ["admin", 1, None]})
        assert out == {"exclude_patterns": ["admin", "1"]}

    def test_filters_extracts_both_keys(self):
        out = self._fn({
            "exclude_patterns": ["admin"],
            "include_extensions": [".html"],
        })
        assert out == {"exclude_patterns": ["admin"], "include_extensions": [".html"]}

    def test_filters_ignores_non_list_values(self):
        out = self._fn({"exclude_patterns": "oops"})
        assert "exclude_patterns" not in out


class TestAnalyzeRequestDataclass:
    def test_from_payload_no_longer_exists(self):
        """from_payload was deleted (un-capped int default)."""
        from django_fusion.fragments.analyzer.schemas import AnalyzeRequest
        assert not hasattr(AnalyzeRequest, "from_payload")

    def test_direct_construction_with_kwargs(self):
        from django_fusion.fragments.analyzer.schemas import AnalyzeRequest
        spec = AnalyzeRequest(
            website_slug="x",
            url="https://example.com",
            include_components=False,
            depth=7,
            filters={"exclude_patterns": ["admin"]},
        )
        assert spec.website_slug == "x"
        assert spec.depth == 7
        assert spec.include_components is False
        assert spec.include_templates is True


# ────────────────────────────────────────────────────────────────────
# AnalyzeView POST contract -- requires Django
# ────────────────────────────────────────────────────────────────────

@pytest.fixture
def django_setup(tmp_path: Path) -> Path:
    """Per-test Django configuration for the AnalyzeView POST tests.

    Returns ``tmp_path`` so tests can write their own templates into
    it; the autouse application makes Django's ``TEMPLATES_DIRS``
    point at the same path.
    """
    _ensure_django(tmp_path)
    return tmp_path


class TestAnalyzeViewPost:
    """The Post-handler's response-code contract.

    The ``django_setup`` fixture is autouse-style here: each test
    *requires* ``tmp_path`` (for response-code tests that don't write
    to disk), so we list it as a fixture dependency on the class
    via an autouse fixture instead of repeating it 6×.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        _ensure_django(tmp_path)

    def test_empty_body_returns_400(self, tmp_path):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        rf = RequestFactory()
        req = rf.post("/api/analyzer/analyze/", data=b"", content_type="application/json")
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 400

    def test_malformed_json_returns_400(self, tmp_path):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=b"not json at all",
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 400

    def test_non_dict_json_returns_400(self, tmp_path):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=jsonlib.dumps(["a", "list"]).encode("utf-8"),
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 400

    def test_valid_minimal_payload_returns_200_spec_shape(self, tmp_path):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        (tmp_path / "hello.html").write_text(
            '{% extends "base.html" %}{% block content %}{% endblock %}'
        )
        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=jsonlib.dumps({
                "website_slug": "my-site",
                "url": "https://example.com",
                "depth": 3,
            }).encode("utf-8"),
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 200
        data = jsonlib.loads(resp.content)
        assert data["status"] == "success"
        for key in ("website", "components", "templates", "pages", "summary"):
            assert key in data, f"missing spec key {key!r}"
        assert data["website"]["slug"] == "my-site"

    def test_garbage_depth_does_not_crash(self, tmp_path):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        (tmp_path / "ok.html").write_text("hi")
        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=jsonlib.dumps({"depth": 99999}).encode("utf-8"),
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 200

    def test_filter_as_string_falls_back_to_empty(self, tmp_path):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=jsonlib.dumps({"filters": "definitely not a dict"}).encode("utf-8"),
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 200


# ────────────────────────────────────────────────────────────────────
# End-to-end with real customizer fragment
# ────────────────────────────────────────────────────────────────────

# Module-scoped so all EndToEnd tests share the same dir. Critical:
# ``_ensure_django`` is guarded by ``if not dj_settings.configured``,
# so per-test ``tmp_path`` settings would stick to whichever test
# ran FIRST -- subsequent tests would scan the wrong dir. A single
# shared dir configured once is the only correct shape.
@pytest.fixture(scope="module")
def shared_e2e_dir(tmp_path_factory, customizer_fragment: str) -> Path:
    """Module-scoped tmp dir containing the real
    ``page_card_grid.html`` and configured as Django's
    ``TEMPLATES.DIRS[0]``.

    Built once per module so the Django settings.configure call
    points at a stable dir for every EndToEnd test, not whichever
    per-test tmp_path the autouse fixture wins the race to.
    """
    shared_dir = tmp_path_factory.mktemp("analyzer_e2e")
    (shared_dir / "page_card_grid.html").write_text(
        customizer_fragment, encoding="utf-8"
    )
    _ensure_django(shared_dir)
    return shared_dir


class TestAnalyzeViewEndToEnd:
    """Drives the analyzer with the REAL
    ``page_card_grid.html`` fragment loaded from disk. Catches
    regressions where the view pipeline changes shape against
    the actual downstream consumer.
    """

    def test_real_fragment_yields_200_response(self, shared_e2e_dir):
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=jsonlib.dumps({
                "website_slug": "real-site",
                "url": "https://example.com",
                "depth": 3,
            }).encode("utf-8"),
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 200
        data = jsonlib.loads(resp.content)
        assert data["status"] == "success"

    def test_real_fragment_response_includes_comp_component(
        self, shared_e2e_dir, customizer_fragment
    ):
        """The view pipeline MUST emit a ``customizer/card`` component
        entry when scanning the real fragment (which contains a
        ``{% comp \"customizer/card\" with ... %}`` invocation).
        """
        from django.test import RequestFactory

        from django_fusion.fragments.analyzer.views import AnalyzeView

        # Skip if the fragment is unavailable (e.g. installed-wheel).
        if not customizer_fragment or "customizer/card" not in customizer_fragment:
            pytest.skip("real fragment doesn't contain the expected comp invocation")

        rf = RequestFactory()
        req = rf.post(
            "/api/analyzer/analyze/",
            data=jsonlib.dumps({
                "website_slug": "real-site",
                "include_components": True,
                "depth": 3,
            }).encode("utf-8"),
            content_type="application/json",
        )
        resp = AnalyzeView.as_view()(req)
        assert resp.status_code == 200
        data = jsonlib.loads(resp.content)
        component_paths = [c["path"] for c in data["components"]]
        assert "customizer/card" in component_paths, (
            f"view pipeline lost the comp invocation from the real fragment: "
            f"{component_paths}"
        )
