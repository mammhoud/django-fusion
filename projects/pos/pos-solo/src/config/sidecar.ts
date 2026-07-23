/**
 * POS Solo sidecar connection settings.
 *
 * Solo and Full use the Python sidecar/Redux API path, while Mini talks to
 * its Rust backend directly. Keep these values in one place so the RTK Query
 * base API, legacy API helpers, and WebSocket middleware cannot drift onto
 * different ports.
 */
const DEFAULT_SIDECAR_BASE = 'http://127.0.0.1:8766';

export const SIDECAR_BASE = (
  import.meta.env.VITE_POS_SIDECAR_URL || DEFAULT_SIDECAR_BASE
).replace(/\/$/, '');

export const SIDECAR_WS_BASE = SIDECAR_BASE.replace(/^http/, 'ws');
