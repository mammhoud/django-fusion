"""POS Cloud — migrated sidecar surface tests.

The Robyn sidecar was removed; Django now serves the same surface directly:
- `/fusion/*` contract (health, render-mode, nav, session-mode, assets)
- Community-UI bridges (`/api/sales`, `/api/products`, `/api/settings`)
- System endpoints (`/stats`)
- Root CRUD paths (generic JSON CRUD, `{count, items}` shape, gated by
  an authenticated session with a JSON 401 for anonymous callers)

These tests verify the surface resolves, serves anonymous parity endpoints,
gates CRUD correctly, and protects sensitive DeviceToken fields.
"""

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import resolve

from apps.core.models import DeviceToken, Organization

User = get_user_model()


class SurfaceUrlResolutionTests(TestCase):
    """All migrated sidecar paths resolve to a handler."""

    SURFACE_PATHS = [
        "/stats",
        "/fusion/health",
        "/fusion/render-mode",
        "/fusion/nav",
        "/fusion/session-mode",
        "/fusion/assets",
        "/organizations/",
        "/device-tokens/",
        "/conflicts/",
        "/queue/",
        "/api/sales",
        "/api/products",
        "/api/settings",
        "/api/organizations/",
        "/api/device-tokens/",
        "/api/conflicts/",
        "/api/queue/",
    ]

    def test_all_surface_paths_resolve(self):
        for path in self.SURFACE_PATHS:
            with self.subTest(path=path):
                match = resolve(path)
                self.assertIsNotNone(match.func or match.url_name)


class AnonymousParityTests(TestCase):
    """Endpoints the sidecar served anonymously keep working anonymously."""

    def setUp(self):
        self.client = Client()

    def test_fusion_health(self):
        r = self.client.get("/fusion/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"healthy", r.content)

    def test_fusion_render_mode(self):
        r = self.client.get("/fusion/render-mode")
        self.assertEqual(r.status_code, 200)

    def test_fusion_nav(self):
        r = self.client.get("/fusion/nav")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"nav_items", r.content)

    def test_fusion_assets(self):
        r = self.client.get("/fusion/assets")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"css", r.content)

    def test_fusion_session_mode_get(self):
        r = self.client.get("/fusion/session-mode")
        self.assertEqual(r.status_code, 200)

    def test_fusion_session_mode_post_delete(self):
        r = self.client.post(
            "/fusion/session-mode",
            data='{"mode": "fusion-render"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        r = self.client.delete("/fusion/session-mode")
        self.assertEqual(r.status_code, 200)

    def test_stats(self):
        r = self.client.get("/stats")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"counts", r.content)

    def test_bridge_sales(self):
        r = self.client.get("/api/sales")
        self.assertEqual(r.status_code, 200)

    def test_bridge_products(self):
        r = self.client.get("/api/products")
        self.assertEqual(r.status_code, 200)

    def test_bridge_settings(self):
        r = self.client.get("/api/settings")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"restaurant_name", r.content)


class FusionSessionModePersistenceTests(TestCase):
    """POST /fusion/session-mode persists to the Django session and a
    subsequent GET reflects the saved preference; DELETE clears it."""

    def setUp(self):
        self.client = Client()

    def _get_mode(self):
        r = self.client.get("/fusion/session-mode")
        self.assertEqual(r.status_code, 200)
        return r.json()

    def test_default_preference(self):
        """A fresh session defaults to fragment-first rendering."""
        self.assertEqual(
            self._get_mode(),
            {"render_first": True, "mode": "fusion-render"},
        )

    def test_post_fusion_render_persists(self):
        r = self.client.post(
            "/fusion/session-mode",
            data='{"mode": "fusion-render"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "fusion-render", "saved": True})
        # Same client/session now returns the persisted preference.
        self.assertEqual(
            self._get_mode(),
            {"render_first": True, "mode": "fusion-render"},
        )

    def test_post_data_api_persists(self):
        r = self.client.post(
            "/fusion/session-mode",
            data='{"mode": "data-api"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "data-api", "saved": True})
        self.assertEqual(
            self._get_mode(),
            {"render_first": False, "mode": "data-api"},
        )

    def test_post_bool_form_persists(self):
        """The fusion_render_first boolean form is equivalent to mode."""
        r = self.client.post(
            "/fusion/session-mode",
            data=json.dumps({"fusion_render_first": True}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "fusion-render", "saved": True})
        self.assertEqual(
            self._get_mode(),
            {"render_first": True, "mode": "fusion-render"},
        )

    def test_invalid_mode_falls_back_to_data_api(self):
        """An unrecognised mode is stored as data-api (never crashes)."""
        r = self.client.post(
            "/fusion/session-mode",
            data='{"mode": "nuclear"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "data-api", "saved": True})
        self.assertEqual(
            self._get_mode(),
            {"render_first": False, "mode": "data-api"},
        )

    def test_post_without_body_falls_back_to_data_api(self):
        """An empty POST body is handled gracefully (mode → data-api)."""
        r = self.client.post(
            "/fusion/session-mode",
            data="",
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "data-api", "saved": True})

    def test_delete_without_prior_preference_is_safe(self):
        """DELETE on a fresh session clears cleanly to the default."""
        r = self.client.delete("/fusion/session-mode")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "data-api", "cleared": True})
        self.assertEqual(
            self._get_mode(),
            {"render_first": True, "mode": "fusion-render"},
        )

    def test_delete_clears_back_to_default(self):
        self.client.post(
            "/fusion/session-mode",
            data='{"mode": "data-api"}',
            content_type="application/json",
        )
        self.assertEqual(self._get_mode()["mode"], "data-api")

        r = self.client.delete("/fusion/session-mode")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"mode": "data-api", "cleared": True})
        # Cleared session falls back to the fragment-first default.
        self.assertEqual(
            self._get_mode(),
            {"render_first": True, "mode": "fusion-render"},
        )

    def test_preference_is_per_session(self):
        """A second client does not inherit the first client's preference."""
        self.client.post(
            "/fusion/session-mode",
            data='{"mode": "data-api"}',
            content_type="application/json",
        )
        other = Client()
        r = other.get("/fusion/session-mode")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.json(),
            {"render_first": True, "mode": "fusion-render"},
        )


