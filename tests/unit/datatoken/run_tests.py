#!/usr/bin/env python3
"""
Standalone verification script for DataToken — DeviceToken integration.

Verifies three key behaviours:
  1. DeviceToken inherits sync_status / app_type from AbstractDataToken
  2. DeviceToken.mark_data_synced() cascades to linked DataToken rows
  3. DataToken.objects.tag_row() accepts and stores the app_type param

Implementation note: django_fusion.core.models.__init__ imports
DisplayModeMixin which triggers wagtail model registration.  To keep
this test lightweight (no wagtail in INSTALLED_APPS), we pre-populate
sys.modules with a mock wagtail.models.i18n before any django_fusion
import happens.

Usage:
    cd /home/structa.cloud
    python3 tests/unit/datatoken/run_tests.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# ── Path setup ──
# parents[3]: tests/ → unit/ → datatoken/ → structa.cloud/
_project_root = Path(__file__).resolve().parents[3]
_fusion_src = _project_root / "libs" / "django-fusion" / "src"

for p in [_fusion_src]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# ── Pre-populate wagtail stubs ────────────────────────────────────────
# django_fusion.core.models.__init__ does:
#   from .mixins import DisplayModeMixin
# which imports wagtail.admin.panels.FieldPanel → wagtail.models.i18n.Locale.
# We mock the full chain so no wagtail package is needed at test time.
# ───────────────────────────────────────────────────────────────────────

_wagtail_i18n = MagicMock()
_wagtail_i18n.Locale = MagicMock()
_wagtail_i18n.Locale._meta = MagicMock()
_wagtail_i18n.Locale._meta.app_label = "wagtail"
_wagtail_i18n.Locale._meta.object_name = "Locale"
_wagtail_i18n.Locale._meta.abstract = False
_wagtail_i18n.Locale._meta.swapped = False
_wagtail_i18n.Locale._meta.proxy = False
_wagtail_i18n.Locale._meta.managed = True
_wagtail_i18n.Locale._meta.auto_created = False
_wagtail_i18n.Locale.DoesNotExist = type("DoesNotExist", (Exception,), {})
_wagtail_i18n.Locale.MultipleObjectsReturned = type("MultipleObjectsReturned", (Exception,), {})

sys.modules["wagtail"] = MagicMock()
sys.modules["wagtail.models"] = MagicMock()
sys.modules["wagtail.models.i18n"] = _wagtail_i18n
sys.modules["wagtail.admin"] = MagicMock()
sys.modules["wagtail.admin.panels"] = MagicMock()

# ── Minimal Django settings (in-memory SQLite) ──
os.environ.pop("DJANGO_SETTINGS_MODULE", None)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "")

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="datatoken-test-secret",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
    )
    django.setup()

# ── Create ContentType + auth tables ──
from django.core.management import call_command
call_command("migrate", "contenttypes", interactive=False, verbosity=0)
call_command("migrate", "auth", interactive=False, verbosity=0)

# ── Now safe to import django_fusion — wagtail stubs are in sys.modules ──
from django_fusion.core.models.datatoken import (
    AbstractDataToken,
    BaseDeviceToken,
    DataToken,
    DataTokenMixin,
)
from django.db.models import Index


class DeviceToken(BaseDeviceToken):
    """Test DeviceToken — thin wrapper over BaseDeviceToken (mirrors pos-full)."""

    class Meta(BaseDeviceToken.Meta):
        abstract = False
        app_label = "contenttypes"
        db_table = "cloud_device_tokens"
        indexes = [
            Index(fields=["token_hash"]),
            Index(fields=["device_id", "is_active"]),
            Index(fields=["role"]),
            Index(fields=["expires_at"]),
            Index(fields=["sync_status"]),
            Index(fields=["app_type", "sync_status"]),
        ]


# ── Create tables via schema_editor ──
from django.db import connection

_TABLES = [DataToken, DeviceToken]
existing = []
try:
    existing = connection.introspection.table_names()
except Exception:
    pass
with connection.schema_editor() as schema_editor:
    for model in _TABLES:
        if model._meta.db_table in existing:
            continue
        try:
            schema_editor.create_model(model)
        except Exception:
            pass

# ── Test framework ──
PASS = 0
FAIL = 0


def check(condition, label):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")


# ════════════════════════════════════════════════════════════════
# 1.  DeviceToken inherits sync_status / app_type from AbstractDataToken
# ════════════════════════════════════════════════════════════════

print("\n── 1. DeviceToken inherits sync_status + app_type from AbstractDataToken ──")

check(issubclass(DeviceToken, AbstractDataToken),
      "DeviceToken is subclass of AbstractDataToken")

sync_field = DeviceToken._meta.get_field("sync_status")
check(sync_field is not None, "DeviceToken has sync_status field")
check(sync_field.default == "pending", "Default sync_status is 'pending'")
check(set(sync_field.choices) == {
    ("pending", "Pending Sync"),
    ("syncing", "Syncing"),
    ("synced", "Synced"),
    ("failed", "Failed"),
}, "sync_status has all 4 Status choices")

app_field = DeviceToken._meta.get_field("app_type")
check(app_field is not None, "DeviceToken has app_type field")
check(app_field.default == "pos-solo", "Default app_type is 'pos-solo'")
check(set(app_field.choices) == {
    ("pos-solo", "POS Solo"),
    ("pos-full", "POS Full"),
    ("pos-mini", "POS Mini"),
    ("cloud", "Cloud Server"),
}, "app_type has all 4 AppType choices")

check(hasattr(DeviceToken, "Status"), "DeviceToken.Status enum accessible")
check(DeviceToken.Status.PENDING == "pending", "DeviceToken.Status.PENDING = 'pending'")
check(DeviceToken.Status.SYNCED == "synced", "DeviceToken.Status.SYNCED = 'synced'")

check(hasattr(DeviceToken, "AppType"), "DeviceToken.AppType enum accessible")
check(DeviceToken.AppType.POS_SOLO == "pos-solo", "DeviceToken.AppType.POS_SOLO = 'pos-solo'")
check(DeviceToken.AppType.POS_FULL == "pos-full", "DeviceToken.AppType.POS_FULL = 'pos-full'")

dt = DeviceToken.objects.create(
    device_id="test-device-001",
    token_hash="abc123hash",
    token_prefix="abc12345",
    role="admin",
    node_type="pos-full",
    expires_at=django.utils.timezone.now() + django.utils.timezone.timedelta(days=90),
)
dt.refresh_from_db()
check(dt.sync_status == "pending",
      f"New DeviceToken sync_status='pending' (got: {dt.sync_status})")
check(dt.app_type == "pos-solo",
      f"New DeviceToken default app_type='pos-solo' (got: {dt.app_type})")
check(not dt.is_synced, "is_synced=False on new token")

dt.app_type = DeviceToken.AppType.POS_FULL
dt.save(update_fields=["app_type"])
dt.refresh_from_db()
check(dt.app_type == "pos-full", "DeviceToken.app_type can be set to 'pos-full'")

check("sync_status" in [f.name for f in AbstractDataToken._meta.fields],
      "sync_status field defined on AbstractDataToken")
check("app_type" in [f.name for f in AbstractDataToken._meta.fields],
      "app_type field defined on AbstractDataToken")

# ════════════════════════════════════════════════════════════════
# 2.  DeviceToken.mark_data_synced() cascades to linked DataTokens
# ════════════════════════════════════════════════════════════════

print("\n── 2. mark_data_synced() cascades to linked DataTokens ──")

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

ct = ContentType.objects.get_for_model(User)

device = DeviceToken.objects.create(
    device_id="cascade-device",
    token_hash="cascade-hash-123",
    token_prefix="cascade1",
    node_id_link="node-cascade-001",
    role="admin",
    node_type="pos-full",
    app_type=DeviceToken.AppType.POS_FULL,
    expires_at=django.utils.timezone.now() + django.utils.timezone.timedelta(days=90),
)

dt1 = DataToken.objects.create(
    token="cascade-test-001", node_id="node-cascade-001",
    content_type=ct, object_id="1",
    sync_status=DataToken.Status.PENDING, sync_order=1,
    app_type=DataToken.AppType.POS_FULL,
)
dt2 = DataToken.objects.create(
    token="cascade-test-002", node_id="node-cascade-001",
    content_type=ct, object_id="2",
    sync_status=DataToken.Status.SYNCING, sync_order=2,
    app_type=DataToken.AppType.POS_FULL,
)
dt3_other = DataToken.objects.create(
    token="cascade-test-003-other-node", node_id="node-other-999",
    content_type=ct, object_id="3",
    sync_status=DataToken.Status.PENDING, sync_order=3,
    app_type=DataToken.AppType.POS_SOLO,
)

check(DataToken.objects.filter(node_id="node-cascade-001", sync_status="pending").count() == 1,
      "Initially: 1 pending DataToken for cascade node")
check(DataToken.objects.filter(node_id="node-cascade-001", sync_status="syncing").count() == 1,
      "Initially: 1 syncing DataToken for cascade node")
check(DataToken.objects.filter(node_id="node-other-999", sync_status="pending").count() == 1,
      "Initially: 1 pending DataToken for other node")

device.mark_data_synced()
device.refresh_from_db()
dt1.refresh_from_db()
dt2.refresh_from_db()
dt3_other.refresh_from_db()

check(device.sync_status == "synced",
      f"DeviceToken sync_status='synced' (got: {device.sync_status})")
check(device.last_synced_at is not None, "DeviceToken.last_synced_at is set")
check(device.is_synced, "DeviceToken.is_synced=True")

check(dt1.sync_status == "synced", f"dt1 (PENDING) -> synced (got: {dt1.sync_status})")
check(dt1.synced_at is not None, "dt1.synced_at is set")
check(dt2.sync_status == "synced", f"dt2 (SYNCING) -> synced (got: {dt2.sync_status})")
check(dt2.synced_at is not None, "dt2.synced_at is set")

check(dt3_other.sync_status == "pending",
      f"dt3 (other node) still pending (got: {dt3_other.sync_status})")
check(dt3_other.synced_at is None, "dt3 (other node) synced_at still None")

synced_count = DataToken.objects.filter(
    node_id="node-cascade-001", sync_status="synced").count()
check(synced_count == 2, f"Exactly 2 DataTokens cascaded (got: {synced_count})")

# Edge: empty node_id_link
device_empty = DeviceToken.objects.create(
    device_id="empty-node-id", token_hash="empty-hash", token_prefix="empty123",
    node_id_link="", role="viewer", node_type="pos-solo",
    expires_at=django.utils.timezone.now() + django.utils.timezone.timedelta(days=90),
)
device_empty.mark_data_synced()
device_empty.refresh_from_db()
check(device_empty.sync_status == "synced",
      "DeviceToken w/o node_id_link still marks itself synced")
check(device_empty.last_synced_at is not None,
      "DeviceToken w/o node_id_link sets last_synced_at")

# ════════════════════════════════════════════════════════════════
# 3.  DataToken.objects.tag_row() accepts and stores app_type
# ════════════════════════════════════════════════════════════════

print("\n── 3. tag_row() accepts app_type param ──")

user = User.objects.create_user(username="testuser", password="testpass")

# Explicit app_type
token1 = DataToken.objects.tag_row(
    model_instance=user, token="tag-token-001", node_id="tag-node-001",
    sync_order=1, app_type="pos-full", metadata={"role": "cashier"},
)
check(token1.app_type == "pos-full",
      f"tag_row() stores explicit app_type='pos-full' (got: {token1.app_type})")
check(token1.token == "tag-token-001", "tag_row() stores token field")
check(token1.node_id == "tag-node-001", "tag_row() stores node_id")
check(token1.sync_order == 1, "tag_row() stores sync_order")
check(token1.metadata == {"role": "cashier"}, "tag_row() stores metadata")
check(token1.sync_status == "pending", "tag_row() defaults sync_status to 'pending'")
check(token1.content_type_id == ct.id, "tag_row() sets content_type")
check(token1.object_id == str(user.pk), "tag_row() sets object_id to user PK")

# Empty app_type defaults to pos-solo
token2 = DataToken.objects.tag_row(
    model_instance=user, token="tag-token-002", node_id="tag-node-002",
    sync_order=2, app_type="",
)
check(token2.app_type == "pos-solo",
      f"tag_row() with empty app_type defaults to 'pos-solo' (got: {token2.app_type})")

# All 4 AppType values
for app_val in ["pos-solo", "pos-full", "pos-mini", "cloud"]:
    t = DataToken.objects.tag_row(
        model_instance=user, token=f"tag-token-{app_val}",
        node_id="tag-node-multi", sync_order=0, app_type=app_val,
    )
    check(t.app_type == app_val,
          f"tag_row() app_type='{app_val}' stored correctly (got: {t.app_type})")

# DataTokenMixin.tag_for_sync()
class TaggedModel(DataTokenMixin, django.db.models.Model):
    name = django.db.models.CharField(max_length=100)
    class Meta:
        # Reuse existing app_label for in-memory testing (table won't collide)
        app_label = "contenttypes"

with connection.schema_editor() as schema_editor:
    try:
        schema_editor.create_model(TaggedModel)
    except Exception:
        pass

obj = TaggedModel.objects.create(name="test-object")
tag_token = obj.tag_for_sync(
    token="mixin-tag-001", node_id="mixin-node",
    sync_order=5, app_type="pos-mini",
)
check(tag_token.app_type == "pos-mini",
      f"DataTokenMixin.tag_for_sync() stores app_type='pos-mini' (got: {tag_token.app_type})")
check(tag_token.token == "mixin-tag-001", "tag_for_sync() stores token")
check(obj.is_tagged_for_sync, "is_tagged_for_sync=True after tag_for_sync()")

# sync_batch includes tagged tokens
batch = DataToken.objects.sync_batch(node_id="tag-node-multi", limit=50)
batch_tokens = [t.token for t in batch]
check(len(batch) >= 4, f"sync_batch returns at least 4 root tokens (got {len(batch)})")
for app_val in ["pos-solo", "pos-full", "pos-mini", "cloud"]:
    check(f"tag-token-{app_val}" in batch_tokens,
          f"sync_batch includes tag-token-{app_val}")

# Filter by app_type
pos_full_count = DataToken.objects.filter(app_type="pos-full").count()
check(pos_full_count >= 1,
      f"Can filter DataToken by app_type='pos-full' (found {pos_full_count})")

# ════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════

total = PASS + FAIL
print(f"\n{'='*60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {total} checks")
print(f"{'='*60}")

if FAIL > 0:
    print("\n❌ SOME TESTS FAILED")
    sys.exit(1)
else:
    print("\n✅ ALL TESTS PASSED — DataToken ↔ DeviceToken integration verified")
    sys.exit(0)
