/**
 * Fragment loader — framework-agnostic.
 *
 * Fetches fusion fragment endpoints (``/fragment/...``) and swaps them
 * into `[data-fusion-fragment]` targets, or any element you pass. Falls
 * back to plain fetch so it works with Django/Wagtail backends and the
 * Astro dev proxy alike.
 *
 * ```ts
 * import { loadFragment, refreshFragments } from 'fusion-js/modules/fragments';
 *
 * await loadFragment('/fragment/ping/', { target: '#ping-slot' });
 * refreshFragments(document.body); // hydrate all data-fusion-fragment nodes
 * ```
 */

export interface FragmentOptions {
  /** Element or CSS selector to receive the HTML. Default: the `data-fusion-fragment` sibling. */
  target?: Element | string;
  /** Whether to replace target content (true) or append (false). Default: true. */
  replace?: boolean;
  /** Extra fetch options (headers, credentials…). Defaults: Accept text/html, same-origin. */
  fetch?: RequestInit;
  /** Element that receives `.is-loading` during the request. */
  loadingEl?: Element | null;
  /** Called after the swap with the fetched HTML string. */
  onSwap?: (html: string, target: Element) => void;
}

const DEFAULT_FETCH: RequestInit = {
  headers: { Accept: 'text/html' },
  credentials: 'same-origin',
};

/** Resolve a `target` option to an element. */
function resolveTarget(
  root: Element,
  option: FragmentOptions['target'],
): Element | null {
  if (typeof option === 'string') return root.querySelector(option);
  if (option instanceof Element) return option;
  return root; // default: the element that carries data-fusion-fragment
}

/**
 * Load a fragment URL and swap it into the target. Returns the swapped
 * HTML string (empty when the request failed).
 */
export async function loadFragment(
  url: string,
  options: FragmentOptions = {},
): Promise<string> {
  const replace = options.replace ?? true;
  const request: RequestInit = { ...DEFAULT_FETCH, ...options.fetch };

  if (options.loadingEl) options.loadingEl.classList.add('is-loading');
  try {
    const response = await fetch(url, request);
    if (!response.ok) return '';
    const html = await response.text();
    const target = resolveTarget(
      (options.loadingEl as Element | null) ?? document.body,
      options.target,
    );
    if (target) {
      if (replace) target.innerHTML = html;
      else target.insertAdjacentHTML('beforeend', html);
      options.onSwap?.(html, target);
    }
    return html;
  } catch {
    return '';
  } finally {
    if (options.loadingEl) options.loadingEl.classList.remove('is-loading');
  }
}

/**
 * Hydrate every `[data-fusion-fragment]` element: each node's
 * `data-fusion-fragment` attribute is the endpoint URL, and its content
 * is swapped in. Resolves when all fragments have been attempted.
 */
export async function refreshFragments(root: ParentNode = document): Promise<string[]> {
  const nodes = Array.from(
    root.querySelectorAll<HTMLElement>('[data-fusion-fragment]'),
  );
  return Promise.all(
    nodes.map((node) => {
      const url = node.dataset.fusionFragment;
      return url ? loadFragment(url, { target: node, loadingEl: node }) : Promise.resolve('');
    }),
  );
}

export default { loadFragment, refreshFragments };
