import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';

describe('useDebouncedSearch', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('exposes initial value on both query and debouncedQuery', () => {
    const { result } = renderHook(() => useDebouncedSearch({ initial: 'hello' }));
    expect(result.current.query).toBe('hello');
    expect(result.current.debouncedQuery).toBe('hello');
    expect(result.current.isPending).toBe(false);
  });

  it('flushes the held value after delayMs of idle time', () => {
    const { result } = renderHook(() => useDebouncedSearch({ delayMs: 250 }));

    act(() => result.current.setQuery('abc'));
    expect(result.current.query).toBe('abc');
    expect(result.current.debouncedQuery).toBe('');
    expect(result.current.isPending).toBe(true);

    act(() => {
      vi.advanceTimersByTime(250);
    });
    expect(result.current.debouncedQuery).toBe('abc');
    expect(result.current.isPending).toBe(false);
  });

  it('collapses repeated keystrokes into a single debounced flush', () => {
    const { result } = renderHook(() => useDebouncedSearch({ delayMs: 250 }));

    act(() => {
      result.current.setQuery('a');
      vi.advanceTimersByTime(50);
      result.current.setQuery('ab');
      vi.advanceTimersByTime(50);
      result.current.setQuery('abc');
    });
    // We have NOT yet advanced 250ms after the last keystroke
    expect(result.current.debouncedQuery).toBe('');
    expect(result.current.isPending).toBe(true);

    act(() => vi.advanceTimersByTime(250));
    expect(result.current.debouncedQuery).toBe('abc');
    expect(result.current.isPending).toBe(false);
  });

  it('returns isPending=false when query and debouncedQuery are already equal', () => {
    const { result } = renderHook(() => useDebouncedSearch({ initial: 'foo' }));
    expect(result.current.isPending).toBe(false);

    act(() => result.current.setQuery('foo'));
    // Setting to the current debouncedQuery must not flip isPending on
    expect(result.current.isPending).toBe(false);
  });

  it('clears back to empty when the input is cleared', () => {
    const { result } = renderHook(() => useDebouncedSearch({ delayMs: 250, initial: 'abc' }));

    act(() => result.current.setQuery(''));
    expect(result.current.query).toBe('');
    expect(result.current.isPending).toBe(true);

    act(() => vi.advanceTimersByTime(250));
    expect(result.current.debouncedQuery).toBe('');
    expect(result.current.isPending).toBe(false);
  });

  it('clears the pending timer on unmount so no setState fires after teardown', () => {
    const { result, unmount } = renderHook(() => useDebouncedSearch({ delayMs: 250 }));
    act(() => result.current.setQuery('partial'));
    unmount();
    // Advancing timers post-unmount must not throw
    expect(() => vi.advanceTimersByTime(250)).not.toThrow();
  });

  it('honours a custom delayMs', () => {
    const { result } = renderHook(() => useDebouncedSearch({ delayMs: 75 }));

    act(() => result.current.setQuery('x'));
    expect(result.current.debouncedQuery).toBe('');
    expect(result.current.isPending).toBe(true);

    act(() => vi.advanceTimersByTime(74));
    expect(result.current.debouncedQuery).toBe('');

    act(() => vi.advanceTimersByTime(1));
    expect(result.current.debouncedQuery).toBe('x');
    expect(result.current.isPending).toBe(false);
  });
});
