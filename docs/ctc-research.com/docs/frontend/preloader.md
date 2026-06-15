# Preloader Component

The Preloader component provides a loading screen while page assets are fetching. It supports multiple predefined types and automatically initializes based on the `data-preloader` attribute on the `<body>` tag.

---

## Usage

Enable the preloader by adding `data-preloader="TYPE"` to your `<body>` tag:

```html
<body data-preloader="1">
    <!-- Body content -->
</body>
```

---

## Preloader Types

| Type | `data-preloader` | Description |
|---|---|---|
| **Type 1** | `"1"` | Circular SVG loader with a progress bar |
| **Type 2** | `"2"` | Spinner animation with a progress bar |
| **Type 3** | `"3"` | Three-dot bouncing animation with a progress bar |

---

## CSS Customization

Customize appearance via CSS variables:

```css
:root {
  /* Circular Preloader */
  --preloader-bg: var(--theme-bg-primary);             /* Overlay background */
  --preloader-path-color: var(--theme-primary);        /* Circular path color */
  --preloader-progress-color: var(--theme-text-tertiary); /* Progress text */

  /* Three-Dot Loading */
  --three-dot-object-color: var(--theme-secondary);    /* Dot color */

  /* Transition Speed */
  --preloader-transition: opacity 0.5s ease;
}
```

---

## JavaScript API

The `Preloader` class is exported from `preloader.init.js`:

```javascript
import { Preloader } from './partials/preloader.init.js';

const loader = new Preloader();
loader.init();

// Manually show/hide
loader.show(); // Removes .loaded class from body
loader.hide(); // Adds .loaded class to body
```

---

## Implementation Details

| Aspect | Detail |
|---|---|
| **Initialization** | Auto-initialized by `UIManager` when `[data-preloader]` is detected on the page |
| **DOM Structure** | Dynamically injected into `<body>` based on selected type |
| **Hide Trigger** | Listens for `window.load` event |
| **Fallback** | 3000ms timeout hides the preloader regardless of load state |
| **Progress Tracking** | Uses the Performance API to estimate resource loading progress |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Preloader not showing | Ensure `data-preloader` attribute is present on `<body>` |
| Preloader stuck | Check `window.load` is firing; fallback hides it after 3 seconds |

---

## Source File

```
assets/static/js/modules/components/partials/preloader.init.js
```

## Further Reading

- [JS Architecture](./js-architecture.md)
- [UIManager](./js-codebase.md)
