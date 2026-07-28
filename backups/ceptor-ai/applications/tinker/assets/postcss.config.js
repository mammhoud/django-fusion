/**
 * PostCSS Configuration for the customizer webpack build.
 *
 * Autoprefixer handles vendor prefixes.
 * RTL flipping is handled by the RtlCssPlugin in webpack.config.js
 * (it runs rtlcss on the full compiled CSS output as a separate step).
 */
module.exports = {
  plugins: [
    'autoprefixer',
  ],
};
