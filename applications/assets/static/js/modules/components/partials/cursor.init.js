/**
 * Custom Cursor Initialization
 */

export class Cursor {
  constructor() {
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    
    const customCursor = document.getElementById("cursor");
    if (!customCursor) return;
    
    const cursor = document.getElementById("cursor");
    
    document.addEventListener('mousemove', (e) => {
      cursor.style.left = e.pageX + 'px';
      cursor.style.top = e.pageY + 'px';
    });

    const mouseElms = document.querySelectorAll("a, button, input, textarea, .accordion-title, .filter li");
    
    mouseElms.forEach((mouseElm) => {
      mouseElm.addEventListener("mouseenter", () => {
        cursor.classList.add("scale-cursor");
      });
      mouseElm.addEventListener("mouseleave", () => {
        cursor.classList.remove("scale-cursor");
      });
    });
    
    this.initialized = true;
    console.log('✅ Custom cursor initialized');
  }
}

export default Cursor;