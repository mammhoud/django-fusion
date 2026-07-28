P/# JavaScript Codebase Analysis

## Overview

This document outlines the structure, flow, and usage of the JavaScript codebase in `assets/static/js`.

---

## Core System

The core system is built around `init.layout.js` (Unified Page & Layout Management System).

### Files

- **`init.layout.js`** — **[USED]** Core file containing `PagesManager`, `BaseLayout`, `LayoutManager`.
  - **Classes:**
    - `PagesManager`: URL, parameters, and page info tracking
    - `BaseLayout`: Parent class for all layouts (notifications, navigation)
    - `LayoutManager`: Handles layout detection and dynamic loading
  - *Restored from `init.layout.orig.js`*

- **`app.js`** — **[USED]** Main application entry point (`Application` class).
  - **Key Methods:**
    - `init()`: Bootstrap application
    - `handleURLChange()`: Route changes
    - `handleError()`: Global error handling

---

## Detailed Method Usage (`init.layout.js`)

### `PagesManager`
| Method | Status | Description |
|---|---|---|
| `initialize(options)` | **[USED]** | Starts URL tracking. Called on DOM ready |
| `getParameter(key, defaultValue)` | **[USED]** | Retrieves URL parameters |
| `setParameter(key, value)` | **[USED]** | Sets URL parameters and updates the URL |
| `updateURL()` | **[USED]** | Syncs state to the browser URL bar |
| `extractPageInfo()` | **[USED]** | Reads metadata from the DOM |

### `BaseLayout`
| Method | Status | Description |
|---|---|---|
| `init()` | **[USED]** | Initializer for layout systems |
| `apply(layoutType, data)` | **[USED]** | Applies specific layout configuration and classes |
| `showNotification(msg, type)` | **[USED]** | Displays UI notifications |
| `createFallbackNotificationSystem()` | **[FALLBACK]** | Only used if no other system exists |

### `LayoutManager`
| Method | Status | Description |
|---|---|---|
| `initialize(app)` | **[USED]** | Detects and loads the initial layout |
| `detectLayout()` | **[USED]** | Determines the current layout from URL/DOM |
| `loadLayout(name)` | **[USED]** | Dynamically imports and instantiates layout files |
| `switchLayout(name)` | **[USED]** | Unloads current layout and loads a new one |

### Other Core Files

- **`main.js`** — **[USED]** Webpack entry point. Imports libraries and initializes `app.js`
- **`static.js`** — **[USED]** Bundle entry point. Imports CSS and `main.js`
- **`init.config.js`** — **[USED]** Configuration settings (`CONFIG` object)

---

## Layouts (`pages/`)

All layouts extend `BaseLayout` from `init.layout.js`.

| File | Status | Description |
|---|---|---|
| `app.layout.js` | **[USED]** | Main dashboard/app layout. Handles sidebar, panels, widgets |
| `auth.layout.js` | **[USED]** | Authentication pages (login, register) |
| `landing.layout.js` | **[USED]** | Public landing pages |
| `profile.layout.js` | **[USED]** | User profile pages |
| `notifications.layout.js` | **[USED]** | Notification handling |
| `init.layout.orig.js` | **[BACKUP]** | Backup — not used in production |

---

## Utilities (`utility/`)

| File | Status | Description |
|---|---|---|
| `base.manager.js` | **[USED]** | Base class for managers |
| `dom.js` | **[USED]** | DOM manipulation helpers (`DOM` object) |
| `helpers.js` | **[USED]** | General utilities (`Utils` object) |
| `url.js` | **[USED]** | URL tracking mixin |
| `app.metrics.js` | **[USED]** | Performance metrics |

---

## Modules (`modules/`)

Structured module system.
- `index.js`: Exports `moduleManager`

---

## Application Flow

```
Browser → static.js → main.js → app.init()
                                    ↓
                            init.layout.js (auto-init on DOM ready)
                                    ↓
                            layoutManager.detectLayout()
                                    ↓
                            layoutManager.loadLayout('app' | 'auth' | ...)
                                    ↓
                            layout.init() → layout.apply()
```

---

## Cleanup Candidates

| File | Status | Reason |
|---|---|---|
| `init.layout.orig.js` | **[NOT USED]** | Backup of `init.layout.js` |
| `_init.js` | **[NOT USED]** | Empty file — likely legacy entry point |
| `_init.orig.js` | **[NOT USED]** | Legacy jQuery/plugin initializations |

---

## Further Reading

- [JS Architecture Overview](./js-architecture.md)
- [Pages Layout System](./pages-layout.md)
- [Webpack Configuration](./webpack.md)
