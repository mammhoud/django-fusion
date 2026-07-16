# Responsive Design

Mobile-first responsive design patterns and practices.

## Breakpoints

### Standard Breakpoints

```
Mobile: 0px - 639px (default)
Tablet: 640px - 1023px (sm)
Desktop: 1024px - 1279px (md)
Large Desktop: 1280px+ (lg)
```

### Tailwind Breakpoints

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

## Mobile-First Approach

### Principle

Start with mobile styles, then add breakpoints for larger screens.

### Example

```html
<!-- Mobile first -->
<div class="w-full md:w-1/2 lg:w-1/3">
  Responsive width
</div>
```

### CSS Equivalent

```css
/* Mobile (default) */
.container {
  width: 100%;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    width: 50%;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    width: 33.333%;
  }
}
```

## Common Responsive Patterns

### Responsive Grid

```html
<!-- 1 column on mobile, 2 on tablet, 3 on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

### Responsive Flex

```html
<!-- Stack on mobile, row on desktop -->
<div class="flex flex-col md:flex-row gap-4">
  <div class="w-full md:w-1/2">Left</div>
  <div class="w-full md:w-1/2">Right</div>
</div>
```

### Responsive Typography

```html
<!-- Smaller text on mobile, larger on desktop -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">
  Responsive Heading
</h1>
```

### Responsive Padding

```html
<!-- Less padding on mobile, more on desktop -->
<div class="p-4 md:p-6 lg:p-8">
  Content with responsive padding
</div>
```

### Responsive Display

```html
<!-- Hide on mobile, show on desktop -->
<div class="hidden md:block">
  Desktop only content
</div>

<!-- Show on mobile, hide on desktop -->
<div class="md:hidden">
  Mobile only content
</div>
```

## Navigation Patterns

### Mobile Menu

```jsx
import { useState } from 'react'

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="text-xl font-bold">Logo</div>

          {/* Mobile menu button */}
          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            Menu
          </button>

          {/* Desktop menu */}
          <div className="hidden md:flex gap-4">
            <a href="#" className="hover:text-blue-500">Home</a>
            <a href="#" className="hover:text-blue-500">About</a>
            <a href="#" className="hover:text-blue-500">Contact</a>
          </div>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden pb-4">
            <a href="#" className="block py-2 hover:text-blue-500">Home</a>
            <a href="#" className="block py-2 hover:text-blue-500">About</a>
            <a href="#" className="block py-2 hover:text-blue-500">Contact</a>
          </div>
        )}
      </div>
    </nav>
  )
}
```

## Image Optimization

### Responsive Images

```html
<!-- Responsive image with srcset -->
<img
  src="image-small.jpg"
  srcset="
    image-small.jpg 640w,
    image-medium.jpg 1024w,
    image-large.jpg 1280w
  "
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  alt="Responsive image"
/>
```

### Picture Element

```html
<picture>
  <source media="(max-width: 640px)" srcset="image-mobile.jpg">
  <source media="(max-width: 1024px)" srcset="image-tablet.jpg">
  <img src="image-desktop.jpg" alt="Responsive image">
</picture>
```

## Container Queries

### CSS Container Queries

```css
@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}
```

### Usage

```html
<div class="card-container">
  <div class="card">
    <h2>Card Title</h2>
    <p>Card content</p>
  </div>
</div>
```

## Testing Responsive Design

### Browser DevTools

1. Open DevTools (F12)
2. Click device toggle (Ctrl+Shift+M)
3. Select device or custom dimensions
4. Test interactions

### Responsive Testing Checklist

- [ ] Mobile (320px - 480px)
- [ ] Tablet (768px - 1024px)
- [ ] Desktop (1280px+)
- [ ] Touch interactions
- [ ] Orientation changes
- [ ] Font scaling
- [ ] Image loading

## Performance Considerations

### Lazy Loading

```html
<img
  src="image.jpg"
  loading="lazy"
  alt="Lazy loaded image"
/>
```

### Responsive Images for Performance

```html
<img
  src="image-small.jpg"
  srcset="
    image-small.jpg 640w,
    image-large.jpg 1280w
  "
  sizes="(max-width: 640px) 100vw, 50vw"
  alt="Optimized image"
/>
```

## Next Steps

- Review [CSS Frameworks](01-css-frameworks.md)
- Check [Styling Conventions](02-styling-conventions.md)
- See [Theme Configuration](03-theme-configuration.md)
