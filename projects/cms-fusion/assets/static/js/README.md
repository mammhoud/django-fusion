# JavaScript Codebase Analysis

## Overview
This document outlines the structure, flow, and usage of the JavaScript codebase in `assets/static/js`.

## Core System
The core system is built around `init.layout.js` (Unified Page & Layout Management System).

### Files
- **`init.layout.js`**: **[USED]** Core file containing `PagesManager`, `BaseLayout`, `LayoutManager`.
  - **Classes**:
    - `PagesManager`: URL, parameters, and page info tracking.
    - `BaseLayout`: Parent class for all layouts (notifications, navigation).
    - `LayoutManager`: Handles layout detection and dynamic loading.
  - *Restored from `init.layout.orig.js`.*

- **`app.js`**: **[USED]** Main application entry point (`Application` class).
  - **Classes**:
    - `Application`: Core application instance.
  - **Key Methods**:
    - `init()`: Bootstrap application.
    - `handleURLChange()`: Route changes.
    - `handleError()`: Global error handling.

## Detailed Method Usage (init.layout.js)

### `PagesManager`
- `initialize(options)`: **[USED]** Starts URL tracking. Called on DOM ready.
- `getParameter(key, defaultValue)`: **[USED]** Retrieves URL parameters.
- `setParameter(key, value)`: **[USED]** Sets URL parameters and updates the URL.
- `updateURL()`: **[USED]** Syncs state to the browser URL bar.
- `extractPageInfo()`: **[USED]** Reads metadata from the DOM.

### `BaseLayout`
- `init()`: **[USED]** Initializer for layout systems (notifications, navigation).
- `apply(layoutType, data)`: **[USED]** Applies the specific layout configuration and classes.
- `showNotification(msg, type)`: **[USED]** Displays UI notifications.
- `createFallbackNotificationSystem()`: **[FALLBACK - # not used]** Only used if no other system exists.

### `LayoutManager`
- `initialize(app)`: **[USED]** Detects and loads the initial layout.
- `detectLayout()`: **[USED]** Logic to determine the current layout from URL/DOM.
- `loadLayout(name)`: **[USED]** Dynamically imports and instantiates layout files.
- `switchLayout(name)`: **[USED]** Unloads current layout and loads a new one.

- **`main.js`**: **[USED]** Entry point for webpack/build. Imports libraries (Bootstrap, jQuery, etc.) and initializes `app.js`.
- **`static.js`**: **[USED]** Bundle entry point. Imports CSS and `main.js`.
- **`init.config.js`**: **[USED]** Configuration settings (`CONFIG` object).

## Layouts `pages/`
All layouts extend `BaseLayout` from `init.layout.js`.

- **`app.layout.js`**: **[USED]** Main dashboard/app layout. Handles sidebar, panels, widgets.
- **`auth.layout.js`**: **[USED]** Authentication pages (login, register).
- **`landing.layout.js`**: **[USED]** Public landing pages.
- **`profile.layout.js`**: **[USED]** User profile pages.
- **`notifications.layout.js`**: **[USED]** Notification handling.
- **`init.layout.orig.js`**: **[BACKUP]** Backup of `init.layout.js`. **[NOT USED IN PRODUCTION]**

## Utilities `utility/`
- **`base.manager.js`**: **[USED]** Base class for managers.
- **`dom.js`**: **[USED]** DOM manipulation helpers (`DOM` object).
- **`helpers.js`**: **[USED]** General utilities (`Utils` object).
- **`url.js`**: **[USED]** URL tracking mixin.
- **`app.metrics.js`**: **[USED]** Performance metrics.

## Modules `modules/`
Structured module system.
- `index.js`: Exports `moduleManager`.

## Flow
1. **Entry**: Browser loads `static.js` (via script tag).
2. **Bootstrap**: `main.js` runs, imports dependent libraries.
3. **Init**: `main.js` calls `app.init()` from `app.js`.
4. **Layout**:
   - `init.layout.js` auto-initializes `pagesManager` and `layoutManager` on DOM ready.
   - `layoutManager` detects the current layout (e.g., 'app', 'auth') based on URL/DOM.
   - It dynamically loads the corresponding layout file (e.g., `app.layout.js`).
   - The specific layout is instantiated and `init()`/`apply()` methods are called.

## Unused / Cleanup Candidates
- **`init.layout.orig.js`**: **[MARKED # not used]** Backup of `init.layout.js`.
- **`_init.js`**: **[MARKED # not used]** Empty file, likely legacy entry point.
- **`_init.orig.js`**: **[MARKED # not used]** Contains legacy jQuery/plugin initializations.


