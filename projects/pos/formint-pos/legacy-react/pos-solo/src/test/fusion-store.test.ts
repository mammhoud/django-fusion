/**
 * Unit tests for POS Solo FusionStore.
 *
 * Covers:
 * - initSession / getSessionPreference / clearSession
 * - initFromHealthCheck with mock fetch
 * - Fallback on fetch error
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fusionStore } from '../lib/fusion-store';

describe('FusionStore session management', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    await fusionStore.clearSession().catch(() => {});
  });

  it('initSession stores the preference', async () => {
    await fusionStore.initSession(true);
    expect(await fusionStore.getSessionPreference()).toBe(true);
  });

  it('getSessionPreference returns undefined when empty', async () => {
    expect(await fusionStore.getSessionPreference()).toBeUndefined();
  });

  it('stores false correctly', async () => {
    await fusionStore.initSession(false);
    expect(await fusionStore.getSessionPreference()).toBe(false);
  });

  it('clearSession removes the stored preference', async () => {
    await fusionStore.initSession(true);
    await fusionStore.clearSession();
    expect(await fusionStore.getSessionPreference()).toBeUndefined();
  });
});

describe('initFromHealthCheck', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    await fusionStore.clearSession().catch(() => {});
  });

  it('fetches /fusion/health and caches true', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ fusion_render_first: true, reason: 'admin' }),
    } as Response);

    const result = await fusionStore.initFromHealthCheck('http://localhost:8766');
    expect(result).toBe(true);
    expect(await fusionStore.getSessionPreference()).toBe(true);
  });

  it('fetches /fusion/health and caches false', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ fusion_render_first: false }),
    } as Response);

    const result = await fusionStore.initFromHealthCheck('http://localhost:8766');
    expect(result).toBe(false);
    expect(await fusionStore.getSessionPreference()).toBe(false);
  });

  it('returns false on fetch failure', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));
    const result = await fusionStore.initFromHealthCheck();
    expect(result).toBe(false);
  });

  it('returns false on non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({ ok: false, status: 500 } as Response);
    const result = await fusionStore.initFromHealthCheck();
    expect(result).toBe(false);
  });
});
