# Styling Conventions

Best practices and conventions for writing CSS and styling code.

## Class Naming

### Tailwind Classes

Use descriptive, semantic class names:

```html
<!-- Good -->
<button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
  Click me
</button>

<!-- Avoid -->
<button class="p-2 b-1 c-blue">
  Click me
</button>
```

### CSS Modules

Use camelCase for class names:

```css
/* Good */
.buttonPrimary {
  background-color: #3B82F6;
  color: white;
}

.buttonPrimaryHover {
  background-color: #2563EB;
}

/* Avoid */
.button-primary {
  background-color: #3B82F6;
}

.button_primary_hover {
  background-color: #2563EB;
}
```

## Component Styling

### Structure

```jsx
// Component.jsx
import styles from './Component.module.css'

export default function Component() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Title</h1>
      <p className={styles.description}>Description</p>
    </div>
  )
}
```

```css
/* Component.module.css */
.container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #111827;
}

.description {
  font-size: 1rem;
  color: #6B7280;
}
```

### Variants

```css
/* Component.module.css */
.button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.buttonPrimary {
  background-color: #3B82F6;
  color: white;
}

.buttonPrimary:hover {
  background-color: #2563EB;
}

.buttonSecondary {
  background-color: #E5E7EB;
  color: #111827;
}

.buttonSecondary:hover {
  background-color: #D1D5DB;
}

.buttonSmall {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.buttonLarge {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}
```

## State Management

### Hover States

```css
.button:hover {
  background-color: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### Active States

```css
.button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

### Disabled States

```css
.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #D1D5DB;
}
```

### Focus States

```css
.button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

## Responsive Design

### Mobile-First Approach

```html
<!-- Start with mobile styles, add breakpoints -->
<div class="w-full md:w-1/2 lg:w-1/3">
  Responsive width
</div>
```

### Breakpoint Usage

```css
/* Mobile (default) */
.container {
  display: flex;
  flex-direction: column;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    flex-direction: row;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    gap: 2rem;
  }
}
```

## Performance Best Practices

### Avoid Inline Styles

```jsx
/* Bad */
<div style={{ color: 'red', fontSize: '16px' }}>
  Content
</div>

/* Good */
<div className={styles.content}>
  Content
</div>
```

### Use CSS Classes

```jsx
/* Bad */
<div style={dynamicStyles}>
  Content
</div>

/* Good */
<div className={`${styles.base} ${condition && styles.active}`}>
  Content
</div>
```

### Minimize Specificity

```css
/* Bad - High specificity */
div.container > div.content > p.text {
  color: #333;
}

/* Good - Low specificity */
.text {
  color: #333;
}
```

## Accessibility

### Color Contrast

Ensure sufficient contrast between text and background:

```css
/* Good - WCAG AA compliant */
.text {
  color: #111827;      /* Dark text */
  background-color: #FFFFFF;  /* Light background */
}
```

### Focus Indicators

Always provide visible focus indicators:

```css
.button:focus {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}
```

### Semantic HTML

```html
<!-- Good -->
<button class="btn btn-primary">Click me</button>

<!-- Avoid -->
<div class="btn btn-primary" role="button">Click me</div>
```

## Common Patterns

### Flexbox Layout

```css
.flexContainer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}
```

### Grid Layout

```css
.gridContainer {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
```

### Centering

```css
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
```

## Next Steps

- Review [CSS Frameworks](01-css-frameworks.md)
- Check [Theme Configuration](03-theme-configuration.md)
- See [Responsive Design](04-responsive-design.md)
