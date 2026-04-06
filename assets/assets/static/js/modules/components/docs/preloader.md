# Preloader Component Documentation

The Preloader component provides a loading screen while the page assets are fetching. It supports multiple predefined types and automatically initializes based on the `data-preloader` attribute on the `<body>` tag.

## Usage

Enable the preloader by adding `data-preloader="TYPE"` to your `<body>` tag.

```html
<body data-preloader="1">
    <!-- Body content -->
</body>
```

## Configuration

### Preloader Types

Currently, there are 3 supported types:

1.  **Type 1 (`data-preloader="1"`)**: Circular SVG loader with a progress bar.
2.  **Type 2 (`data-preloader="2"`)**: Spinner animation with a progress bar.
3.  **Type 3 (`data-preloader="3"`)**: Three-dot bouncing animation with a progress bar.

### Customization

You can customize the appearance using CSS variables defined in your stylesheet (e.g., `preloader.css` or your theme CSS).

#### CSS Variables

```css
:root {
  /* Circular Preloader Colors */
  --preloader-bg: var(--theme-bg-primary);          /* Background color of the overlay */
  --preloader-path-color: var(--theme-primary);     /* Color of the circular path */
  --preloader-progress-color: var(--theme-text-tertiary); /* Color of the progress text */

  /* Three-Dot Loading Colors */
  --three-dot-object-color: var(--theme-secondary); /* Color of the dots */

  /* Transition Speed */
  --preloader-transition: opacity 0.5s ease;
}
```

### JavaScript API

The `Preloader` class is exported from `preloader.init.js`.

```javascript
import { Preloader } from './partials/preloader.init.js';

const loader = new Preloader();
loader.init();

// Manually show/hide
loader.show(); // Removes .loaded class from body
loader.hide(); // Adds .loaded class to body
```

## Implementation Details

-   **Initialization**: The preloader is automatically initialized by the `UIManager` when it detects `[data-preloader]` on the page.
-   **Structure**: The DOM structure for the preloader is dynamically injected into the `<body>` based on the selected type.
-   **Events**: The preloader listens for `window.load` to hide automatically. It also has a fallback timeout of 3000ms.
-   **Progress**: It attempts to track resource loading progress using the Performance API.

## Troubleshooting

-   **Preloader not showing**: Ensure `data-preloader` attribute is present on the `<body>` tag.
-   **Preloader stuck**: Check if `window.load` event is firing. The fallback timeout should hide it after 3 seconds regardless.

