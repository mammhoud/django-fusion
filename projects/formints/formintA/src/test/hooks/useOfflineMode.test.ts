import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOfflineMode } from '@/hooks/useOfflineMode';

function setOnline(value: boolean) {
  Object.defineProperty(window.navigator, 'onLine', {
    configurable: true,
    value,
  });
  window.dispatchEvent(new Event(value ? 'online' : 'offline'));
}

describe('useOfflineMode', () => {
  afterEach(() => {
    setOnline(true);
    vi.restoreAllMocks();
  });

  it('returns false when the device is online', () => {
    setOnline(true);
    const { result } = renderHook(() => useOfflineMode());
    expect(result.current).toBe(false);
  });

  it('returns true when the device goes offline', () => {
    setOnline(true);
    const { result } = renderHook(() => useOfflineMode());
    act(() => setOnline(false));
    expect(result.current).toBe(true);
  });

  it('returns false again when back online', () => {
    setOnline(true);
    const { result } = renderHook(() => useOfflineMode());
    act(() => setOnline(false));
    act(() => setOnline(true));
    expect(result.current).toBe(false);
  });
});
