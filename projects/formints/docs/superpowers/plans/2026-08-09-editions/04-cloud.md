# Cloud Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Cloud edition (`formintB/`, `pos-cloud`) by shipping the last missing capability — automatic backups + monitoring — with design, architecture, and data model documented as the top of the extension chain.

**Architecture:** Hosted multi-terminal SaaS master. Full Django setup: `apps/core` (models + viewsets + BoltAPI analytics), `apps/domain` (sync broker/queue/conflict resolution), `apps/handlers` (sync API, dashboard, fusion contract, surface CRUD), Channels ASGI on daphne. This plan adds a `BackupRun` model (apps/core), a `backup_db` management command (SQLite online backup), and a `/monitor/status` endpoint (DB health + last backup + sync queue depth).

**Tech Stack:** Python (Django 5.2, channels, django-fusion, django-bolt), pytest. New code uses only the Python stdlib (`sqlite3`, `os`, `datetime`) — no new dependencies.

## Global Constraints

- All changes live under `projects/formints/formintB/backend/` only.
- **No new third-party dependencies** — stdlib `sqlite3` for backups.
- Model conventions: mirror `apps/core/models.py` (plain `class Meta` with `verbose_name`/`ordering`; Django infers `app_label="core"` and the table name).
- Management commands live in `apps/core/management/commands/` (next to `process_sync_queue.py`).
- Root system routes are wired in `configs/urls.py` (next to `health` / `stats`); the app-level route exists at line ~10 (`_root_health` lambda).
- Test command: `cd projects/formints/formintB/backend && make test` (see `Makefile`; tests live in `apps/`, e.g. `apps/test_surface.py`).
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
- Modify: `formintB/backend/apps/core/models.py`
- Test: `formintB/backend/apps/test_backup.py` (create)

**Interfaces:**
- Produces: `BackupRun` model (importable as `from apps.core.models import BackupRun`). Consumed by Task C2 (command) and Task C3 (monitor).

- [ ] **Step 1: Write the failing test**

Create `formintB/backend/apps/test_backup.py` (mirror the style of `apps/test_surface.py`):

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

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'apps.core.models'` (model missing) or import error on `BackupRun`.

> If the test suite normally runs through `make test` with a specific settings module, use the same invocation the `Makefile` uses for `apps/test_surface.py`.

- [ ] **Step 3: Write the model**

Append to `formintB/backend/apps/core/models.py`:

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

- [ ] **Step 4: Generate and apply the migration**

Run:
```bash
cd projects/formints/formintB/backend
python manage.py makemigrations core
make migrate
```
Expected: migration for `BackupRun` created and applied.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: PASS — 2 tests green.

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintB/backend/apps/core/models.py projects/formints/formintB/backend/apps/core/migrations/ projects/formints/formintB/backend/apps/test_backup.py
git commit -m "feat(pos-cloud): BackupRun model records database backup attempts"
```

---

## Task C2: `backup_db` management command

**Files:**
- Create: `formintB/backend/apps/core/management/commands/backup_db.py`
- Modify: `formintB/backend/apps/test_backup.py` (add command test)

**Interfaces:**
- Consumes: `BackupRun` (Task C1), Django settings `DATABASES["default"]["NAME"]`.
- Produces: `manage.py backup_db [--dest DIR]` — writes a timestamped SQLite backup and a `BackupRun` row. Consumed by Task C3's monitor (reads `BackupRun`).

- [ ] **Step 1: Write the failing test**

Append to `formintB/backend/apps/test_backup.py`:

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

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: FAIL — `CommandError: Unknown command: 'backup_db'`

- [ ] **Step 3: Write the command**

Create `formintB/backend/apps/core/management/commands/backup_db.py`:

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

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: PASS — 3 tests green.

- [ ] **Step 5: Run the full suite**

Run: `cd projects/formints/formintB/backend && make test`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintB/backend/apps/core/management/commands/backup_db.py projects/formints/formintB/backend/apps/test_backup.py
git commit -m "feat(pos-cloud): backup_db management command with online SQLite backup"
```

---

## Task C3: `/monitor/status` endpoint

**Files:**
- Modify: `formintB/backend/apps/handlers/surface.py` (add `monitor_status`)
- Modify: `formintB/backend/configs/urls.py` (wire route)
- Test: `formintB/backend/apps/test_monitor.py` (create)

**Interfaces:**
- Consumes: `BackupRun` (Task C1), `SyncQueueItem` (exists in `apps.core.models`).
- Produces: `monitor_status(request) -> JsonResponse` at `/monitor/status` — payload `{database, last_backup, sync_queue_depth}`.

- [ ] **Step 1: Write the failing test**

Create `formintB/backend/apps/test_monitor.py`:

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

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q`
Expected: FAIL — `NoReverseMatch` for `monitor-status`

