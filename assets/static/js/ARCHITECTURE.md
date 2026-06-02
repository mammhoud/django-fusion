# Frontend Architecture - Unified JS Organization

## Overview
Consolidated JavaScript architecture for 3 websites (CTC-Research, LMS-Demo, VResume) with shared utilities, plugins, theme system, and page-specific handlers.

## Directory Structure

```
assets/static/js/
├── core/                          # Core app initialization and configuration
│   ├── app.js                     # Main app instance
│   ├── config.js                  # App configuration
│   ├── main.js                    # Entry point
│   └── init.config.js             # Initial config setup
│
├── utility/                       # Shared utility functions (reusable across all sites)
│   ├── index.js                   # Utility exports
│   ├── helpers.js                 # Essential functions (debounce, throttle, formatting, etc.)
│   ├── dom.js                     # DOM manipulation helpers
│   ├── state.js                   # State management
│   ├── url.js                     # URL/query utilities
│   ├── app.metrics.js             # Performance metrics
│   ├── base.manager.js            # Base manager class
│   └── bootbox-shim.js            # Bootbox compatibility shim
│
├── theme/                         # Unified theme and vendor system
│   ├── index.js                   # Theme exports (vendors, usecases, plugins)
│   ├── vendor-packages.js         # Dynamic vendor package loader
│   ├── animations/                # Animation usecases
│   ├── crm/                       # CRM usecases
│   ├── forms/                     # Form usecases
│   ├── landing/                   # Landing page usecases
│   ├── lms/                       # LMS usecases
│   ├── modal/                     # Modal usecases
│   └── spa/                       # SPA usecases
│
├── plugins/                       # Plugin system (page enhancements)
│   ├── index.js                   # Plugin manager and exports
│   ├── active-links.js            # Active navigation links
│   ├── backgroundImages.js        # Background image handler
│   ├── layoutDetector.js          # Layout detection
│   ├── pageLoader.js              # Page loading
│   ├── scrollTracking.js          # Scroll tracking
│   └── transparentHeaders.js      # Transparent header handling
│
├── modules/                       # Feature modules (organized by feature)
│   ├── index.js                   # Module exports
│   ├── manager.init.js            # Module manager
│   ├── auth/                      # Authentication
│   │   ├── index.js
│   │   ├── FormValidator.js
│   │   └── NotificationManager.js
│   ├── components/                # Component management
│   │   ├── index.js
│   │   ├── manager.init.js
│   │   ├── accordion.init.js
│   │   ├── modal.init.js
│   │   ├── tabs.init.js
│   │   ├── progress.init.js
│   │   ├── listing/               # Listing components
│   │   ├── media/                 # Media components
│   │   ├── partials/              # Partial components
│   │   ├── widgets/               # Widget components
│   │   └── features/              # Feature components
│   ├── forms/                     # Form handling
│   │   ├── index.js
│   │   ├── formsManager.js
│   │   ├── formHandler.js
│   │   ├── authHandler.js
│   │   ├── contactHandler.js
│   │   └── validationUtils.js
│   ├── handlers/                  # Event and system handlers
│   │   ├── index.js
│   │   ├── events.js
│   │   ├── cookies.js
│   │   ├── htmxSSENotifications.js
│   │   └── sseSecurity.js
│   ├── navigations/               # Navigation handling
│   │   ├── index.js
│   │   └── menu.init.js
│   ├── notifications/             # Notification system
│   │   ├── index.js
│   │   ├── notification.js
│   │   └── notification-init.js
│   └── readiness.js               # App readiness check
│
├── pages/                         # Page-specific initialization (layouts)
│   ├── init.layout.js             # Initialization page layout
│   ├── auth.layout.js             # Authentication page layout
│   ├── app.layout.js              # Application page layout
│   ├── landing.layout.js          # Landing page layout
│   ├── profile.layout.js          # Profile page layout
│   └── notifications.layout.js    # Notifications page layout
│
├── registry.js                    # Global component/module registry
├── config.helpers.js              # Configuration helpers
└── readiness.js                   # Global readiness check
```

## Site-Specific Entry Points

```
ctc-research/assets/static/js/
├── ctc-app.js                     # CTC-Research app initialization
└── usecase-config.js              # CTC-Research usecase configuration

lms-demo/assets/static/js/
├── lms-app.js                     # LMS-Demo app initialization
└── usecase-config.js              # LMS-Demo usecase configuration

VResume/assets/static/js/
├── vresume-app.js                 # VResume app initialization
├── index.js                       # Main entry point
├── static.js                      # Static page handler
├── usecases/
│   └── config.js                  # VResume-specific usecases
├── components/                    # VResume components
├── core/                          # VResume core logic
├── lib/                           # VResume libraries
├── navigation/                    # VResume navigation
└── services/                      # VResume services
```

## Import Patterns

### Shared Utilities (from all sites)
```javascript
import { Utils, debounce, throttle } from '@utility/helpers';
import { DOM } from '@utility/dom';
import { AppState } from '@utility/state';
```

### Theme System
```javascript
import { loadThemeVendorPackages, initLandingUsecase } from '@theme';
import { pluginManager, initializePlugins } from '@theme';
```

### Modules
```javascript
import { FormsManager } from '@modules/forms';
import { ComponentManager } from '@modules/components';
import { NotificationSystem } from '@modules/notifications';
```

