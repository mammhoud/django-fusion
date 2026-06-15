# CSS Frameworks

CSS frameworks and styling libraries used across projects.

## Tailwind CSS

### Overview
Utility-first CSS framework for rapidly building custom designs.

**Version**: 3.x
**Used in**: ctc-research, structa, blinko

### Configuration

**File**: `tailwind.config.js`

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      },
      spacing: {
        '128': '32rem',
      },
    },
  },
  plugins: [],
}
```

### Key Features
- Utility classes for styling
- Responsive design utilities
- Dark mode support
- Plugin system
- JIT compilation

### Common Utilities

**Spacing**
```html
<div class="p-4 m-2">Padding and margin</div>
```

**Colors**
```html
<div class="bg-blue-500 text-white">Colored box</div>
```

**Responsive**
```html
<div class="w-full md:w-1/2 lg:w-1/3">Responsive width</div>
```

**Flexbox**
```html
<div class="flex justify-center items-center">Centered content</div>
```

## CSS Modules

### Overview
Scoped CSS for component-level styling.

**Used in**: ctc-research, structa

### Example

**Component.module.css**
```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.title {
  font-size: 2rem;
  color: #333;
}
```

**Component.jsx**
```jsx
import styles from './Component.module.css'

export default function Component() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Title</h1>
    </div>
  )
}
```

### Benefits
- Scoped styling
- No naming conflicts
- Easy to maintain
- Component-specific styles

## PostCSS

### Overview
Tool for transforming CSS with JavaScript plugins.

**Configuration**: `postcss.config.js`

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### Plugins Used
- **tailwindcss** - Utility CSS framework
- **autoprefixer** - Add vendor prefixes
- **postcss-nested** - Nested CSS support

## Styling Conventions

### Naming Conventions

**Tailwind Classes**
```html
<!-- Use descriptive class names -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  Content
</div>
```

**CSS Modules**
```css
/* Use camelCase for class names */
.containerHeader {
  display: flex;
  justify-content: space-between;
}

.containerTitle {
  font-size: 1.5rem;
  font-weight: bold;
}
```

### File Organization

```
src/
├── styles/
│   ├── globals.css
│   ├── variables.css
│   └── utilities.css
├── components/
│   ├── Button/
│   │   ├── Button.jsx
│   │   └── Button.module.css
│   └── Card/
│       ├── Card.jsx
│       └── Card.module.css
```

## Design Tokens

### Colors

**Primary Colors**
- Primary: #3B82F6 (Blue)
- Secondary: #10B981 (Green)
- Danger: #EF4444 (Red)
- Warning: #F59E0B (Amber)

**Neutral Colors**
- Gray-50: #F9FAFB
- Gray-500: #6B7280
- Gray-900: #111827

### Typography

**Font Families**
- Primary: Inter, system-ui, sans-serif
- Monospace: Menlo, Monaco, monospace

**Font Sizes**
- xs: 0.75rem
- sm: 0.875rem
- base: 1rem
- lg: 1.125rem
- xl: 1.25rem
- 2xl: 1.5rem

### Spacing Scale

```
0: 0
1: 0.25rem
2: 0.5rem
4: 1rem
6: 1.5rem
8: 2rem
12: 3rem
16: 4rem
```

## Responsive Design

### Breakpoints

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

### Mobile-First Approach

```html
<!-- Mobile first -->
<div class="w-full md:w-1/2 lg:w-1/3">
  Responsive width
</div>
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
<!-- Dark mode class -->
<div class="bg-white dark:bg-gray-900">
  Content
</div>
```

## Next Steps

- Review [Styling Conventions](02-styling-conventions.md)
- Check [Theme Configuration](03-theme-configuration.md)
- See [Responsive Design](04-responsive-design.md)
