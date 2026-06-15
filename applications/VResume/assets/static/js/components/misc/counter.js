/**
 * Unified Counter Component
 * Handles both general counters and skills counters with SVG progress
 * Supports HTMX fragment re-initialization
 */

export class CounterComponent {
  constructor(config = {}) {
    this.config = {
      counterSelector: '.counter',
      skillSelector: '.count',
      svgSelector: '.progress',
      duration: 2500,
      easing: 'swing',
      ...config
    };
    this.initialized = false;
    this.animatingElements = new Set();
  }

  /**
   * Initialize all counters
   */
  init() {
    if (this.initialized) return;
    this.initGeneralCounters();
    this.initSkillCounters();
    this.initialized = true;
    console.log('✅ Counters initialized');
    return true;
  }

  /**
   * Reinitialize counters (called on HTMX fragment loads)
   */
  reinit() {
    // Reset animation tracking
    this.animatingElements.clear();
    this.initGeneralCounters();
    this.initSkillCounters();
    console.log('🔄 Counters reinitialized (HTMX)');
  }

  /**
   * Initialize general counters with jQuery animate
   */
  initGeneralCounters() {
    const $ = window.jQuery;
    if (!$ || !$.fn || !$.fn.appear) return;

    const elements = document.querySelectorAll(this.config.counterSelector);
    if (!elements.length) return;

    $(this.config.counterSelector).appear(
      function () {
        const $el = $(this);
        if (this.animatingElements?.has(this)) return; // Skip if already animating

        $el.prop('Counter', 0).animate(
          { Counter: parseInt($el.text()) },
          {
            duration: this.config.duration,
            easing: this.config.easing,
            step: function (now) {
              $el.text(Math.ceil(now));
            },
            complete: () => {
              this.animatingElements?.delete(this);
            }
          }
        );
        this.animatingElements?.add(this);
      }.bind(this),
      { accX: 0, accY: -10 }
    );
  }

  /**
   * Initialize skill counters with SVG progress
   */
  initSkillCounters() {
    const $ = window.jQuery;
    if (!$) return;

    const elements = document.querySelectorAll(this.config.skillSelector);
    if (!elements.length) return;

    elements.forEach(el => {
      if (this.animatingElements.has(el)) return; // Skip if already animating

      const $el = $(el);
      const target = parseInt($el.data('skill-level') || $el.text());

      if (isNaN(target)) return;

      // Animate counter text
      $({ Counter: 0 }).animate(
        { Counter: target },
        {
          duration: 1500,
          easing: 'linear',
          step: function () {
            $el.text(Math.ceil(this.Counter));
          },
          complete: () => {
            this.animatingElements.delete(el);
          }
        }
      );

      // Animate SVG progress offset
      const $svg = $el.siblings('svg').find(this.config.svgSelector);
      if ($svg.length) {
        const circumference = 314.16;
        const offset = circumference - (target / 100) * circumference;
        $({ offset: circumference }).animate(
          { offset: offset },
          {
            duration: 1500,
            easing: 'linear',
            step: function () {
              $svg.css('--dash-offset', `${Math.ceil(this.offset)}px`);
            }
          }
        );
      }

      this.animatingElements.add(el);
    });
  }

  /**
   * Destroy and cleanup
   */
  destroy() {
    this.animatingElements.clear();
    this.initialized = false;
  }
}

// Auto-initialize on DOM ready
function initializeCounters() {
  const counter = new CounterComponent();
  counter.init();

  // Re-initialize on HTMX fragment loads
  if (window.htmx) {
    document.body.addEventListener('htmx:load', () => {
      counter.reinit();
    });
  }
}

document.addEventListener('DOMContentLoaded', initializeCounters);

export default CounterComponent;
