/**
 * HTMX navigation runtime — framework-agnostic.
 *
 * Turns a plain document link into an HTMX fragment swap against the
 * django-fusion fragment contract (``/apis/fragments/``):
 *
 * ```html
 * <a href="/about/" hx-get="/fragment/pages/about/" hx-target="#page-region"
 *    hx-swap="innerHTML" hx-push-url="/about/" data-fusion-nav>
 * ```
 *
 * The module is split in three pieces so every road can use the part it
 * needs — the backend renders the attributes with its own template tag, the
 * Astro build renders them from the contract API, and the runtime below runs
 * in the browser:
 *
 * * {@link htmxNavAttributes} — pure: link href in, htmx attribute map out.
 * * {@link isFragmentNavigable} — pure: which hrefs are fragment-backed.
 * * {@link installHtmxNavigation} — the post-swap runtime: updates the
 *   document title, the active navigation state, the canonical URL and the
 *   scroll position, then emits ``fusion:navigated`` so islands can react.
 *
 * Zero dependencies — safe to import from any TS framework or bundle.
 */

/** Defaults mirror the backend fragment contract (``FUSION_FRAGMENTS``). */
export interface HtmxNavOptions {
  /** Region the fragment is swapped into. Default: `#page-region`. */
  target: string;
  /** Swap strategy. Default: `innerHTML`. */
  swap: string;
  /** Push the canonical path into history. Default: true. */
  pushUrl: boolean;
  /** Fragment endpoint template. Default: `/fragment/pages/{slug}/`. */
  endpointTemplate: string;
  /** Site name appended to the document title. Default: ''. */
  siteName: string;
  /** Attribute marking a link as navigation. Default: `data-fusion-nav`. */
  navAttribute: string;
  /** Class toggled on the active link. Default: `nav-link--active`. */
  activeClass: string;
  /** Scroll to top after a swap. Default: true. */
  scrollToTop: boolean;
  /** Report a per-link endpoint override (contract routes). */
  endpointFor?: (path: string) => string | null | undefined;
}

export const HTMX_NAV_DEFAULTS: Omit<HtmxNavOptions, 'endpointFor'> = {
  target: '#page-region',
  swap: 'innerHTML',
  pushUrl: true,
  endpointTemplate: '/fragment/pages/{slug}/',
  siteName: '',
  navAttribute: 'data-fusion-nav',
  activeClass: 'nav-link--active',
  scrollToTop: true,
};

/** Path prefixes served by whole documents, never by fragment swaps. */
const NON_FRAGMENT_PREFIXES = [
  '/admin',
  '/django-admin',
  '/accounts',
  '/api/',
  '/apis/',
  '/fragment/',
  '/learning',
  '/invite',
  '/tasks',
  '/documents',
  '/fusion',
  '/components',
  '/i18n/',
  '/static',
  '/media',
];

/** Paths with these extensions are files, not pages. */
const FILE_EXTENSION = /\.[a-z0-9]{1,6}$/i;

/** Normalize an href to a site-root path (`/about/`), or null if external. */
export function fragmentPath(href: string): string | null {
  const raw = String(href || '').trim();
  if (!raw || raw.startsWith('#') || raw.startsWith('mailto:') || raw.startsWith('tel:')) {
    return null;
  }
  if (/^[a-z][a-z0-9+.-]*:/i.test(raw) && !raw.startsWith('/')) {
    // Absolute URL — only same-origin links are fragment-backed.
    if (typeof window === 'undefined') return null;
    try {
      const url = new URL(raw, window.location.origin);
      if (url.origin !== window.location.origin) return null;
      return normalizePath(url.pathname);
    } catch {
      return null;
    }
  }
  const hashless = raw.split('#')[0] ?? '';
  const withoutHash = hashless.split('?')[0] ?? '';
  if (!withoutHash.startsWith('/')) return null;
  return normalizePath(withoutHash);
}

function normalizePath(path: string): string {
  const clean = path.split('?')[0] ?? path;
  if (clean === '/' || clean === '') return '/';
  return (clean.startsWith('/') ? clean : `/${clean}`).replace(/\/+$/, '/');
}

/** True when a link should be served by an HTMX fragment swap. */
export function isFragmentNavigable(href: string): boolean {
  const path = fragmentPath(href);
  if (!path) return false;
  if (FILE_EXTENSION.test(path)) return false;
  if (NON_FRAGMENT_PREFIXES.some((prefix) => path.startsWith(prefix))) return false;
  return true;
}

