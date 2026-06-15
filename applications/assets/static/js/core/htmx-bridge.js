/**
 * @file core/htmx-bridge.js
 * HTMX lifecycle bridge for components that need re-initialization after HTMX swaps.
 *
 * Problems this solves:
 *   1. Sliders (Owl Carousel / Swiper) rendered inside HTMX fragments don't init
 *      because the DOMContentLoaded event has already fired.
 *   2. Notification toasts in HTMX-swapped pages miss their container setup.
 *   3. Auth/form pages refreshed via HTMX lose FormValidator bindings.
 *   4. Duplicate component instances when HTMX swaps a target that already had a component.
 *
 * Usage:
 *   import { HTMXBridge } from '@core/htmx-bridge';
 *   HTMXBridge.register('sliders', { selectors: ['.owl-carousel'], reinit: (root) => ... });
 */

/** Symbol used to mark DOM nodes that already have a live instance */
const INIT_KEY = '__htmxBridgeInit__';

// ─────────────────────────────────────────────────────────────────────────────
// Registry of HTMX-aware components
// ─────────────────────────────────────────────────────────────────────────────

/** @type {Map<string, HTMXComponentEntry>} */
const registry = new Map();

/**
 * @typedef {Object} HTMXComponentEntry
 * @property {string}    name        - Component identifier
 * @property {string[]}  selectors   - CSS selectors that match this component's root elements
 * @property {Function}  reinit      - Called with (element, swapTarget) after HTMX swap
 * @property {Function}  [destroy]   - Called with (element) before HTMX swaps it out
 * @property {boolean}   [dedup]     - Skip elements already initialized (default: true)
 * @property {string[]}  [events]    - Extra htmx event names that trigger reinit (e.g. 'htmx:afterSettle')
 */

// ─────────────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────────────

