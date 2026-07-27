

/**
 * Background Images Class
 */
export class BackgroundImages {
  constructor() {
    // console.log('🎨 BackgroundImages instance created');
  }

  init() {
    const bgImages = document.querySelectorAll(".bg-image");
    
    if (bgImages.length === 0) return;
    
    bgImages.forEach(bgImage => {
      const bgData = bgImage.getAttribute("data-bg-src");
      if (bgData) {
        bgImage.style.backgroundImage = `url("${bgData}")`;
      }
    });
    
    console.log(`✅ ${bgImages.length} background images initialized`);
  }
}