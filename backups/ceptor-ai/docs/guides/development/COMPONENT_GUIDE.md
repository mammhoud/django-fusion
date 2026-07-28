# Component Development Guide

Learn how to create, register, and initialize custom JavaScript components in VResume.

---

## Component Architecture

VResume uses a **lazy-loading component system** managed by `UIManager`. Components are initialized on-demand based on DOM selectors, reducing initial bundle size and improving performance.

### File Structure

```
v1/assets/static/js/
├── components/
│   ├── manager.js              ← Component registry & UIManager
│   ├── projects/                   ← UI components (accordion, tabs, etc.)
│   ├── effects/                ← Visual effects (preloader, animations)
│   ├── filters/                ← Filtering logic
│   ├── forms/                  ← Form handling & validation
│   ├── media/                  ← Sliders, lightbox, video
│   ├── modals/                 ← Modal dialogs
│   ├── search/                 ← Search & filtering
│   └── index.js                ← Component exports
```

---

## Step 1: Create Your Component

### File Placement

Place your component in the appropriate category:

```javascript
// ✅ v1/assets/static/js/components/media/carousel.js (media component)
// ✅ v1/assets/static/js/components/effects/fade-in.js (visual effect)
// ✅ v1/assets/static/js/components/modals/custom-modal.js (modal)
```

### Component Template

Every component should follow this structure:

```javascript
/**
 * CustomComponent — Brief description
 * 
 * Usage: Add [data-custom-component] to your HTML
 * Features:
 * - Feature 1
 * - Feature 2
 * 
 * @example
 * <div data-custom-component data-config="value">
 *   Content
 * </div>
 */
export class CustomComponent {
    constructor({ element, manager } = {}) {
        this.element = element;
        this.manager = manager;
        this.isInitialized = false;
    }

    /**
     * Initialize component
     * @returns {Promise<boolean>} Success status
     */
    async init() {
        if (!this.element) return false;

        try {
            // 1. Setup DOM references
            this.setup();
            
            // 2. Load external dependencies (if needed)
            await this.loadDependencies();
            
            // 3. Initialize event listeners
            this.attachEvents();
            
            // 4. Configure component
            this.configure();
            
            this.isInitialized = true;
            console.log('✅ CustomComponent initialized');
            return true;
        } catch (error) {
            console.error('Failed to initialize CustomComponent:', error);
            return false;
        }
    }

    setup() {
        // Find child elements, store references
        this.items = this.element.querySelectorAll('[data-item]');
    }

    async loadDependencies() {
        // Load external libraries if needed
        // Example: await this.loadScript('https://cdn.example.com/lib.js');
    }

    attachEvents() {
        // Bind event listeners
        this.items.forEach(item => {
            item.addEventListener('click', (e) => this.handleItemClick(e));
        });
    }

    configure() {
        // Read data attributes and configure
        const config = this.element.dataset.config;
        // Apply config...
    }

    handleItemClick(event) {
        console.log('Item clicked:', event.target);
    }

    destroy() {
        // Cleanup: remove listeners, clear refs
        this.items.forEach(item => {
            item.removeEventListener('click', (e) => this.handleItemClick(e));
        });
        this.items = null;
        this.isInitialized = false;
    }
}
```

---

## Step 2: Register in UIManager

### Location

Edit `v1/assets/static/js/components/manager.js`

### Registration

Find the `UI_COMPONENTS` definitions map and add your component:

```javascript
export const UI_COMPONENTS = {
    definitions: new Map([
        // ... existing components ...

        ['custom-component', {
            name: 'Custom Component',                    // Display name
            loader: () => import('./media/custom-component.js'),  // Dynamic import
            className: 'CustomComponent',                 // Class name to instantiate
            autoInit: true,                              // Auto-initialize on page load
            priority: 50,                                // Init order (0-100, higher first)
            dependencies: [],                            // Other components required first
            selectors: ['[data-custom-component]'],      // DOM selector(s) to find
            detection: 'auto',                           // How to detect: 'auto', 'manual'
        }],

        // ... more components ...
    ]),
};
```

### Priority Levels

Components with higher priority initialize first:

- **Priority 5**: Preloader (must be first)
- **Priority 10**: Sliders, lightbox (media)
- **Priority 40**: Accordion, tabs (core UI)
- **Priority 50-70**: Forms, filters, modals
- **Priority 90-100**: Heavy operations (last)

**Rule**: Put high-priority items first because other components might depend on them.

---

## Step 3: Export in Index

Edit `v1/assets/static/js/components/index.js`:

```javascript
// ── Media ─────────────────────────────────────────
export * from './media/index.js';  // includes your component

// Inside v1/assets/static/js/components/media/index.js:
export { default as CustomComponent } from './custom-component.js';
```

---

## Step 4: Use in HTML Template

### Basic Usage

