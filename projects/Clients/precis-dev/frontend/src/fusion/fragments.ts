/**
 * Fragments binding — precis.
 *
 * Hydrates `[data-fusion-fragment]` nodes on load. HTMX LiveFragments
 * keep using their own swap path; this covers plain fetch-driven
 * fragments (SSG shells, islands) from the shared module.
 */
import { loadFragment, refreshFragments } from '@fusion/modules/fragments';

let hydrated = false;

export function hydrateFragments(root: ParentNode = document): Promise<string[]> {
  hydrated = true;
  return refreshFragments(root);
}

export function initFusionFragments(): void {
  if (hydrated) return;
  // Script runs at end of body — DOM is ready; still guard for safety.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => void hydrateFragments());
  } else {
    void hydrateFragments();
  }
}

export { loadFragment, refreshFragments };
export type { FragmentOptions } from '@fusion/modules/fragments';
