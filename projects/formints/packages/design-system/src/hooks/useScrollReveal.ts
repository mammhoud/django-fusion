/**
 * @formints/design-system — useScrollReveal Hook
 * 
 * Intersection Observer hook for scroll-triggered entry animations.
 * Applies staggered reveals to child elements.
 */

import { useEffect, useRef, type RefObject } from 'react';

interface UseScrollRevealOptions {
  /** Threshold to trigger (0-1) */
  threshold?: number;
  /** Root margin */
  rootMargin?: string;
  /** Apply stagger to children */
  stagger?: boolean;
}

interface UseScrollRevealResult<T extends HTMLElement> {
  ref: RefObject<T>;
  isVisible: boolean;
}

export function useScrollReveal<T extends HTMLElement = HTMLDivElement>(
  options: UseScrollRevealOptions = {},
): UseScrollRevealResult<T> {
  const { threshold = 0.1, rootMargin = '0px 0px -50px 0px', stagger = true } = options;
  const ref = useRef<T>(null);
  const isVisible = useRef(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !isVisible.current) {
            isVisible.current = true;
            element.classList.add('is-visible');
            
            if (stagger) {
              // Add stagger class to container
              element.classList.add('scroll-reveal-stagger');
            }
          }
        });
      },
      { threshold, rootMargin }
    );

    // Add initial class
    element.classList.add('scroll-reveal');
    if (stagger) {
      element.classList.add('scroll-reveal-stagger');
    }

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [threshold, rootMargin, stagger]);

  return { ref, isVisible: isVisible.current };
}

/**
 * Simple scroll reveal for vanilla JS/React
 */
export function initScrollReveal() {
  if (typeof document === 'undefined') return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
  );

  document.querySelectorAll('.scroll-reveal').forEach((el) => {
    observer.observe(el);
  });

  return () => observer.disconnect();
}
