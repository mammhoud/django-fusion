/**
 * Home-page GSAP enhancement — re-exports the lazy fusion motion module.
 *
 * GSAP + ScrollTrigger now live in src/fusion/motion.ts and are dynamic-
 * imported only when `[data-gsap]` hooks exist (zero cost on pages without
 * motion). This file keeps the old `@/lib/home-motion` import path working
 * for the home page while delegating to the single bundle module.
 */
export { initFusionMotion, startFusionMotion } from '@/fusion/motion';