class CrudAuthGatingTests(TestCase):
    """Root CRUD is gated: anonymous gets a JSON 401, authenticated gets
    the sidecar's JSON ``{count, items}`` shape."""

    # Root surface paths — JSON CRUD served by apps/handlers/surface.py.
    SURFACE_PATHS = [
        "/organizations/",
        "/device-tokens/",
        "/conflicts/",
        "/queue/",
    ]
    # Pre-existing /api/ mount keeps its own HTML-viewset behaviour.
    LEGACY_API_PATHS = [
        "/api/organizations/",
        "/api/device-tokens/",
        "/api/conflicts/",
        "/api/queue/",
    ]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser("surface_tester", "a@b.c", "x")

    def test_anonymous_gets_json_401(self):
        for path in self.SURFACE_PATHS:
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 401)
                self.assertIn(b"authentication required", r.content)

    def test_legacy_api_still_gates(self):
        for path in self.LEGACY_API_PATHS:
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertIn(r.status_code, (302, 301))

    def test_surface_authenticated_serves_json(self):
        self.client.force_login(self.user)
        for path in self.SURFACE_PATHS:
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 200)
                self.assertIn(b"count", r.content)
                self.assertIn(b"items", r.content)

    def test_surface_write_paths(self):
        """POST creates and returns 201; GET/PATCH/DELETE round-trip."""
        self.client.force_login(self.user)
        r = self.client.post(
            "/organizations/",
            data=json.dumps({"name": "JSON CRUD Org", "slug": "json-crud-org"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertIn(b"json-crud-org", r.content)
        org_id = r.json()["id"]

        r = self.client.get("/organizations/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        r = self.client.patch(
            f"/organizations/{org_id}/",
            data=json.dumps({"name": "Renamed Org"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Renamed Org", r.content)

        r = self.client.delete(f"/organizations/{org_id}/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"deleted", r.content)
        self.assertEqual(Organization.objects.count(), 0)

    def test_missing_pk_returns_404(self):
        self.client.force_login(self.user)
        r = self.client.get("/organizations/99999/")
        self.assertEqual(r.status_code, 404)

    def test_invalid_json_post_returns_400(self):
        self.client.force_login(self.user)
        r = self.client.post(
            "/organizations/",
            data="not-json{",
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_anonymous_post_rejected(self):
        r = self.client.post(
            "/organizations/",
            data=json.dumps({"name": "Nope"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 401)


class DeviceTokenProtectionTests(TestCase):
    """Sensitive DeviceToken fields are hidden and not writable."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("plain_user", "p@b.c", "x")
        self.staff = User.objects.create_superuser("token_staff", "s@b.c", "x")
        self.token = DeviceToken.objects.create(
            device_id="dev-1",
            token_hash="sensitive-hash-abc",
            token_prefix="sens",
            role="viewer",
            is_active=False,
            expires_at="2030-01-01T00:00:00Z",
        )

    def test_token_hash_never_serialized(self):
        self.client.force_login(self.staff)
        r = self.client.get(f"/device-tokens/{self.token.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(b"sensitive-hash-abc", r.content)
        self.assertNotIn(b"token_hash", r.content)
        self.assertNotIn(b"token_prefix", r.content)

    def test_non_staff_cannot_set_role_or_active(self):
        """A non-staff user's PATCH cannot escalate role / re-enable a token."""
        self.client.force_login(self.user)
        r = self.client.patch(
            f"/device-tokens/{self.token.id}/",
            data=json.dumps({"role": "admin", "is_active": True}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.token.refresh_from_db()
        # Escalation ignored — defaults preserved.
        self.assertEqual(self.token.role, "viewer")
        self.assertFalse(self.token.is_active)

    def test_staff_can_set_role_and_active(self):
        """Staff may promote a token's role and re-enable it."""
        self.client.force_login(self.staff)
        r = self.client.patch(
            f"/device-tokens/{self.token.id}/",
            data=json.dumps({"role": "admin", "is_active": True}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.token.refresh_from_db()
        self.assertEqual(self.token.role, "admin")
        self.assertTrue(self.token.is_active)

    def test_non_staff_cannot_downgrade_staff_admin_token(self):
        """A non-staff user cannot lower a token's role either (no field
        escalation in either direction)."""
        self.token.role = "admin"
        self.token.save()
        self.client.force_login(self.user)
        r = self.client.patch(
            f"/device-tokens/{self.token.id}/",
            data=json.dumps({"role": "viewer"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.token.refresh_from_db()
        self.assertEqual(self.token.role, "admin")

    def test_staff_cannot_write_sensitive_fields(self):
        """token_hash / capabilities are excluded even for staff."""
        self.client.force_login(self.staff)
        r = self.client.patch(
            f"/device-tokens/{self.token.id}/",
            data=json.dumps({
                "token_hash": "MALLOC",
                "capabilities": {"x": 1},
                "allowed_entities": ["products"],
            }),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.token.refresh_from_db()
        self.assertEqual(self.token.token_hash, "sensitive-hash-abc")
        self.assertEqual(self.token.capabilities, {})
        self.assertEqual(self.token.allowed_entities, [])
