/**
 * @file theme/usecases.js
 * Merged helpers + usecase registry for all 3 workspace websites.
 *
 * This file is the single source of truth for:
 *   - The usecase registration system (formerly helpers.js)
 *   - All 7 concrete usecases: animations, landing, lms, crm, forms, modal, spa
 *
 * Usage:
 *   import { registerUsecase, initLandingUsecase, USECASES } from '@theme/usecases';
 *   import { initAllUsecases, initUsecase }                  from '@theme/usecases';
 */

import { ready } from '../utility/index.js';

// ─────────────────────────────────────────────────────────────────────────────
// PART 1 — Registration engine  (was helpers.js)
// ─────────────────────────────────────────────────────────────────────────────

/** Internal registry: name → { selectors, loader, init } */
const _registry = new Map();

/**
 * Register a usecase and return its initialiser function.
 *
 * @param {string}    name       Unique key, e.g. 'crm', 'lms'
 * @param {string[]}  selectors  CSS selectors that identify the shell element(s)
 * @param {Function}  [loader]   Optional async loader(shell) → module with optional .init()
 * @returns {Function} initUsecase(root?) – call manually or let auto-init fire on DOMContentLoaded
 */
export function registerUsecase(name, selectors, loader = null) {
  if (_registry.has(name)) {
    console.warn(`[usecases] "${name}" already registered – skipping duplicate.`);
    return _registry.get(name).init;
  }

  /** Init one shell element */
  const _initShell = async (shell) => {
    if (shell.__usecaseInit) return;       // guard against double-init
    shell.__usecaseInit = true;
    shell.dataset.usecaseReady = name;
    try {
      if (loader) {
        const mod = await loader(shell);
        if (mod && typeof mod.init === 'function') await mod.init(shell);
      }
    } catch (err) {
      console.error(`[usecases/${name}] shell init failed`, err);
    }
  };

  /** Init all matching shells inside root */
  const initUsecase = (root = document) => {
    const shells = [];
    for (const sel of selectors) {
      try { root.querySelectorAll(sel).forEach((el) => shells.push(el)); }
      catch (_) { /* invalid selector */ }
    }
    shells.forEach(_initShell);
    return shells;
  };

  _registry.set(name, { selectors, loader, init: initUsecase });

  // Auto-run on DOM ready (page load)
  ready(() => initUsecase(document));

  return initUsecase;
}

/**
 * Get metadata for a registered usecase.
 * @param {string} name
 * @returns {{ selectors, loader, init }|null}
 */
export function getUsecase(name) { return _registry.get(name) ?? null; }

/** All registered usecase names */
export function getUsecaseNames() { return Array.from(_registry.keys()); }

/**
 * Re-run every registered usecase against `root`.
 * Call this after an HTMX swap to reinitialise shells in the new fragment.
 * @param {Element|Document} root
 */
export function reinitUsecases(root = document) {
  for (const { init } of _registry.values()) init(root);
}

// ─────────────────────────────────────────────────────────────────────────────
// PART 2 — Concrete usecases
// ─────────────────────────────────────────────────────────────────────────────

// ── Animations ────────────────────────────────────────────────────────────────
// Pure IntersectionObserver — no external vendor dependency.

const _ANIM_SEL  = '[data-animate], .usecase-animate';
const _ANIM_CLS  = 'is-animated';

/**
 * Activate CSS entrance animations for matching elements.
 * Respects `prefers-reduced-motion`.
 * @param {Element|Document} root
 * @returns {Element[]}
 */
export function initAnimationsUsecase(root = document) {
  const elements = Array.from(root.querySelectorAll(_ANIM_SEL));
  if (!elements.length) return [];

  if (
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ||
    !('IntersectionObserver' in window)
  ) {
    elements.forEach((el) => el.classList.add(_ANIM_CLS));
    return elements;
  }

  const io = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add(_ANIM_CLS);
        obs.unobserve(e.target);
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -10% 0px' },
  );

  elements.forEach((el) => io.observe(el));
  return elements;
}

// Auto-run animations on page load
ready(initAnimationsUsecase);

// ── Shell usecases ─────────────────────────────────────────────────────────────

/** Landing / marketing page shell */
export const initLandingUsecase = registerUsecase(
  'landing', ['.landing-shell', '[data-usecase~="landing"]'],
);

/** Learning-management-system shell */
export const initLmsUsecase = registerUsecase(
  'lms', ['.lms-shell', '[data-usecase~="lms"]'],
);

/** CRM / dashboard shell */
export const initCrmUsecase = registerUsecase(
  'crm', ['.crm-shell', '[data-usecase~="crm"]'],
);

/** Form-stack shell */
export const initFormsUsecase = registerUsecase(
  'forms', ['.form-stack', '[data-usecase~="forms"]'],
);

/** Modal shell */
export const initModalUsecase = registerUsecase(
  'modal', ['.modal-shell', '[data-usecase~="modal"]'],
);

/** Single-page-app shell — VResume */
export const initSpaUsecase = registerUsecase(
  'spa', ['.spa-shell', '[data-usecase~="spa"]'],
);

// ─────────────────────────────────────────────────────────────────────────────
// PART 3 — Convenience API
// ─────────────────────────────────────────────────────────────────────────────

/** Map of all name → init function */
export const USECASES = {
  animations: initAnimationsUsecase,
  landing:    initLandingUsecase,
  lms:        initLmsUsecase,
  crm:        initCrmUsecase,
  forms:      initFormsUsecase,
  modal:      initModalUsecase,
  spa:        initSpaUsecase,
};

/**
 * Run all usecases on `root` — used after HTMX swaps.
 * @param {Element|Document} root
 */
export function initAllUsecases(root = document) {
  reinitUsecases(root);
  initAnimationsUsecase(root); // animations not in registry so call explicitly
}

/**
 * Run one usecase by name.
 * @param {string} name
 * @param {Element|Document} root
 */
export function initUsecase(name, root = document) {
  const fn = USECASES[name];
  if (!fn) { console.warn(`[usecases] Unknown usecase: "${name}"`); return []; }
  return fn(root);
}

export default USECASES;
