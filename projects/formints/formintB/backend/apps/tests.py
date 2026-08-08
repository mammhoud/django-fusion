"""POS Cloud — apps package smoke tests (precis-style layout).

Verifies the restructured apps/ package imports cleanly and that the
django-fusion viewset routes + sync receivers resolve from their new homes
(apps.core models/viewsets, apps.domain services, apps.handlers receivers).
"""

from django.test import SimpleTestCase
from django.urls import resolve


class AppsLayoutSmokeTests(SimpleTestCase):
    """The precis-style apps/ package resolves end to end."""

    def test_core_models_importable(self):
        from apps.core.models import (
            Organization, Branch, Lead, Contact, Deal,
            BranchProduct, BranchSale, BranchInventory, DeviceToken,
        )

        for model in (Organization, Branch, Lead, Contact, Deal,
                      BranchProduct, BranchSale, BranchInventory, DeviceToken):
            self.assertIsNotNone(model._meta.app_label)

    def test_domain_services_importable(self):
        from apps.domain.sync_broker import broker, BrokerMessage
        from apps.domain.sync_queue import sync_queue
        from apps.domain.conflict_resolver import ConflictResolutionEngine

        self.assertTrue(callable(broker.on))
        self.assertIsNotNone(BrokerMessage)
        self.assertIsNotNone(sync_queue)
        self.assertIsNotNone(ConflictResolutionEngine)

    def test_handlers_importable(self):
        from apps.handlers.sync_api import sync_receive_products
        from apps.handlers.consumers import SyncEventConsumer
        from apps.handlers.middleware import BoltSyncEventsMiddleware

        self.assertTrue(callable(sync_receive_products))
        self.assertIsNotNone(SyncEventConsumer)
        self.assertIsNotNone(BoltSyncEventsMiddleware)

    def test_api_routes_resolve(self):
        resolve("/api/health")
        resolve("/api/organizations/")
        resolve("/api/sync/push/products")
        resolve("/api/dashboard/branches/health")
        resolve("/fusion/health")
        resolve("/fusion/render-mode")

    def test_core_app_is_canonical(self):
        from django.apps import apps

        core_config = apps.get_app_config("core")
        self.assertEqual(core_config.name, "apps.core")
        self.assertEqual(core_config.label, "core")
