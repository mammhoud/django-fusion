/**
 * Formint POS - Tabler icon sprite generator.
 *
 * Reads official Tabler Icons outline geometry (MIT license, https://tabler.io/icons)
 * from the installed `@tabler/icons` package and emits an Astro component containing
 * a single hidden <svg> with <symbol> defs. Icons are referenced via
 * <svg><use href="#i-{name}" /></svg>, which works in static markup AND inside
 * Alpine.js templates (:href bindings).
 *
 * Regenerate after changing the ICONS list:
 *   cd frontend && node scripts/gen-tabler-sprite.mjs
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

const ICONS_JSON = new URL('../node_modules/@tabler/icons/tabler-nodes-outline.json', import.meta.url);
const OUT_FILE = new URL('../src/components/ui/icons/Sprite.astro', import.meta.url);

/**
 * Icon names (kebab-case, per @tabler/icons) required by the app.
 * `alias` maps our canonical names to Tabler names where they differ.
 */
const ALIAS = {
  cart: 'shopping-cart',
  // material-icon names coming from the sidecar navigation API
  shopping_cart: 'shopping-cart',
  restaurant: 'chef-hat',
  people: 'users',
  contact_page: 'id-badge',
  analytics: 'chart-line',
  settings_applications: 'settings',
  admin_panel_settings: 'shield-check',
  // tabler v3 renames
  'bell-ring': 'bell-ringing',
  'sticky-note': 'note',
  banknote: 'cash-banknote',
  'receipt-text': 'receipt-2',
  handshake: 'heart-handshake',
  steak: 'meat',
};

const ICONS = [
  // ── Shell / chrome ──
  'menu-2', 'search', 'plus', 'minus', 'x', 'check',
  'chevron-left', 'chevron-right', 'chevron-down', 'chevron-up',
  'arrow-left', 'arrow-right', 'arrow-up-right',
  'refresh', 'trash', 'pencil', 'printer', 'eye',
  'moon', 'sun', 'lock', 'key', 'info-circle', 'alert-triangle', 'circle-check',
  'bell', 'bell-off', 'bell-ring', 'clock', 'calendar', 'calendar-stats',
  'note', 'lifebuoy', 'settings', 'shield', 'shield-check', 'writing', 'edit',
  'wallet', 'cash', 'banknote', 'credit-card', 'device-mobile', 'cash-register',
  'receipt', 'receipt-text', 'tag', 'ticket', 'rocket', 'map-2', 'map-pin',
  'ruler', 'table', 'package', 'truck', 'user', 'users', 'cart',
  'clipboard-list', 'layout-dashboard', 'chart-line', 'chart-bar', 'chart-donut',
  'columns', 'trophy', 'circle-x',
  'flask', 'book', 'building-store', 'heart-handshake', 'id-badge',
  'building', 'phone', 'mail', 'pin', 'star', 'filter',
  'sort-ascending', 'sort-descending', 'database', 'world', 'report', 'file-text',
  'tool', 'folder', 'home', 'trending-up', 'trending-down', 'rotate', 'scale',
  // ── Menu items / foods (sale page product grid, tabler v3 set) ──
  'burger', 'pizza', 'coffee', 'mug', 'glass', 'salad', 'fish', 'bowl',
  'bread', 'cake', 'ice-cream', 'bottle', 'cup', 'soup', 'beer', 'milk',
  'egg', 'cookie', 'candy', 'cheese', 'apple', 'banana', 'lemon', 'cherry',
  'carrot', 'mushroom', 'pepper', 'avocado', 'meat', 'bowl-spoon', 'grill-fork', 'chef-hat',
];

function resolve(name) {
  const target = ALIAS[name] || name;
  return target;
}

const nodes = JSON.parse(readFileSync(ICONS_JSON, 'utf8'));

const missing = [];
const symbols = [];
for (const name of ICONS) {
  const target = resolve(name);
  const paths = nodes[target];
  if (!paths) {
    missing.push(`${name} (→ ${target})`);
    continue;
  }
  const inner = paths
    .map(([tag, attrs]) => {
      const attrStr = Object.entries(attrs)
        .map(([k, v]) => `${k}="${String(v).replace(/"/g, '&quot;')}"`)
        .join(' ');
      return `    <${tag} ${attrStr} />`;
    })
    .join('\n');
  symbols.push(
    `  <!-- ${target} -->\n` +
    `  <symbol id="i-${name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">\n` +
    `${inner}\n` +
    `  </symbol>`
  );
}

const astro = `---
// Formint POS - Tabler icon sprite (auto-generated).
// Source: @tabler/icons (MIT) - https://tabler.io/icons
// Regenerate: node scripts/gen-tabler-sprite.mjs
// Reference an icon with: <svg><use href="#i-{name}" /></svg>
---

<svg xmlns="http://www.w3.org/2000/svg" style="display: none" aria-hidden="true">
${symbols.join('\n')}
</svg>
`;

mkdirSync(new URL('../src/components/ui/icons/', import.meta.url), { recursive: true });
writeFileSync(OUT_FILE, astro);

console.log(`Wrote ${symbols.length} icons to ${OUT_FILE.pathname}`);
if (missing.length) {
  console.warn('MISSING from @tabler/icons:');
  for (const m of missing) console.warn('  -', m);
  process.exitCode = 1;
}
