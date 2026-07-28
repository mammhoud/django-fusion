# Component Lifecycle & Initialization

Deep dive into how VResume components are detected, initialized, and managed throughout the page lifecycle.

---

## Component Lifecycle States

Every component progresses through distinct states:

```
NOT_FOUND
  ↓
  (UI Manager scans DOM)
  ↓
DETECTED
  ↓
  (Lazy load JS module)
  ↓
LOADING
  ↓
  (Instantiate & call .init())
  ↓
INITIALIZING
  ↓
READY ✅
  ↓
  (User interacts)
  ↓
ACTIVE ✅
  ↓
  (HTMX swap / page unload)
  ↓
DESTROYED
  ↓
  (Optional: cleanup)
  ↓
DEAD ❌
```

---

## UIManager: The Component Registry

### What UIManager Does

`UIManager` is the central component orchestrator:

1. **Registers** all components (definitions)
2. **Detects** component instances in DOM
3. **Lazy-loads** component modules
4. **Initializes** components
5. **Tracks** initialized components
6. **Can re-initialize** after HTMX swaps

### Registry Structure

**Location**: `v1/assets/static/js/components/manager.js`

```javascript
export const UI_COMPONENTS = {
    definitions: new Map([
        ['sliders', {
            name: 'Sliders',                                 // Display name
            loader: () => import('./media/sliders.js'),      // Lazy loader
            className: 'SlidersComponent',                   // Constructor name
            autoInit: true,                                  // Auto-initialize?
            priority: 10,                                    // Init order (0-100)
            dependencies: [],                                // Pre-requisites
            selectors: ['[data-slider]', '.swiper'],        // Find elements
            detection: 'auto',                              // How to detect
        }],
        
        // ... more components ...
    ]),
};
```

### Priority System

Components initialize in **priority order** (highest first):

```
Priority 5    ← Preloader (must be first!)
Priority 10   ← Sliders, lightbox (media)
Priority 40   ← Accordion, tabs (core UI)
Priority 50   ← Forms, validation
Priority 70   ← Modals
Priority 90   ← Heavy operations (last)
```

**Why?** Some components depend on others. Preloader must run before everything else.

---

## Initialization Flow: Step by Step

### On Page Load (DOMContentLoaded)

```javascript
// 1. Event fires
document.addEventListener('DOMContentLoaded', async () => {
    // 2. Create UIManager instance
    window.UIManager = new UIManager();
    
    // 3. Initialize all components
    await UIManager.initializeComponents();
    
    // 4. Done! User sees interactive page
});
```

### UIManager.initializeComponents() Process

```javascript
async initializeComponents() {
    // 1. Sort components by priority (descending)
    const sorted = Array.from(definitions)
        .sort((a, b) => (b[1].priority || 0) - (a[1].priority || 0));
    
    // 2. For each component definition
    for (const [name, definition] of sorted) {
        
        // 3. Skip if no selectors
        if (!definition.selectors?.length) continue;
        
        // 4. Find matching DOM elements
        const selector = definition.selectors.join(', ');
        const elements = document.querySelectorAll(selector);
        
        console.log(`Found ${elements.length} ${name} elements`);
        
        // 5. For each matching element
        for (const element of elements) {
            
            // 6. Lazy-load component module
            const module = await definition.loader();
            const ComponentClass = module[definition.className];
            
            // 7. Create instance
            const instance = new ComponentClass({ element, manager: this });
            
            // 8. Initialize
            const success = await instance.init();
            
            // 9. Track it
            if (success) {
                this.components.push(instance);
                this.componentsByElement.set(element, instance);
            }
        }
    }
}
```

---

## The HTMX Problem: Lost Components

### Scenario: Tab Switch

```
1. Page loads → DOMContentLoaded fires → Components init ✅

2. User clicks "Portfolio" tab

3. HTMX sends request → Receives fragment → Swaps DOM

4. NEW SLIDER HTML appears in DOM
   <div class="swiper">...</div>  ← New element!

5. ❌ PROBLEM: DOMContentLoaded doesn't fire again!
   - UIManager only runs once
   - New slider element NOT initialized
   - Slider JavaScript doesn't load
   - User clicks slider → Nothing happens
```

### Visual: Before vs After HTMX Swap

```
BEFORE SWAP                    AFTER SWAP
─────────────────────────────────────────────────

#vresume-tab-content           #vresume-tab-content
  ├─ [data-slider]             ├─ [data-slider]  ← NEW!
  │   └─ ✅ Initialized         │   └─ ❌ Not init!
  └─ .project-card             └─ .project-card
      └─ ✅ Works                  └─ ✅ Works (doesn't need JS)
```

---

## Solutions: Component Re-initialization

### Solution 1: HTMX Event Listener (RECOMMENDED)

