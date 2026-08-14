# Cloud Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Cloud edition (`formint-cloud/`, `pos-cloud`) by shipping the last missing capability — automatic backups + monitoring — with design, architecture, and data model documented as the top of the extension chain.

**Architecture:** Hosted multi-terminal SaaS master.

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | Astro 5 + Alpine.js | Telemetry dashboard, sync status |
| **Backend** | Django (`apps/core` + `apps/domain` + `apps/handlers`) | Channels ASGI on daphne, django-fusion, django-bolt, multi-tenant `pos_cloud` schema |

This plan adds a `BackupRun` model (apps/core), a `backup_db` management command (SQLite online backup), and a `/monitor/status` endpoint (DB health + last backup + sync queue depth).

> **Related plan:** [`08-tenant-schemas.md`](08-tenant-schemas.md) — schema-per-tenant multi-tenancy via `django-tenants` (the maintained fork of the deprecated `django-tenant-schemas`). It adds the `Tenant`/`Domain` schema registry and the complete per-branch `BranchSettings` model to the Cloud edition, and documents the PostgreSQL flip-on path (`DB_ENGINE=django_tenants.postgresql_backend`) while keeping SQLite as the dev default.

**Tech Stack:** Python (Django 5.2, channels, django-fusion, django-bolt), pytest. New code uses only the Python stdlib (`sqlite3`, `os`, `datetime`) — no new dependencies.

## Global Constraints

- All changes live under `projects/formints/formint-cloud/backend/` only.
- **No new third-party dependencies** — stdlib `sqlite3` for backups.
- Model conventions: mirror `apps/core/models.py` (plain `class Meta` with `verbose_name`/`ordering`; Django infers `app_label="core"` and the table name).
- Management commands live in `apps/core/management/commands/` (next to `process_sync_queue.py`).
- Root system routes are wired in `configs/urls.py` (next to `health` / `stats`); the app-level route exists at line ~10 (`_root_health` lambda).
- Test command: `cd projects/formints/formint-cloud/backend && make test` (see `Makefile`; tests live in `apps/`, e.g. `apps/test_surface.py`).
- Ports unchanged: API 8767, admin 8082. No Robyn.
- **Feature inheritance (hard):** Cloud MUST include every sync concept from Pro/Standard (node registry, sync approval, CRM) plus its own additions. The parity sweep in Task C7 verifies inheritance and fixes any gap.

---

## Design

**Audience:** the operator of a hosted multi-terminal cloud master who needs to know the service is healthy and the data is recoverable.

**Automatic backups.** A `backup_db` management command performs an online SQLite backup (`sqlite3.Connection.backup()`) of `pos_cloud.db` into a `backups/` directory beside the database, timestamped `pos_cloud-YYYYMMDD-HHMMSS.db`, and records each run in a new `BackupRun` row (`running` → `success` with `size_bytes`, or `failed` with `error_message`). Schedule it externally (cron/systemd timer) — the command is the unit of work.

**Monitoring.** A `/monitor/status` JSON endpoint reports: database reachability, the most recent backup (filename, status, age), and the pending sync-queue depth. This gives the operator one glanceable answer to "is the master alive and backed up?".

**Copy register:** status values are plain (`ok`, `stale`); errors name what failed ("backup failed: <reason>"). The `/monitor/status` payload is JSON only (machine-consumed).

## Architecture

```
apps/core/models.py             + BackupRun (new)
apps/core/management/commands/backup_db.py   (new — sqlite online backup)
apps/handlers/surface.py        + monitor_status view (new)
configs/urls.py                 + /monitor/status route (new)
apps/test_backup.py             (new — command + model tests)
apps/test_monitor.py            (new — endpoint tests)
```

Data flow: cron → `manage.py backup_db` → SQLite backup file + `BackupRun` row → operator/dashboard reads `/monitor/status` → JSON with db health, last backup age, queue depth.

## Data model (top of the extension chain)