```html
<!-- Simple activation -->
<div data-custom-component>
    <div data-item>Item 1</div>
    <div data-item>Item 2</div>
</div>
```

### With Configuration

```html
<!-- With data attributes -->
<div data-custom-component 
     data-config="advanced"
     data-delay="500"
     data-autoplay="true">
    <div data-item>Item</div>
</div>

{# In your component's configure() method: #}
configure() {
    const delay = parseInt(this.element.dataset.delay || 0);
    const autoplay = this.element.dataset.autoplay === 'true';
    this.setup({ delay, autoplay });
}
```

### Multiple Instances

Each matching selector creates a separate instance:

```html
<!-- Two independent component instances -->
<section>
    <div data-custom-component>Content A</div>
</section>

<section>
    <div data-custom-component>Content B</div>
</section>
```

---

## Step 5: Testing

### Local Testing

1. **Check console for initialization**
   ```javascript
   // You should see:
   // ✅ CustomComponent initialized
   ```

2. **Verify DOM is correct**
   ```javascript
   // In DevTools console:
   document.querySelector('[data-custom-component]')
   ```

3. **Check UIManager registration**
   ```javascript
   // In DevTools console:
   window.UIManager.components
   ```

### With HTMX (Important!)

If your component might appear via HTMX tab switch:

```javascript
// Test: Switch tabs and verify component re-initializes

// Problem: Components don't auto-reinit after HTMX swap!
// Solution: Add event listener in your component:

document.addEventListener('htmx:afterSettle', () => {
    // Manually check for new elements
    const newElements = document.querySelectorAll('[data-custom-component]:not([data-component-init])');
    newElements.forEach(el => {
        el.setAttribute('data-component-init', 'true');
        new CustomComponent({ element: el }).init();
    });
});
```

---

## Complete Example: Image Gallery Component

### Step 1: Create `v1/assets/static/js/components/media/gallery.js`

```javascript
/**
 * Gallery — Lightbox image gallery with keyboard navigation
 * 
 * @example
 * <div data-gallery data-columns="3">
 *   <figure data-gallery-item>
 *     <img src="image1.jpg" alt="Image 1">
 *   </figure>
 *   <figure data-gallery-item>
 *     <img src="image2.jpg" alt="Image 2">
 *   </figure>
 * </div>
 */
export class GalleryComponent {
    constructor({ element } = {}) {
        this.element = element;
        this.items = [];
        this.currentIndex = 0;
        this.isInitialized = false;
    }

    async init() {
        if (!this.element) return false;

        try {
            this.setup();
            this.attachEvents();
            this.configure();
            this.isInitialized = true;
            console.log('✅ Gallery initialized with', this.items.length, 'items');
            return true;
        } catch (error) {
            console.error('Gallery init failed:', error);
            return false;
        }
    }

    setup() {
        this.items = Array.from(this.element.querySelectorAll('[data-gallery-item]'));
        this.columns = parseInt(this.element.dataset.columns || 3);
        
        // Apply grid layout
        this.element.style.display = 'grid';
        this.element.style.gridTemplateColumns = `repeat(${this.columns}, 1fr)`;
        this.element.style.gap = '1rem';
    }

    attachEvents() {
        this.items.forEach((item, index) => {
            const img = item.querySelector('img');
            if (img) {
                img.style.cursor = 'pointer';
                img.addEventListener('click', () => this.openLightbox(index));
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    configure() {
        // Read any data attributes
        const autoplay = this.element.dataset.autoplay === 'true';
        if (autoplay) {
            this.startAutoplay();
        }
    }

    openLightbox(index) {
        this.currentIndex = index;
        const item = this.items[index];
        const img = item.querySelector('img');
        
        console.log('Opening:', img.src);
        // TODO: Create and show lightbox modal
    }

    handleKeydown(e) {
        if (!this.isInitialized) return;
        
        if (e.key === 'ArrowRight') {
            this.currentIndex = (this.currentIndex + 1) % this.items.length;
            this.updateDisplay();
        } else if (e.key === 'ArrowLeft') {
            this.currentIndex = (this.currentIndex - 1 + this.items.length) % this.items.length;
            this.updateDisplay();
        }
    }

    updateDisplay() {
        console.log('Current image:', this.currentIndex);
        // TODO: Update lightbox display
    }

    startAutoplay() {
        setInterval(() => {
            this.currentIndex = (this.currentIndex + 1) % this.items.length;
            this.updateDisplay();
        }, 5000);
    }

    destroy() {
        this.items.forEach(item => {
            const img = item.querySelector('img');
            if (img) img.removeEventListener('click', () => {});
        });
        document.removeEventListener('keydown', (e) => this.handleKeydown(e));
        this.items = [];
        this.isInitialized = false;
    }
}
```

### Step 2: Register in `components/manager.js`