### Page Layouts
```javascript
import { initAppLayout } from '@pages/app.layout';
import { initLandingLayout } from '@pages/landing.layout';
```

## Key Conventions

### 1. File Naming
- **Utilities**: `lowercase-with-hyphens.js` or `camelCase.js`
- **Classes**: `CapitalizedClass.js`
- **Initializers**: `component.init.js`
- **Index files**: `index.js` (exports from directory)

### 2. Unique Exports
- Each module has **unique exports** to avoid conflicts
- Use `export { ClassName }` for explicit exports
- Default exports only for main class/function

### 3. Module Organization
- **Features grouped by function** (auth, forms, components)
- **Clear separation of concerns**
- **Shared utilities in `utility/` directory**
- **Theme system isolated in `theme/` directory**

### 4. Reusability Patterns
- **Base classes** in `utility/base.manager.js`
- **Shared helpers** in `utility/helpers.js`
- **DOM utilities** in `utility/dom.js`
- **Plugin system** for extensibility

## Feature Modules

### Auth Module (`modules/auth/`)
- User authentication
- Form validation
- Notification management
- **Exports**: `FormValidator`, `NotificationManager`, `authModule`

### Components Module (`modules/components/`)
- UI component initialization
- Component manager
- Accordion, modal, tabs, progress bars
- **Exports**: `ComponentManager`, `initComponentsModule`

### Forms Module (`modules/forms/`)
- Form handling and validation
- Contact form handler
- Auth form handler
- **Exports**: `FormsManager`, `FormValidator`, `formHandler`

### Handlers Module (`modules/handlers/`)
- Event handling
- Cookie management
- HTMX SSE notifications
- **Exports**: `EventManager`, `CookieManager`, `SSEManager`

### Notifications Module (`modules/notifications/`)
- Notification system
- Toast/alert management
- **Exports**: `NotificationSystem`, `Notification`

## Plugin System

### Available Plugins
1. **active-links** - Highlight active navigation links
2. **backgroundImages** - Handle background images
3. **layoutDetector** - Detect page layout
4. **pageLoader** - Page loading indicator
5. **scrollTracking** - Track scroll position
6. **transparentHeaders** - Transparent header styling

### Plugin Manager
```javascript
import { pluginManager, PluginManager } from '@theme';

// Initialize plugins
await pluginManager.init(appContext);

// Get specific plugin
const plugin = pluginManager.getPlugin('active-links');
```

## Theme System

### Vendor Packages
Dynamically loaded npm packages (jQuery, Bootstrap, HTMX, etc.)
```javascript
import { loadThemeVendorPackages } from '@theme';
await loadThemeVendorPackages({ debug: false });
```

### Usecases
Product-specific component systems:
- **Animations** - Animation handlers
- **CRM** - CRM-specific components
- **Forms** - Form components
- **Landing** - Landing page components
- **LMS** - Learning management components
- **Modal** - Modal components
- **SPA** - Single-page app components

## Page Layouts

Each page type has a dedicated layout:
- `init.layout.js` - Initialization/onboarding
- `auth.layout.js` - Authentication pages
- `app.layout.js` - Application dashboard
- `landing.layout.js` - Marketing/landing pages
- `profile.layout.js` - User profile pages
- `notifications.layout.js` - Notification center

## Best Practices

### 1. Always Use Unique Names
- Avoid generic names like `manager.js`, `handler.js`
- Use descriptive names: `FormValidator`, `ComponentManager`
- Use file-based categorization in modules/

### 2. Import from Correct Paths
- Utilities: Always from `@utility/`
- Theme: Always from `@theme/`
- Modules: Always from `@modules/`
- Pages: Always from `@pages/`

### 3. Avoid Duplication
- Use `merge()` from utilities for deep merging
- Use base classes for common functionality
- Extend from `BaseManager` for managers

### 4. Initialize in Order
1. Load utilities
2. Initialize plugins
3. Load theme vendors
4. Initialize modules
5. Set up page layout

### 5. Error Handling
- Use try/catch in async initializers
- Log errors with context
- Dispatch error events
- Graceful degradation

## Export Pattern Template

```javascript
// Bad (generic, can conflict)
export { manager }

// Good (unique, clear)
export class FormValidator { ... }
export { FormValidator, validateEmail, validatePhone }
```

## Testing & Debugging

Enable debug mode in `init.config.js`:
```javascript
export const CONFIG = {
  debug: true,  // Enables console logs
  site: 'ctc-research',
  version: '1.0.0'
};
```

View app state in console:
```javascript
window.app.debug()
window.APP_STATE?.getState()
```

## Migration Guide

If moving code to this structure:

1. **Utilities** → Move to `utility/helpers.js`
2. **DOM helpers** → Move to `utility/dom.js`
3. **State management** → Move to `utility/state.js`
4. **Feature code** → Create module in `modules/`
5. **Page logic** → Create layout in `pages/`
6. **Themes/Usecases** → Keep in `theme/`
7. **Plugins** → Keep in `plugins/`

## Size Metrics (Current)

- Shared Utilities: ~50KB (minified: ~15KB)
- Theme System: ~20KB (minified: ~6KB)
- Plugins: ~30KB (minified: ~9KB)
- Modules: ~100KB (minified: ~30KB)
- **Total Core: ~200KB (minified: ~60KB)**

Per-site bundles:
- CTC-Research: 172 bundles, 9.8MB
- LMS-Demo: 172 bundles, 11MB
- VResume: 317 bundles, 14MB