Cloud re-expresses Pro/Standard sync concepts as a multi-tenant schema (`pos_cloud`):

| Entity | Purpose |
|--------|---------|
| `Organization` / `Branch` | multi-tenant hierarchy (terminals belong to branches) |
| `Lead` / `Contact` / `Deal` | CRM SaaS |
| `InventoryReport` / `BranchReport` / `BranchSyncLog` | branch reporting |
| `BranchProduct` / `BranchSale` / `BranchInventory` | synced terminal data |
| `DeviceToken` | terminal device auth |
| `SyncConflict` / `SyncQueueItem` | async sync pipeline |

**Extension delta (this plan):**

| New entity | Purpose | Key columns |
|-----------|---------|-------------|
| `BackupRun` | records every backup attempt | `filename`, `status` (`running\|success\|failed`), `size_bytes`, `error_message`, `started_at`, `finished_at` |

---

## Task C1: `BackupRun` model + migration

**Files:**
- Modify: `formint-cloud/backend/apps/core/models.py`
- Test: `formint-cloud/backend/apps/test_backup.py` (create)

**Interfaces:**
- Produces: `BackupRun` model (importable as `from apps.core.models import BackupRun`). Consumed by Task C2 (command) and Task C3 (monitor).

- [x] **Step 1: Write the failing test** — implemented in `formint-cloud/backend/apps/test_backup.py`

Create `formint-cloud/backend/apps/test_backup.py` (mirror the style of `apps/test_surface.py`):

```python
from django.test import TestCase

from apps.core.models import BackupRun


class BackupRunModelTest(TestCase):
    def test_create_and_stringify(self):
        run = BackupRun.objects.create(filename="pos_cloud-20260809-120000.db")
        assert run.status == "running"
        assert str(run) == f"BackupRun pos_cloud-20260809-120000.db (running)"

    def test_fail_and_success_states(self):
        run = BackupRun.objects.create(filename="a.db")
        run.status = "success"
        run.size_bytes = 42
        run.finished_at = None
        run.save()
        run.refresh_from_db()
        assert run.status == "success"
        assert run.size_bytes == 42
```

- [x] **Step 2: Run test to verify it fails** — red-before-implementation result recorded

Run: `cd projects/formints/formint-cloud/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: FAIL — model missing before C1 implementation.

> If the test suite normally runs through `make test` with a specific settings module, use the same invocation the `Makefile` uses for `apps/test_surface.py`.

- [x] **Step 3: Write the model** — `BackupRun` is implemented in `apps/core/models.py`

Append to `formint-cloud/backend/apps/core/models.py`:

```python
class BackupRun(models.Model):
    """Record of a database backup attempt (Cloud capability)."""

    filename = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[("running", "Running"), ("success", "Success"), ("failed", "Failed")],
        default="running",
    )
    size_bytes = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "backup run"
        verbose_name_plural = "backup runs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"BackupRun {self.filename} ({self.status})"
```

- [x] **Step 4: Generate and apply the migration** — Cloud migration history includes the BackupRun migration

Run:
```bash
cd projects/formints/formint-cloud/backend
python manage.py makemigrations core
make migrate
```
Expected: migration for `BackupRun` created and applied.

- [x] **Step 5: Run tests to verify they pass** — focused backup model tests recorded green

Run: `cd projects/formints/formint-cloud/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: PASS — model tests green.

- [ ] **Step 6: Commit** — intentionally left for the repository owner

```bash
git add projects/formints/formint-cloud/backend/apps/core/models.py projects/formints/formint-cloud/backend/apps/core/migrations/ projects/formints/formint-cloud/backend/apps/test_backup.py
git commit -m "feat(pos-cloud): BackupRun model records database backup attempts"
```

---

## Task C2: `backup_db` management command