```javascript
['gallery', {
    name: 'Gallery',
    loader: () => import('./media/gallery.js'),
    className: 'GalleryComponent',
    autoInit: true,
    priority: 60,
    dependencies: [],
    selectors: ['[data-gallery]'],
    detection: 'auto',
}],
```

### Step 3: Export in `components/media/index.js`

```javascript
export { default as GalleryComponent } from './gallery.js';
```

### Step 4: Use in Template

```html
<!-- portfolio/sections/gallery.html -->
<div data-gallery data-columns="3" data-autoplay="true">
    {% for image in gallery_images %}
    <figure data-gallery-item>
        <img src="{{ image.url }}" alt="{{ image.title }}" loading="lazy">
        <figcaption>{{ image.title }}</figcaption>
    </figure>
    {% endfor %}
</div>
```

---

## Debugging

### Enable Verbose Logging

Edit `v1/assets/static/js/components/manager.js`:

```javascript
const DEBUG = true;  // Set to true for verbose logs

class UIManager {
    async initializeComponents() {
        for (const [name, definition] of this.definitions) {
            if (DEBUG) console.log(`[UIManager] Checking ${name}...`);
            
            if (definition.selectors?.length) {
                const elements = document.querySelectorAll(definition.selectors.join(', '));
                if (DEBUG) console.log(`[UIManager] Found ${elements.length} ${name} elements`);
                // ... rest of code
            }
        }
    }
}
```

### Check UIManager State

```javascript
// In browser DevTools console:
window.UIManager.components          // All initialized components
window.UIManager.definitions         // All registered definitions
window.VResume.components           // Components namespace
```

### Test Component in Isolation

```javascript
// In DevTools console:
const el = document.querySelector('[data-custom-component]');
const comp = new (await import('./path/to/component.js')).CustomComponent({ element: el });
await comp.init();
```

---

## Best Practices

### 1. Always Check Element Existence
```javascript
if (!this.element) return false;
```

### 2. Use Data Attributes for Configuration
```html
<!-- Good -->
<div data-slider data-autoplay="true" data-speed="2000"></div>

<!-- Bad -->
<div class="slider" id="slider-1"></div>
<!-- Hardcoded config → needs JS to configure -->
```

### 3. Clean Up Event Listeners
```javascript
destroy() {
    this.items.forEach(item => {
        item.removeEventListener('click', this.onClick);  // Remove listener!
    });
}
```

### 4. Use `.bind()` or Arrow Functions for Event Handlers
```javascript
// Problem: 'this' context lost
item.addEventListener('click', this.handleClick);

// Solution: Use arrow function or .bind()
item.addEventListener('click', (e) => this.handleClick(e));
// or
item.addEventListener('click', this.handleClick.bind(this));
```

### 5. Lazy Load External Dependencies
```javascript
async loadDependencies() {
    if (window.Swiper) return;  // Already loaded
    
    const script = document.createElement('script');
    script.src = 'https://cdn.example.com/lib.js';
    document.body.appendChild(script);
    
    return new Promise((resolve) => {
        script.onload = () => resolve();
        script.onerror = () => resolve();  // Don't fail on error
    });
}
```

### 6. Dispatch Custom Events
```javascript
this.element.dispatchEvent(
    new CustomEvent('gallery:opened', { 
        detail: { index: this.currentIndex },
        bubbles: true 
    })
);
```

### 7. Document Data Attributes

```javascript
/**
 * @data data-gallery-columns {number} Number of columns in grid (default: 3)
 * @data data-gallery-autoplay {boolean} Enable autoplay (default: false)
 * @data data-gallery-speed {number} Autoplay speed in ms (default: 5000)
 */
```

---

## Troubleshooting

### Component Not Initializing

1. ✅ Check selector matches element: `document.querySelector('[data-custom-component]')`
2. ✅ Check registration in manager.js
3. ✅ Check export in index.js
4. ✅ Check console for errors
5. ✅ Verify component init returns true

### Component Initializes but Doesn't Work

1. ✅ Add console.log statements to setup(), attachEvents()
2. ✅ Check DevTools Elements panel for correct DOM structure
3. ✅ Verify event listeners attached: Add breakpoint in attachEvents()
4. ✅ Check data attributes: `element.dataset`

### Component Lost After HTMX Tab Switch

1. ❌ Component not re-initializing (expected)
2. ✅ **Solution**: Add HTMX event listener in your component
   ```javascript
   document.addEventListener('htmx:afterSettle', () => {
       UIManager.reinitializeComponentsForSelector('[data-custom-component]');
   });
   ```

---

## Next Steps

- Read [HTMX Integration Guide](HTMX_INTEGRATION.md) for tab switching details
- Check [UIManager Source](../../../applications/VResume/assets/static/js/components/manager.js) for advanced usage
- Review existing components in `components/` for real-world examples
