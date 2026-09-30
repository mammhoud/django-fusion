/**
 * Scroll reveal + smooth anchors — framework-agnostic.
 *
 * IntersectionObserver-based reveal for `[data-fusion-reveal]` elements
 * (plus a CSS class toggle) and smooth scrolling for in-page anchors.
 * Respects `prefers-reduced-motion`.
 *
 * ```html
 * <section data-fusion-reveal>…</section>
 * ```
 * ```ts
 * import { initScrollReveal } from 'fusion-js/modules/scroll';
 * const stop = initScrollReveal({ staggerMs: 80 });
 * ```
 */

export interface ScrollRevealOptions {
  /** Elements to observe. Default: `[data-fusion-reveal]`. */
  selector?: string;
  /** Class added when the element enters the viewport. Default: 'is-revealed'. */
  revealedClass?: string;
  /** Optional per-element stagger in ms (index × staggerMs applied via transition-delay). */
  staggerMs?: number;
  /** IntersectionObserver ratio. Default: 0.15. */
  threshold?: number;
  /** Root margin passed to the observer. Default: '0px 0px -40px'. */
  rootMargin?: string;
}

export interface ScrollHandle {
  /** Stop observing (revealed elements keep their state). */
  stop: () => void;
}

const prefersReducedMotion = (): boolean =>
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Reveal elements as they scroll into view. Returns a handle whose
 * `stop()` disconnects the observer.
 */
export function initScrollReveal(options: ScrollRevealOptions = {}): ScrollHandle {
  const selector = options.selector ?? '[data-fusion-reveal]';
  const revealedClass = options.revealedClass ?? 'is-revealed';
  const threshold = options.threshold ?? 0.15;
  const rootMargin = options.rootMargin ?? '0px 0px -40px';
  const staggerMs = options.staggerMs ?? 0;

  if (typeof IntersectionObserver === 'undefined' || prefersReducedMotion()) {
    // No observer or reduced motion — reveal everything immediately.
    document.querySelectorAll<HTMLElement>(selector).forEach((el) => {
      el.classList.add(revealedClass);
    });
    return { stop: () => undefined };
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target as HTMLElement;
        if (staggerMs > 0) {
          const index = Array.from(
            document.querySelectorAll<HTMLElement>(selector),
          ).indexOf(el);
          el.style.transitionDelay = `${Math.min(index * staggerMs, 800)}ms`;
        }
        el.classList.add(revealedClass);
        observer.unobserve(el);
      }
    },
    { threshold, rootMargin },
  );

  document.querySelectorAll<HTMLElement>(selector).forEach((el) => observer.observe(el));

  return {
    stop: () => observer.disconnect(),
  };
}

/** Smooth-scroll in-page anchors (`a[href^="#"]`) — respects reduced motion. */
export function initSmoothAnchors(offset = 0): () => void {
  if (prefersReducedMotion()) return () => undefined;

  const onClick = (event: Event): void => {
    const anchor = (event.currentTarget as HTMLAnchorElement).getAttribute('href');
    if (!anchor || !anchor.startsWith('#')) return;
    const target = document.getElementById(anchor.slice(1));
    if (!target) return;
    event.preventDefault();
    const top = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: 'smooth' });
    history.replaceState(null, '', anchor);
  };

  const anchors = Array.from(document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'));
  anchors.forEach((a) => a.addEventListener('click', onClick));
  return () => anchors.forEach((a) => a.removeEventListener('click', onClick));
}

export default { initScrollReveal, initSmoothAnchors };