export const HTMXBridge = {
  /**
   * Register a component for HTMX lifecycle awareness.
   * @param {string} name
   * @param {Omit<HTMXComponentEntry, 'name'>} entry
   */
  register(name, entry) {
    if (registry.has(name)) {
      console.warn(`[HTMXBridge] "${name}" already registered — overwriting.`);
    }
    registry.set(name, { dedup: true, events: [], ...entry, name });
  },

  /** Unregister a component */
  unregister(name) {
    registry.delete(name);
  },

  /**
   * Manually trigger reinit for all registered components inside `root`.
   * Useful for server-side rendered pages that don't go through HTMX.
   * @param {Element|Document} root
   */
  reinit(root = document) {
    registry.forEach((entry) => _reinitEntry(entry, root, null));
  },

  /** Return all registered component names */
  getRegistered() {
    return Array.from(registry.keys());
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// HTMX event listeners (set up once)
// ─────────────────────────────────────────────────────────────────────────────

let _listenersAttached = false;

function _attachListeners() {
  if (_listenersAttached) return;
  _listenersAttached = true;

  /**
   * htmx:beforeSwap
   * Destroy existing instances inside the target being replaced.
   */
  document.addEventListener('htmx:beforeSwap', (e) => {
    const target = e.detail?.target;
    if (!target) return;

    registry.forEach((entry) => {
      if (typeof entry.destroy !== 'function') return;
      _findMatches(entry, target).forEach((el) => {
        try {
          if (el[INIT_KEY]) {
            entry.destroy(el, el[INIT_KEY]);
            delete el[INIT_KEY];
          }
        } catch (err) {
          console.warn(`[HTMXBridge] destroy "${entry.name}":`, err);
        }
      });
    });
  });

  /**
   * htmx:afterSwap
   * Re-initialize components that appear in the freshly swapped fragment.
   */
  document.addEventListener('htmx:afterSwap', (e) => {
    const target = e.detail?.target ?? document;
    _runReinit(target, e);
  });

  /**
   * htmx:afterSettle
   * Secondary pass after any CSS transitions settle (useful for animations).
   */
  document.addEventListener('htmx:afterSettle', (e) => {
    const target = e.detail?.target ?? document;
    registry.forEach((entry) => {
      if (!entry.events?.includes('htmx:afterSettle')) return;
      _reinitEntry(entry, target, e);
    });
  });
}

function _runReinit(root, originalEvent = null) {
  registry.forEach((entry) => {
    _reinitEntry(entry, root, originalEvent);
  });
}

function _reinitEntry(entry, root, event) {
  _findMatches(entry, root).forEach((el) => {
    // Skip already-initialized elements if dedup is on
    if (entry.dedup && el[INIT_KEY]) return;

    try {
      const instance = entry.reinit(el, root, event);
      if (entry.dedup) {
        el[INIT_KEY] = instance ?? true;
      }
    } catch (err) {
      console.warn(`[HTMXBridge] reinit "${entry.name}":`, err);
    }
  });
}

function _findMatches(entry, root) {
  const elements = [];
  for (const sel of entry.selectors) {
    // root itself may match
    try {
      if (root instanceof Element && root.matches(sel)) elements.push(root);
      root.querySelectorAll?.(sel).forEach((el) => elements.push(el));
    } catch (_) {
      // invalid selector — skip silently
    }
  }
  return [...new Set(elements)];
}

// ─────────────────────────────────────────────────────────────────────────────
// Auto-setup built-in registrations
// ─────────────────────────────────────────────────────────────────────────────

function _setupBuiltins() {
  // ── Sliders ────────────────────────────────────────────────────────────────
  HTMXBridge.register('sliders', {
    selectors: ['.owl-carousel', '.hero-slider', '[data-slider]', '.swiper'],
    dedup: true,

    destroy(el, instance) {
      // Owl Carousel
      if (window.jQuery) {
        try { window.jQuery(el).owlCarousel('destroy'); } catch (_) {}
      }
      // Swiper
      if (instance?.swiper?.destroy) {
        try { instance.swiper.destroy(true, true); } catch (_) {}
      }
    },

    reinit(el, root, event) {
      // Mark element so we can track it
      el.dataset.htmxSliderPending = 'true';

      // Defer to next tick so DOM is fully settled
      requestAnimationFrame(() => {
        delete el.dataset.htmxSliderPending;

        // Owl Carousel
        if (el.classList.contains('owl-carousel') && window.jQuery?.fn?.owlCarousel) {
          const config = _readOwlConfig(el);
          const instance = window.jQuery(el).owlCarousel(config);
          el.__owlInstance = instance;
          return instance;
        }

        // Swiper
        if ((el.classList.contains('swiper') || el.dataset.slider === 'swiper') &&
            (window.Swiper || typeof Swiper !== 'undefined')) {
          const SwiperClass = window.Swiper ?? Swiper;
          const config = _readSwiperConfig(el);
          const swiper = new SwiperClass(el, config);
          el.__swiperInstance = swiper;
          return { swiper };
        }

        // Fallback: dispatch event so app-level code can handle it
        el.dispatchEvent(new CustomEvent('slider:reinit', { bubbles: true, detail: { el, root } }));
      });
    },
  });

  // ── Notifications ──────────────────────────────────────────────────────────
  HTMXBridge.register('notifications', {
    // Matches the toast container AND inline notification lists
    selectors: [
      '#toast-container',
      '[data-notifications]',
      '.notifications-list',
      '.notification-item',
    ],
    dedup: false, // Always re-process on swap (new items may have arrived)

    reinit(el, root, event) {
      // Re-bind close buttons that appear in freshly swapped fragments
      el.querySelectorAll('[data-bs-dismiss="toast"], .btn-close').forEach((btn) => {
        if (btn.__notifBound) return;
        btn.__notifBound = true;
        btn.addEventListener('click', () => {
          const toast = btn.closest('.toast, .alert');
          if (toast) toast.remove();
        });
      });

      // Re-initialize Bootstrap toasts inside swapped fragment
      if (typeof bootstrap !== 'undefined') {
        el.querySelectorAll('.toast:not(.show)').forEach((toastEl) => {
          try {
            const bsToast = new bootstrap.Toast(toastEl);
            bsToast.show();
          } catch (_) {}
        });
      }

      // Re-fire notification:show events for items that carry data
      el.querySelectorAll('[data-notification-message]').forEach((item) => {
        if (item.__notifShown) return;
        item.__notifShown = true;
        const msg   = item.dataset.notificationMessage;
        const type  = item.dataset.notificationType || 'info';
        const title = item.dataset.notificationTitle || '';
        if (msg && window.showNotification) {
          window.showNotification(msg, { type, title });
        }
      });
    },
  });

  // ── Forms (Auth + Contact) ─────────────────────────────────────────────────
  HTMXBridge.register('forms', {
    selectors: [
      'form[data-auth-form]',
      'form[data-validate]',
      'form[data-htmx-form]',
      'form[hx-post]',
      'form[hx-get]',
    ],
    dedup: true,
    events: ['htmx:afterSettle'], // also run after CSS settle

    destroy(el, instance) {
      if (instance?.destroy) {
        try { instance.destroy(); } catch (_) {}
      }
    },

    reinit(el, root, event) {
      // Re-attach client-side validation
      el.querySelectorAll('[required], [data-validate-email], [data-validate-phone]')
        .forEach((field) => {
          if (field.__validationBound) return;
          field.__validationBound = true;

          field.addEventListener('blur', () => _validateField(field));
          field.addEventListener('input', () => {
            if (field.classList.contains('is-invalid')) _validateField(field);
          });
        });

      // Password strength meter
      el.querySelectorAll('input[type="password"]').forEach((pw) => {
        if (pw.__strengthBound) return;
        pw.__strengthBound = true;
        _attachPasswordStrength(pw);
      });

      // Notify any global form manager
      el.dispatchEvent(new CustomEvent('form:htmx-reinit', { bubbles: true, detail: { form: el } }));

      return { element: el };
    },
  });

  // ── Animations ─────────────────────────────────────────────────────────────
  HTMXBridge.register('animations', {
    selectors: ['[data-animate]', '[data-aos]', '.usecase-animate'],
    dedup: true,

    reinit(el) {
      // AOS
      if (typeof AOS !== 'undefined') {
        el.removeAttribute('data-aos-done');
        AOS.refreshHard?.() ?? AOS.refresh?.();
      }

      // Custom CSS animation
      el.classList.remove('is-animated');
      requestAnimationFrame(() => {
        const io = new IntersectionObserver((entries, obs) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-animated');
            obs.unobserve(entry.target);
          });
        }, { threshold: 0.15 });
        io.observe(el);
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _readOwlConfig(el) {
  const d = el.dataset;
  return {
    items:              parseInt(d.owlItems)            || 1,
    loop:               d.owlLoop !== 'false',
    nav:                d.owlNav  === 'true',
    dots:               d.owlDots !== 'false',
    autoplay:           d.owlAutoplay !== 'false',
    autoplayTimeout:    parseInt(d.owlAutoplayTimeout)  || 5000,
    smartSpeed:         parseInt(d.owlSmartSpeed)       || 800,
    animateOut:         d.owlAnimateOut                 || 'fadeOut',
    animateIn:          d.owlAnimateIn                  || 'fadeIn',
    touchDrag:          d.owlTouchDrag !== 'false',
    lazyLoad:           d.owlLazyLoad  !== 'false',
    responsiveClass:    true,
    responsive: {
      0:   { items: parseInt(d.owlXs) || 1 },
      576: { items: parseInt(d.owlSm) || 2 },
      768: { items: parseInt(d.owlMd) || 3 },
      992: { items: parseInt(d.owlLg) || 4 },
    },
  };
}

function _readSwiperConfig(el) {
  const d = el.dataset;
  return {
    loop:           d.swiperLoop  !== 'false',
    autoplay:       d.swiperAutoplay === 'true' ? { delay: parseInt(d.swiperDelay) || 5000 } : false,
    pagination:     d.swiperPagination === 'true' ? { el: '.swiper-pagination', clickable: true } : false,
    navigation:     d.swiperNav === 'true' ? { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' } : false,
    slidesPerView:  parseInt(d.swiperItems) || 1,
    spaceBetween:   parseInt(d.swiperGap)   || 0,
  };
}

function _validateField(field) {
  const value = field.value.trim();
  let valid   = true;
  let message = '';

  if (field.required && !value) {
    valid   = false;
    message = `${field.dataset.label || field.name || 'This field'} is required.`;
  } else if (field.dataset.validateEmail !== undefined) {
    valid   = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    message = valid ? '' : 'Enter a valid email address.';
  } else if (field.dataset.validatePhone !== undefined) {
    valid   = /^[\+]?[\d\s\-\(\)\.]{7,}$/.test(value);
    message = valid ? '' : 'Enter a valid phone number.';
  }

  field.classList.toggle('is-invalid', !valid);
  field.classList.toggle('is-valid',    valid && !!value);

  let feedback = field.nextElementSibling;
  if (!feedback || !feedback.classList.contains('invalid-feedback')) {
    feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    field.insertAdjacentElement('afterend', feedback);
  }
  feedback.textContent = message;
}

function _attachPasswordStrength(field) {
  let meter = field.parentElement?.querySelector('.pw-strength');
  if (!meter) {
    meter = document.createElement('div');
    meter.className = 'pw-strength mt-1';
    meter.innerHTML = `
      <div class="progress" style="height:4px">
        <div class="progress-bar" role="progressbar"></div>
      </div>
      <small class="pw-strength-label form-text"></small>`;
    field.insertAdjacentElement('afterend', meter);
  }

  const bar   = meter.querySelector('.progress-bar');
  const label = meter.querySelector('.pw-strength-label');

  field.addEventListener('input', () => {
    const s = _passwordScore(field.value);
    const colors = ['bg-danger', 'bg-danger', 'bg-warning', 'bg-info', 'bg-success'];
    const labels = ['Very weak', 'Weak', 'Fair', 'Good', 'Strong'];

    bar.style.width = `${(s / 4) * 100}%`;
    bar.className   = `progress-bar ${colors[s]}`;
    label.textContent = s > 0 ? labels[s] : '';
  });
}

function _passwordScore(pw) {
  if (!pw) return 0;
  let s = 0;
  if (pw.length >= 8)         s++;
  if (pw.length >= 12)        s++;
  if (/[A-Z]/.test(pw))       s++;
  if (/[0-9]/.test(pw))       s++;
  if (/[^A-Za-z0-9]/.test(pw)) s++;
  return Math.min(s, 4);
}

// ─────────────────────────────────────────────────────────────────────────────
// Boot
// ─────────────────────────────────────────────────────────────────────────────

_setupBuiltins();
_attachListeners();

export default HTMXBridge;
