/**
 * @file navigations/plugins/layout-detector.js
 * Layout type detection and application
 */

export class LayoutDetectorPlugin {
  constructor(options = {}) {
    this.settings = {
      autoApplyClasses: true,
      bodyClassPrefix: 'layout-',
      layoutMap: {
        'forms': ['/forms', '/register', '/checkout', '/login'],
        'dashboard': ['/dashboard', '/app', '/admin'],
        'profile': ['/profile', '/account', '/settings'],
        'landing': ['/', '/home', '/index','/about', '-page']
      },
      ...options
    };
    
    this.navigation = null;
    this.currentLayout = null;
    this.handleLayoutChange = this.handleLayoutChange.bind(this);
  }
  
  install(navigation) {
    this.navigation = navigation;
    this.currentLayout = null;
    
    // Listen for layout changes
    navigation.on('navigation:layout-changed', this.handleLayoutChange);
    
    // Initial detection
    this.detectAndApplyLayout();
  }
  
  handleLayoutChange(event) {
    const { layout } = event.detail;
    this.applyLayout(layout);
  }
  
  detectAndApplyLayout() {
    const currentUrl = this.navigation.getCurrentPage()?.url || window.location.href;
    const layout = this.detectLayout(currentUrl);
    this.applyLayout(layout);
  }
  
  detectLayout(url) {
    const urlObj = new URL(url, window.location.origin);
    const path = urlObj.pathname;
    
    for (const [layout, patterns] of Object.entries(this.settings.layoutMap)) {
      if (patterns.some(pattern => path.includes(pattern))) {
        return layout;
      }
    }
    
    return 'default';
  }
  
  applyLayout(layout) {
    if (this.currentLayout === layout) return;
    
    const previousLayout = this.currentLayout;
    this.currentLayout = layout;
    
    // Remove previous layout classes
    if (previousLayout && this.settings.autoApplyClasses) {
      document.body.classList.remove(`${this.settings.bodyClassPrefix}${previousLayout}`);
    }
    
    // Apply new layout class
    if (this.settings.autoApplyClasses) {
      document.body.classList.add(`${this.settings.bodyClassPrefix}${layout}`);
    }
    
    // Dispatch event
    document.dispatchEvent(new CustomEvent('layout:changed', {
      detail: { layout, previousLayout }
    }));
  }
  
  getCurrentLayout() {
    return this.currentLayout;
  }
  
  uninstall() {
    if (this.currentLayout && this.settings.autoApplyClasses) {
      document.body.classList.remove(`${this.settings.bodyClassPrefix}${this.currentLayout}`);
    }
    
    if (this.navigation) {
      this.navigation.off('navigation:layout-changed', this.handleLayoutChange);
    }
    
    this.navigation = null;
    this.currentLayout = null;
  }
}

// Optional: Export a convenience function to maintain backward compatibility
export const createLayoutDetector = (options) => new LayoutDetectorPlugin(options);