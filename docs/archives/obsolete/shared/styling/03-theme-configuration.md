# Theme Configuration

Design tokens and theme customization.

## Design Tokens

### Color Palette

**Primary Colors**
```
Primary Blue: #3B82F6
Primary Dark: #1E40AF
Primary Light: #DBEAFE
```

**Secondary Colors**
```
Secondary Green: #10B981
Secondary Dark: #047857
Secondary Light: #D1FAE5
```

**Status Colors**
```
Success: #10B981
Warning: #F59E0B
Error: #EF4444
Info: #3B82F6
```

**Neutral Colors**
```
White: #FFFFFF
Gray-50: #F9FAFB
Gray-100: #F3F4F6
Gray-200: #E5E7EB
Gray-300: #D1D5DB
Gray-400: #9CA3AF
Gray-500: #6B7280
Gray-600: #4B5563
Gray-700: #374151
Gray-800: #1F2937
Gray-900: #111827
Black: #000000
```

### Typography

**Font Families**
```
Primary: 'Inter', system-ui, -apple-system, sans-serif
Monospace: 'Menlo', 'Monaco', 'Courier New', monospace
```

**Font Sizes**
```
xs: 0.75rem (12px)
sm: 0.875rem (14px)
base: 1rem (16px)
lg: 1.125rem (18px)
xl: 1.25rem (20px)
2xl: 1.5rem (24px)
3xl: 1.875rem (30px)
4xl: 2.25rem (36px)
```

**Font Weights**
```
Light: 300
Normal: 400
Medium: 500
Semibold: 600
Bold: 700
```

**Line Heights**
```
Tight: 1.25
Normal: 1.5
Relaxed: 1.625
Loose: 2
```

### Spacing Scale

```
0: 0
1: 0.25rem (4px)
2: 0.5rem (8px)
3: 0.75rem (12px)
4: 1rem (16px)
6: 1.5rem (24px)
8: 2rem (32px)
12: 3rem (48px)
16: 4rem (64px)
20: 5rem (80px)
24: 6rem (96px)
```

### Border Radius

```
none: 0
sm: 0.125rem (2px)
base: 0.25rem (4px)
md: 0.375rem (6px)
lg: 0.5rem (8px)
xl: 0.75rem (12px)
2xl: 1rem (16px)
full: 9999px
```

### Shadows

```
sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
base: 0 1px 3px 0 rgba(0, 0, 0, 0.1)
md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1)
```

## Tailwind Configuration

**File**: `tailwind.config.js`

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          900: '#1E40AF',
        },
        secondary: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          900: '#065F46',
        },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
      },
      borderRadius: {
        'sm': '0.125rem',
        'base': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem',
        'xl': '0.75rem',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
```

## CSS Variables

**File**: `src/styles/variables.css`

```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-primary-dark: #1E40AF;
  --color-primary-light: #DBEAFE;

  --color-secondary: #10B981;
  --color-secondary-dark: #047857;
  --color-secondary-light: #D1FAE5;

  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* Typography */
  --font-primary: 'Inter', system-ui, sans-serif;
  --font-mono: 'Menlo', 'Monaco', monospace;

  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #111827;
    --color-text: #F9FAFB;
  }
}
```

## Dark Mode

### Configuration

```javascript
module.exports = {
  darkMode: 'class',
  // ...
}
```

### Usage

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content
</div>
```

### CSS Variables for Dark Mode

```css
:root {
  --color-bg: #FFFFFF;
  --color-text: #111827;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #111827;
    --color-text: #F9FAFB;
  }
}
```

## Customization

### Adding Custom Colors

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#FF6B6B',
      },
    },
  },
}
```

### Adding Custom Fonts

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        display: ['Playfair Display', 'serif'],
      },
    },
  },
}
```

## Next Steps

- Review [CSS Frameworks](01-css-frameworks.md)
- Check [Styling Conventions](02-styling-conventions.md)
- See [Responsive Design](04-responsive-design.md)
