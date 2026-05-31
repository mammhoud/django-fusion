# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.1] - 2026-05-24

### Fixed
- **Slider Navigator**: Fixed duplicate `refreshAll()` method that shadowed the async destroy+reinit version, causing slides to not re-initialize after HTMX navigation
- **Slider Swiper Dual-loading**: Added early-return in `loadDependencies()` when Swiper is already bundled via Webpack (avoids wasted CDN fallback)
- **Sidebar Toggle (Mobile)**: Added `sidebar--active` class toggle to expand parent `max-height` — sidebar content was clipped at 180px even when `.sidebar__more.open` expanded
- **Unified Modal Display**: Fixed component never initializing — selectors `[data-modal-trigger]`/`[data-htmx-modal]` didn't match any DOM elements. Added `#unified-modal-overlay` and `[data-modal-overlay]` to selectors
- **Unified Modal Close**: Modal now clears stale content from container on close
- **Preloader Memory Leak**: `showHTMXPreloader()` now removes stale Map entries before creating new ones, with `requestAnimationFrame` for proper transition
- **Tag Filter Listener Leak**: Fixed `bindEvents()` using anonymous arrow functions that couldn't be cleaned up. Now uses stored bound handler references
- **DOM Cache Fragmentation**: Removed duplicate `clearCache()`/`invalidateCache()` methods that appeared twice in dom.js
- **DOM Global Access**: `window.DOM` now always available (was conditional on `CONFIG.debug`), fixing cache invalidation failing in production
- **Component Double-init Guard**: Added `data-{componentId}-init` marker to prevent duplicate component instances on HTMX swaps
- **N+1 Database Queries**: Added `select_related`/`prefetch_related` to blog and project detail views
- **Cookie Consent**: SessionStorage tracking ensures dialog shows only once per browsing session
- **Theme Hover Colors**: Replaced hardcoded `rgba(238, 155, 0, ...)` with `var(--color-accent-rgb)` for theme-adaptive hover effects
- **Documentation**: Fixed Tailwind CSS v4 reference → correct Bootstrap 5/SCSS stack in architecture docs

### Removed
- **Dead Files (10)**: bootbox-manager.js, countdown.js, maps.js, language.js, skills-counter.js, cursor.js, fullscreen.js, parallax.js, form-handler.js, validation.js (~60KB dead code deleted)
- **Dead Code**: `setupThemeToggle()` function (no `data-theme-toggle` elements exist), `CookiePreferencesManager` class, `initHTMXFallback()` function, `APP_SUB_TYPES` deprecated alias, `componentRegistry` and helper functions, dead comment-only `modals/index.js` and `navigation/index.js`, "Application is ready!" toast notification
- **Stale Exports**: Removed references to deleted files from `misc/index.js`, `services/index.js`

### Added
- `.env.example` file with safe defaults for new contributors

### Updated Known Issues
- ~~🔴 Slider not re-initializing after HTMX tab switch~~ (Fixed in 1.1.1)
- ~~🟡 Memory leak in preloader map~~ (Fixed in 1.1.1)
- ~~🟡 Form listener cleanup has reference mismatch~~ (Fixed in 1.1.1)
- 🟡 Preloader progress tracking still broken for HTMX requests (requires migration to `htmx:xhr:loadstart/loadend` events)

---

## [1.1.0] - 2026-05-23

### Added
- **Shared Filter Component**: Unified `filter_form.html` for blog and portfolio (replaces duplicate filter templates)
- **Tag Filtering**: Active/inactive tag visibility system for portfolio projects
- **Preloader System**: Multi-type preloader with HTMX request support (3 preset styles)
- **Infinite Scroll**: HTMX-powered pagination for blog and portfolio listings
- **Component Re-initialization**: Automatic component detection and initialization on page load

### Changed
- **Template Structure**: Blog and portfolio now use shared filter form component
- **Fragment System**: Unified HTMX fragment pattern across all tabs for consistency
- **Slider Component**: Migrated to dynamic Swiper.js CDN loading with responsive breakpoints
- **Context Flow**: Improved context data passing for HTMX requests

