/**
 * Progress Bars Initialization
 */

class Progress {
  constructor() {
    this.initialized = false;
    this.init();
  }

  init() {
    if (this.initialized) return;
    
    const progressElements = document.querySelectorAll('.animated-progress div');
    if (!progressElements.length) return;
    
    this.initWaypoints();
    
    this.initialized = true;
    console.log('✅ Progress bars initialized');
  }

  initWaypoints() {
    const $ = window.jQuery;
    if (!$ || !$.fn || !$.fn.appear) return;
    
    $(".animated-progress div").each(function() {
      $(this).appear(function() {
        $(this).css("width", $(this).attr("data-progress") + "%");
      }, { accX: 0, accY: -10 });
    });
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  new Progress();
});