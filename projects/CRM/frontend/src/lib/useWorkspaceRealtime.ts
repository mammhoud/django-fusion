// useWorkspaceRealtime — subscribe a React island to its workspace's event
// group over the same Channels consumer the SSE road uses. A single WebSocket
// delivers ``{ event, data }`` frames for every mutation published by the
// backend; islands filter to the events they care about and re-fetch.
//
// Transport notes:
//   * The workspace id is resolved from the session via
//     ``/apis/core/workspace/current/`` (the canonical named road;
//     the /api/v1/ copy is deprecated).
//   * The socket URL reuses ``window.location``, which keeps the connection
//     same-origin (and cookie-authenticated) behind the Astro dev proxy and in
//     production alike.
//   * Reconnects with capped exponential backoff, and is cleaned up on unmount.

import { useEffect, useRef } from 'react';

export interface WorkspaceEvent {
  event: string;
  data: Record<string, unknown>;
}

interface Options {
  /** Only invoke ``onEvent`` for events matching this predicate. */
  filter?: (event: WorkspaceEvent) => boolean;
  /** Enable/disable the subscription (defaults to always-on). */
  enabled?: boolean;
  /** Override the workspace id (used by tests); defaults to session lookup. */
  workspaceId?: number | string;
}

// The deprecated compatibility copy remains at /api/v1/workspace/current/;
// the canonical session-cookie road below is /apis/core/.
const WORKSPACE_ENDPOINT = '/apis/core/workspace/current/';
const MAX_BACKOFF_MS = 10_000;

function socketUrl(workspaceId: number | string): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}/ws/workspace/${workspaceId}/`;
}

async function resolveWorkspaceId(): Promise<number | string | null> {
  try {
    const res = await fetch(WORKSPACE_ENDPOINT, { headers: { Accept: 'application/json' } });
    if (!res.ok) return null;
    const payload = (await res.json()) as { workspace_id?: number | string | null };
    return payload.workspace_id ?? null;
  } catch {
    return null;
  }
}

export function useWorkspaceRealtime(
  onEvent: (event: WorkspaceEvent) => void,
  { filter, enabled = true, workspaceId: workspaceIdOverride }: Options = {},
): void {
  // Keep the latest handler/filter in refs so the effect never needs to
  // tear down and reconnect the socket when the callback identity changes.
  const onEventRef = useRef(onEvent);
  const filterRef = useRef(filter);
  const enabledRef = useRef(enabled);
  onEventRef.current = onEvent;
  filterRef.current = filter;
  enabledRef.current = enabled;

  useEffect(() => {
    if (!enabledRef.current) return;

    let socket: WebSocket | null = null;
    let disposed = false;
    let attempts = 0;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = (workspaceId: number | string) => {
      if (disposed) return;
      const ws = new WebSocket(socketUrl(workspaceId));
      socket = ws;

      ws.onopen = () => {
        attempts = 0;
      };

      ws.onmessage = (message: MessageEvent) => {
        let event: WorkspaceEvent;
        try {
          event = JSON.parse(message.data as string) as WorkspaceEvent;
        } catch {
          return; // Ignore malformed frames — realtime is best-effort.
        }
        if (!filterRef.current || filterRef.current(event)) {
          onEventRef.current(event);
        }
      };

      ws.onclose = () => {
        if (disposed) return;
        const delay = Math.min(MAX_BACKOFF_MS, 500 * 2 ** attempts);
        attempts += 1;
        reconnectTimer = setTimeout(() => connect(workspaceId), delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    (async () => {
      const id = workspaceIdOverride ?? (await resolveWorkspaceId());
      if (id != null) connect(id);
    })();

    return () => {
      disposed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceIdOverride]);
}
