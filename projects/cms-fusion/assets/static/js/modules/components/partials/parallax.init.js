/**
 * Parallax Effects Initialization
 */

export class Parallax {
  constructor() {
    this.initialized = false;
    this.init();
  }

  init() {
    if (this.initialized) return;

    this.initParallaxEffect();

    if (window.innerWidth > 1200) {
      this.initParallaxie();
    }

    this.initialized = true;
    // console.log('✅ Parallax effects initialized');
  }

  initParallaxEffect() {
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      const parallaxSections = document.querySelectorAll('.parallax-section');

      parallaxSections.forEach(parallax => {
        const rate = scrolled * -0.4;
        parallax.style.transform = `translate3d(0, ${rate}px, 0)`;
      });
    });
  }

  initParallaxie() {
    const $ = window.jQuery;
    if (!$ || !$.fn || !$.fn.parallaxie) return;

    const parallaxBg = $(".parallax");

    if (parallaxBg.length) {
      parallaxBg.each(function () {
        $(this).parallaxie({
          speed: 0.2
        });
      });
    }
  }
}

const parallax = new Parallax();
parallax.init();
