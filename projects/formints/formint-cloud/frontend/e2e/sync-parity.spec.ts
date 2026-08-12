import { test, expect } from '@playwright/test';

/**
 * Sync-feature inheritance parity sweep (Task C7 Step 3).
 *
 * Verifies the Cloud surface still exposes every Pro/Standard sync concept
 * against a live backend on :8767 (`make dev-api`):
 *
 *   - branch health (sync dashboard)          GET /api/dashboard/branches/health
 *   - per-branch health                       GET /api/dashboard/branches/{code}/health
 *   - queue summary / by-branch / list        GET /api/dashboard/queue/*
 *   - conflicts list / stats / resolve / dism. GET/POST /api/dashboard/conflicts*
 *   - recent activity                         GET /api/dashboard/activity
 *
 * Requires seed data: at least one Branch, one pending SyncQueueItem, and
 * one unresolved SyncConflict (see the parity seed step in 04-cloud.md).
 *
 * NOTE: the conflicts test CONSUMES its seed rows (resolves one, dismisses
 * another), so reseed pending conflicts before re-running against a live DB.
 */

const API = process.env.E2E_API_BASE || 'http://127.0.0.1:8767';

test('branch health — all branches and per-branch', async ({ request }) => {
  const res = await request.get(`${API}/api/dashboard/branches/health`);
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(Array.isArray(body.branches)).toBe(true);
  expect(body).toHaveProperty('total');

  const first = body.branches[0];
  expect(first).toBeTruthy();
  const one = await request.get(`${API}/api/dashboard/branches/${first.code}/health`);
  expect(one.status()).toBe(200);
  const oneBody = await one.json();
  expect(oneBody.branch.code).toBe(first.code);
});

test('queue summary, by-branch, and pending list', async ({ request }) => {
  const summary = await request.get(`${API}/api/dashboard/queue/summary`);
  expect(summary.status()).toBe(200);
  const s = await summary.json();
  for (const key of ['pending', 'failed', 'total', 'estimated_backlog_seconds']) {
    expect(s).toHaveProperty(key);
  }

  const byBranch = await request.get(`${API}/api/dashboard/queue/by-branch`);
  expect(byBranch.status()).toBe(200);
  expect(Array.isArray((await byBranch.json()).branches)).toBe(true);

  const list = await request.get(`${API}/api/dashboard/queue/list/pending`);
  expect(list.status()).toBe(200);
  expect(Array.isArray((await list.json()).items)).toBe(true);
});

test('conflicts list, stats, and resolution actions', async ({ request }) => {
  const list = await request.get(`${API}/api/dashboard/conflicts`);
  expect(list.status()).toBe(200);
  const conflicts = (await list.json()).conflicts;
  expect(Array.isArray(conflicts)).toBe(true);

  const stats = await request.get(`${API}/api/dashboard/conflicts/stats`);
  expect(stats.status()).toBe(200);
  const st = await stats.json();
  for (const key of ['pending', 'resolved', 'dismissed', 'total', 'by_entity_type']) {
    expect(st).toHaveProperty(key);
  }

  // Exercise mutating actions when the local E2E database provides pending
  // fixtures. A clean checkout has no conflicts, but it must still pass the
  // read-only contract checks above; seeded CI/staging runs cover the actions.
  const pending = conflicts.filter((c: { status: string }) => c.status === 'pending');
  if (pending.length > 0) {
    const target = pending[0];
    const resolved = await request.post(`${API}/api/dashboard/conflicts/${target.id}/resolve`, {
      data: { resolution: 'use_remote', notes: 'parity sweep' },
    });
    expect(resolved.status()).toBe(200);
    const r = await resolved.json();
    expect(r.status).toBe('resolved');

    // Dismiss a different conflict when more than one is seeded (otherwise
    // the single row would be resolved AND dismissed, which is misleading).
    if (pending.length > 1) {
      const dismissed = await request.post(`${API}/api/dashboard/conflicts/${pending[1].id}/dismiss`, {
        data: {},
      });
      expect(dismissed.status()).toBe(200);
      expect((await dismissed.json()).status).toBe('dismissed');
    }
  }
});

test('recent activity responds', async ({ request }) => {
  const res = await request.get(`${API}/api/dashboard/activity`);
  expect(res.status()).toBe(200);
  expect((await res.json())).toHaveProperty('entries');
});
