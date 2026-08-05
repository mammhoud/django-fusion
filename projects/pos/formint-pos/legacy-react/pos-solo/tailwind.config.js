/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      'xs': '480px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
    extend: {
      colors: {
        // ═══ POS Standardized Color Palette ═══
        // All colors driven by CSS custom properties so theme
        // switching and dark mode work without rebuilds.
        pos: {
          // Brand
          primary: 'var(--pos-primary, #2563eb)',
          'primary-dark': 'var(--pos-primary-dark, #1d4ed8)',
          'primary-light': 'var(--pos-primary-light, #60a5fa)',
          'primary-bg': 'var(--pos-primary-bg, #eff6ff)',
          'on-primary': 'var(--pos-on-primary, #ffffff)',
          'on-primary-bg': 'var(--pos-on-primary-bg, #1e3a5f)',

          // Success
          success: 'var(--pos-success, #059669)',
          'success-bg': 'var(--pos-success-bg, #ecfdf5)',
          'on-success': 'var(--pos-on-success, #ffffff)',
          'on-success-bg': 'var(--pos-on-success-bg, #064e3b)',

          // Warning
          warning: 'var(--pos-warning, #f59e0b)',
          'warning-bg': 'var(--pos-warning-bg, #fffbeb)',
          'on-warning': 'var(--pos-on-warning, #1a1000)',
          'on-warning-bg': 'var(--pos-on-warning-bg, #78350f)',

          // Danger
          danger: 'var(--pos-danger, #ef4444)',
          'danger-bg': 'var(--pos-danger-bg, #fef2f2)',
          'on-danger': 'var(--pos-on-danger, #ffffff)',
          'on-danger-bg': 'var(--pos-on-danger-bg, #991b1b)',

          // Info
          info: 'var(--pos-info, #0891b2)',
          'info-bg': 'var(--pos-info-bg, #ecfeff)',
          'on-info': 'var(--pos-on-info, #ffffff)',
          'on-info-bg': 'var(--pos-on-info-bg, #155e75)',

          // Surfaces
          surface: 'var(--pos-surface, #f8fafc)',
          'surface-alt': 'var(--pos-surface-alt, #f1f5f9)',
          'surface-raised': 'var(--pos-surface-raised, #ffffff)',

          // Backgrounds
          bg: 'var(--pos-bg, #f1f5f9)',
          'bg-alt': 'var(--pos-bg-alt, #e2e8f0)',

          // Borders
          border: 'var(--pos-border, #e2e8f0)',
          'border-light': 'var(--pos-border-light, #f1f5f9)',

          // Text
          text: 'var(--pos-text, #1e293b)',
          'text-secondary': 'var(--pos-text-secondary, #64748b)',
          'text-muted': 'var(--pos-text-muted, #94a3b8)',
          'text-inverse': 'var(--pos-text-inverse, #f8fafc)',
        },

        // Legacy theme-driven colors — kept for backward compat
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
      },

      // Responsive spacing scale
      spacing: {
        '2xs': '2px',
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
        'sidebar': '240px',
        'sidebar-collapsed': '64px',
        'topbar': '56px',
        'topbar-mobile': '48px',
      },

      // Responsive font sizes
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1.25' }],
        'xs': ['0.75rem', { lineHeight: '1.25' }],
        'sm': ['0.875rem', { lineHeight: '1.4' }],
        'base': ['0.9375rem', { lineHeight: '1.5' }],
        'md': ['1.0625rem', { lineHeight: '1.5' }],
        'lg': ['1.25rem', { lineHeight: '1.5' }],
        'xl': ['1.5rem', { lineHeight: '1.4' }],
        '2xl': ['1.875rem', { lineHeight: '1.3' }],
        '3xl': ['2.25rem', { lineHeight: '1.2' }],
      },

      // Responsive border radius
      borderRadius: {
        'xs': '3px',
        'sm': '6px',
        'DEFAULT': '8px',
        'md': '10px',
        'lg': '12px',
        'xl': '16px',
      },

      // Animation durations
      transitionDuration: {
        'fast': '120ms',
        'DEFAULT': '200ms',
        'slow': '300ms',
      },

      // Shadows
      boxShadow: {
        'pos-sm': 'var(--pos-shadow-sm)',
        'pos-md': 'var(--pos-shadow-md)',
        'pos-lg': 'var(--pos-shadow-lg)',
        'pos-xl': 'var(--pos-shadow-xl)',
      },
    },
  },
  plugins: [],
}
