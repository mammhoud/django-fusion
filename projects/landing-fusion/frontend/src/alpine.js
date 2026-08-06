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

// Staggered-cascade cleanup — each grid card carries an inline `--reveal-i`
// (its cascade index). Once its reveal transition lands, drop the delay so
// card hovers are never delayed by the cascade. Mirrors the listener in the
// Django base.html, so both render roads share one motion behavior.
if (typeof document !== 'undefined') {
  document.addEventListener(
    'transitionend',
    (e) => {
      const el = e.target;
      if (el && el.style && el.style.getPropertyValue('--reveal-i') && e.propertyName === 'opacity') {
        el.style.transitionDelay = '0ms';
      }
    },
    true
  );
}

export default (Alpine) => {
  Alpine.plugin(intersect);
  Alpine.plugin(collapse);

  // Magnetic hero CTA — the button drifts toward the cursor (≤6px) and snaps
  // back on leave. Motion is a transform on the wrapper (x-data="magnetic"
  // on a .btn-magnetic span), so the button's own :active press-scale and
  // btn-chip arrow animation stay untouched. Tracked 1:1 while the pointer
  // is inside (.btn-magnetic--tracking kills the transition); on leave the
  // CSS spring re-engages for the snap-back. Mirrors the Alpine.data
  // registration in the Django base.html. GPU-cheap: one layout read per
  // pointer-enter, transform-only updates after that.
  Alpine.data('magnetic', () => ({
    mx: 0,
    my: 0,
    active: false,
    reduce: false,
    cx: 0,
    cy: 0,
    init() {
      this.reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },
    center() {
      const r = this.$el.getBoundingClientRect();
      this.cx = r.left + r.width / 2;
      this.cy = r.top + r.height / 2;
    },
    track(e) {
      if (this.reduce) return;
      this.mx = Math.max(-6, Math.min(6, (e.clientX - this.cx) * 0.08));
      this.my = Math.max(-6, Math.min(6, (e.clientY - this.cy) * 0.08));
    },
    leave() {
      this.active = false;
      this.mx = 0;
      this.my = 0;
    },
  }));
};
