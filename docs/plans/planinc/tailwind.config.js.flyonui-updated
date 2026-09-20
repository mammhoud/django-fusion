/** @type {import('tailwindcss').Config} */
const { heroui } = require('@heroui/react');
const flyonui = require('flyonui/plugin');
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../node_modules/@tremor/**/*.{js,ts,jsx,tsx}',
    '../node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}',
    '../node_modules/flyonui/dist/**/*.{js,ts,jsx,tsx}',
  ],
  plugins: [
    flyonui,
  ],
  darkMode: 'class',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'var(--border)',
        ignore: 'var(--ignore)',
        desc: 'var(--desc)',
        hover: 'var(--hover)',
        input: 'var(--input)',
        tag: 'var(--tag)',
        ring: 'var(--ring)',
        background: 'var(--background)',
        secondbackground: 'var(--secondbackground)',
        foreground: 'var(--foreground)',
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)',
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)',
        },
        destructive: {
          DEFAULT: 'var(--destructive)',
          foreground: 'var(--destructive-foreground)',
        },
        success: {
          DEFAULT: 'var(--success)',
          foreground: 'var(--success-foreground)',
          soft: 'var(--success-soft)',
          'soft-foreground': 'var(--success-soft-foreground)',
        },
        warning: {
          DEFAULT: 'var(--warning)',
          foreground: 'var(--warning-foreground)',
          soft: 'var(--warning-soft)',
          'soft-foreground': 'var(--warning-soft-foreground)',
        },
        info: {
          DEFAULT: 'var(--info)',
          foreground: 'var(--info-foreground)',
          soft: 'var(--info-soft)',
          'soft-foreground': 'var(--info-soft-foreground)',
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)',
        },
        popover: {
          DEFAULT: 'var(--popover)',
          foreground: 'var(--popover-foreground)',
        },
        card: {
          DEFAULT: 'var(--card)',
          foreground: 'var(--card-foreground)',
        },
        header: 'var(--header)'
      },
      spacing: {
        '90': '90px',
      },
      // Radius comes from the token contract (tokens.css tier 4).
      // The derived values are identical to the previous calc() expressions,
      // so this is a single-source change, not a visual one.
      // All radii scale responsively via html[data-tier="..."] in tokens.css.
      borderRadius: {
        lg: 'var(--pi-radius-lg)',
        md: 'var(--pi-radius-md)',
        sm: 'var(--pi-radius-sm)',
        xl: 'var(--pi-radius-xl)',
        '2xl': 'var(--pi-radius-2xl)',
      },
      // Responsive border-radius utility variants
      // These allow `radius-sm`, `radius-md`, `radius-lg` etc.
      // to respond to the tier attribute without media queries.
      // HeroUI layout radii are also responsive via the same tokens.
      // fontFamily: {
      //   sans: ['Inter', 'var(--font-sans)', ...fontFamily.sans],
      // },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  safelist: [
    {
      pattern:
        /^(bg-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|background|primary)-(?:50|100|200|300|400|500|600|700|800|900|950))$/,
      variants: ['hover', 'ui-selected'],
    },
    {
      pattern: /^(bg-(?:background|primary)\/[0-9]+)$/,
      variants: ['hover'],
    },
    {
      pattern:
        /^(text-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950))$/,
      variants: ['hover', 'ui-selected'],
    },
    {
      pattern:
        /^(border-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950))$/,
      variants: ['hover', 'ui-selected'],
    },
    {
      pattern:
        /^(ring-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950))$/,
    },
    {
      pattern:
        /^(stroke-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950))$/,
    },
    {
      pattern:
        /^(fill-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950))$/,
    },
  ],
  plugins: [
    require('tailwindcss-animate'),
    require('@headlessui/tailwindcss'),
    require('@tailwindcss/typography'),
    heroui({
      prefix: 'heroui',
      addCommonColors: false,
      defaultTheme: 'light',
      defaultExtendTheme: 'light',
      // HeroUI composes colours as `hsl(var(--heroui-<slot>))`, so every slot is
      // fed a *channel triplet* token from tokens.css tier 3. Those channels
      // remap under `.dark` on their own, which is why light and dark share one
      // mapping here and no `dark:` branch exists in component code.
      layout: {
        radius: {
          small: 'var(--pi-radius-sm)',
          medium: 'var(--pi-radius-md)',
          large: 'var(--pi-radius-lg)',
        },
      },
      themes: {
        light: {
          colors: {
            background: 'var(--background-channels)',
            foreground: 'var(--foreground-channels)',
            divider: 'var(--border-channels)',
            focus: 'var(--ring-channels)',
            content1: 'var(--card-channels)',
            content2: 'var(--secondbackground-channels)',
            content3: 'var(--muted-channels)',
            content4: 'var(--accent-channels)',
            primary: {
              DEFAULT: 'var(--primary-channels)',
              foreground: 'var(--primary-foreground-channels)',
            },
            secondary: {
              DEFAULT: 'var(--secondary-channels)',
              foreground: 'var(--secondary-foreground-channels)',
            },
            danger: {
              DEFAULT: 'var(--destructive-channels)',
              foreground: 'var(--destructive-foreground-channels)',
            },
            success: {
              DEFAULT: 'var(--success-channels)',
              foreground: 'var(--success-foreground-channels)',
            },
            warning: {
              DEFAULT: 'var(--warning-channels)',
              foreground: 'var(--warning-foreground-channels)',
            },
            // NOT remapped on purpose: `default` (HeroUI's neutral ramp) and
            // `overlay`. They need a real design pass rather than an invented
            // mapping — tracked in PI-011 §6 (P3/P4).
          },
        },
        dark: {
          colors: {
            background: 'var(--background-channels)',
            foreground: 'var(--foreground-channels)',
            divider: 'var(--border-channels)',
            focus: 'var(--ring-channels)',
            content1: 'var(--card-channels)',
            content2: 'var(--secondbackground-channels)',
            content3: 'var(--muted-channels)',
            content4: 'var(--accent-channels)',
            primary: {
              DEFAULT: 'var(--primary-channels)',
              foreground: 'var(--primary-foreground-channels)',
            },
            secondary: {
              DEFAULT: 'var(--secondary-channels)',
              foreground: 'var(--secondary-foreground-channels)',
            },
            danger: {
              DEFAULT: 'var(--destructive-channels)',
              foreground: 'var(--destructive-foreground-channels)',
            },
            success: {
              DEFAULT: 'var(--success-channels)',
              foreground: 'var(--success-foreground-channels)',
            },
            warning: {
              DEFAULT: 'var(--warning-channels)',
              foreground: 'var(--warning-foreground-channels)',
            },
          },
        },
      },
    })
  ],
};