/** The page slug a fragment endpoint resolves by (last path segment). */
export function fragmentSlug(path: string): string {
  const normalized = normalizePath(path);
  if (normalized === '/') return 'home';
  const segments = normalized.split('/').filter(Boolean);
  return segments[segments.length - 1] || 'home';
}

/**
 * HTMX attributes for a link, or `null` when the link is not fragment-backed.
 * Pass the contract route overrides through `options.endpointFor`.
 */
export function htmxNavAttributes(
  href: string,
  options: Partial<HtmxNavOptions> = {},
): Record<string, string> | null {
  const merged = { ...HTMX_NAV_DEFAULTS, ...options };
  const path = fragmentPath(href);
  if (!path || !isFragmentNavigable(href)) return null;

  const override = merged.endpointFor?.(path);
  const endpoint =
    override && override.length > 0
      ? override
      : merged.endpointTemplate.replace('{slug}', encodeURIComponent(fragmentSlug(path)));

  return {
    'hx-get': endpoint,
    'hx-target': merged.target,
    'hx-swap': merged.swap,
    'hx-push-url': merged.pushUrl ? path : 'false',
    // Marker for the post-swap active-state sync (both roads emit it: this
    // module on the Astro side, {% hx_nav %} on the Django side).
    [merged.navAttribute]: 'true',
  };
}

interface RuntimeOptions extends Partial<Omit<HtmxNavOptions, 'endpointFor'>> {}

interface HtmxSwapLike {
  detail?: { elt?: Element | null; target?: Element | null };
}

declare global {
  interface Window {
    __fusionHtmxNav?: boolean;
  }
}

/**
 * Install the post-swap navigation runtime. Idempotent per document (htmx
 * persists across swaps). Returns a teardown function.
 */
export function installHtmxNavigation(options: RuntimeOptions = {}): () => void {
  const merged = { ...HTMX_NAV_DEFAULTS, ...options };
  if (typeof document === 'undefined') return () => undefined;
  if (window.__fusionHtmxNav) return () => undefined;
  window.__fusionHtmxNav = true;

  const updateActiveLinks = (): void => {
    const current = normalizePath(window.location.pathname);
    document.querySelectorAll<HTMLAnchorElement>(`a[${merged.navAttribute}]`).forEach((link) => {
      const path = fragmentPath(link.getAttribute('href') || '');
      const active =
        path === '/'
          ? current === '/'
          : path !== null && (current === path || current.startsWith(path));
      link.classList.toggle(merged.activeClass, active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  };

  const updateCanonical = (): void => {
    const canonical = document.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (canonical) canonical.href = window.location.href;
  };

  const sync = (root: ParentNode | null): void => {
    const node = root?.querySelector?.('[data-fusion-title]') as HTMLElement | null;
    const title = node?.getAttribute('data-fusion-title') || '';
    if (title) {
      document.title = merged.siteName && title !== merged.siteName
        ? `${title} · ${merged.siteName}`
        : title;
    }
    updateActiveLinks();
    updateCanonical();
    if (merged.scrollToTop) {
      const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    }
    document.body?.dispatchEvent(
      new CustomEvent('fusion:navigated', {
        detail: { url: window.location.href, title: document.title },
      }),
    );
  };

  const onAfterSwap = (event: Event): void => {
    const detail = (event as CustomEvent<HtmxSwapLike['detail']>).detail;
    const region = detail?.target ?? detail?.elt ?? null;
    // Only react to content-region swaps — a cart badge or a comment card
    // must not move the page or rewrite the title.
    if (!region || !region.closest?.(merged.target)) return;
    sync(document.querySelector(merged.target));
  };

  const onHistoryRestore = (): void => sync(document.querySelector(merged.target));

  document.addEventListener('htmx:afterSwap', onAfterSwap);
  document.addEventListener('htmx:historyRestore', onHistoryRestore);

  return () => {
    document.removeEventListener('htmx:afterSwap', onAfterSwap);
    document.removeEventListener('htmx:historyRestore', onHistoryRestore);
    window.__fusionHtmxNav = false;
  };
}

export default {
  HTMX_NAV_DEFAULTS,
  htmxNavAttributes,
  isFragmentNavigable,
  fragmentPath,
  fragmentSlug,
  installHtmxNavigation,
};
