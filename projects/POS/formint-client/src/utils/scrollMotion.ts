/**
 * useScrollMotion — GSAP ScrollTrigger choreography for the POS client.
 *
 * Same motion language as the Formint Café storefront (ScrollMotion.astro):
 *   1. Image Scale & Fade — `[data-gsap-media]` starts at scale 0.8 / opacity
 *      0.35 and grows to full as it scrolls in; darkens and fades out as it
 *      leaves the viewport (transform + opacity only).
 *   2. Card Stacking — `[data-stack-card]` children rise and overlap as the
 *      user scrolls, giving the featured section physical depth.
 *
 * Motion is gated behind gsap.matchMedia so `prefers-reduced-motion` users
 * get a static, fully readable layout. Every tween uses only transform and
 * opacity (hardware-accelerated). Call `refresh()` after async data renders
 * new nodes; `dispose()` on unmount kills every trigger.
 */
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const imageTriggers: gsap.core.Tween[] = [];
const stackTriggers: gsap.core.Tween[] = [];

function killAll() {
  while (imageTriggers.length) {
    const t = imageTriggers.pop();
    t?.scrollTrigger?.kill();
    t?.kill();
  }
  while (stackTriggers.length) {
    const t = stackTriggers.pop();
    t?.scrollTrigger?.kill();
    t?.kill();
  }
}

export function useScrollMotion() {
  /** Image Scale & Fade — scrubs media in/out as it crosses the viewport. */
  function initImageFade(scope: Element | Document = document) {
    const imgs = scope.querySelectorAll<HTMLElement>('[data-gsap-media]');
    if (!imgs.length) {
      return;
    }

    const mm = gsap.matchMedia();
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      imgs.forEach((el) => {
        const tween = gsap.fromTo(
          el,
          { scale: 0.8, opacity: 0.35 },
          {
            scale: 1,
            opacity: 1,
            ease: 'none',
            scrollTrigger: {
              trigger: el,
              start: 'top 92%',
              end: 'bottom 20%',
              scrub: 1.2,
            },
          },
        );
        imageTriggers.push(tween);
      });
      return () => killAll();
    });
  }

  /** Card Stacking — consecutive cards rise and overlap the previous one. */
  function initCardStack(scope: Element | Document = document) {
    const cards = scope.querySelectorAll<HTMLElement>('[data-stack-card]');
    if (!cards.length) {
      return;
    }

    const mm = gsap.matchMedia();
    mm.add('(min-width: 768px) and (prefers-reduced-motion: no-preference)', () => {
      cards.forEach((el, i) => {
        const tween = gsap.fromTo(
          el,
          { y: 60 * i, opacity: 0.4 },
          {
            y: 0,
            opacity: 1,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: el,
              start: 'top 88%',
              end: 'bottom 30%',
              scrub: 1,
            },
          },
        );
        stackTriggers.push(tween);
      });
      return () => killAll();
    });
  }

  /** Re-apply motion to a scope (call after async data renders). */
  function refresh(scope?: Element) {
    killAll();
    ScrollTrigger.refresh();
    if (scope) {
      initImageFade(scope);
      initCardStack(scope);
      ScrollTrigger.refresh();
    }
  }

  /** Kill every active trigger (call from onUnmounted). */
  function dispose() {
    killAll();
    ScrollTrigger.getAll().forEach((st) => st.kill());
  }

  return { initImageFade, initCardStack, refresh, dispose };
}
