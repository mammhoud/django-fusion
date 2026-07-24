/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        ctc: {
          primary: '#00a1b3',
          'primary-dark': '#007a88',
          'primary-light': '#1a7fd4',
          secondary: '#008080',
          accent: '#6C63FF',
          'accent-alt': '#FF6B8B',
        },
      },
      fontFamily: {
        heading: ['Urbanist', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
