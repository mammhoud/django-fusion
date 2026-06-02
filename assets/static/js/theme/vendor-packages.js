const loadedVendors = new Map();

function expose(name, value) {
  if (value === undefined || value === null) return;
  window[name] = value;
}

function moduleValue(module) {
  return module?.default || module;
}

const vendorLoaders = [
  ['bootstrap', () => import('bootstrap/dist/js/bootstrap.bundle.min.js').then((module) => expose('bootstrap', moduleValue(module)))],
  ['bootstrap-select', () => import('./vendor/bootstrap-select.min.js')],
  ['imagesloaded', () => import('imagesloaded').then((module) => expose('imagesLoaded', moduleValue(module)))],
  ['isotope-layout', () => import('./vendor/isotop.js').then((module) => expose('Isotope', moduleValue(module)))],
  ['jquery.appear', () => import('./vendor/jquery-appear.js')],
  ['jquery-countdown', () => import('jquery-countdown/dist/jquery.countdown.min.js')],
  ['jquery-one-page-nav', () => import('./vendor/jquery-one-page-nav.js')],
  ['jquery-ui', () => import('jquery-ui/dist/jquery-ui.min.js')],
  ['jquery.easy-pie-chart', () => import('./vendor/easypie.js')],
  ['jquery.magnify', () => import('./vendor/magnify.min.js')],
  ['magnific-popup', () => import('magnific-popup/dist/jquery.magnific-popup.min.js')],
  ['masonry-layout', () => import('masonry-layout').then((module) => expose('Masonry', moduleValue(module)))],
  ['modernizr', () => import('./vendor/modernizr.min.js')],
  ['odometer', () => import('./vendor/odometer.js').then((module) => expose('Odometer', moduleValue(module)))],
  ['owl.carousel', () => import('owl.carousel/dist/owl.carousel.min.js')],
  ['parallax-js', () => import('./vendor/paralax.min.js').then((module) => expose('Parallax', moduleValue(module)))],
  ['plyr', () => import('plyr').then((module) => expose('Plyr', moduleValue(module)))],
  ['sal.js', () => import('./vendor/sal.js').then((module) => expose('sal', moduleValue(module)))],
  ['scrollcue', () => import('scrollcue').then((module) => expose('scrollCue', moduleValue(module)))],
  ['slick-carousel', () => import('slick-carousel/slick/slick.js')],
  ['swiper', () => import('swiper/bundle').then((module) => expose('Swiper', moduleValue(module)))],
  ['waypoints', () => Promise.all([
    import('waypoints/lib/noframework.waypoints.min.js').then((module) => expose('Waypoint', moduleValue(module))),
    import('waypoints/lib/jquery.waypoints.min.js'),
  ])],
  ['wowjs', () => import('wowjs/dist/wow.min.js').then((module) => expose('WOW', moduleValue(module).WOW || moduleValue(module)))],
  ['aos', () => import('aos').then((module) => expose('AOS', moduleValue(module)))],
  ['glightbox', () => import('glightbox').then((module) => expose('GLightbox', moduleValue(module)))],
  ['mixitup', () => import('mixitup').then((module) => expose('mixitup', moduleValue(module)))],
];

export async function loadThemeVendorPackages({ debug = false } = {}) {
  if (loadedVendors.size === vendorLoaders.length) {
    return loadedVendors;
  }

  const results = await Promise.allSettled(
    vendorLoaders.map(async ([name, loader]) => {
      if (loadedVendors.has(name)) return loadedVendors.get(name);
      const result = await loader();
      loadedVendors.set(name, result || true);
      return result;
    }),
  );

  if (debug) {
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        console.warn(`[theme-vendors] ${vendorLoaders[index][0]} failed`, result.reason);
      }
    });
  }

  return loadedVendors;
}
