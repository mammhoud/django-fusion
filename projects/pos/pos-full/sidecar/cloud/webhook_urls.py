"""
Webhook URL configuration for Cloud Master.

@tested pos-portal/full/cloud - Webhook URLs
"""

from __future__ import annotations

from django.urls import path

from . import webhook_receiver

urlpatterns = [
    path("node-aggregate/", webhook_receiver.receive_node_aggregate, name="webhook-node-aggregate"),
    path("transaction-batch/", webhook_receiver.receive_transaction_batch, name="webhook-transaction-batch"),
    path("product-update/", webhook_receiver.receive_product_update, name="webhook-product-update"),
    path("heartbeat/", webhook_receiver.receive_heartbeat, name="webhook-heartbeat"),
    path("stats/", webhook_receiver.webhook_stats, name="webhook-stats"),
]