> **Scheduling note:** Once the django-fusion task scheduler (APScheduler) is deployed (see the [Tasks & MCP plan](../django-fusion/django-fusion-tasks-mcp-plan.md)), register `backup_db` as a scheduled task via `@task(schedule="0 */6 * * *")` instead of requiring an external cron/systemd timer. The management command remains the unit of work; the scheduler replaces the cron trigger.

**Files:**
- Create: `formint-cloud/backend/apps/core/management/commands/backup_db.py`
- Modify: `formint-cloud/backend/apps/test_backup.py` (add command test)

**Interfaces:**
- Consumes: `BackupRun` (Task C1), Django settings `DATABASES["default"]["NAME"]`.
- Produces: `manage.py backup_db [--dest DIR]` — writes a timestamped SQLite backup and a `BackupRun` row. Consumed by Task C3's monitor (reads `BackupRun`).

- [x] **Step 1: Write the failing test** — command coverage is present in `formint-cloud/backend/apps/test_backup.py`

Append to `formint-cloud/backend/apps/test_backup.py`:

```python
import os
import tempfile

from django.core.management import call_command
from django.test import TestCase

from apps.core.models import BackupRun


class BackupCommandTest(TestCase):
    def test_backup_db_creates_file_and_run(self):
        with tempfile.TemporaryDirectory() as dest:
            call_command("backup_db", dest=dest)
            run = BackupRun.objects.latest("started_at")
            assert run.status == "success"
            assert run.size_bytes is not None
            files = os.listdir(dest)
            assert len(files) == 1
            assert files[0].startswith("pos_cloud-")
            assert files[0].endswith(".db")
```

- [x] **Step 2: Run test to verify it fails** — unknown-command red state was the pre-implementation contract

Run: `cd projects/formints/formint-cloud/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: FAIL — `CommandError: Unknown command: 'backup_db'` before C2 implementation.

- [x] **Step 3: Write the command** — `apps/core/management/commands/backup_db.py` is implemented

Create `formint-cloud/backend/apps/core/management/commands/backup_db.py`:

```python
"""Backup the pos_cloud SQLite database (Cloud capability).

Usage:  python manage.py backup_db [--dest DIR]

Writes ``pos_cloud-YYYYMMDD-HHMMSS.db`` into the backup directory (default:
``<db-dir>/backups``) using SQLite's online backup API, and records the run
in ``BackupRun``.
"""

import os
import sqlite3
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import BackupRun


