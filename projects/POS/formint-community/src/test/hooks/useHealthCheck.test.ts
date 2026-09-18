import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useHealthCheck } from '@/hooks/useHealthCheck';

const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

afterEach(() => {
  fetchMock.mockReset();
});

describe('useHealthCheck', () => {
  it('stays idle when no baseUrl is provided', () => {
    const { result } = renderHook(() => useHealthCheck(''));
    expect(result.current.idle).toBe(false);
    expect(result.current.healthy).toBe(false);
    expect(result.current.status).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('reports healthy after a successful monitor probe', async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          database: 'ok',
          last_backup: null,
          sync_queue_depth: 0,
        }),
        { status: 200 },
      ),
    );

    const { result } = renderHook(() =>
      useHealthCheck('http://127.0.0.1:8767'),
    );

    // Initially idle (fetch in flight).
    expect(result.current.idle).toBe(true);

    await waitFor(() => {
      expect(result.current.idle).toBe(false);
    });

    expect(result.current.healthy).toBe(true);
    expect(result.current.status?.database).toBe('ok');
    expect(result.current.error).toBeNull();
  });

  it('reports unhealthy when the probe fails', async () => {
    fetchMock.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() =>
      useHealthCheck('http://127.0.0.1:8767'),
    );

    await waitFor(() => {
      expect(result.current.idle).toBe(false);
    });

    expect(result.current.healthy).toBe(false);
    expect(result.current.status).toBeNull();
    expect(result.current.error).toContain('Network error');
  });

  it('reports unhealthy on a non-2xx response', async () => {
    fetchMock.mockResolvedValue(
      new Response('Not Found', { status: 404 }),
    );

    const { result } = renderHook(() =>
      useHealthCheck('http://127.0.0.1:8767'),
    );

    await waitFor(() => {
      expect(result.current.idle).toBe(false);
    });

    expect(result.current.healthy).toBe(false);
    expect(result.current.error).toContain('404');
  });
});
