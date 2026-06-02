# Shared SCSS usecase layers

The SCSS usecase partials expose BEM shell classes and keep legacy aliases in
place so existing templates and JavaScript selectors continue to work while new
markup can use the organized structure. Every partial in this directory has a
matching JavaScript module under `assets/static/js/usecases/<name>/index.js` so
webpack can bundle behavior and styles through the same naming contract.

| SCSS partial | JS module | Primary hooks | Purpose |
| --- | --- | --- | --- |
| `_animations.scss` | `animations/index.js` | `.usecase-animate`, `[data-animate]` | Cross-site reveal/fade/scale/slide animation utilities. |
| `_landing.scss` | `landing/index.js` | `.landing-shell`, `.landing-shell__section`, `.landing-shell__cta` | Landing and marketing page wrappers. |
| `_lms.scss` | `lms/index.js` | `.lms-shell`, `.lms-shell__course-card`, `.lms-shell__lesson-list`, `.lms-shell__progress` | Learning/course surfaces shared by LMS-enabled sites. |
| `_crm.scss` | `crm/index.js` | `.crm-shell`, `.crm-shell__metric` | CRM and dashboard metric surfaces. |
| `_forms.scss` | `forms/index.js` | `.form-stack`, `.form-stack__field`, `.form-stack__actions` | Form layouts and action rows. |
| `_modal.scss` | `modal/index.js` | `.modal-shell`, `.modal-shell__dialog` | Dialog and modal shell sizing. |
| `_spa.scss` | `spa/index.js` | `.spa-shell`, `.spa-shell__view`, `.spa-shell__loading` | SPA/fragment layout and loading surfaces. |

The root `assets/static/styles/main.scss` imports this index for shared/base
sites. `ctc-research`, `lms-demo`, and `VResume` also import these layers, so the
same hooks are available across all three websites.
