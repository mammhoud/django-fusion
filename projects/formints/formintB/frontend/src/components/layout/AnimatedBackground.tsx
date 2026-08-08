import { useEffect, useRef } from 'react';
import gsap from 'gsap';

/**
 * AnimatedBackground — GSAP-driven ambient gradient blobs.
 *
 * Renders a fixed, pointer-events-none layer of large blurred color blobs
 * that drift slowly behind the app content. Colors are pulled from the
 * active FlyonUI theme via CSS variables, so they adapt to every variant
 * (perplexity / corporate / luxury / pastel) in both light & dark mode.
 *
 * Performance: only `transform` + `opacity` are animated (GPU-friendly),
 * and the whole layer is disabled under `prefers-reduced-motion`.
 */
export default function AnimatedBackground() {
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    // Respect reduced-motion — render a static, subtle layer instead.
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) return;

    const blobs = Array.from(root.querySelectorAll<HTMLElement>('[data-blob]'));
    const ctx = gsap.context(() => {
      blobs.forEach((blob, i) => {
        const seed = i * 37.5; // unique phase per blob
        gsap.to(blob, {
          x: `${gsap.utils.random(-8, 8)}%`,
          y: `${gsap.utils.random(-8, 8)}%`,
          scale: gsap.utils.random(1.05, 1.25),
          opacity: gsap.utils.random(0.55, 0.9),
          duration: gsap.utils.random(18, 30),
          delay: seed * 0.1,
          ease: 'sine.inOut',
          repeat: -1,
          yoyo: true,
        });
      });
    }, root);

    return () => ctx.revert();
  }, []);

  return (
    <div
      ref={rootRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden"
    >
      {/* Base wash — tints the whole canvas with the theme surface */}
      <div
        className="absolute inset-0 opacity-70"
        style={{
          background:
            'linear-gradient(135deg, var(--color-base-100) 0%, var(--color-base-200) 55%, var(--color-base-100) 100%)',
        }}
      />
      {/* Drifting blobs — large, heavy blur, theme semantic colors */}
      <div
        data-blob
        className="absolute -top-[15%] -left-[10%] h-[55vmax] w-[55vmax] rounded-full blur-[110px]"
        style={{ backgroundColor: 'var(--color-primary)', opacity: 0.16 }}
      />
      <div
        data-blob
        className="absolute top-[30%] -right-[15%] h-[48vmax] w-[48vmax] rounded-full blur-[110px]"
        style={{ backgroundColor: 'var(--color-secondary)', opacity: 0.14 }}
      />
      <div
        data-blob
        className="absolute -bottom-[20%] left-[20%] h-[50vmax] w-[50vmax] rounded-full blur-[120px]"
        style={{ backgroundColor: 'var(--color-accent)', opacity: 0.12 }}
      />
      <div
        data-blob
        className="absolute top-[5%] left-[40%] h-[38vmax] w-[38vmax] rounded-full blur-[100px]"
        style={{ backgroundColor: 'var(--color-info)', opacity: 0.1 }}
      />
    </div>
  );
}
