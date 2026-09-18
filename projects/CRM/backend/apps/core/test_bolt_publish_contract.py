"""Source-contract test for publish-on-mutation parity on the Bolt road.

``django_bolt`` is an optional runtime (``bolt`` is ``None`` when it is not
installed), so the registered CRUD handlers cannot be exercised through the
HTTP layer in this environment. This test pins the source wiring instead: the
canonical road must emit the same ``resource.created/updated/deleted``
workspace events as the compatibility ``resource_api`` so the realtime
dashboard (trend/count) refreshes regardless of which road performed the
mutation.
"""
from __future__ import annotations

from pathlib import Path

from django.test import SimpleTestCase

_BOLT_API = Path(__file__).resolve().parent / "bolt_api.py"


class BoltPublishContractTests(SimpleTestCase):
    def _source(self) -> str:
        return _BOLT_API.read_text()

    def test_bolt_road_imports_the_async_publish_helper(self):
        self.assertIn("from .realtime import safe_apublish_workspace_event", self._source())

    def test_bolt_crud_handlers_publish_create_update_delete(self):
        source = self._source()
        # One call each in the create/update/delete resource handlers.
        self.assertEqual(source.count("safe_apublish_workspace_event("), 3)
        self.assertIn('"resource.created"', source)
        self.assertIn('"resource.updated"', source)
        self.assertIn('"resource.deleted"', source)
