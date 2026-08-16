# Customizer SPA-style navigation

The customizer uses small HTMX fragments instead of replacing the entire page.
Navigation controls should request a fragment with `hx-get`, render it into a
stable container with `hx-target`, and choose the replacement strategy with
`hx-swap`.

```html
<button hx-get="/cypercloud/fragments/page-card-grid/precis-ctc/"
        hx-target="#customizer-page-grid"
        hx-swap="innerHTML"
        hx-push-url="/cypercloud/websites/precis-ctc/pages/">
  CTC Research
</button>
```

Use `hx-push-url` when the fragment represents a navigable state that should be
bookmarkable, such as the selected website page grid. Omit it for local state
changes, such as expanding the section list inside a single page card.

The currently supported fragments are:

- page navigator: `/cypercloud/fragments/page-navigator/`
- page card grid: `/cypercloud/fragments/page-card-grid/<website_slug>/`
- page section list: `/cypercloud/fragments/page-section-list/<website_slug>/<page_path>/`
- message send result: `/cypercloud/fragments/message-send-result/`
