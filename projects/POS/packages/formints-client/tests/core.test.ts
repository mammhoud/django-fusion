import { describe, it, expect, vi, afterEach } from 'vitest';
import { createClient, ApiError } from '../src/core';

describe('core client', () => {
  afterEach(() => vi.restoreAllMocks());

  it('GETs JSON and applies the base URL', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'content-type': 'application/json' } }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const client = createClient('http://127.0.0.1:8767');
    const data = await client.request<{ ok: boolean }>('/health');
    expect(fetchMock).toHaveBeenCalledWith('http://127.0.0.1:8767/health', expect.any(Object));
    expect(data).toEqual({ ok: true });
  });

  it('throws ApiError on non-2xx', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('nope', { status: 403 })));
    const client = createClient('http://x');
    await expect(client.request('/secret')).rejects.toThrow(ApiError);
  });
});
