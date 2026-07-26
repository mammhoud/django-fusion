/**
 * Fullscreen Menu Initialization
 */

export class Fullscreen {
  constructor() {
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    
    const fm = document.querySelector(".fullscreen-menu");
    if (!fm) return;

    const fmToggle = document.querySelector(".fm-toggle");
    const fmClose = document.querySelector(".fm-close");

    if (fmToggle) {
      fmToggle.addEventListener("click", () => {
        fm.classList.toggle("fm-show");
      });
    }

    if (fmClose) {
      fmClose.addEventListener("click", () => {
        fm.classList.remove("fm-show");
        if (fmToggle) fmToggle.classList.remove("fm-toggle-hide");
      });
    }
    
    this.initialized = true;
    console.log('✅ Fullscreen menu initialized');
  }
}

// Backward compatibility alias
export const FullscreenMenu = Fullscreen;
export default Fullscreen;
