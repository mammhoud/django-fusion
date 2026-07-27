/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        '3xl': '1600px',
        '4xl': '1920px',
      },
      colors: {
        // Theme-driven colors — override via CSS custom properties
        theme: {
          primary: 'var(--theme-primary, #6366f1)',
          'primary-hover': 'var(--theme-primary-hover, #4f46e5)',
          'primary-light': 'var(--theme-primary-light, #e0e7ff)',
          secondary: 'var(--theme-secondary, #8b5cf6)',
          accent: 'var(--theme-accent, #06b6d4)',
          'accent-light': 'var(--theme-accent-light, #cffafe)',
          surface: 'var(--theme-surface, #ffffff)',
          'surface-elevated': 'var(--theme-surface-elevated, #f8fafc)',
          text: 'var(--theme-text, #0f172a)',
          'text-muted': 'var(--theme-text-muted, #64748b)',
          border: 'var(--theme-border, #e2e8f0)',
          success: 'var(--theme-success, #10b981)',
          warning: 'var(--theme-warning, #f59e0b)',
          danger: 'var(--theme-danger, #ef4444)',
        },
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

