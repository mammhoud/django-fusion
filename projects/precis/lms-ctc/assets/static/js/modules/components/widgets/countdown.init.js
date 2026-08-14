/**
 * Countdown Timers Initialization
 */

class Countdown {
  constructor() {
    this.initialized = false;
    this.init();
  }

  init() {
    if (this.initialized) return;
    
    const countdownElements = document.querySelectorAll('.countdown');
    if (!countdownElements.length) return;
    
    this.initCountdownTimers();
    
    this.initialized = true;
    console.log('✅ Countdown timers initialized');
  }

  initCountdownTimers() {
    const $ = window.jQuery;
    if (!$ || !$.fn || !$.fn.countdown) return;
    
    $(".countdown").each(function() {
      const finalDate = $(this).attr('data-countdown');
      
      $(this).countdown(finalDate, function(event) {
        $(this).html(event.strftime('%D days %H:%M:%S'));
      });
    });
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  new Countdown();
});