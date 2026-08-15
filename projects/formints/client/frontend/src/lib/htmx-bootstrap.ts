/**
 * HTMX bootstrap — wires CSRF headers onto every htmx request (the backend
 * expects the Django CSRF token on POSTs) and surfaces server errors to the
 * Alpine toast system.
 *
 * `HX-Trigger` response headers (e.g. `cartUpdated`) are handled natively by
 * htmx.org — it fires the named events on the request target, which bubble to
 * `body` where the badge/drawer listen via `cartUpdated from:body`. No manual
 * dispatch is needed (a previous version double-fired every event).
 */
import type Htmx from 'htmx.org';
import { getCsrfToken } from './csrf';

type HtmxEvent = Event & { detail?: Record<string, any> };

function asHtmxDetail(evt: Event): Record<string, any> {
  return (evt as HtmxEvent).detail ?? {};
}

export function initHtmxBootstrap(htmx: typeof Htmx): void {
  // Inject the CSRF token header on every request (HTMX does not forward it
  // from forms whose buttons live outside a <form>).
  htmx.on('htmx:configRequest', (evt: Event) => {
    const detail = asHtmxDetail(evt);
    const csrf = getCsrfToken();
    if (csrf && detail.verb !== 'get') {
      detail.headers = detail.headers || {};
      detail.headers['X-CSRFToken'] = csrf;
    }
    // Keep the session cookie flowing across proxied origins.
    detail.credentials = 'same-origin';
  });

  // Surf 4xx/5xx fragment responses as error toasts.
  htmx.on('htmx:responseError', (evt: Event) => {
    const detail = asHtmxDetail(evt);
    const status = detail?.xhr?.status;
    const message =
      status === 403
        ? // A 403 with a token present means a stale session; without one the
          // CSRF cookie simply had not arrived yet.
          getCsrfToken()
          ? 'Session expired — sign in again.'
          : 'Security check failed — refresh the page.'
        : `Request failed (${status}).`;
    window.dispatchEvent(
      new CustomEvent('fusion:toast', {
        detail: { message, kind: 'error' },
      }),
    );
  });
}
