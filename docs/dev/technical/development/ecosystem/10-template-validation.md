# Template Validation Report

This report summarizes the findings from scanning the codebase for dummy data, placeholders, and potential issues.

## Summary
- **Scanned Directories**: `assets/templates`, `apps/templates`, `components`, `layouts`
- **Patterns Searched**: `lorem ipsum`, `dummy`, `temp value`, `foo`, `bar`, `baz`, `TODO`, `FIXME`

## Findings

### High Priority (Lorem Ipsum / Dummy Data)
These files contain placeholder text that should be replaced with real content or dynamic variables.

- **`assets/templates/blog/`**: Multiple files (blog-left-sidebar, blog-details, etc.) contain `lorem ipsum`.
- **`apps/templates/team/sections/team.html`**: Contains `lorem ipsum`.
- **`assets/templates/wagtailadmin/.home.html`**: Contains `dummy` (Likely the task source itself).

### Medium Priority (Placeholder Variable Names)
These files contain `bar`, `foo`, `baz`.
*Note: `bar` was found in many files but inspection suggests it is often part of CSS classes like `header-bar`. However, `foo` is more suspicious.*

- **`assets/templates/500.html`**: Contains `foo`.
- **`assets/templates/blog/*.html`**: Many contain `foo`.
- **`apps/templates/services/services.html`**: Contains `bar` (Verified as CSS class `header-bar`).
- **`apps/templates/common/partials/cart_drawer.html`**: Contains `foo`.
- **`components/profile/*.html`**: Many contain `foo`.

### Low Priority (Todos)
- **`components/profile/notes.html`**: Contains `TODO`.

## Recommendations
1.  **Replace Lorem Ipsum**: Review the blog and team templates and replace placeholder text with appropriate Wagtial tags or static content.
2.  **Investigate 'foo'**: `foo` is highly suspicious and likely a placeholder variable or text.
    - Example: `apps/templates/common/partials/cart_drawer.html`
3.  **Address TODOs**: Check `components/profile/notes.html` and resolve the TODO item.

## Action Taken
- A validation script `validate_templates.py` was created and run to generate this list.
- This report serves as the "confirmation" step for the unchecked templates.
