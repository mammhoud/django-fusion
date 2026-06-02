# Shared SCSS usecase layers

The SCSS usecase partials expose BEM shell classes and keep legacy aliases in
place so existing templates and JavaScript selectors continue to work while new
markup can use the organized structure.

- `landing`: `.landing-shell`, `.landing-shell__section`, `.landing-shell__cta`
- `lms`: `.lms-shell`, `.lms-shell__course-card`, `.lms-shell__lesson-list`, `.lms-shell__progress`
- `crm`: `.crm-shell`, `.crm-shell__metric`
- `forms`: `.form-stack`, `.form-stack__field`, `.form-stack__actions`
- `modal`: `.modal-shell`, `.modal-shell__dialog`
- `spa`: `.spa-shell`, `.spa-shell__view`, `.spa-shell__loading`

`lms-demo/assets/static/styles/main.scss` imports the shared theme and these
layers so the LMS demo uses the same theme data as ctc-research.
