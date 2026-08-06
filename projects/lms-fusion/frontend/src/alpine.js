/**
 * Alpine entrypoint — registered via @astrojs/alpinejs in astro.config.mjs.
 *
 * The integration injects `setup(Alpine)` (calling this module's default
 * export) before `Alpine.start()`, so this file must NOT call Alpine.start()
 * itself — that double-initializes Alpine and logs a warning.
 *
 * Registers the plugins the components rely on:
 *   - @alpinejs/intersect — `x-intersect` scroll reveals (hero, cards, stats)
 *   - @alpinejs/collapse  — `x-collapse` accordions (FAQ, pricing, Accordion)
 *
 * Without the entrypoint only core Alpine loads and every `x-intersect`
 * directive silently no-ops — reveal elements stay at `opacity: 0` forever.
 */
import intersect from '@alpinejs/intersect';
import collapse from '@alpinejs/collapse';

export default (Alpine) => {
  Alpine.plugin(intersect);
  Alpine.plugin(collapse);
};
