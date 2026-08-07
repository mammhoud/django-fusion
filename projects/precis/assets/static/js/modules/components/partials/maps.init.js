/**
 * Google Maps Initialization
 */

class Maps {
  constructor() {
    this.initialized = false;
    this.init();
  }

  async init() {
    if (this.initialized) return;
    
    await this.loadGMaps();
    this.initGoogleMaps();
    
    this.initialized = true;
    console.log('✅ Google Maps initialized');
  }

  async loadGMaps() {
    if (typeof GMaps === 'undefined') {
      try {
        const GMapsModule = await import('gmaps');
        window.GMaps = GMapsModule.default || GMapsModule;
      } catch (error) {
        console.warn('GMaps not available:', error);
      }
    }
  }

  initGoogleMaps() {
    const mapCanvas = document.querySelectorAll(".gmap");
    if (!mapCanvas.length || !window.GMaps) return;
    
    for (let i = 0; i < mapCanvas.length; i++) {
      const m = mapCanvas[i];
      const initLatitude = m.dataset.latitude;
      const initLongitude = m.dataset.longitude;
      const divId = "#" + m.id;

      const map = new window.GMaps({
        el: divId,
        lat: initLatitude,
        lng: initLongitude,
        zoom: 16,
        scrollwheel: false
      });

      map.addMarker({
        lat: initLatitude,
        lng: initLongitude
      });
    }
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  new Maps();
});