/**
 * Unit tests for FusionStore — Tauri-compatible session preference adapter.
 *
 * Covers:
 * - initSession stores the preference
 * - getSessionPreference returns stored/previously stored values
 * - clearSession removes the preference
 * - initFromHealthCheck fetches /fusion/health and caches preference
 * - initFromHealthCheck falls back to false on fetch error
 * - Multiple sequential operations maintain state
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fusionStore } from '../lib/fusion-store';

// ═══════════════════════════════════════════════════════════════════
// initSession / getSessionPreference / clearSession
// ═══════════════════════════════════════════════════════════════════

describe('FusionStore session management', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    await fusionStore.clearSession().catch(() => {});
  });

  it('initSession stores the preference', async () => {
    await fusionStore.initSession(true);
    const pref = await fusionStore.getSessionPreference();
    expect(pref).toBe(true);
  });

  it('getSessionPreference returns undefined when nothing is stored', async () => {
    const pref = await fusionStore.getSessionPreference();
    expect(pref).toBeUndefined();
  });

  it('getSessionPreference returns false when stored as false', async () => {
    await fusionStore.initSession(false);
    const pref = await fusionStore.getSessionPreference();
    expect(pref).toBe(false);
  });

  it('clearSession removes the stored preference', async () => {
    await fusionStore.initSession(true);
    expect(await fusionStore.getSessionPreference()).toBe(true);

    await fusionStore.clearSession();
    expect(await fusionStore.getSessionPreference()).toBeUndefined();
  });

  it('supports multiple sequential operations', async () => {
    await fusionStore.initSession(true);
    expect(await fusionStore.getSessionPreference()).toBe(true);

    await fusionStore.initSession(false);
    expect(await fusionStore.getSessionPreference()).toBe(false);

    await fusionStore.clearSession();
    expect(await fusionStore.getSessionPreference()).toBeUndefined();
  });
});

// ═══════════════════════════════════════════════════════════════════
// initFromHealthCheck
// ═══════════════════════════════════════════════════════════════════

describe('initFromHealthCheck', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    await fusionStore.clearSession().catch(() => {});
  });

  it('fetches /fusion/health and caches a true preference', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ fusion_render_first: true, reason: 'admin' }),
    } as Response);

    const result = await fusionStore.initFromHealthCheck('http://localhost:8766');
    expect(result).toBe(true);

    const pref = await fusionStore.getSessionPreference();
    expect(pref).toBe(true);
  });

  it('fetches /fusion/health and caches a false preference', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ fusion_render_first: false, reason: 'cashier' }),
    } as Response);

    const result = await fusionStore.initFromHealthCheck('http://localhost:8766');
    expect(result).toBe(false);

    const pref = await fusionStore.getSessionPreference();
    expect(pref).toBe(false);
  });

  it('returns false when fetch fails', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    const result = await fusionStore.initFromHealthCheck('http://localhost:8766');
    expect(result).toBe(false);
  });

  it('returns false when response is not ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
    } as Response);

    const result = await fusionStore.initFromHealthCheck('http://localhost:8766');
    expect(result).toBe(false);
  });

  it('uses default URL when none is provided', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ fusion_render_first: true }),
    } as Response);

    await fusionStore.initFromHealthCheck();
    expect(fetch).toHaveBeenCalledWith('http://localhost:8766/fusion/health');
  });
});
