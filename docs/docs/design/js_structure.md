# VResume JavaScript Structure - Reorganized

## Overview

The JavaScript codebase has been reorganized into a clean, modular structure with clear separation of concerns. All files have been consolidated, duplicates removed, and naming standardized.

## Directory Structure

```
/js/
├── index.js                    # Main entry point - exports all modules
├── STRUCTURE.md               # This file
│
├── core/                      # Core application files
│   ├── index.js              # Core exports
│   ├── app.js                # Application class & lifecycle
│   ├── config.js             # Global configuration & helpers
│   ├── registry.js           # Service & module registry
│   └── main.js               # Entry point with library loading
│
├── lib/                       # Utility libraries
│   ├── index.js              # Library exports
│   ├── base-manager.js       # Base class for all managers
│   ├── dom.js                # DOM manipulation utilities
│   ├── helpers.js            # 100+ utility functions
│   └── url.js                # URL tracking & History API
│
├── services/                  # Service handlers
│   ├── index.js              # Service exports & registry
│   ├── cookies.js            # Cookie management & CSRF
│   ├── events.js             # Window event handling
│   ├── sse.js                # Server-Sent Events
│   └── notifications.js      # Notification system
│
├── modules/                   # Module system
│   ├── index.js              # Module API & exports
│   ├── manager.js            # Module loader & manager
│   └── loader.js             # Module loading logic
│
├── components/                # UI Components
│   ├── index.js              # Component registry & exports
│   ├── manager.js            # UIManager for component lifecycle
│   ├── orchestrator.js       # VResumeComponent orchestrator
│   │
│   ├── core/                 # Core UI components
│   │   ├── sidebar.js        # Sidebar toggle
│   │   ├── modal.js          # Modal dialogs
│   │   ├── tabs.js           # Tab navigation
│   │   ├── accordion.js      # Accordion sections
│   │   └── progress.js       # Progress bars
│   │
│   ├── forms/                # Form components
│   │   ├── form-handler.js   # Generic form handler
│   │   ├── contact-form.js   # Contact form component
│   │   └── validation.js     # Form validation utilities
│   │
│   ├── media/                # Media components
│   │   ├── lightbox.js       # Lightbox gallery
│   │   ├── sliders.js        # Swiper sliders
│   │   ├── images.js         # Image handling
│   │   └── masonry.js        # Masonry layout
│   │
│   ├── effects/              # Visual effects
│   │   ├── animations.js     # AOS animations
│   │   ├── parallax.js       # Parallax effects
│   │   ├── cursor.js         # Custom cursor
│   │   ├── preloader.js      # Loading preloader
│   │   └── fullscreen.js     # Fullscreen mode
│   │
│   └── misc/                 # Miscellaneous components
│       ├── portfolio-filter.js
│       ├── testimonials.js
│       ├── language.js
│       ├── maps.js
│       ├── counter.js
│       └── countdown.js
│
└── navigation/                # Navigation system
    ├── index.js              # Navigation exports
    └── tracker.js            # Navigation tracker
```

## File Organization Changes

### Consolidation
- ✅ Merged `init.config.js` into `core/config.js`
- ✅ Moved `modules.manager.js` → `modules/manager.js`
- ✅ Moved `modules.index.js` → `modules/index.js`
- ✅ Renamed `base.manager.js` → `lib/base-manager.js`
- ✅ Removed `cookie-popup-manager.js` (unused)
- ✅ Removed `modal-handler.js` (consolidated)

### Standardization
- ✅ Removed `.init.js` suffix from all files
- ✅ Standardized naming: `sidebar.init.js` → `core/sidebar.js`
- ✅ Consistent file naming across all components

### Reorganization
- ✅ Core files → `core/` directory
- ✅ Utilities → `lib/` directory
- ✅ Services → `services/` directory
- ✅ Components organized by type:
  - `core/` - Core UI components
  - `forms/` - Form-related components
  - `media/` - Media & gallery components
  - `effects/` - Visual effects & animations
  - `misc/` - Miscellaneous components

## Import Path Changes

### Before
```javascript
import { CONFIG } from './init.config.js';
import { app } from './app.js';
import SidebarComponent from './modules/components/sidebar.init.js';
import { DOM } from './utility/dom.js';
```

### After
```javascript
import { CONFIG } from './core/config.js';
import { app } from './core/app.js';
import { SidebarComponent } from './components/core/sidebar.js';
import { DOM } from './lib/dom.js';

// Or use the main index
import { CONFIG, app, SidebarComponent, DOM } from './index.js';
```

## Module Exports

### Core Module
```javascript
import { 
    Application, 
    createApp, 
    app,
    CONFIG, 
    ConfigHelpers,
    RegistryManager,
    registry
} from './core/index.js';
```

