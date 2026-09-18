"""Per-resource OpenAPI docs contract for the Bolt road.

``django_bolt`` is an optional runtime (``bolt`` is ``None`` when it is not
installed), so the resource registry metadata is asserted unconditionally while
the route-level tag/summary wiring is asserted only when the runtime is present.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from apps.core.bolt_api import bolt
from apps.core.resources import RESOURCES


class ResourceOpenAPIMetadataTests(SimpleTestCase):
    """Every registered resource must carry human-readable OpenAPI metadata."""

    def test_every_resource_has_label_singular_and_description(self):
        for slug, resource in RESOURCES.items():
            self.assertTrue(resource.label, f"{slug} is missing a label")
            self.assertTrue(resource.singular, f"{slug} is missing a singular label")
            self.assertTrue(resource.description, f"{slug} is missing a description")

    def test_email_resources_are_registered_with_crud_metadata(self):
        self.assertIn("email_accounts", RESOURCES)
        self.assertIn("email_messages", RESOURCES)
        self.assertEqual(RESOURCES["email_accounts"].label, "Email accounts")
        self.assertEqual(RESOURCES["email_messages"].label, "Email messages")

    def test_pipeline_stage_resource_supports_ordered_crud_without_secret_fields(self):
        resource = RESOURCES["pipeline_stages"]
        self.assertEqual(resource.required_fields, ("pipeline_id", "name"))
        self.assertIn("order", resource.write_fields)
        self.assertIn("probability", resource.write_fields)
        self.assertEqual(resource.singular, "pipeline stage")

    def test_email_account_resource_never_exposes_oauth_tokens(self):
        resource = RESOURCES["email_accounts"]
        secret_fields = {"oauth_token", "oauth_refresh_token", "token_expires_at", "sync_cursor"}
        self.assertTrue(secret_fields.isdisjoint(set(resource.read_fields)))
        self.assertTrue(secret_fields.isdisjoint(set(resource.write_fields)))


class BoltRouteOpenAPIDocTests(SimpleTestCase):
    """Route-level tags/summaries must be emitted when Bolt is available."""

    def _route_meta(self) -> dict[str, dict]:
        meta = {}
        for method, path, _handler_id, handler in bolt._routes:
            meta.setdefault(path, {})[method] = bolt._handler_meta.get(handler, {})
        return meta

    def test_top_level_openapi_config_documents_the_api(self):
        if bolt is None:
            self.skipTest("django_bolt is not installed in this environment")
        self.assertTrue(bolt.openapi_config.description)
        self.assertEqual(
            sorted(tag.name for tag in bolt.openapi_config.tags),
            sorted(resource.label for resource in RESOURCES.values()),
        )

    def test_each_resource_route_is_tagged_and_summarized(self):
        if bolt is None:
            self.skipTest("django_bolt is not installed in this environment")
        routes = self._route_meta()
        for slug, resource in RESOURCES.items():
            list_meta = routes.get(f"/bolt/{slug}", {}).get("GET", {})
            self.assertEqual(list_meta.get("openapi_tags"), [resource.label], slug)
            self.assertTrue(list_meta.get("openapi_summary"), slug)
            detail_meta = routes.get(f"/bolt/{slug}/{{pk}}", {})
            for method in ("GET", "PATCH", "DELETE"):
                self.assertEqual(
                    detail_meta.get(method, {}).get("openapi_tags"),
                    [resource.label],
                    f"{slug} {method}",
                )
                self.assertTrue(
                    detail_meta.get(method, {}).get("openapi_summary"),
                    f"{slug} {method}",
                )
            create_meta = routes.get(f"/bolt/{slug}", {}).get("POST", {})
            self.assertEqual(create_meta.get("openapi_tags"), [resource.label], slug)
            self.assertTrue(create_meta.get("openapi_summary"), slug)

    def test_openapi_schema_generates_with_resource_tags(self):
        if bolt is None:
            self.skipTest("django_bolt is not installed in this environment")
        from django_bolt.openapi.schema_generator import SchemaGenerator

        schema = SchemaGenerator(bolt, bolt.openapi_config).generate()
        paths = schema.paths
        self.assertIn("/bolt/companies", paths)
        self.assertEqual(paths["/bolt/companies"].get.tags, ["Companies"])
        self.assertEqual(paths["/bolt/companies/{pk}"].get.tags, ["Companies"])
