/**
 * Sync Events WebSocket
 * =====================
 * Typed client for the POS Cloud real-time sync stream, served by the
 * Django Channels ``SyncEventConsumer`` at ``/ws/sync-events/`` (the
 * surface formerly served by the Robyn sidecar's ``/ws/sync``).
 *
 * The frontend connects once (optionally identifying with a
 * `branch_code`), and receives live `sync_event` / `broker_message`
 * frames whenever the Django API surface mutates data — so the UI
 * updates in real time without polling.
 *
 * Usage:
 *   import { createSyncEventsWs } from './sync-events';
 *
 *   const conn = createSyncEventsWs({
 *     branchCode: 'BR001',
 *     onEvent: (event) => console.log(event.entity_type, event.action),
 *   });
 *   conn.send({ type: 'heartbeat' });
 *   conn.close();
 */

import { SIDECAR_WS_BASE } from './sidecar';

// ---- Types ----------------------------------------------------------------

/** Frames the sidecar sends to connected clients. */
export interface SyncEventFrame {
  type: 'sync_event' | 'broker_message' | 'identify_ack' | 'error';
  entity_type?: string;
  action?: string;
  subtype?: string;
  data?: Record<string, unknown>;
  branch_code?: string;
  node_id?: string;
  status?: string;
  payload?: { message?: string };
}

export interface SyncEventsOptions {
  /** Branch code to identify with (joins the per-branch group). */
  branchCode?: string;
  /** Node id sent with the identify frame. */
  nodeId?: string;
  /** Called for every frame received from the sidecar. */
  onEvent?: (frame: SyncEventFrame) => void;
  /** Called when the connection closes (after reconnect attempts stop). */
  onClose?: (code: number, reason: string) => void;
  /** Called when the connection errors. */
  onError?: (error: Event) => void;
  /** Auto-reconnect with backoff after unexpected drops (default true). */
  autoReconnect?: boolean;
  /** Maximum reconnect attempts before giving up (default: unlimited). */
  maxReconnectAttempts?: number;
}

export interface SyncEventsConnection {
  /** True while the socket is open. */
  readonly open: boolean;
  /** Send a JSON frame to the sidecar. */
  send: (frame: Record<string, unknown>) => boolean;
  /** Close the connection. */
  close: () => void;
}

// ---- Client ---------------------------------------------------------------

/**
 * Open a WebSocket connection to the sidecar sync-events stream.
 */
export function createSyncEventsWs(options: SyncEventsOptions = {}): SyncEventsConnection {
  const {
    branchCode,
    nodeId,
    onEvent,
    onClose,
    onError,
    autoReconnect = true,
    maxReconnectAttempts,
  } = options;

  let socket: WebSocket | null = null;
  let open = false;
  let closedByUser = false;
  let reconnectAttempts = 0;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  const connect = () => {
    socket = new WebSocket(`${SIDECAR_WS_BASE}/ws/sync-events/`);

    socket.onopen = () => {
      open = true;
      reconnectAttempts = 0;
      // The Django consumer requires an explicit identify frame to join
      // the per-branch group (query params are not interpreted).
      if (branchCode) {
        socket?.send(JSON.stringify({
          type: 'identify',
          payload: { branch_code: branchCode, node_id: nodeId ?? '' },
        }));
      }
    };

    socket.onmessage = (message: MessageEvent) => {
      try {
        const frame = JSON.parse(String(message.data)) as SyncEventFrame;
        onEvent?.(frame);
      } catch {
        // Non-JSON frames are ignored.
      }
    };

    socket.onerror = (event: Event) => {
      onError?.(event);
    };

    socket.onclose = (event: CloseEvent) => {
      open = false;
      socket = null;
      if (closedByUser) {
        onClose?.(event.code, event.reason);
        return;
      }
      if (!autoReconnect) {
        onClose?.(event.code, event.reason);
        return;
      }
      if (maxReconnectAttempts !== undefined && reconnectAttempts >= maxReconnectAttempts) {
        onClose?.(event.code, event.reason);
        return;
      }
      // Exponential backoff: 1s → 2s → 4s → … capped at 15s.
      const delay = Math.min(1000 * 2 ** reconnectAttempts, 15_000);
      reconnectAttempts += 1;
      reconnectTimer = setTimeout(connect, delay);
    };
  };

  connect();

  return {
    get open() {
      return open;
    },
    send: (frame: Record<string, unknown>): boolean => {
      if (!socket || socket.readyState !== WebSocket.OPEN) return false;
      socket.send(JSON.stringify(frame));
      return true;
    },
    close: () => {
      closedByUser = true;
      open = false;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      socket?.close();
    },
  };
}

export default createSyncEventsWs;
