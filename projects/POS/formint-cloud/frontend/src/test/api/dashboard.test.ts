/**
 * POS Cloud — dashboard API client contract tests.
 *
 * Pins the request paths, HTTP methods, and typed payloads the client
 * issues for every `/api/dashboard/*` endpoint, so the frontend stays in
 * lockstep with `apps.handlers.sync_dashboard`.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { dashboard } from '../../api/dashboard';

const mockFetch = vi.fn();

function jsonOk(body: unknown): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch);
  mockFetch.mockResolvedValue(jsonOk({}));
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

function lastFetch() {
  const call = mockFetch.mock.calls[mockFetch.mock.calls.length - 1]!;
  return {
    url: String(call[0]),
    init: (call[1] ?? {}) as RequestInit,
  };
}

describe('dashboard API client', () => {
  it('fetches all branches health at the right path', async () => {
    await dashboard.getBranchesHealth();
    expect(lastFetch().url).toBe('/api/dashboard/branches/health');
  });

  it('URL-encodes the branch code in the single-health path', async () => {
    await dashboard.getBranchHealth('BR 001');
    expect(lastFetch().url).toBe('/api/dashboard/branches/BR%20001/health');
  });

  it('fetches queue summary and by-branch at the right paths', async () => {
    await dashboard.getQueueSummary();
    expect(lastFetch().url).toBe('/api/dashboard/queue/summary');

    await dashboard.getQueueByBranch();
    expect(lastFetch().url).toBe('/api/dashboard/queue/by-branch');
  });

  it('defaults queue list to pending and encodes status', async () => {
    await dashboard.getQueueList();
    expect(lastFetch().url).toBe('/api/dashboard/queue/list/pending');

    await dashboard.getQueueList('delivering');
    expect(lastFetch().url).toBe('/api/dashboard/queue/list/delivering');
  });

  it('POSTs queue retry and cancel with the item id', async () => {
    await dashboard.retryQueueItem(42);
    expect(lastFetch().url).toBe('/api/dashboard/queue/retry/42');
    expect(lastFetch().init.method).toBe('POST');

    await dashboard.cancelQueueItem(7);
    expect(lastFetch().url).toBe('/api/dashboard/queue/cancel/7');
    expect(lastFetch().init.method).toBe('POST');
  });

  it('fetches conflicts and conflict stats at the right paths', async () => {
    await dashboard.getConflicts();
    expect(lastFetch().url).toBe('/api/dashboard/conflicts');

    await dashboard.getConflictStats();
    expect(lastFetch().url).toBe('/api/dashboard/conflicts/stats');
  });

  it('POSTs conflict resolve with the resolution + notes body', async () => {
    await dashboard.resolveConflict(3, 'use_remote', { notes: 'take branch' });
    const { url, init } = lastFetch();
    expect(url).toBe('/api/dashboard/conflicts/3/resolve');
    expect(init.method).toBe('POST');
    expect(JSON.parse(String(init.body))).toEqual({
      resolution: 'use_remote',
      merged_data: undefined,
      notes: 'take branch',
    });
  });

  it('POSTs conflict dismiss with the conflict id', async () => {
    await dashboard.dismissConflict(9);
    expect(lastFetch().url).toBe('/api/dashboard/conflicts/9/dismiss');
    expect(lastFetch().init.method).toBe('POST');
  });

  it('fetches activity with a limit query param', async () => {
    await dashboard.getActivity(5);
    expect(lastFetch().url).toBe('/api/dashboard/activity?limit=5');
  });

  it('unwraps a 4xx error into the envelope', async () => {
    mockFetch.mockResolvedValueOnce(
      new Response(JSON.stringify({ error: 'not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    const res = await dashboard.getQueueList('bogus');
    expect(res.ok).toBe(false);
    expect(res.status).toBe(404);
    expect(res.error).toBe('not found');
    expect(res.data).toBeNull();
  });

  it('surfaces network failures as a non-ok envelope', async () => {
    mockFetch.mockRejectedValueOnce(new Error('boom'));
    const res = await dashboard.getQueueSummary();
    expect(res.ok).toBe(false);
    expect(res.status).toBe(0);
    expect(res.error).toBe('boom');
  });
});
