/**
 * useStaggeredReveal — IntersectionObserver hook for staggered entry animations
 * 
 * Applies scroll-triggered staggered reveals to child elements.
 * Uses GPU-safe properties (transform, opacity) for smooth performance.
 * 
 * Usage:
 * const { containerRef, getItemProps } = useStaggeredReveal({ count: items.length });
 * 
 * return (
 *   <div ref={containerRef} className="grid grid-cols-3 gap-4">
 *     {items.map((item, idx) => (
 *       <div key={item.id} {...getItemProps(idx)}>
 *         {item.name}
 *       </div>
 *     ))}
 *   </div>
 * );
 */

import { useEffect, useRef, useCallback, type RefObject } from 'react';

interface UseStaggeredRevealOptions {
  /** Number of items to stagger */
  count: number;
  /** Threshold to trigger (0-1) */
  threshold?: number;
  /** Root margin */
  rootMargin?: string;
  /** Base delay between items (ms) */
  staggerDelay?: number;
  /** Enable animations */
  enabled?: boolean;
}

interface UseStaggeredRevealResult {
  /** Ref to attach to the container element */
  containerRef: RefObject<HTMLDivElement | null>;
  /** Get props for each item */
  getItemProps: (index: number) => {
    ref: (el: HTMLDivElement | null) => void;
    style: React.CSSProperties;
    className: string;
  };
}

export function useStaggeredReveal({
  count,
  threshold = 0.1,
  rootMargin = '0px 0px -50px 0px',
  staggerDelay = 75,
  enabled = true,
}: UseStaggeredRevealOptions): UseStaggeredRevealResult {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const revealedItems = useRef(new Set<number>());

  // Reset on count change
  useEffect(() => {
    itemRefs.current = itemRefs.current.slice(0, count);
    revealedItems.current.clear();
  }, [count]);

  // Create observer
  useEffect(() => {
    if (!enabled || typeof IntersectionObserver === 'undefined') return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const index = itemRefs.current.indexOf(entry.target as HTMLDivElement);
            if (index !== -1 && !revealedItems.current.has(index)) {
              revealedItems.current.add(index);
              
              // Apply stagger delay
              const delay = index * staggerDelay;
              const el = entry.target as HTMLDivElement;
              
              el.style.transitionDelay = `${delay}ms`;
              el.classList.add('is-visible');
            }
          }
        });
      },
      { threshold, rootMargin }
    );

    observerRef.current = observer;

    return () => {
      observer.disconnect();
      observerRef.current = null;
    };
  }, [enabled, threshold, rootMargin, staggerDelay]);

  // Observe items
  useEffect(() => {
    if (!enabled || !observerRef.current) return;

    itemRefs.current.forEach((el) => {
      if (el && !revealedItems.current.has(itemRefs.current.indexOf(el))) {
        observerRef.current?.observe(el);
      }
    });

    return () => {
      itemRefs.current.forEach((el) => {
        if (el) {
          observerRef.current?.unobserve(el);
        }
      });
    };
  }, [enabled, count]);

  const getItemProps = useCallback((index: number) => {
    return {
      ref: (el: HTMLDivElement | null) => {
        itemRefs.current[index] = el;
      },
      style: {
        opacity: 0,
        transform: 'translateY(16px)',
        transition: 'opacity 600ms cubic-bezier(0.32, 0.72, 0, 1), transform 600ms cubic-bezier(0.32, 0.72, 0, 1)',
      } as React.CSSProperties,
      className: 'stagger-reveal-item',
    };
  }, []);

  return { containerRef, getItemProps };
}

/**
 * Simple scroll reveal hook for a single element
 */
export function useScrollReveal<T extends HTMLElement = HTMLDivElement>(
  options: {
    threshold?: number;
    rootMargin?: string;
    enabled?: boolean;
  } = {}
): { ref: RefObject<T | null>; isVisible: boolean } {
  const { threshold = 0.1, rootMargin = '0px 0px -50px 0px', enabled = true } = options;
  const ref = useRef<T | null>(null);
  const isVisible = useRef(false);

  useEffect(() => {
    if (!enabled || !ref.current || typeof IntersectionObserver === 'undefined') return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !isVisible.current) {
            isVisible.current = true;
            entry.target.classList.add('is-visible');
          }
        });
      },
      { threshold, rootMargin }
    );

    ref.current.classList.add('scroll-reveal');
    observer.observe(ref.current);

    return () => {
      observer.disconnect();
    };
  }, [enabled, threshold, rootMargin]);

  return { ref, isVisible: isVisible.current };
}
