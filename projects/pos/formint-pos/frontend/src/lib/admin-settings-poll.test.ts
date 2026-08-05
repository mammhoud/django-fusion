import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminSettingsWatcher, type AdminSettingsState } from './admin-settings-poll';

function state(overrides: Partial<AdminSettingsState>): AdminSettingsState {
  return {
    session_preference: null,
    admin_preference: null,
    admin_version: null,
    ...overrides,
  };
}

describe('AdminSettingsWatcher', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('does not fire on baseline when the session cache matches the row', async () => {
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () =>
        state({ session_preference: false, admin_preference: false, admin_version: 1 }),
      onChange,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(onChange).not.toHaveBeenCalled();
    watcher.dispose();
  });

  it('fires on baseline when the session cache is stale vs the row', async () => {
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () =>
        state({ session_preference: true, admin_preference: false, admin_version: 1 }),
      onChange,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(onChange).toHaveBeenCalledWith(false);
    watcher.dispose();
  });

  it('fires when the admin preference changes (version bump + pref diff)', async () => {
    const states = [
      state({ session_preference: false, admin_preference: false, admin_version: 1 }),
      state({ session_preference: false, admin_preference: true, admin_version: 2 }),
    ];
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () => states.shift() ?? null,
      onChange,
      intervalMs: 1000,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(onChange).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1000);
    expect(onChange).toHaveBeenCalledWith(true);
    watcher.dispose();
  });

  it('does not fire on a same-mode admin save (version bump, pref unchanged)', async () => {
    const states = [
      state({ session_preference: true, admin_preference: true, admin_version: 1 }),
      state({ session_preference: true, admin_preference: true, admin_version: 2 }),
    ];
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () => states.shift() ?? null,
      onChange,
      intervalMs: 1000,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    await vi.advanceTimersByTimeAsync(1000);
    expect(onChange).not.toHaveBeenCalled();
    watcher.dispose();
  });

  it('maps default → null and fires a clear when it differs from a stale session', async () => {
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () =>
        state({ session_preference: true, admin_preference: null, admin_version: 7 }),
      onChange,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(onChange).toHaveBeenCalledWith(null);
    watcher.dispose();
  });

  it('does nothing when no settings row exists (both fields null)', async () => {
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () => state({}),
      onChange,
      intervalMs: 1000,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    await vi.advanceTimersByTimeAsync(1000);
    expect(onChange).not.toHaveBeenCalled();
    watcher.dispose();
  });

  it('fires when a settings row is created after startup', async () => {
    const states = [
      state({}),
      state({ session_preference: null, admin_preference: true, admin_version: 5 }),
    ];
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () => states.shift() ?? null,
      onChange,
      intervalMs: 1000,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(onChange).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1000);
    expect(onChange).toHaveBeenCalledWith(true);
    watcher.dispose();
  });

  it('keeps the baseline on fetch failure and fires on a later change', async () => {
    const states: (AdminSettingsState | null)[] = [
      state({ session_preference: false, admin_preference: false, admin_version: 1 }),
      null, // network blip
      state({ session_preference: false, admin_preference: true, admin_version: 2 }),
    ];
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () => states.shift() ?? null,
      onChange,
      intervalMs: 1000,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(onChange).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1000); // blip
    expect(onChange).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1000); // change
    expect(onChange).toHaveBeenCalledWith(true);
    watcher.dispose();
  });

  it('stop() halts polling and dispose() makes further checks inert', async () => {
    let fetches = 0;
    const onChange = vi.fn();
    const watcher = new AdminSettingsWatcher({
      fetchState: async () => {
        fetches += 1;
        return state({ session_preference: true, admin_preference: true, admin_version: fetches });
      },
      onChange,
      intervalMs: 1000,
    });
    watcher.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(fetches).toBe(1);
    watcher.stop();
    await vi.advanceTimersByTimeAsync(3000);
    expect(fetches).toBe(1);
    watcher.dispose();
    await watcher.checkNow();
    expect(fetches).toBe(1);
  });
});
