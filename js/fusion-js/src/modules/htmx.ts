/**
 * HTMX wrapper — framework-agnostic.
 *
 * Attaches an HTMX instance, applies safe defaults for fusion backends
 * (cross-origin fragments), and exposes typed request helpers. Zero
 * dependencies: pass any htmx 1.x/2.x instance (e.g. `import htmx from
 * 'htmx.org'`) or let `attachHtmx` pick one from `window.htmx`.
 *
 * ```ts
 * import { attachHtmx, isHtmxRequest } from 'fusion-js/modules/htmx';
 * import htmx from 'htmx.org';
 *
 * attachHtmx(htmx, { selfRequestsOnly: false });
 * if (isHtmxRequest(headers)) { /* respond with a fragment *\/ }
 * ```
 */

/** Minimal structural type — keeps this module decoupled from htmx's own types. */
export interface HtmxLike {
  config?: Record<string, unknown>;
  on?: (event: string, handler: (event: Event) => void) => void;
  trigger?: (element: Element | string, event: string, detail?: unknown) => void;
  [key: string]: unknown;
}

declare global {
  interface Window {
    htmx?: HtmxLike;
  }
}

export interface HtmxConfig {
  /** Allow requests to the fusion backend origin (fragments). Default: false. */
  selfRequestsOnly?: boolean;
  /** Global indicator element id toggled during requests. Default: 'htmx-global-indicator'. */
  indicatorId?: string;
}

const DEFAULT_CONFIG: HtmxConfig = {
  selfRequestsOnly: false,
  indicatorId: 'htmx-global-indicator',
};

/** True when the given headers object carries the htmx request marker. */
export function isHtmxRequest(headers?: Headers | Record<string, string>): boolean {
  if (!headers) return false;
  const value =
    headers instanceof Headers
      ? headers.get('HX-Request')
      : (headers as Record<string, string>)['HX-Request'];
  return value === 'true';
}

/** True when the request targets a fragment swap (HX-Target present). */
export function isFragmentRequest(headers?: Headers | Record<string, string>): boolean {
  if (!headers) return false;
  const value =
    headers instanceof Headers ? headers.get('HX-Target') : (headers as Record<string, string>)['HX-Target'];
  return Boolean(value);
}

/**
 * Attach an htmx instance and apply fusion-friendly defaults.
 * Returns the instance. When `instance` is omitted, resolves from
 * `window.htmx` (import the runtime somewhere first).
 */
export function attachHtmx(instance?: HtmxLike, config: HtmxConfig = {}): HtmxLike | null {
  const htmx = instance ?? window.htmx ?? null;
  if (!htmx) return null;

  const options = { ...DEFAULT_CONFIG, ...config };
  htmx.config = {
    ...(htmx.config ?? {}),
    selfRequestsOnly: options.selfRequestsOnly ?? false,
  };
  return htmx;
}

/** Show/hide a global request indicator bound to htmx lifecycle events. */
export function bindIndicator(htmx: HtmxLike, indicatorId = 'htmx-global-indicator'): () => void {
  const el = () => document.getElementById(indicatorId);
  const on = htmx.on ?? (() => undefined);

  const show = (): void => {
    const node = el();
    if (node) node.classList.add('is-active');
  };
  const hide = (): void => {
    const node = el();
    if (node) node.classList.remove('is-active');
  };

  on('htmx:beforeRequest', show);
  on('htmx:afterRequest', hide);
  on('htmx:responseError', hide);
  on('htmx:sendError', hide);

  return () => {
    hide();
  };
}

/** Detail payload of htmx swap events (structural — decoupled from htmx types). */
export interface HtmxSwapDetail {
  elt: Element;
  target?: Element | null;
  [key: string]: unknown;
}

/** Wait for an htmx element swap (used after `hx-boost` navigation). */
export function onSwap(
  htmx: HtmxLike,
  handler: (detail: HtmxSwapDetail) => void,
): () => void {
  const on = htmx.on ?? (() => undefined);
  on('htmx:afterSwap', handler as unknown as (event: Event) => void);
  return () => undefined;
}

export default {
  attachHtmx,
  isHtmxRequest,
  isFragmentRequest,
  bindIndicator,
  onSwap,
};
