/**
 * Loop-CRM SVG icon set — keyed by the navigation icon names in
 * `src/lib/navigation.ts`. Mirrors `apps/core/templatetags/nav_icons.py` on
 * the Django side so both render roads draw identical icons.
 */
export const ICON_PATHS: Record<string, string> = {
  overview:
    '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  crm: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17.5" cy="9" r="2.6"/><path d="M16 14.6a5 5 0 0 1 5.5 5.2"/>',
  marketing: '<path d="M3 11.2 20.5 5.8v12.4L3 12.8v-1.6z"/><path d="M11.6 16.6a3 3 0 1 1-5.7-1.6"/>',
  finance:
    '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>',
  attribution:
    '<circle cx="12" cy="12" r="9"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><circle cx="12" cy="12" r="1.15" fill="currentColor" stroke="none"/>',
  tasks: '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
  reports: '<path d="M4 20V10M10 20V4M16 20v-7M21 20H3"/>',
  workspace:
    '<path d="M21 4h-7M10 4H3M21 12h-9M8 12H3M21 20h-5M12 20H3"/><circle cx="12" cy="4" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="14" cy="20" r="2"/>',
  people: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17.5" cy="9" r="2.6"/><path d="M16 14.6a5 5 0 0 1 5.5 5.2"/>',
  ai: '<path d="M4 5h16v14H4z"/><path d="m8 10 2 2-2 2M12.5 14H16"/>',
  loop: '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20.5 3.5v4.5H16"/>',
};

const ATTRIBUTES =
  'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';

/** Inline SVG markup for a named icon (empty string for unknown keys). */
export function iconSvg(name: string, size = 18): string {
  const paths = ICON_PATHS[name];
  if (!paths) return '';
  return `<svg class="loop-nav-svg" width="${size}" height="${size}" ${ATTRIBUTES}>${paths}</svg>`;
}