### Libraries
```javascript
import { 
    BaseManager,
    DOM,
    Utils,
    debounce,
    throttle,
    URLTrackerMixin
} from './lib/index.js';
```

### Services
```javascript
import { 
    CookieManagerHandler,
    EventManagerHandler,
    SSEHandler,
    NotificationSystem,
    registerService,
    getService
} from './services/index.js';
```

### Components
```javascript
import { 
    SidebarComponent,
    ModalComponent,
    TabsComponent,
    FormHandler,
    LightboxComponent,
    AnimationsComponent,
    UIManager,
    VResumeComponent,
    registerComponent,
    getComponent
} from './components/index.js';
```

### Navigation
```javascript
import { 
    NavigationTracker,
    navigationTracker
} from './navigation/index.js';
```

## Key Features

### 1. Clean Separation of Concerns
- **Core**: Application lifecycle and configuration
- **Lib**: Reusable utilities and helpers
- **Services**: External integrations and handlers
- **Modules**: Module loading system
- **Components**: UI components organized by type
- **Navigation**: Navigation tracking and management

### 2. Standardized Naming
- All files use lowercase with hyphens: `sidebar.js`, `form-handler.js`
- Consistent suffixes removed (no more `.init.js`)
- Clear categorization by directory

### 3. Centralized Exports
- Each directory has an `index.js` for clean imports
- Main `index.js` exports everything
- Component registry for dynamic access

### 4. No Duplicates
- Removed backward compatibility wrappers
- Consolidated overlapping functionality
- Single source of truth for each feature

### 5. Enhanced Documentation
- Clear directory structure
- Organized by functionality
- Easy to locate and maintain code

## Migration Guide

### For Existing Code

1. **Update imports from root level**
   ```javascript
   // Old
   import { CONFIG } from './init.config.js';
   
   // New
   import { CONFIG } from './core/config.js';
   // Or
   import { CONFIG } from './index.js';
   ```

2. **Update component imports**
   ```javascript
   // Old
   import SidebarComponent from './modules/components/sidebar.init.js';
   
   // New
   import { SidebarComponent } from './components/core/sidebar.js';
   // Or
   import { SidebarComponent } from './components/index.js';
   ```

3. **Update utility imports**
   ```javascript
   // Old
   import { DOM } from './utility/dom.js';
   
   // New
   import { DOM } from './lib/dom.js';
   // Or
   import { DOM } from './lib/index.js';
   ```

## Statistics

| Category | Count | Status |
|----------|-------|--------|
| Core files | 4 | ✅ Organized |
| Library files | 5 | ✅ Organized |
| Service files | 4 | ✅ Organized |
| Module files | 3 | ✅ Organized |
| Component files | 26 | ✅ Organized |
| Navigation files | 2 | ✅ Organized |
| **Total** | **44** | ✅ Complete |

## Removed Files

- ✅ `init.config.js` - Merged into `core/config.js`
- ✅ `modules.manager.js` - Moved to `modules/manager.js`
- ✅ `modules.index.js` - Moved to `modules/index.js`
- ✅ `cookie-popup-manager.js` - Unused
- ✅ `modal-handler.js` - Consolidated into `core/modal.js`

## Next Steps

1. **Update all import statements** in HTML files and other JS files
2. **Test all components** to ensure functionality
3. **Update build configuration** if using bundlers
4. **Update documentation** with new import paths
5. **Consider lazy-loading** components for performance

## Benefits

✅ **Cleaner codebase** - Organized by functionality
✅ **Easier maintenance** - Clear file locations
✅ **Better discoverability** - Logical directory structure
✅ **No duplicates** - Single source of truth
✅ **Standardized naming** - Consistent conventions
✅ **Improved imports** - Centralized exports
✅ **Better scalability** - Easy to add new components

## Questions?

Refer to the individual module documentation or check the component files for detailed comments and usage examples.


## Defined vs Undefined JS References

To avoid `ReferenceError: <name> is not defined`, these globals are intentionally available at runtime:

- `window.uiManager`: initialized by the component manager bootstrap and used by dynamic components after HTMX swaps.
- `window.htmx`: provided by HTMX script include and used for request lifecycle hooks.
- `window.Swiper`: loaded by slider dependency loader when not pre-bundled.
- `window.SlidersManager`: optional fallback singleton used only when UI manager refresh is unavailable.

Rules for docs and code examples:

1. Prefer module imports over globals when possible.
2. If a global is required, guard it with optional chaining or existence checks (e.g. `window.htmx?.process(...)`).
3. Do not reference undeclared names in examples; use `window.<name>` for explicit globals.
