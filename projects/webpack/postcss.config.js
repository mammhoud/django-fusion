const path = require("path");

/** @type {import('postcss-load-config').Config} */
module.exports = (ctx) => ({
  plugins: {
    'postcss-import': {},
    // '@tailwindcss/nesting': 'postcss-nesting',
    // 'tailwindcss': {},
    'autoprefixer': {},
    'postcss-preset-env': {},
    ...(ctx.env === 'production' ? {
      '@fullhuman/postcss-purgecss': {
        content: [
          './assets/static/**/*.{html,js,vue}',
          './templates/**/*.html',
          './**/*.py',
        ],
        defaultExtractor: content => {
          const broadMatches = content.match(/[^<>"'`\s]*[^<>"'`\s:]/g) || [];
          const innerMatches = content.match(/[^<>"'`\s.(){}[\]#=%]*[^<>"'`\s.(){}[\]#=%:]/g) || [];
          return broadMatches.concat(innerMatches);
        },
        safelist: {
          standard: [
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