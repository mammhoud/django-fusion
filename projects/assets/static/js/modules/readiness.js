/**
 * Module Readiness Checker
 * Ensures modules are loaded before page initialization
 */

"use strict";

export class ModuleReadiness {
  constructor() {
    this.requiredModules = new Set();
    this.loadedModules = new Set();
  }

  require(moduleName) {
    this.requiredModules.add(moduleName);
    return this;
  }

  isReady(moduleName) {
    return this.loadedModules.has(moduleName);
  }

  async waitFor(moduleName, timeout = 5000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      if (this.isReady(moduleName)) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    throw new Error(`Module ${moduleName} not ready after ${timeout}ms`);
  }

  async waitForAll(timeout = 5000) {
    const startTime = Date.now();
    const modules = Array.from(this.requiredModules);
    
    while (Date.now() - startTime < timeout) {
      const ready = modules.every(module => this.isReady(module));
      if (ready) return true;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    const missing = modules.filter(module => !this.isReady(module));
    throw new Error(`Modules not ready after ${timeout}ms: ${missing.join(', ')}`);
  }

  markReady(moduleName) {
    this.loadedModules.add(moduleName);
    console.log(`✅ Module ready: ${moduleName}`);
  }
}

// Global instance
window.moduleReadiness = new ModuleReadiness();