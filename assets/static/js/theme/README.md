# Shared JavaScript usecase registry

These modules group frontend behavior by product usecase instead of by source
website. The same bundle is consumed by `ctc-research`, `lms-demo`, and
`VResume` through the shared webpack `static` entry.

Every module name mirrors a Sass partial in `assets/static/styles/usecases`:

| Usecase | JS module | SCSS partial | BEM/data hook | Related websites | Purpose |
| --- | --- | --- | --- | --- | --- |
| `animations` | `animations/index.js` | `_animations.scss` | `.usecase-animate`, `[data-animate]` | all sites | IntersectionObserver-based reveal animation utilities. |
| `lms` | `lms/index.js` | `_lms.scss` | `.lms-shell`, `data-usecase="lms"` | `lms-demo`, `ctc-research` | Course cards, lesson lists, LMS progress, and theme integration. |
| `landing` | `landing/index.js` | `_landing.scss` | `.landing-shell`, `data-usecase="landing"` | `lms-demo`, `ctc-research` | Marketing pages, headers, CTA sections, and newsletter blocks. |
| `crm` | `crm/index.js` | `_crm.scss` | `.crm-shell`, `data-usecase="crm"` | all sites | Dashboard/customer relationship surfaces. |
| `forms` | `forms/index.js` | `_forms.scss` | `.form-stack`, `data-usecase="forms"` | all sites | Shared validation-ready form layouts. |
| `modal` | `modal/index.js` | `_modal.scss` | `.modal-shell`, `data-usecase="modal"` | all sites | Modal/dialog sizing and integration hooks. |
| `spa` | `spa/index.js` | `_spa.scss` | `.spa-shell`, `data-usecase="spa"` | `VResume`, app layouts | Single-page/fragment navigation and loading states. |

The non-animation modules mark initialized shells with `data-usecase-ready` so
JavaScript, SCSS, and templates use one unified class/data-hook vocabulary.

## Website overrides

Each website can define `window.STRUCTA_USECASE_CONFIG` from its site asset entry
before the shared webpack `static` entry runs. Components can be disabled with
`{ enabled: false }`, enabled with `true`, or overridden with `selectors` and
`options` at either `components[componentId]` or
`usecases[usecase].components[componentId]`.
