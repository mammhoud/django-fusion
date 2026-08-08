/**
 * home-motion.ts — GSAP + ScrollTrigger layer for the Astro home page.
 *
 * Awwwards-grade motion as PROGRESSIVE ENHANCEMENT: every "from" state is
 * applied only when GSAP actually runs, so the server-rendered HTML (and the
 * Django road, which ships the same content without this module) stays fully
 * readable with JS off, JS broken, or `prefers-reduced-motion: reduce`.
 *
 * Paradigms wired here:
 *   1. Hero intro — cinematic staggered entrance (eyebrow, heading, intro,
 *      actions) with a soft blur-fade, driven on load.
 *   2. Scale & fade cards — course and content cards rise (scale 0.92 → 1)
 *      as they enter and dim as they leave.
 *   3. Gallery scale-in — visual previews ease into view after content settles
 *      and darken/fade (opacity → 0.25) as they exit.
 *
 * (The products preview moved from a pinned editorial rail to a simple
 * responsive card grid, so the rail pinning paradigm was removed.)
 */

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const reduceMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ── 1. Hero intro ───────────────────────────────────────────────────────────
function heroIntro(): void {
  if (reduceMotion) return;
  const scope = document.querySelector('[data-gsap="hero-intro"]');
  if (!scope) return;

  const targets = scope.querySelectorAll<HTMLElement>(
    '[data-gsap="hero-child"]',
  );
  if (!targets.length) return;

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

// ── 2. Scale & fade cards ───────────────────────────────────────────────────

function scaleAndFade(): void {
  if (reduceMotion) return;
  const cards = document.querySelectorAll<HTMLElement>('[data-gsap="rise"]');
  if (!cards.length) return;

  gsap.fromTo(
    cards,
    { opacity: 0, scale: 0.92, y: 24 },
    {
      opacity: 1,
      scale: 1,
      y: 0,
      ease: 'power2.out',
      stagger: 0.12,
      scrollTrigger: {
        trigger: cards[0].parentElement,
        start: 'top 82%',
        once: true,
      },
    },
  );

  // Gentle exit fade — cards dim as they scroll past the lower fold.
  // overwrite: 'auto' prevents this scrub from stealing the rise tween's
  // opacity on short viewports where enter/exit ranges overlap.
  gsap.to(cards, {
    opacity: 0.25,
    ease: 'none',
    overwrite: 'auto',
    scrollTrigger: {
      trigger: cards[0].parentElement,
      start: 'bottom 78%',
      end: 'bottom 30%',
      scrub: 0.8,
    },
  });
}

// ── 3. Gallery scale-in ──────────────────────────────────────────────────────
function galleryScaleIn(): void {
  if (reduceMotion) return;
  const items = document.querySelectorAll<HTMLElement>('[data-gsap="gallery-child"]');
  if (!items.length) return;

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

// ── Boot ────────────────────────────────────────────────────────────────────
function init(): void {
  if (typeof document === 'undefined') return;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
}

function mount(): void {
  heroIntro();
  scaleAndFade();
  galleryScaleIn();

  // Offsets are measured before webfonts/images settle — recompute
  // once everything is painted so pin start/end stays accurate.
  const refresh = (): void => ScrollTrigger.refresh();
  window.addEventListener('load', refresh, { once: true });
  if (typeof document !== 'undefined' && document.fonts) {
    document.fonts.ready.then(refresh).catch(() => {});
  }
}

init();
