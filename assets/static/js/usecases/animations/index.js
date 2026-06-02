import { ready } from '../../base/utils/index.js';

const ANIMATION_SELECTOR = '[data-animate], .usecase-animate';
const VISIBLE_CLASS = 'is-animated';

function markAnimated(element) {
  element.classList.add(VISIBLE_CLASS);
}

export function initAnimationsUsecase(root = document) {
  const elements = Array.from(root.querySelectorAll(ANIMATION_SELECTOR));

  if (elements.length === 0) {
    return [];
  }

  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
    elements.forEach(markAnimated);
    return elements;
  }

  const observer = new IntersectionObserver((entries, instance) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      }

      markAnimated(entry.target);
      instance.unobserve(entry.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });

  elements.forEach((element) => observer.observe(element));
  return elements;
}

ready(initAnimationsUsecase);