**Problem**: Components don't auto-reinit after HTMX swap

**Fix**: Listen for `htmx:afterSettle` event

```javascript
// In v1/assets/static/js/projects/main.js
// Add after initial UIManager setup:

document.addEventListener('htmx:afterSettle', async () => {
    console.log('[HTMX] afterSettle → re-initializing components');
    
    // Find NEW components that appeared
    const allElements = document.querySelectorAll('[data-slider], [data-modal], [data-form]');
    
    for (const element of allElements) {
        // Skip if already initialized
        if (element.hasAttribute('data-component-init')) continue;
        
        // Mark as processing
        element.setAttribute('data-component-init', 'true');
        
        // Re-initialize
        await UIManager.initializeComponents();
    }
});
```

### Solution 2: Mutation Observer (MORE ROBUST)

```javascript
// Watch for DOM changes
const observer = new MutationObserver(() => {
    // Find new elements that match component selectors
    const newElements = document.querySelectorAll(
        '[data-slider]:not([data-slider-init]), ' +
        '[data-modal]:not([data-modal-init]), ' +
        '[data-form]:not([data-form-init])'
    );
    
    newElements.forEach(el => {
        // Mark and initialize
        const selector = el.getAttribute('data-component-type');
        el.setAttribute(`${selector}-init`, 'true');
        // Initialize this specific element
    });
});

observer.observe(document.body, {
    childList: true,      // Watch child additions/removals
    subtree: true,        // Watch entire tree
    attributes: false,    // Don't watch attribute changes
});
```

### Solution 3: Component-Specific Detection (PER COMPONENT)

Each component detects new instances of itself:

```javascript
export class SlidersComponent {
    constructor({ element } = {}) {
        this.element = element;
        this.setupMutationObserver();  // ← New method
    }
    
    setupMutationObserver() {
        const observer = new MutationObserver(() => {
            // Look for NEW sliders that aren't initialized
            const newSliders = document.querySelectorAll('[data-slider]:not([data-slider-init])');
            
            newSliders.forEach(el => {
                el.setAttribute('data-slider-init', 'true');
                new SlidersComponent({ element: el }).init();
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
}
```

**Pros**: ✅ Each component manages itself, no global coordination  
**Cons**: ❌ Might create duplicate instances

---

## Dependencies & Initialization Order

### Dependency Chain Example

```
Preloader (priority 5)
  ↓ (must init first)
Forms (priority 50)
  ├─ Validation
  └─ Error display
      ↓
Modals (priority 70)
  └─ Can use forms inside
      ↓
Lightbox (priority 100, lowest)
  └─ Can open modals
```

### Declaring Dependencies

```javascript
// In manager.js:
['modals', {
    name: 'Modals',
    loader: () => import('./modals/unified-modal.js'),
    dependencies: ['forms'],  // ← Requires forms to init first
    priority: 70,
    selectors: ['[data-modal]'],
}],
```

### Checking Dependencies

```javascript
async initializeComponents() {
    for (const [name, definition] of sortedByPriority) {
        
        // Check dependencies
        for (const depName of definition.dependencies || []) {
            const dep = definitions.get(depName);
            
            // Verify dependency is loaded
            if (!dep || !dep.loaded) {
                console.warn(`[${name}] Dependency missing: ${depName}`);
                continue;  // Skip this component
            }
        }
        
        // Safe to initialize
        await this.initializeComponent(name, definition);
    }
}
```

---

## Component State Management

### Tracking Component State

```javascript
class UIManager {
    constructor() {
        this.components = [];  // All initialized instances
        this.componentsByElement = new Map();  // element → component
        this.componentsByName = new Map();  // name → [instances]
    }
}
```

### Example: Track All Sliders

```javascript
// After initialization
UIManager.getComponentsByName('sliders');
// Returns: [SlidersComponent, SlidersComponent, ...]
// (One for home slider, one for team slider, etc.)

// Get specific slider
const sliderElement = document.querySelector('[data-slider]');
const sliderComponent = UIManager.componentsByElement.get(sliderElement);
sliderComponent.destroy();  // Cleanup
```

---

## Cleanup & Destruction

### Proper Component Destruction

```javascript
export class MyComponent {
    destroy() {
        // 1. Remove event listeners
        this.element.removeEventListener('click', this.handleClick);
        
        // 2. Stop animations/timers
        if (this.animationFrame) cancelAnimationFrame(this.animationFrame);
        if (this.timeout) clearTimeout(this.timeout);
        
        // 3. Clean up references
        this.items = null;
        this.element = null;
        
        // 4. Mark as destroyed
        this.isInitialized = false;
        
        console.log('✅ Component destroyed');
    }
}
```

### When to Destroy

