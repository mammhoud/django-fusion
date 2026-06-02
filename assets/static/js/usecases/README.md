# Shared JavaScript usecase registry

These modules group frontend behavior by product usecase instead of by source
website. The same bundle is consumed by `ctc-research`, `lms-demo`, and
`VResume` through the shared webpack `static` entry.

| Usecase | BEM/data hook | Related websites | Purpose |
| --- | --- | --- | --- |
| `lms` | `.lms-shell`, `data-usecase="lms"` | `lms-demo`, `ctc-research` | Course cards, lesson lists, LMS progress, and theme integration. |
| `landing` | `.landing-shell`, `data-usecase="landing"` | `lms-demo`, `ctc-research` | Marketing pages, headers, CTA sections, and newsletter blocks. |
| `crm` | `.crm-shell`, `data-usecase="crm"` | all sites | Dashboard/customer relationship surfaces. |
| `forms` | `.form-stack`, `data-usecase="forms"` | all sites | Shared validation-ready form layouts. |
| `modal` | `.modal-shell`, `data-usecase="modal"` | all sites | Modal/dialog sizing and integration hooks. |
| `spa` | `.spa-shell`, `data-usecase="spa"` | `VResume`, app layouts | Single-page/fragment navigation and loading states. |

Each module marks initialized shells with `data-usecase-ready` so JavaScript,
SCSS, and templates use one unified class/data-hook vocabulary.
