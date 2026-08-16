/**
 * Fusion motion module — lazy GSAP + ScrollTrigger for the precis-landing
 * frontend.
 *
 * GSAP is deliberately NOT part of the main bundle: it is only fetched (via
 * dynamic `import()`) when the page actually contains `[data-gsap]` hooks,
 * so pages without motion pay zero bytes for the library while the home page
 * keeps its Awwwards-grade entrance/rise/gallery animations.
 *
 * The document remains readable without JavaScript or with
 * `prefers-reduced-motion: reduce` — every "from" state is applied only
 * when GSAP actually runs (the Django road ships the same content without
 * this module).
 *
 * Paradigms wired here:
 *   1. Hero intro — cinematic staggered entrance (eyebrow, heading, intro,
 *      actions) with a soft blur-fade, driven on load.
 *   2. Scale & fade cards — course and content cards rise (scale 0.92 → 1)
 *      as they enter and dim as they leave.
 *   3. Gallery scale-in — visual previews ease into view after content
 *      settles and darken/fade (opacity → 0.25) as they exit.
 */
const reduceMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function hasMotionHooks(): boolean {
  return Boolean(document.querySelector('[data-gsap="hero-intro"], [data-gsap="rise"], [data-gsap="gallery"]'));
}

/** Lazily load GSAP and run the page's motion hooks. */
export async function initFusionMotion(): Promise<void> {
  if (reduceMotion || typeof document === 'undefined' || !hasMotionHooks()) {
    return;
  }
  const [{ gsap }, { ScrollTrigger }] = await Promise.all([
    import('gsap'),
    import('gsap/ScrollTrigger'),
  ]);
  gsap.registerPlugin(ScrollTrigger);

  // ── 1. Hero intro ──
  const heroScope = document.querySelector('[data-gsap="hero-intro"]');
  if (heroScope) {
    const targets = heroScope.querySelectorAll<HTMLElement>('[data-gsap="hero-child"]');
    if (targets.length) {
      gsap.fromTo(
        targets,
        { opacity: 0, y: 28, filter: 'blur(6px)' },
        {
          opacity: 1,
          y: 0,
          filter: 'blur(0px)',
          duration: 1.05,
          ease: 'power3.out',
          stagger: 0.14,
          delay: 0.15,
          overwrite: 'auto',
        },
      );
    }
  }

  // ── 2. Scale & fade cards ──
  const cards = document.querySelectorAll<HTMLElement>('[data-gsap="rise"]');
  if (cards.length) {
    const trigger = cards[0].parentElement;
    gsap.fromTo(
      cards,
      { opacity: 0, scale: 0.92, y: 24 },
      {
        opacity: 1,
        scale: 1,
        y: 0,
        ease: 'power2.out',
        stagger: 0.12,
        scrollTrigger: { trigger, start: 'top 82%', once: true },
      },
    );

    // Gentle exit fade — cards dim as they scroll past the lower fold.
    gsap.to(cards, {
      opacity: 0.25,
      ease: 'none',
      overwrite: 'auto',
      scrollTrigger: {
        trigger,
        start: 'bottom 78%',
        end: 'bottom 30%',
        scrub: 0.8,
      },
    });
  }

  // ── 3. Gallery scale-in ──
  const items = document.querySelectorAll<HTMLElement>('[data-gsap="gallery-child"]');
  if (items.length) {
    gsap.fromTo(
      items,
      { opacity: 0, scale: 0.94, y: 16 },
      {
        opacity: 1,
        scale: 1,
        y: 0,
        duration: 0.7,
        ease: 'power2.out',
        stagger: 0.1,
        scrollTrigger: {
          trigger: items[0].closest('[data-gsap="gallery"]') || items[0].parentElement,
          start: 'top 84%',
          once: true,
        },
      },
    );
  }

  // Recompute scroll measurements once fonts/images settle.
  const refresh = (): void => ScrollTrigger.refresh();
  window.addEventListener('load', refresh, { once: true });
  if (document.fonts) document.fonts.ready.then(refresh).catch(() => {});
}

// Side-effect boot: pages that import this module directly (e.g. the home
// page's <script>) run motion immediately. initFusion() also calls this, so
// the idempotent guard below prevents double-registration.
let started = false;
export function startFusionMotion(): void {
  if (started) return;
  started = true;
  void initFusionMotion();
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startFusionMotion, { once: true });
  } else {
    startFusionMotion();
  }
}
