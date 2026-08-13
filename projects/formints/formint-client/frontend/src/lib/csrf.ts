/**
 * Django CSRF helpers — single source for the token used by both the HTMX
 * bootstrap (htmx:configRequest) and the Alpine fetch calls (login/logout).
 *
 * Django sets the `csrftoken` cookie on the first fragment/HTMX response
 * (the product-grid template renders `{% csrf_token %}`), so the token is
 * available on the storefront origin before any mutation is attempted.
 */

export function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Build the headers object for credentialed POST/DELETE fetches to the
 * Django backend. Omits the token when the cookie has not arrived yet so
 * the request is not sent with a stale/empty header.
 */
export function csrfHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getCsrfToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'X-CSRFToken': token } : {}),
    ...extra,
  };
}