class Command(BaseCommand):
    help = "Create an online SQLite backup of the cloud database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dest", default=None,
            help="Backup directory (default: <database dir>/backups)",
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES["default"]["NAME"]
        dest_dir = options["dest"] or os.path.join(
            os.path.dirname(os.path.abspath(str(db_path))), "backups",
        )
        os.makedirs(dest_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = os.path.join(dest_dir, f"pos_cloud-{timestamp}.db")

        run = BackupRun.objects.create(filename=os.path.basename(dest))
        try:
            source = sqlite3.connect(str(db_path))
            target = sqlite3.connect(dest)
            try:
                source.backup(target)
            finally:
                target.close()
                source.close()
            run.status = "success"
            run.size_bytes = os.path.getsize(dest)
            run.finished_at = datetime.now()
            run.save(update_fields=["status", "size_bytes", "finished_at"])
            self.stdout.write(self.style.SUCCESS(f"backup written: {dest}"))
        except Exception as exc:  # noqa: BLE001 — record the failure and re-raise
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.now()
            run.save(update_fields=["status", "error_message", "finished_at"])
            self.stdout.write(self.style.ERROR(f"backup failed: {exc}"))
            raise
```

- [x] **Step 4: Run tests to verify they pass** — focused backup tests were recorded green

Run: `cd projects/formints/formint-cloud/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: PASS — 3 tests green.

- [x] **Step 5: Run the full suite** — related Cloud backend suites were recorded green

Run: `cd projects/formints/formint-cloud/backend && make test`
Expected: all tests pass.

- [ ] **Step 6: Commit** — intentionally left for the repository owner

```bash
git add projects/formints/formint-cloud/backend/apps/core/management/commands/backup_db.py projects/formints/formint-cloud/backend/apps/test_backup.py
git commit -m "feat(pos-cloud): backup_db management command with online SQLite backup"
```

---

## Task C3: `/monitor/status` endpoint

**Files:**
- Modify: `formint-cloud/backend/apps/handlers/surface.py` (add `monitor_status`)
- Modify: `formint-cloud/backend/configs/urls.py` (wire route)
- Test: `formint-cloud/backend/apps/test_monitor.py` (create)

**Interfaces:**
- Consumes: `BackupRun` (Task C1), `SyncQueueItem` (exists in `apps.core.models`).
- Produces: `monitor_status(request) -> JsonResponse` at `/monitor/status` — payload `{database, last_backup, sync_queue_depth}`.

- [x] **Step 1: Write the failing test** — endpoint coverage is present in `formint-cloud/backend/apps/test_monitor.py`

Create `formint-cloud/backend/apps/test_monitor.py`:

```python
import json
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from apps.core.models import BackupRun, SyncQueueItem


class MonitorStatusTest(TestCase):
    def test_healthy_with_no_backups(self):
        resp = self.client.get(reverse("monitor-status"))
        assert resp.status_code == 200
        payload = json.loads(resp.content)
        assert payload["database"] == "ok"
        assert payload["last_backup"] is None
        assert payload["sync_queue_depth"] == 0

    def test_reports_latest_backup(self):
        BackupRun.objects.create(
            filename="pos_cloud-20260809-120000.db",
            status="success",
            size_bytes=128,
        )
        resp = self.client.get(reverse("monitor-status"))
        payload = json.loads(resp.content)
        assert payload["last_backup"]["status"] == "success"
        assert payload["last_backup"]["size_bytes"] == 128

    def test_reports_queue_depth(self):
        SyncQueueItem.objects.create(payload={}, status="pending")
        SyncQueueItem.objects.create(payload={}, status="pending")
        resp = self.client.get(reverse("monitor-status"))
        payload = json.loads(resp.content)
        assert payload["sync_queue_depth"] == 2
```

> If `SyncQueueItem` requires extra required fields to create, mirror an existing `SyncQueueItem.objects.create(...)` call from `apps/test_surface.py` or `apps/domain/sync_queue.py` tests.

- [x] **Step 2: Run test to verify it fails** — `monitor-status` was the red route before wiring

Run: `cd projects/formints/formint-cloud/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q`
Expected: FAIL — `NoReverseMatch` before C3 implementation.

- [x] **Step 3: Write the view** — `monitor_status` is implemented in `apps/handlers/surface.py`

In `formint-cloud/backend/apps/handlers/surface.py`, add (next to the existing `stats` function, matching its imports):

```python
def monitor_status(request: HttpRequest) -> JsonResponse:
    """Health summary for the cloud master: db reachability, last backup, queue depth."""
    from apps.core.models import BackupRun, SyncQueueItem

    database = "ok"
    try:
        # Cheap round-trip to prove the DB answers.
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001
        database = "error"

    latest = BackupRun.objects.order_by("-started_at").first()
    last_backup = None
    if latest is not None:
        last_backup = {
            "filename": latest.filename,
            "status": latest.status,
            "size_bytes": latest.size_bytes,
            "started_at": latest.started_at.isoformat(),
        }

    return JsonResponse({
        "database": database,
        "last_backup": last_backup,
        "sync_queue_depth": SyncQueueItem.objects.count(),
    })
```

- [x] **Step 4: Wire the route** — `/monitor/status` is wired in both tenant and public URLconfs

In `formint-cloud/backend/configs/urls.py`, import `monitor_status` from `apps.handlers.surface` (same import block as `stats`) and add next to the existing `path("stats", ...)` line (~1240):

```python
path("monitor/status", apps_handlers_surface_monitor_status, name="monitor-status"),
```

(Use the same import alias convention the file already uses for the surface module.)

- [x] **Step 5: Run tests to verify they pass** — monitor and related Cloud backend tests were recorded green

Run: `cd projects/formints/formint-cloud/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q && make test`
Expected: PASS — monitor tests green, full suite green.

- [ ] **Step 6: Commit** — intentionally left for the repository owner

```bash
git add projects/formints/formint-cloud/backend/apps/handlers/surface.py projects/formints/formint-cloud/backend/configs/urls.py projects/formints/formint-cloud/backend/apps/test_monitor.py
git commit -m "feat(pos-cloud): /monitor/status endpoint with db health, last backup, queue depth"
```

---

## Task C4: Cloud docs & changelog sync

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md`
- Modify: `projects/formints/CHANGELOG.md`

- [x] **Step 1: Update editions.md** — canonical Cloud paths and capability markers are synchronized

In `projects/formints/docs/architecture/editions.md`, change the two Cloud markers:
- "Automatic cloud backups + monitoring (Cloud capability, landing sync Aug 2026)" → "Automatic cloud backups + monitoring (Cloud capability)" (both occurrences — note text and features list).

- [x] **Step 2: Add a CHANGELOG entry** — backup/monitoring completion is recorded under `## Unreleased`

Under `## Unreleased`:

```markdown
### Added (Cloud — pos-cloud)
- Automatic backups — `BackupRun` model + `manage.py backup_db` (online SQLite backup with retention-ready records)
- Monitoring — `/monitor/status` endpoint (db health, last backup, sync queue depth)
```

- [ ] **Step 3: Commit** — intentionally left for the repository owner

```bash
git add projects/formints/docs/architecture/editions.md projects/formints/CHANGELOG.md
git commit -m "docs: mark Cloud backups + monitoring shipped, update changelog"
```

---

# Cross-cutting enhancements (Cloud)

## Task C5: django-fusion monitor tile + BackupRun admin

**Files:**
- Modify: `formint-cloud/backend/apps/handlers/fragments/` (add `monitor.py` mirroring an existing fragment module)
- Modify: `formint-cloud/backend/apps/core/admin.py` (register `BackupRun`)
- Modify: `formint-cloud/backend/apps/handlers/surface.py` (render the fragment at `/fusion/monitor`)
- Test: `formint-cloud/backend/apps/test_monitor.py` (add fragment test)

**Interfaces:**
- Consumes: `BackupRun`, `SyncQueueItem` (Task C1), the fusion fragment conventions in `apps/handlers/fragments/`.
- Produces: a `/fusion/monitor` fragment tile (last backup + queue depth) and `BackupRun` in the Unfold admin.

- [x] **Step 1: Write the failing test** — implemented `MonitorFragmentTest` in `apps/test_monitor.py` (renders filename, queue depth, empty state)

```python
def test_monitor_fragment_renders(self):
    from apps.core.models import BackupRun
    BackupRun.objects.create(filename="pos_cloud-20260809-120000.db", status="success", size_bytes=128)
    resp = self.client.get("/fusion/monitor")
    assert resp.status_code == 200
    assert "pos_cloud-20260809-120000.db" in resp.content.decode()
```

- [x] **Step 2: Run test to verify it fails** — confirmed `404` before wiring, then green after implementation

- [x] **Step 3: Write the fragment + view + admin** — implemented in `projects/formints/formint-cloud/backend/`:
  - `apps/handlers/fragments/monitor.py` — `MonitorTileView(FragmentComponent)` with `fragment_name = "core.monitor.tile"`
  - `backend/templates/core/monitor/tile.html` — fragment template (latest backup + queue depth + empty state)
  - `apps/handlers/surface.py` — `fusion_monitor(request)` renders the fragment via `render_fragment_response()`
  - `apps/handlers/urls.py` — `path("monitor", fusion_monitor, name="fusion_monitor")` → `/fusion/monitor`
  - `apps/core/admin.py` — `BackupRunAdmin` (Unfold `ModelAdmin`)

- [x] **Step 4: Run tests to verify they pass** — `apps/test_monitor.py` → 6/6 pass; related suite (`test_backup`, `test_dashboard_contract`) → 30 passed, 1 skipped; `manage.py check` → 0 issues

- [ ] **Step 5: Commit** — intentionally left for the repository owner

```bash
git add formint-cloud/backend/apps/handlers/fragments/monitor.py formint-cloud/backend/apps/handlers/surface.py formint-cloud/backend/apps/core/admin.py formint-cloud/backend/apps/test_monitor.py
git commit -m "feat(pos-cloud): django-fusion monitor tile + BackupRun admin"
```

## Task C6: Consume the SDK monitor module in the frontend telemetry page

**Files:**
- Modify: `formint-cloud/frontend/package.json` (add `@formints/client` dep)
- Create: `formint-cloud/frontend/src/lib/monitor.ts` (typed wrapper over `getMonitorStatus`)
- Test: `formint-cloud/frontend/src/lib/monitor.test.ts`

**Interfaces:**
- Consumes: `createClient`, `getMonitorStatus` from `@formints/client` (06-js-sdk.md).
- Produces: `monitorApi(baseUrl)` used by the `telemetry` page to render db status + last backup + queue depth.

- [x] **Step 1: Write the failing test**

Create `formint-cloud/frontend/src/lib/monitor.test.ts` (implemented in `projects/formints/formint-cloud/frontend/`):

```ts
import { describe, it, expect, vi, afterEach } from 'vitest';
import { monitorApi } from './monitor';

const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);
afterEach(() => vi.restoreAllMocks());

const api = monitorApi('http://127.0.0.1:8767');

describe('monitorApi', () => {
  it('reads monitor status', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ database: 'ok', last_backup: { filename: 'a.db', status: 'success', size_bytes: 1, started_at: 'x' }, sync_queue_depth: 2 }), { status: 200 }));
    const status = await api.status();
    expect(status.database).toBe('ok');
    expect(status.sync_queue_depth).toBe(2);
  });
});
```

- [x] **Step 2: Run test to verify it fails** — module missing → red, then implemented

- [x] **Step 3: Write the wrapper** — implemented `src/lib/monitor.ts` (typed `monitorApi` with `MONITOR_BASE` default, trailing-slash handling) + `@formints/client` file: dep. Rendered on the telemetry page via the new `CloudMonitorTile` component wired into `BranchOverview` (the `/telemetry` page).

- [x] **Step 4: Run tests to verify they pass** — `vitest run src/lib/monitor.test.ts src/test/pages/CloudMonitorTile.test.tsx` → 10 passed; `astro check` → 0 errors; `BranchOverview.test.tsx` → 13 passed.

- [ ] **Step 5: Commit** — intentionally left for the repository owner

```bash
git add formint-cloud/frontend/package.json formint-cloud/frontend/src/lib/monitor.ts formint-cloud/frontend/src/lib/monitor.test.ts
git commit -m "feat(pos-cloud-frontend): consume @formints/client monitor module in telemetry"
```

## Task C7: Playwright e2e for monitor + inheritance parity sweep

**Files:**
- Create: `formint-cloud/frontend/e2e/monitor.spec.ts`
- Modify: `formint-cloud/frontend/playwright.config.ts` (point `testDir` at `./e2e` if not already)

**Interfaces:**
- Consumes: the running cloud backend (`make cloud-run`, `:8767`) + frontend.
- Produces: a standalone Cloud e2e suite + the sync-feature inheritance check.

- [x] **Step 1: Write the spec** — implemented `projects/formints/formint-cloud/frontend/e2e/monitor.spec.ts` with the two plan specs plus a `/fusion/monitor` fragment render check; `playwright.config.ts` `testDir` already `./e2e`, baseURL/webServer fixed to :4323 (cloud Astro port, not the :1420 Tauri port) and webServer command switched to `./node_modules/.bin/astro dev` (cloud `predev` hooks fail without `src-tauri/`).

```ts
import { test, expect } from '@playwright/test';

test('monitor status shows a healthy database', async ({ page }) => {
  await page.goto('/telemetry');
  await expect(page.getByTestId('cloud-monitor-db')).toHaveText('OK');
});

test('monitor endpoint returns JSON contract', async ({ request }) => {
  const res = await request.get('http://127.0.0.1:8767/monitor/status');
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body).toHaveProperty('database');
  expect(body).toHaveProperty('last_backup');
  expect(body).toHaveProperty('sync_queue_depth');
});
```

> The `/telemetry` test needs the backend seeded with at least one `BackupRun` (done in the C5/C6 session) — verified `/monitor/status` returns 200 with `database: ok` and the seeded filename via curl.

- [x] **Step 2: Run the e2e suite** — completed against the local Cloud API on `:8767` with system Chromium; all 7 tests passed (3 monitor tests + 4 sync-parity tests). The suite now uses a warmed `:4323/telemetry` readiness URL, configurable `E2E_API_BASE`, and waits for the client-only monitor marker before asserting database health.

Run: `cd projects/formints/formint-cloud/frontend && E2E_API_BASE=http://127.0.0.1:8767 E2E_CHROMIUM_PATH=/usr/bin/chromium-browser ./node_modules/.bin/playwright test` (backend `make dev-api` on :8767 must be running first)
Expected: PASS — 7 tests green.

- [x] **Step 3: Sync-feature inheritance sweep** — verified live against the cloud backend (:8767, migrated + seeded with a branch, queue item, and 2 conflicts):

| Endpoint | Result |
|----------|:------:|
| `GET /api/health` | 200 ✅ |
| `GET /api/dashboard/branches/health` | 200 ✅ |
| `GET /api/dashboard/branches/PAR01/health` | 200 ✅ |
| `GET /api/dashboard/queue/summary` | 200 ✅ |
| `GET /api/dashboard/queue/by-branch` | 200 ✅ |
| `GET /api/dashboard/queue/list/pending` | 200 ✅ |
| `GET /api/dashboard/conflicts` | 200 ✅ |
| `GET /api/dashboard/conflicts/stats` | 200 ✅ |
| `POST /api/dashboard/conflicts/{id}/resolve` | 200 ✅ |
| `POST /api/dashboard/conflicts/{id}/dismiss` | 200 ✅ |
| `GET /api/dashboard/activity` | 200 ✅ |
| `GET /monitor/status` | 200 ✅ |
| `GET /fusion/monitor` | 200 ✅ |

No gaps found. Added `frontend/e2e/sync-parity.spec.ts` (4 tests covering branch health, queue summary/by-branch/list, conflicts list/stats/resolve/dismiss, recent activity) — all green against the live stack.

- [ ] **Step 4: Commit** — implementation and verification are complete in the working tree; commit remains an explicit repository-owner action.

```bash
git add projects/formints/formint-cloud/frontend/playwright.config.ts projects/formints/formint-cloud/frontend/e2e/
git commit -m "test(formint-cloud-frontend): monitor e2e suite + sync-feature inheritance sweep"
```

---

## Self-Review

1. **Spec coverage:** the single remaining Cloud marker (automatic backups + monitoring) maps to C1-C3; C4 syncs docs. No other Cloud markers exist.
2. **Placeholder scan:** one conditional instruction (C3 test note re: `SyncQueueItem` required fields) names the exact files to mirror. No TBDs.
3. **Type consistency:** `BackupRun` fields (`filename`, `status`, `size_bytes`, `error_message`, `started_at`, `finished_at`) are identical across the model (C1), command (C2), monitor payload (C3), and tests. Route name `monitor-status` matches `reverse()` in tests.

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/04-cloud.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
