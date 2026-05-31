/** @type {import('postcss-load-config').Config} */
module.exports = (ctx) => ({
  plugins: {
    'postcss-import': {},
    '@tailwindcss/postcss': {},  // Tailwind v4 — handles prefix(tw) from CSS
    'autoprefixer': {},
    'postcss-preset-env': {},
    ...(ctx.env === 'production' ? {
      '@fullhuman/postcss-purgecss': {
        content: [
          './apps/**/*.{html,py}',
          './assets/templates/**/*.html',
          './core/**/*.html',
        ],
        defaultExtractor: content => {
          const broadMatches = content.match(/[^<>"'`\s]*[^<>"'`\s:]/g) || [];
          const innerMatches = content.match(/[^<>"'`\s.(){}[\]#=%]*[^<>"'`\s.(){}[\]#=%:]/g) || [];
          return broadMatches.concat(innerMatches);
        },
        safelist: {
          standard: [
            /^tw:/,      // Tailwind tw: prefix
            /^hs-/,      // Preline hs- prefix
            /^bg-/,
            /^text-/,
            /^border-/,
            /^hover:/,
            /^focus:/,
            /^active:/,
            /^disabled:/,
          ],
          deep: [/^vue/, /^v-/, /^router-/],
          greedy: [
            /^tw:/,      // Tailwind tw: prefix
            /^hs-/,      // Preline hs- prefix
            /^form-/,
            /^btn-/,
            /^modal/,
            /^tooltip/,
            /^popover/,
            /^alert/,
            /^nav-/,
            /^dropdown/,
            /^carousel/,
            /^collaps/,
            /^is-/,
            /^has-/,
          ],
        },
        variables: true,
        fontFace: true,
        keyframes: true,
      }
    } : {})
  }
});