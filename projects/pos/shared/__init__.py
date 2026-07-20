#!/usr/bin/env python
"""
Shared module for POS sidecar servers.

Provides:
  - Models: SignalEvent, SyncApproval, DeviceToken
  - Signals: config_changed, master_device_changed, etc.
  - Handlers: signal logging, webhook delivery, audit persistence
  - Services: ProductSyncEngine for data sync
  - API/middleware: CRUD helpers, auth
"""
