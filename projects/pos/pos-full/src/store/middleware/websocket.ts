/**
 * Redux WebSocket Middleware — connects to Robyn sidecar streams.
 *
 * Handles:
 *   /ws/entities  — real-time entity CRUD events → invalidates RTK Query caches
 *   /ws/nodes     — node status events
 *   /ws/config    — configuration change events
 */

import { Middleware } from '@reduxjs/toolkit';
import { api } from '../api/baseApi';

interface WsMessage {
  type: 'connected' | 'entity_event' | 'node_event' | 'config_event';
  entity?: string;
  action?: 'create' | 'update' | 'delete';
  data?: { id?: number };
}

let entityWs: WebSocket | null = null;
let nodeWs: WebSocket | null = null;
let configWs: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

// Derive WebSocket URL from the same base as the API
const WS_BASE = 'http://localhost:8766'.replace('http', 'ws');

function connectWebSocket(
  path: string,
  store: any,
  onMessage: (msg: WsMessage) => void,
): WebSocket {
  const ws = new WebSocket(`${WS_BASE}${path}`);

  ws.onopen = () => {
    console.log(`[Redux WS] Connected to ${path}`);
  };

  ws.onmessage = (event) => {
    try {
      const msg: WsMessage = JSON.parse(event.data);
      onMessage(msg);
    } catch (e) {
      console.error(`[Redux WS] Parse error on ${path}:`, e);
    }
  };

  ws.onclose = () => {
    console.log(`[Redux WS] Disconnected from ${path}, reconnecting in 5s...`);
    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      connectWebSocket(path, store, onMessage);
    }, 5000);
  };

  ws.onerror = (err) => {
    console.error(`[Redux WS] Error on ${path}:`, err);
  };

  return ws;
}

function invalidateEntity(store: any, entity: string, action: string, data?: { id?: number }) {
  if (!entity) return;

  // Invalidate LIST tag — causes all queries for this entity to refetch
  if (action === 'create' || action === 'delete') {
    store.dispatch(api.util.invalidateTags([{ type: entity, id: 'LIST' }]));
  }

  // Invalidate specific item tag — causes detail queries to refetch
  if (action === 'update' && data?.id) {
    store.dispatch(api.util.invalidateTags([{ type: entity, id: data.id }]));
  }

  console.log(`[Redux WS] Invalidated ${entity} cache (action: ${action})`);
}

function startWsConnections(store: any) {
  // Entity stream: invalidate RTK Query caches on CRUD events
  if (entityWs?.readyState === WebSocket.OPEN) return;
  entityWs = connectWebSocket('/ws/entities', store, (msg) => {
    if (msg.type === 'entity_event' && msg.entity && msg.action) {
      invalidateEntity(store, msg.entity, msg.action, msg.data);
    }
  });
}

export const websocketMiddleware: Middleware = (store) => {
  // Connect WebSocket on first action dispatch
  let started = false;

  return (next) => (action: any) => {
    if (!started && typeof window !== 'undefined') {
      started = true;
      startWsConnections(store);
    }
    return next(action);
  };
};

// Expose for manual reconnect / status checks
export const wsStatus = () => ({
  entity: entityWs?.readyState ?? 'not_connected',
  node: nodeWs?.readyState ?? 'not_connected',
  config: configWs?.readyState ?? 'not_connected',
});
