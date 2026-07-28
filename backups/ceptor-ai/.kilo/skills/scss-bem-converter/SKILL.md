---
name: scss-bem-converter
description: Convert plain CSS or non‑BEM SCSS to BEM‑compliant SCSS. Use this when the user provides a new design or asks to refactor existing styles.
---
# SCSS BEM Converter Skill

You are a frontend expert specialising in BEM (Block, Element, Modifier) naming.

## BEM Rules
- **Block**: The component name (e.g., `.card`, `.button`).
- **Element**: A child of the block (e.g., `.card__title`, `.button__icon`).
- **Modifier**: A variation of the block or element (e.g., `.card--large`, `.button__icon--small`).

## Conversion Process
1. Identify all top‑level selectors in the provided CSS.
2. For each selector:
   - If it's a component (e.g., `.hero`), treat it as a Block.
   - Move all nested selectors into Elements or Modifiers.
   - Use `&` for nesting in SCSS.
3. Update the HTML templates to use the new BEM classes.
4. Remove any ID‑based styling.
5. Ensure all variables are defined in `_variables.scss`.

## Example
**Before** (non‑BEM):
```css
.hero { background: blue; }
.hero h1 { color: white; }
.hero .button { padding: 10px; }
After (BEM):

.hero {
  background: blue;
  &__title { color: white; }
  &__button { padding: 10px; }
}
Output
Provide the new SCSS file content.
List the corresponding HTML changes needed.
If multiple components are involved, create separate SCSS files per component.
