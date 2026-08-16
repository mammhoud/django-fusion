import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useStatusToast } from '../../hooks/useStatusToast';

describe('useStatusToast hook', () => {
  it('starts with a null status', () => {
    const { result } = renderHook(() => useStatusToast());
    expect(result.current.status).toBeNull();
  });

  it('showSuccess stores a success entry', () => {
    const { result } = renderHook(() => useStatusToast());
    act(() => result.current.showSuccess('Saved!'));
    expect(result.current.status).toEqual({ type: 'success', message: 'Saved!' });
  });

  it('showError stores an error entry', () => {
    const { result } = renderHook(() => useStatusToast());
    act(() => result.current.showError('Network error'));
    expect(result.current.status).toEqual({ type: 'error', message: 'Network error' });
  });

  it('dismiss clears the current status', () => {
    const { result } = renderHook(() => useStatusToast());
    act(() => result.current.showError('X'));
    expect(result.current.status).not.toBeNull();
    act(() => result.current.dismiss());
    expect(result.current.status).toBeNull();
  });

  it('auto-dismisses after the default 4 s window', () => {
    vi.useFakeTimers();
    try {
      const { result } = renderHook(() => useStatusToast());
      act(() => result.current.showError('temporary'));
      expect(result.current.status).not.toBeNull();
      act(() => {
        vi.advanceTimersByTime(4001);
      });
      expect(result.current.status).toBeNull();
    } finally {
      vi.useRealTimers();
    }
  });

  it('respects a custom durationMs option', () => {
    vi.useFakeTimers();
    try {
      const { result } = renderHook(() => useStatusToast({ durationMs: 1000 }));
      act(() => result.current.showError('quick'));
      act(() => {
        vi.advanceTimersByTime(999);
      });
      expect(result.current.status).not.toBeNull();
      act(() => {
        vi.advanceTimersByTime(2);
      });
      expect(result.current.status).toBeNull();
    } finally {
      vi.useRealTimers();
    }
  });
});
