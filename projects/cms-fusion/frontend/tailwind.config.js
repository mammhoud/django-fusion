/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'fu-primary': 'var(--fu-primary, #7c3aed)',
        'fu-secondary': 'var(--fu-secondary, #5b21b6)',
        'fu-accent': 'var(--fu-accent, #4c1d95)',
        'fu-bg': 'var(--fu-bg, #fafafa)',
        'fu-text': 'var(--fu-text, #18181b)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
