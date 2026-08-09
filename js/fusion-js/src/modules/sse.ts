/**
 * Server-Sent Events client — framework-agnostic.
 *
 * Typed EventSource wrapper with automatic reconnect + exponential
 * backoff and named-event dispatch. Works with the fusion `SSEMixin`
 * endpoints (text/event-stream) from any TS framework.
 *
 * ```ts
 * import { createSSEClient } from 'fusion-js/modules/sse';
 *
 * const client = createSSEClient('/api/stream/', {
 *   onMessage: (data) => updateUI(data),
 *   events: { 'course-progress': (e) => trackProgress(e) },
 * });
 * client.close();
 * ```
 */

export interface SSEHandlers {
  /** Called for every `message` event with the parsed JSON payload. */
  onMessage?: (data: unknown, raw: MessageEvent<string>) => void;
  /** Named-event handlers keyed by event name. */
  events?: Record<string, (data: unknown, raw: MessageEvent<string>) => void>;
  /** Called when the connection opens. */
  onOpen?: () => void;
  /** Called when the connection errors (before retry scheduling). */
  onError?: (error: Event) => void;
  /** Called when the stream ends permanently (close() or fatal). */
  onClose?: () => void;
}

export interface SSEClientOptions extends SSEHandlers {
  /** Base reconnect delay in ms. Default: 1500. */
  retryBaseMs?: number;
  /** Max reconnect delay in ms. Default: 30_000. */
  retryMaxMs?: number;
  /** Max consecutive retries before giving up (Infinity = always). Default: Infinity. */
  maxRetries?: number;
  /** Parse payloads as JSON. Set false to receive raw strings. Default: true. */
  json?: boolean;
  /** Credentials mode. Default: 'same-origin'. */
  withCredentials?: boolean;
}

export interface SSEClient {
  /** The underlying EventSource (null once closed). */
  readonly source: EventSource | null;
  /** Close the stream and stop reconnecting. */
  close: () => void;
  /** Whether the client is still connected or retrying. */
  readonly active: boolean;
  /** Current retry count. */
  readonly retries: number;
}

const parse = (raw: string, json: boolean): unknown =>
  json ? (JSON.parse(raw) as unknown) : raw;

/**
 * Create a resilient SSE client. Auto-reconnects with backoff; named
 * events dispatch to `handlers.events[event]`; close() is idempotent.
 */
export function createSSEClient(url: string, options: SSEClientOptions = {}): SSEClient {
  const retryBaseMs = options.retryBaseMs ?? 1500;
  const retryMaxMs = options.retryMaxMs ?? 30_000;
  const maxRetries = options.maxRetries ?? Infinity;
  const json = options.json ?? true;

  let source: EventSource | null = null;
  let closed = false;
  let retries = 0;
  let timer: ReturnType<typeof setTimeout> | null = null;

  const dispatch = (event: MessageEvent<string>, name: string): void => {
    let data: unknown;
    try {
      data = parse(event.data, json);
    } catch {
      data = event.data; // fall back to raw when JSON parsing fails
    }
    if (name === 'message') {
      options.onMessage?.(data, event);
    } else {
      options.events?.[name]?.(data, event);
    }
  };

  const scheduleReconnect = (): void => {
    if (closed) return;
    if (retries >= maxRetries) {
      options.onClose?.();
      return;
    }
    const delay = Math.min(retryBaseMs * 2 ** retries, retryMaxMs);
    retries += 1;
    timer = setTimeout(connect, delay);
  };

  const connect = (): void => {
    if (closed) return;
    source = new EventSource(url, { withCredentials: options.withCredentials ?? true });
    source.onopen = () => {
      retries = 0;
      options.onOpen?.();
    };
    source.onmessage = (event) => dispatch(event as MessageEvent<string>, 'message');
    source.onerror = (event) => {
      options.onError?.(event);
      source?.close();
      source = null;
      scheduleReconnect();
    };
    if (options.events) {
      for (const name of Object.keys(options.events)) {
        source.addEventListener(name, (event) =>
          dispatch(event as MessageEvent<string>, name),
        );
      }
    }
  };

  connect();

  return {
    get source() {
      return source;
    },
    get active() {
      return !closed;
    },
    get retries() {
      return retries;
    },
    close() {
      closed = true;
      if (timer) clearTimeout(timer);
      source?.close();
      source = null;
      options.onClose?.();
    },
  };
}

export default { createSSEClient };
