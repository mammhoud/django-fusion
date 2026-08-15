/**
 * HTMX bootstrap — loaded once from Layout.astro (bundled as a client script).
 *
 * Ported from landing-fusion's `htmx-bootstrap.ts` and adapted for Formint POS:
 *   - No Redux toast — status is announced through the `#htmx-global-status`
 *     aria-live region instead.
 *   - Request counter — nested HTMX calls don't prematurely hide the indicator
 *   - Fade transitions — smooth in/out via CSS classes, not abrupt display toggle
 *   - Timeout safety — auto-dismiss after 15 s to prevent stuck overlay
 *   - Target label — shows which region is being swapped (via data-skeleton-label)
 *   - Elapsed-time hint — switches from "Loading…" to "Still loading (Xs)" after 4 s
 *   - Branded skeleton — Layout.astro renders a full-page mimetic placeholder
 */

import htmx from 'htmx.org';

// Expose on window for components that reference window.htmx (e.g. data.astro
// uses htmx.ajax() to refresh the table slot after a form save).
window.htmx = htmx;

// Allow cross-origin requests to the configured Django server.
// htmx 2.x defaults `selfRequestsOnly` to true, so an HTMX fragment pointing
// at the server on another origin (Astro on :4321 → Django on :8074) is
// rejected with `htmx:invalidPath`. The server gates fragment CORS to its
// allowed origins, so this only widens the client to reach that gated backend.
htmx.config.selfRequestsOnly = false;

// ── Request state ────────────────────────────────────────────────────────

let requestCount = 0;
let dismissTimer: ReturnType<typeof setTimeout> | null = null;
let elapsedTimer: ReturnType<typeof setInterval> | null = null;
let startTime = 0;
const MAX_REQUEST_MS = 15_000; // auto-dismiss after 15 s
const SLOW_THRESHOLD_MS = 4_000; // switch hint text after 4 s

const getIndicator = (): HTMLElement | null =>
  document.getElementById('htmx-global-indicator');

const getTargetLabel = (): HTMLElement | null =>
  document.getElementById('htmx-indicator-target');

const getHint = (): HTMLElement | null =>
  document.getElementById('htmx-indicator-hint');

const getStatus = (): HTMLElement | null =>
  document.getElementById('htmx-global-status');

/**
 * Show the global indicator with a fade-in.
 * Called on `htmx:beforeRequest`. Safe to call multiple times — uses a
 * counter so nested requests keep the indicator visible.
 */
function showIndicator(triggerElement?: Element | null): void {
  const indicator = getIndicator();
  if (!indicator) return;

  requestCount++;

  // First request — show the overlay
  if (requestCount === 1) {
    startTime = Date.now();
    indicator.classList.add('htmx-request');
    indicator.setAttribute('aria-hidden', 'false');

    // Show which region triggered the request
    const targetLabel = getTargetLabel();
    if (targetLabel && triggerElement) {
      const targetId = triggerElement.getAttribute('hx-target') || '';
      const swapArea = targetId
        ? document.getElementById(targetId)
        : triggerElement;
      const label =
        swapArea?.getAttribute('data-skeleton-label') ||
        swapArea?.closest('[data-skeleton-label]')?.getAttribute('data-skeleton-label') ||
        (targetId ? `#${targetId}` : 'this region');
      targetLabel.textContent = `Swapping ${label}`;
    }

    // Start elapsed-time counter
    if (elapsedTimer) clearInterval(elapsedTimer);
    elapsedTimer = setInterval(updateHint, 500);

    // Safety timeout — auto-dismiss
    if (dismissTimer) clearTimeout(dismissTimer);
    dismissTimer = setTimeout(forceDismiss, MAX_REQUEST_MS);
  }
}

/**
 * Hide the global indicator with a fade-out.
 * Called on `htmx:afterRequest` and `htmx:responseError`.
 * Only hides when all in-flight requests have completed.
 */
function hideIndicator(): void {
  const indicator = getIndicator();
  if (!indicator) return;

  if (requestCount > 0) requestCount--;

  // Only dismiss when all requests are done
  if (requestCount === 0) {
    // Small delay so the user sees the skeleton briefly (avoids flash)
    // but skip the delay if the request was instant (< 200 ms)
    const elapsed = Date.now() - startTime;
    const delay = elapsed < 200 ? 0 : 180;

    setTimeout(() => {
      if (requestCount === 0) {
        indicator.classList.remove('htmx-request');
        indicator.setAttribute('aria-hidden', 'true');
        clearTimers();
      }
    }, delay);
  }
}

/** Force-dismiss the indicator (timeout safety net). */
function forceDismiss(): void {
  if (requestCount === 0) return;
  const indicator = getIndicator();
  if (indicator) {
    indicator.classList.remove('htmx-request');
    indicator.setAttribute('aria-hidden', 'true');
  }
  clearTimers();

  const status = getStatus();
  if (status) status.textContent = 'Request timed out; please retry the section.';
}

function clearTimers(): void {
  if (dismissTimer) { clearTimeout(dismissTimer); dismissTimer = null; }
  if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
  requestCount = 0;
}

/** Update the hint text with elapsed time after slow threshold. */
function updateHint(): void {
  const hint = getHint();
  if (!hint) return;
  const elapsed = Date.now() - startTime;
  if (elapsed > SLOW_THRESHOLD_MS) {
    const seconds = Math.round(elapsed / 1000);
    hint.innerHTML = `<span class="htmx-indicator__pulse htmx-indicator__pulse--slow" aria-hidden="true"></span> Still loading (${seconds}s)&hellip;`;
  }
}

// ── Event listeners ──────────────────────────────────────────────────────

document.addEventListener('htmx:beforeRequest', (event) => {
  const detail = (event as CustomEvent)?.detail;
  const trigger = detail?.elt as Element | null;
  showIndicator(trigger);
});

document.addEventListener('htmx:afterRequest', () => {
  hideIndicator();
});

document.addEventListener('htmx:responseError', () => {
  hideIndicator();
});

// ── LiveFragment error fallback ───────────────────────────────────────────

document.addEventListener('htmx:responseError', (event) => {
  const target = (event as CustomEvent).detail?.elt as HTMLElement | null;
  if (!target || !target.matches('[data-live-fragment] .live-fragment__target')) return;
  const fallback = target.querySelector<HTMLTemplateElement>('[data-fragment-fallback]');
  if (fallback) target.innerHTML = fallback.innerHTML;
});

// ── Status announcements (aria-live, replaces Redux toast) ────────────────

document.body.addEventListener('htmx:responseError', () => {
  const status = getStatus();
  if (status) status.textContent = 'Something went wrong; please retry the section.';
});
