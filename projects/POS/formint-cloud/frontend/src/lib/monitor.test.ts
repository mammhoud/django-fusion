import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { monitorApi } from './monitor';

const fetchMock = vi.fn();

beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

const api = monitorApi('http://127.0.0.1:8767');

describe('monitorApi', () => {
  it('reads monitor status', async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          database: 'ok',
          last_backup: {
            filename: 'a.db',
            status: 'success',
            size_bytes: 1,
            started_at: 'x',
          },
          sync_queue_depth: 2,
        }),
        { status: 200 },
      ),
    );
    const status = await api.status();
    expect(status.database).toBe('ok');
    expect(status.sync_queue_depth).toBe(2);
    expect(status.last_backup?.filename).toBe('a.db');
  });

  it('surfaces null last_backup when no backups exist', async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({ database: 'ok', last_backup: null, sync_queue_depth: 0 }),
        { status: 200 },
      ),
    );
    const status = await api.status();
    expect(status.last_backup).toBeNull();
    expect(status.sync_queue_depth).toBe(0);
  });

  it('throws ApiError on a failed response', async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ error: 'boom' }), { status: 503 }),
    );
    await expect(api.status()).rejects.toThrow(/503/);
  });

  it('strips a trailing slash from the base URL', async () => {
    const api2 = monitorApi('http://127.0.0.1:8767/');
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ database: 'ok', last_backup: null, sync_queue_depth: 0 }), {
        status: 200,
      }),
    );
    await api2.status();
    const [url] = fetchMock.mock.calls[0];
    expect(String(url)).toBe('http://127.0.0.1:8767/monitor/status');
  });
});
