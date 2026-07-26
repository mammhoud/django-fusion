/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'fu-primary': 'var(--fu-primary, #00a1b3)',
        'fu-secondary': 'var(--fu-secondary, #008080)',
        'fu-accent': 'var(--fu-accent, #005f73)',
        'fu-bg': 'var(--fu-bg, #f8fafc)',
        'fu-text': 'var(--fu-text, #1e293b)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fusion-pulse': 'fusion-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'fusion-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [],
};
