/**
 * HTMX bootstrap — wires CSRF headers onto every htmx request (the backend
 * expects the Django CSRF token on POSTs) and surfaces server errors + the
 * cartUpdated event to the Alpine toast system.
 */
import type Htmx from 'htmx.org';

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[2]) : null;
}

type HtmxEvent = Event & { detail?: Record<string, any> };

function asHtmxDetail(evt: Event): Record<string, any> {
  return (evt as HtmxEvent).detail ?? {};
}

export function initHtmxBootstrap(htmx: typeof Htmx): void {
  // Inject the CSRF token header on every request (HTMX does not forward it
  // from forms whose buttons live outside a <form>).
  htmx.on('htmx:configRequest', (evt: Event) => {
    const detail = asHtmxDetail(evt);
    const csrf = getCookie('csrftoken');
    if (csrf && detail.verb !== 'get') {
      detail.headers = detail.headers || {};
      detail.headers['X-CSRFToken'] = csrf;
    }
    // Keep the session cookie flowing across proxied origins.
    detail.credentials = 'same-origin';
  });

  // Broadcast cart mutations to every listener (badge, drawer).
  htmx.on('htmx:afterSwap', (evt: Event) => {
    const detail = asHtmxDetail(evt);
    const trigger = detail?.xhr?.getResponseHeader?.('HX-Trigger');
    if (trigger) {
      document.body.dispatchEvent(new CustomEvent(trigger.replace(/[^\w:]/g, '')));
    }
  });

  // Surf 4xx/5xx fragment responses as error toasts.
  htmx.on('htmx:responseError', (evt: Event) => {
    const detail = asHtmxDetail(evt);
    const status = detail?.xhr?.status;
    window.dispatchEvent(
      new CustomEvent('fusion:toast', {
        detail: {
          message: status === 403 ? 'Session expired — sign in again.' : `Request failed (${status}).`,
          kind: 'error',
        },
      }),
    );
  });

  // Server-set HX-Trigger on the response header (Django sets HX-Trigger) is
  // handled natively by HTMX; this just guards custom event dispatch.
}
