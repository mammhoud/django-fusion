/**
 * Animated Counters Initialization
 */

class Counter {
  constructor() {
    this.initialized = false;
    this.init();
  }

  init() {
    if (this.initialized) return;
    
    const counterElements = document.querySelectorAll('.counter');
    if (!counterElements.length) return;
    
    this.initWaypoints();
    
    this.initialized = true;
    console.log('✅ Animated counters initialized');
  }

  async loadWaypoints() {
    if (typeof Waypoint === 'undefined') {
      try {
        const WaypointModule = await import('waypoints/lib/noframework.waypoints.min.js');
        window.Waypoint = WaypointModule.default || WaypointModule;
      } catch (error) {
        console.warn('Waypoints not available:', error);
      }
    }
  }

  initWaypoints() {
    const $ = window.jQuery;
    if (!$ || !$.fn || !$.fn.appear) return;
    
    $(".counter").appear(function() {
      $(this).each(function() {
        $(this).prop("Counter", 0).animate({
          Counter: $(this).text()
        }, {
          duration: 2500,
          easing: "swing",
          step: function(now) {
            $(this).text(Math.ceil(now));
          }
        });
      });
    }, { accX: 0, accY: -10 });
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  new Counter();
});