- [ ] **Step 3: Write the view**

In `formintB/backend/apps/handlers/surface.py`, add (next to the existing `stats` function, matching its imports):

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

- [ ] **Step 4: Wire the route**

In `formintB/backend/configs/urls.py`, import `monitor_status` from `apps.handlers.surface` (same import block as `stats`) and add next to the existing `path("stats", ...)` line (~1240):

```python
path("monitor/status", apps_handlers_surface_monitor_status, name="monitor-status"),
```

(Use the same import alias convention the file already uses for the surface module.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q && make test`
Expected: PASS — monitor tests green, full suite green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintB/backend/apps/handlers/surface.py projects/formints/formintB/backend/configs/urls.py projects/formints/formintB/backend/apps/test_monitor.py
git commit -m "feat(pos-cloud): /monitor/status endpoint with db health, last backup, queue depth"
```

---

## Task C4: Cloud docs & changelog sync

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md`
- Modify: `projects/formints/CHANGELOG.md`

- [ ] **Step 1: Update editions.md**

In `projects/formints/docs/architecture/editions.md`, change the two Cloud markers:
- "Automatic cloud backups + monitoring (Cloud capability, landing sync Aug 2026)" → "Automatic cloud backups + monitoring (Cloud capability)" (both occurrences — note text and features list).

- [ ] **Step 2: Add a CHANGELOG entry**

Under `## Unreleased`:

```markdown
### Added (Cloud — pos-cloud)
- Automatic backups — `BackupRun` model + `manage.py backup_db` (online SQLite backup with retention-ready records)
- Monitoring — `/monitor/status` endpoint (db health, last backup, sync queue depth)
```

- [ ] **Step 3: Commit**

```bash
git add projects/formints/docs/architecture/editions.md projects/formints/CHANGELOG.md
git commit -m "docs: mark Cloud backups + monitoring shipped, update changelog"
```

---

# Cross-cutting enhancements (Cloud)

## Task C5: django-fusion monitor tile + BackupRun admin

**Files:**
- Modify: `formintB/backend/apps/handlers/fragments/` (add `monitor.py` mirroring an existing fragment module)
- Modify: `formintB/backend/apps/core/admin.py` (register `BackupRun`)
- Modify: `formintB/backend/apps/handlers/surface.py` (render the fragment at `/fusion/monitor`)
- Test: `formintB/backend/apps/test_monitor.py` (add fragment test)

**Interfaces:**
- Consumes: `BackupRun`, `SyncQueueItem` (Task C1), the fusion fragment conventions in `apps/handlers/fragments/`.
- Produces: a `/fusion/monitor` fragment tile (last backup + queue depth) and `BackupRun` in the Unfold admin.

- [ ] **Step 1: Write the failing test**

Append to `formintB/backend/apps/test_monitor.py`:

```python
def test_monitor_fragment_renders(self):
    from apps.core.models import BackupRun
    BackupRun.objects.create(filename="pos_cloud-20260809-120000.db", status="success", size_bytes=128)
    resp = self.client.get("/fusion/monitor")
    assert resp.status_code == 200
    assert "pos_cloud-20260809-120000.db" in resp.content.decode()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q`
Expected: FAIL — `404` for `/fusion/monitor`

- [ ] **Step 3: Write the fragment + view + admin**

In `formintB/backend/apps/handlers/fragments/`, create `monitor.py` mirroring the structure of an existing fragment module in that directory (e.g., `reports.py` — same component base, same template convention):

```python
from apps.core.models import BackupRun, SyncQueueItem

# Follow the existing fragment module's component class + template wiring.
# Content: latest BackupRun (filename, status, size_bytes) and SyncQueueItem count.
```

In `formintB/backend/apps/handlers/surface.py`, add `fusion_monitor(request)` that renders the monitor fragment (mirror how the existing `/fusion/*` handlers render fragments). Wire `path("fusion/monitor", fusion_monitor, name="fusion-monitor")` in the app's url config next to the other `/fusion/*` routes.

In `formintB/backend/apps/core/admin.py`, register `BackupRun` using the same admin registration pattern the file already uses for other core models.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q && make test`
Expected: PASS — monitor + fragment tests green, full suite green

- [ ] **Step 5: Commit**

```bash
git add formintB/backend/apps/handlers/fragments/monitor.py formintB/backend/apps/handlers/surface.py formintB/backend/apps/core/admin.py formintB/backend/apps/test_monitor.py
git commit -m "feat(pos-cloud): django-fusion monitor tile + BackupRun admin"
```

## Task C6: Consume the SDK monitor module in the frontend telemetry page

**Files:**
- Modify: `formintB/frontend/package.json` (add `@formints/client` dep)
- Create: `formintB/frontend/src/lib/monitor.ts` (typed wrapper over `getMonitorStatus`)
- Test: `formintB/frontend/src/lib/monitor.test.ts`

**Interfaces:**
- Consumes: `createClient`, `getMonitorStatus` from `@formints/client` (06-js-sdk.md).
- Produces: `monitorApi(baseUrl)` used by the `telemetry` page to render db status + last backup + queue depth.

- [ ] **Step 1: Write the failing test**

Create `formintB/frontend/src/lib/monitor.test.ts`:

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

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/frontend && pnpm vitest run src/lib/monitor.test.ts`
Expected: FAIL — cannot find module `./monitor`

- [ ] **Step 3: Write the wrapper**

Create `formintB/frontend/src/lib/monitor.ts`:

```ts
import { createClient, getMonitorStatus } from '@formints/client';

export function monitorApi(baseUrl: string) {
  const client = createClient(baseUrl);
  return { status: () => getMonitorStatus(client) };
}
```

Add `"@formints/client": "workspace:*"` (or file: reference per `06-js-sdk.md`) to `formintB/frontend/package.json` dependencies. Render the status on the `telemetry` page using `monitorApi`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/formintB/frontend && pnpm vitest run src/lib/monitor.test.ts && pnpm check`
Expected: PASS — test green, Astro check green

- [ ] **Step 5: Commit**

```bash
git add formintB/frontend/package.json formintB/frontend/src/lib/monitor.ts formintB/frontend/src/lib/monitor.test.ts
git commit -m "feat(pos-cloud-frontend): consume @formints/client monitor module in telemetry"
```

## Task C7: Playwright e2e for monitor + inheritance parity sweep

**Files:**
- Create: `formintB/frontend/e2e/monitor.spec.ts`
- Modify: `formintB/frontend/playwright.config.ts` (point `testDir` at `./e2e` if not already)

**Interfaces:**
- Consumes: the running cloud backend (`make cloud-run`, `:8767`) + frontend.
- Produces: a standalone Cloud e2e suite + the sync-feature inheritance check.

- [ ] **Step 1: Write the spec**

Create `formintB/frontend/e2e/monitor.spec.ts`:

```ts
import { test, expect } from '@playwright/test';

test('monitor status shows a healthy database', async ({ page }) => {
  await page.goto('/telemetry');
  await expect(page.getByText('ok').first()).toBeVisible();
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

> If `/telemetry` renders the status via `monitorApi` (Task C6), the first test needs the backend seeded with at least one `BackupRun`; otherwise assert the JSON contract (second test) only.

- [ ] **Step 2: Run the e2e suite**

Run: `cd projects/formints/formintB/frontend && pnpm exec playwright test`
Expected: PASS — both specs green.

- [ ] **Step 3: Sync-feature inheritance sweep**

Verify the Cloud surface still exposes every Pro/Standard sync concept: branch health (sync dashboard), queue summary, conflicts list/resolve, recent activity. For each, open the page/endpoint and confirm it responds. Fix any gap found and add a spec row.

- [ ] **Step 4: Commit**

```bash
git add formintB/frontend/playwright.config.ts formintB/frontend/e2e/
git commit -m "test(pos-cloud-frontend): monitor e2e suite + sync-feature inheritance sweep"
```

---

## Self-Review

1. **Spec coverage:** the single remaining Cloud marker (automatic backups + monitoring) maps to C1-C3; C4 syncs docs. No other Cloud markers exist.
2. **Placeholder scan:** one conditional instruction (C3 test note re: `SyncQueueItem` required fields) names the exact files to mirror. No TBDs.
3. **Type consistency:** `BackupRun` fields (`filename`, `status`, `size_bytes`, `error_message`, `started_at`, `finished_at`) are identical across the model (C1), command (C2), monitor payload (C3), and tests. Route name `monitor-status` matches `reverse()` in tests.

## Execution Handoff

**Plan complete and saved to `projects/formints/docs/superpowers/plans/2026-08-09-editions/04-cloud.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