### Fixed
- HTML structure: Corrected unclosed tags in portfolio modals
- Fragment template rendering: Proper nesting in all section partials
- Modal content: Fixed broken closing `</div>` elements in project detail template

### Deprecated
- ⚠️ `pages/templates/blog/sections/filter.html` (replaced by shared component)
- ⚠️ `pages/templates/portfolio/sections/filter.html` (replaced by shared component)

### Documentation
- ❌ **Missing**: Changelog not maintained in previous versions
- ❌ **Missing**: Tag filtering behavior documentation
- ❌ **Missing**: Preloader configuration guide
- ❌ **Missing**: HTMX component lifecycle documentation

### Known Issues
- 🔴 **Slider not re-initializing after HTMX tab switch** — Workaround: Manual component re-init on HTMX event
- 🟡 **Preloader progress tracking broken for HTMX requests** — Uses XHR events, not fetch API
- 🟡 **Memory leak in preloader map** — `htmxPreloaders` Map grows unbounded after many tab switches
- 🟡 **Form listener cleanup has reference mismatch** — `.removeEventListener()` calls won't actually clean up

### Migration Guide

#### From 1.0.x to 1.1.0

**Breaking Changes**: None

**Recommendations**:
1. Clear browser cache (static file versions may have changed)
2. Run database migrations: `make migrate`
3. Rebuild frontend assets: `make frontend-production`
4. Redeploy Celery workers for background tasks

**Template Updates** (if custom templates):
- If you extended `blog/sections/filter.html` or `portfolio/sections/filter.html`, migrate to using `components/search/filter_form.html`
- Fragment templates now require `storage_key` and `persist` parameters

---

## [1.0.3] - 2026-04-15

### Added
- Enhanced form validation with HTMX indicators
- Newsletter subscription management
- Contact form with server-side validation

### Fixed
- CSS specificity issues in Bootstrap overrides
- Form submission error handling

---

## [1.0.2] - 2026-03-20

### Added
- Multi-language support (i18n)
- Dark/light theme toggle
- GDPR cookie consent

### Fixed
- Theme persistence in localStorage
- Cookie banner display logic

---

## [1.0.1] - 2026-02-10

### Fixed
- Responsive layout issues on mobile
- Image lazy loading
- Navigation accessibility

---

## [1.0.0] - 2026-01-01

### Added
- Initial VResume release
- Django + Wagtail CMS integration
- HTMX for dynamic page interactions
- Portfolio with project filtering
- Blog with categories and search
- Resume timeline sections
- Contact form with email notifications
- Newsletter double opt-in
- Admin panel with Wagtail CMS

---

## Unreleased (Development)

### Planned Features
- [ ] Page-specific JavaScript code splitting
- [ ] WebP image format support
- [ ] Critical CSS inlining for faster first paint
- [ ] Type hints for Python models (mypy compatibility)
- [ ] Enhanced test coverage (target: 85%+)
- [ ] Analytics dashboard for editors
- [ ] Advanced component marketplace

### Known Limitations
- Max 5000 projects before pagination optimization needed
- Single Redis instance (no cluster support)
- Email delivery via Celery (no real-time guarantee)
- No API versioning for potential future REST API

---

## Guidelines for Future Releases

### When Adding Features
1. Update this file with `[Unreleased]` section
2. Include section: Added, Changed, Fixed, Deprecated, Removed
3. Add breaking changes clearly with ⚠️
4. Document migration steps for breaking changes

### Before Release
1. Move `[Unreleased]` to version number with date
2. Create release notes in `docs/releases/v{VERSION}.md`
3. Update `v1/__about__.py` version
4. Create Git tag: `git tag v1.1.0`
5. Update `README.md` version badge

### Semantic Versioning
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

**Example**:
- 1.0.0 → 1.1.0: Added tag filtering feature
- 1.1.0 → 1.1.1: Fixed preloader memory leak
- 1.1.0 → 2.0.0: Removed deprecated filter templates (breaking)
