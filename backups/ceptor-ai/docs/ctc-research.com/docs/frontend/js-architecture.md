# JavaScript Architecture

## Overview

This document describes the JavaScript module architecture for Alliance. The architecture is designed for modularity, dynamic loading, and centralized configuration.

## Directory Structure

```
assets/static/js/
├── main.js              # Entry point — loads libraries and initializes app
├── app.js               # Application class with core functionality
├── registry.js          # Unified registry for services and infrastructure
├── init.config.js       # Centralized configuration and page detection
├── config.helpers.js    # Logic for layout and page type detection
│
├── utility/             # Core utilities
│   ├── base.manager.js  # Base class for all managers
│   ├── dom.js           # DOM manipulation helpers
│   ├── helpers.js       # General utility functions
│   ├── state.js         # State management
│   └── index.js         # Utility exports
│
├── modules/             # Feature modules
│   ├── manager.init.js  # ModuleManager — handles dynamic module loading
│   ├── index.js         # Module exports
│   ├── components/      # UI components
│   │   ├── manager.init.js  # UIManager — handles UI component lifecycle
│   │   ├── docs/            # Component documentation
│   │   └── index.js
│   ├── handlers/        # Service handlers (Events, Cookies, SSE)
│   ├── forms/           # Form handling logic
│   ├── navigations/     # Navigation tracking
│   └── notifications/   # Notification system (Toast, Alert, SSE)
│
└── plugins/             # Optional plugins
    └── backgroundImages.js
```

---

## Initialization Flow

1. **Browser loads `main.js`**
   - Imports external libraries (jQuery, Bootstrap, AlpineJS, etc.)
   - Imports `CONFIG` from `init.config.js` (starts auto-detection)
   - Imports `app` singleton from `app.js`

2. **DOMContentLoaded**
   - `main.js` calls `initialize()`
   - `app.init()` is called, which:
     - Initializes URL tracking
     - Sets up core event listeners
     - Automatically initializes `uiManager` and `registry`

3. **Registry & Component Discovery**
   - `registry.init()`: Initializes core services — Events, Cookies, SSE
   - `uiManager.init()`: Scans the DOM for components (defined in `UI_COMPONENTS`) and initializes them

---

## Core Managers

### Application (`app.js`)
The main orchestrator. Manages the high-level lifecycle and coordinates between managers.
- **Singleton:** `app`
- **Responsibilities:** Error handling, global event coordination

### RegistryManager (`registry.js`)
Unified registry for infrastructure services.
- **Singleton:** `registry`
- **Core Services:** `events`, `cookies`, `sse`, `notifications`
- **Logic:** Handles dynamic service loading from the `handlers/` directory

### ModuleManager (`modules/manager.init.js`)
Handles dynamic module loading with dependency resolution and retry logic.
- **Singleton:** `moduleManager`
- **Key Methods:** `registerModule()`, `load()`, `getModule()`

### UIManager (`modules/components/manager.init.js`)
Manages the lifecycle of UI components (sliders, tabs, modals, etc.).
- **Singleton:** `uiManager`
- **Key Methods:** `initComponents()`, `refreshAll()`

---

## Configuration

Configuration is centralized in `init.config.js` via the `CONFIG` object:

| Key | Purpose |
|---|---|
| `layout` | Automatic page and layout detection settings |
| `security` | CSRF and cookie configurations |
| `sse` / `notifications` | Real-time update settings |
| `modules` | Dependency maps and loading orders |
| `preloader` | Configuration for the page loading screen |
| `page` | (Runtime) Detected page type and discovered components |

---

## Adding New Features

### Adding a Service
1. Create a handler class in `modules/handlers/`
2. Register it in `registry.js` under the `services` configuration

### Adding a Component
1. Create a component class in `modules/components/`
2. Register it in the `UI_COMPONENTS` map within `modules/components/manager.init.js`
3. Define its CSS selectors for auto-detection

---

## Global Access (Development)

```javascript
window.app         // Application instance
window.registry    // Infrastructure registry
window.uiManager   // UI component manager
window.APP_CONFIG  // Active configuration
```

---

## Further Reading

- [JS Codebase Analysis](./js-codebase.md)
- [Pages Layout System](../../../../docs/ctc-research.com/frontend/pages-layout.md)
- [Preloader Component](./preloader.md)
- [Webpack Configuration](../../../../docs/ctc-research.com/frontend/webpack.md)