```javascript
// On HTMX beforeSwap (before content changes)
document.addEventListener('htmx:beforeSwap', (e) => {
    const target = e.detail.target;
    
    // Find components inside target
    const componentsToRemove = UIManager.componentsByElement
        .entries()
        .filter(([el]) => target.contains(el));
    
    // Destroy them
    componentsToRemove.forEach(([el, comp]) => {
        comp.destroy();
        UIManager.componentsByElement.delete(el);
    });
});
```

---

## Performance Considerations

### Lazy Loading Benefits

```
Traditional (all at once):
  App JS: 400KB
  Includes: Sliders, Lightbox, Modals, Forms, etc.
  Load time: 2s

Lazy Loading (VResume):
  App JS: 150KB (core only)
  Sliders: 80KB (loaded when needed)
  Lightbox: 50KB (loaded when needed)
  Load time: 800ms (40% faster!)
```

### Component Detection Performance

```javascript
// ✅ Fast: Single query
const sliders = document.querySelectorAll('[data-slider]');
// One pass through DOM

// ❌ Slow: Multiple queries
for (let i = 0; i < definitions.length; i++) {
    for (let j = 0; j < definitions[i].selectors.length; j++) {
        document.querySelectorAll(definitions[i].selectors[j]);
    }
}
// Many passes through DOM
```

### HTMX Re-init Performance

```javascript
// ❌ Inefficient: Re-init everything
document.addEventListener('htmx:afterSettle', () => {
    UIManager.initializeComponents();  // Searches entire DOM again
});

// ✅ Better: Only check target
document.addEventListener('htmx:afterSettle', (e) => {
    const target = e.detail.target;
    UIManager.initializeComponentsInElement(target);  // Only target
});
```

---

## Debugging Component Issues

### Common Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| Component doesn't init | Selector doesn't match | Check data attribute, DevTools |
| Component init fails | Module import error | Check console for import errors |
| Component works, then breaks | HTMX swap, no re-init | Add event listener |
| Multiple instances created | Mutation observer fires twice | Add flag to prevent duplicates |
| Memory leaks | Listeners not removed | Add proper destroy() method |

### Debugging Checklist

1. **Selector matches?**
   ```javascript
   document.querySelector('[data-slider]')  // Returns element?
   ```

2. **Definition registered?**
   ```javascript
   UIManager.definitions.get('sliders')  // Returns definition?
   ```

3. **Module loads?**
   ```javascript
   import('./media/sliders.js')  // Promise resolves?
   ```

4. **Component initializes?**
   ```javascript
   const comp = new SlidersComponent({ element: el });
   const success = await comp.init();  // Returns true?
   ```

5. **Listens to HTMX?**
   ```javascript
   // In htmx:afterSettle, do components re-init?
   document.addEventListener('htmx:afterSettle', () => console.log('Hi!'));
   // Click tab and check console
   ```

---

## Best Practices

### ✅ Component Do's

1. **Always check element exists**
   ```javascript
   if (!this.element) return false;
   ```

2. **Implement proper destroy()**
   ```javascript
   destroy() {
       // Remove listeners, clear refs
   }
   ```

3. **Use data attributes for config**
   ```html
   <div data-slider data-speed="2000"></div>
   ```

4. **Add console logs for debugging**
   ```javascript
   console.log('✅ Component initialized');
   ```

5. **Return success/failure**
   ```javascript
   async init() {
       try {
           // ... code ...
           return true;  // ✅
       } catch (error) {
           return false;  // ❌
       }
   }
   ```

### ❌ Component Don'ts

1. **Don't assume element never gets removed**
   ```javascript
   // ❌ Will crash after HTMX swap
   this.items = this.element.querySelectorAll('[data-item]');
   
   // ✅ Query each time or re-init
   queryItems() {
       return this.element.querySelectorAll('[data-item]');
   }
   ```

2. **Don't forget to remove listeners**
   ```javascript
   // ❌ Leaks listeners
   this.items.forEach(item => {
       item.addEventListener('click', this.onClick);
   });
   
   // ✅ Remove in destroy()
   destroy() {
       this.items.forEach(item => {
           item.removeEventListener('click', this.onClick);
       });
   }
   ```

3. **Don't hardcode selectors**
   ```javascript
   // ❌ Can't be reused
   const items = document.querySelectorAll('.my-items');
   
   // ✅ Use data attributes
   const items = this.element.querySelectorAll('[data-item]');
   ```

---

## Next Steps

- [Component Development Guide](../../guides/development/COMPONENT_GUIDE.md) — Build your own components
- [HTMX Integration Guide](../../guides/development/HTMX_INTEGRATION.md) — HTMX patterns
- [HTMX Flow Diagrams](./HTMX_FLOW.md) — Visual request lifecycle
