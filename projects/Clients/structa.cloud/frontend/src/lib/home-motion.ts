/**
 * home-motion.ts — GSAP + ScrollTrigger layer for the Astro home page.
 *
 * GSAP now lives in src/fusion/motion.ts and is dynamic-imported only when
 * `[data-gsap]` hooks exist (zero cost on pages without motion). This file
 * keeps the old `@/lib/home-motion` import path working for the home page
 * while delegating to the single lazy bundle module.
 */
export { initFusionMotion, startFusionMotion } from '@/fusion/motion';
