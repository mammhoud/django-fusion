/**
 * HTMX bootstrap — loaded as a client island.
 *
 * Previously this lived inline in Layout.astro's monolithic <script> block.
 * Now it's an importable module that only loads on pages that need it.
 */

import htmx from 'htmx.org';

// Expose on window for components that reference window.htmx
window.htmx = htmx;

// ── Global in-flight indicator ────────────────────────────────────────
const htmxIndicator = document.getElementById('htmx-global-indicator');

document.addEventListener('htmx:beforeRequest', () => {
  htmxIndicator?.classList.add('htmx-request');
});

document.addEventListener('htmx:afterRequest', () => {
  htmxIndicator?.classList.remove('htmx-request');
});

document.addEventListener('htmx:responseError', () => {
  htmxIndicator?.classList.remove('htmx-request');
});

// ── LiveFragment error fallback ───────────────────────────────────────
document.addEventListener('htmx:responseError', (event) => {
  const target = (event as CustomEvent).detail?.elt as HTMLElement | null;
  if (!target || !target.matches('[data-live-fragment] .live-fragment__target')) return;
  const fallback = target.querySelector<HTMLTemplateElement>('[data-fragment-fallback]');
  if (fallback) target.innerHTML = fallback.innerHTML;
});

// ── Toast on HTMX errors ──────────────────────────────────────────────
document.body.addEventListener('htmx:responseError', () => {
  const Alpine = (window as any).Alpine;
  if (Alpine?.store) {
    Alpine.store('toast').show('Something went wrong — please try again.', 'error');
  }
});
