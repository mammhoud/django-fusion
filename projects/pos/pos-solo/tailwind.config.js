/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Light theme colors
        light: {
          bg: {
            primary: '#ffffff',
            secondary: '#f8fafc',
            tertiary: '#f1f5f9',
          },
          text: {
            primary: '#0f172a',
            secondary: '#475569',
            tertiary: '#64748b',
          },
          border: '#e2e8f0',
        },
        // Dark theme colors
        dark: {
          bg: {
            primary: '#0f172a',
            secondary: '#1e293b',
            tertiary: '#334155',
          },
          text: {
            primary: '#f8fafc',
            secondary: '#cbd5e1',
            tertiary: '#94a3b8',
          },
          border: '#334155',
        },
      },
    },
  },
  plugins: [],
}

