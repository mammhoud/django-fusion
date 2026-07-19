/**
 * Chat API
 * ========
 * REST + WebSocket API for the sidecar chat service.
 *
 * REST endpoints:
 *   GET  /chat/<room_id>   — get chat history
 *   POST /chat/<room_id>   — post a chat message
 *
 * WebSocket:
 *   ws://127.0.0.1:8765/ws/chat/<room_id>
 */

import { SIDECAR_WS_BASE } from './sidecar';
import sidecar from './sidecar';

// ---- Types ----------------------------------------------------------------

export interface ChatMessage {
  id: string;
  room_id: string;
  user: string;
  content: string;
  timestamp: string;
}

export interface ChatHistoryResponse {
  room_id: string;
  messages: ChatMessage[];
}

export interface WsChatFrame {
  type: 'message' | 'typing' | 'status';
  text?: string;
  content?: string;
  sender?: string;
  user?: string;
  ts?: string;
  timestamp?: string;
}

export type WsConnState = 'connecting' | 'open' | 'closed' | 'error';

export interface ChatWsConnection {
  /** Send a JSON-serializable message through the persistent WebSocket */
  send: (data: Record<string, unknown>) => void;
  /** Close the connection and stop auto-reconnecting */
  close: () => void;
}

export interface ChatWsOptions {
  room: string;
  onMessage: (msg: ChatMessage) => void;
  onStateChange?: (state: WsConnState) => void;
  onTyping?: (isTyping: boolean) => void;
  reconnectMs?: number;
}

// ---- REST API -------------------------------------------------------------

export const chat = {
  /**
   * Get chat history for a room.
   */
  getHistory: (roomId: string) =>
    sidecar.get<ChatHistoryResponse>(`/chat/${roomId}`),

  /**
   * Post a message to a chat room via REST (HTTP fallback).
   */
  postMessage: (roomId: string, user: string, content: string) =>
    sidecar.post<ChatMessage>(`/chat/${roomId}`, { user, content }),
};

// ---- WebSocket ------------------------------------------------------------

/**
 * Create and manage a WebSocket connection to the chat service.
 * Returns a `ChatWsConnection` with `send` and `close` methods.
 * Auto-reconnects on disconnect.
 */
export function createChatWs(options: ChatWsOptions): ChatWsConnection {
  const {
    room,
    onMessage,
    onStateChange,
    onTyping,
    reconnectMs = 4000,
  } = options;

  let ws: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let typingTimer: ReturnType<typeof setTimeout> | null = null;
  let destroyed = false;

  /** Send a JSON message through the persistent WebSocket. No-op if disconnected. */
  const send = (data: Record<string, unknown>) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  };

  const connect = () => {
    if (destroyed) return;
    if (ws?.readyState === WebSocket.OPEN) return;

    onStateChange?.('connecting');
    ws = new WebSocket(`${SIDECAR_WS_BASE}/ws/chat/${room}`);

    ws.onopen = () => {
      onStateChange?.('open');
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
    };

    ws.onmessage = (ev) => {
      try {
        const data: WsChatFrame = JSON.parse(ev.data);

        // Handle typing indicator
        if (data.type === 'typing') {
          onTyping?.(true);
          if (typingTimer) clearTimeout(typingTimer);
          typingTimer = setTimeout(() => onTyping?.(false), 2500);
          return;
        }

        onTyping?.(false);

        // Normalize to ChatMessage format
        const msg: ChatMessage = {
          id: data.ts || data.timestamp || Date.now().toString(),
          room_id: room,
          user: data.sender || data.user || 'support',
          content: data.text || data.content || '',
          timestamp: data.ts || data.timestamp || new Date().toISOString(),
        };

        onMessage(msg);
      } catch {
        // Non-JSON frame — ignore
      }
    };

    ws.onclose = () => {
      onStateChange?.('closed');
      if (!destroyed) {
        reconnectTimer = setTimeout(connect, reconnectMs);
      }
    };

    ws.onerror = () => {
      onStateChange?.('error');
      ws?.close();
    };
  };

  const close = () => {
    destroyed = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (typingTimer) clearTimeout(typingTimer);
    ws?.close();
    ws = null;
  };

  // Start connection
  connect();

  return { send, close };
}
