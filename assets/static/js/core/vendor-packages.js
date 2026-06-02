/**
 * Theme Vendor Packages Loader
 * Dynamically loads vendor libraries from npm packages installed in assets/package.json
 * Each vendor is loaded on-demand and exposed to window object when needed
 */

const loadedVendors = new Map();

function expose(name, value) {
  if (value === undefined || value === null) return;
  window[name] = value;
}

function moduleValue(module) {
  return module?.default || module;
}

const vendorLoaders = [
  ['alpinejs', () => import('alpinejs').then((module) => expose('Alpine', moduleValue(module)))],
  ['aos', () => import('aos').then((module) => expose('AOS', moduleValue(module)))],
  ['apexcharts', () => import('apexcharts').then((module) => expose('ApexCharts', moduleValue(module)))],
  ['bootstrap', () => import('bootstrap/dist/js/bootstrap.bundle.min.js').then((module) => expose('bootstrap', moduleValue(module)))],
  ['bootstrap-icons', () => import(/* webpackIgnore: true */ 'bootstrap-icons')],
  ['bootstrap-select', () => import(/* webpackIgnore: true */ 'bootstrap-select').then((module) => expose('$.fn.selectpicker', moduleValue(module)))],
  ['chart.js', () => import('chart.js').then((module) => expose('Chart', moduleValue(module)))],
  ['choices.js', () => import('choices.js').then((module) => expose('Choices', moduleValue(module)))],
  ['cleave.js', () => import('cleave.js').then((module) => expose('Cleave', moduleValue(module)))],
  ['countup.js', () => import('countup.js').then((module) => expose('CountUp', moduleValue(module)))],
  ['dragula', () => import('dragula').then((module) => expose('dragula', moduleValue(module)))],
  ['dropzone', () => import('dropzone').then((module) => expose('Dropzone', moduleValue(module)))],
  ['dual-listbox', () => import(/* webpackIgnore: true */ 'dual-listbox')],
  ['echarts', () => import('echarts').then((module) => expose('echarts', moduleValue(module)))],
  ['feather-icons', () => import('feather-icons').then((module) => expose('feather', moduleValue(module)))],
  ['flyonui', () => import(/* webpackIgnore: true */ 'flyonui')],
  ['frostui', () => import(/* webpackIgnore: true */ 'frostui')],
  ['glightbox', () => import('glightbox').then((module) => expose('GLightbox', moduleValue(module)))],
  ['gmaps', () => import(/* webpackIgnore: true */ 'gmaps').then((module) => expose('GMaps', moduleValue(module)))],
  ['gridjs', () => import('gridjs').then((module) => expose('Grid', moduleValue(module)))],
  ['htmx.org', () => import('htmx.org/dist/htmx.min.js').then((module) => expose('htmx', moduleValue(module)))],
  ['imagesloaded', () => import('imagesloaded').then((module) => expose('imagesLoaded', moduleValue(module)))],
  ['isotope-layout', () => import(/* webpackIgnore: true */ 'isotope-layout').then((module) => expose('Isotope', moduleValue(module)))],
  ['jquery', () => import('jquery').then((module) => expose('$', moduleValue(module)))],
  ['jquery-countdown', () => import('jquery-countdown/dist/jquery.countdown.min.js')],
  ['jquery-parallax', () => import(/* webpackIgnore: true */ 'jquery-parallax')],
  ['jquery-ui', () => import('jquery-ui/dist/jquery-ui.min.js')],
  ['jquery.appear', () => import(/* webpackIgnore: true */ 'jquery.appear')],
  ['jquery.easing', () => import(/* webpackIgnore: true */ 'jquery.easing')],
  ['easy-pie-chart', () => import(/* webpackIgnore: true */ 'easy-pie-chart').then((module) => expose('easyPieChart', moduleValue(module)))],
  ['jquery.magnify', () => import(/* webpackIgnore: true */ 'jquery.magnify')],
  ['jquery.marquee', () => import(/* webpackIgnore: true */ 'jquery.marquee')],
  ['jsvectormap', () => import('jsvectormap').then((module) => expose('jsVectorMap', moduleValue(module)))],
  ['leaflet', () => import('leaflet').then((module) => expose('L', moduleValue(module)))],
  ['list.js', () => import('list.js').then((module) => expose('List', moduleValue(module)))],
  ['magnific-popup', () => import('magnific-popup/dist/jquery.magnific-popup.min.js')],
  ['masonry-layout', () => import('masonry-layout').then((module) => expose('Masonry', moduleValue(module)))],
  ['mixitup', () => import('mixitup').then((module) => expose('mixitup', moduleValue(module)))],
  ['modernizr', () => import(/* webpackIgnore: true */ 'modernizr').then((module) => expose('Modernizr', moduleValue(module)))],
  ['nouislider', () => import('nouislider').then((module) => expose('noUiSlider', moduleValue(module)))],
  ['odometer', () => import(/* webpackIgnore: true */ 'odometer').then((module) => expose('Odometer', moduleValue(module)))],
  ['owl.carousel', () => import('owl.carousel/dist/owl.carousel.min.js')],
  ['parallax-js', () => import(/* webpackIgnore: true */ 'parallax-js').then((module) => expose('Parallax', moduleValue(module)))],
  ['plyr', () => import('plyr').then((module) => expose('Plyr', moduleValue(module)))],
  ['preline', () => import(/* webpackIgnore: true */ 'preline')],
  ['prismjs', () => import('prismjs').then((module) => expose('Prism', moduleValue(module)))],
  ['quill', () => import('quill').then((module) => expose('Quill', moduleValue(module)))],
  ['remixicon', () => import(/* webpackIgnore: true */ 'remixicon')],
  ['sal.js', () => import(/* webpackIgnore: true */ 'sal.js').then((module) => expose('sal', moduleValue(module)))],
  ['scrollcue', () => import('scrollcue').then((module) => expose('scrollCue', moduleValue(module)))],
  ['select2', () => import('select2/dist/js/select2.full.min.js')],
  ['shepherd.js', () => import('shepherd.js').then((module) => expose('Shepherd', moduleValue(module)))],
  ['simplebar', () => import('simplebar').then((module) => expose('SimpleBar', moduleValue(module)))],
  ['slick-carousel', () => import('slick-carousel/slick/slick.js')],
  ['sortablejs', () => import('sortablejs').then((module) => expose('Sortable', moduleValue(module)))],
  ['star-rating.js', () => import(/* webpackIgnore: true */ 'star-rating.js')],
  ['sweetalert2', () => import('sweetalert2').then((module) => expose('Swal', moduleValue(module)))],
  ['swiper', () => import('swiper/bundle').then((module) => expose('Swiper', moduleValue(module)))],
  ['theme-change', () => import(/* webpackIgnore: true */ 'theme-change')],
  ['unpoly', () => import('unpoly').then((module) => expose('up', moduleValue(module)))],
  ['vanilla-tilt', () => import('vanilla-tilt').then((module) => expose('VanillaTilt', moduleValue(module)))],
  ['vue', () => import('vue').then((module) => expose('Vue', moduleValue(module)))],
  ['waypoints', () => Promise.all([
    import('waypoints/lib/noframework.waypoints.min.js').then((module) => expose('Waypoint', moduleValue(module))),
    import('waypoints/lib/jquery.waypoints.min.js'),
  ])],
  ['wowjs', () => import('wowjs/dist/wow.min.js').then((module) => expose('WOW', moduleValue(module).WOW || moduleValue(module)))],
  ['yaireo/tagify', () => import('@yaireo/tagify').then((module) => expose('Tagify', moduleValue(module)))],
];

/**
 * Load theme vendor packages
 * @param {Object} options - Configuration options
 * @param {boolean} options.debug - Enable debug logging for failed packages
 * @returns {Promise<Map>} Map of loaded vendors
 */
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

/**
 * Load a specific vendor package
 * @param {string} name - Vendor package name
 * @returns {Promise<any>} Loaded module
 */
export async function loadThemeVendor(name) {
  const loader = vendorLoaders.find(([n]) => n === name);
  if (!loader) {
    throw new Error(`Unknown vendor: ${name}`);
  }

  if (loadedVendors.has(name)) {
    return loadedVendors.get(name);
  }

  const result = await loader[1]();
  loadedVendors.set(name, result || true);
  return result;
}

/**
 * Check if a vendor is loaded
 * @param {string} name - Vendor package name
 * @returns {boolean} True if vendor is loaded
 */
export function isThemeVendorLoaded(name) {
  return loadedVendors.has(name);
}

/**
 * Get all loaded vendors
 * @returns {Map} Map of loaded vendors
 */
export function getLoadedThemeVendors() {
  return new Map(loadedVendors);
}
