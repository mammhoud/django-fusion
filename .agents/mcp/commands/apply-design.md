---
description: Apply a new SCSS design from Figma
agent: frontend-developer
---
# Apply Design Workflow

You are applying a new Figma design to the Django frontend.

1. Ask the user for the Figma design URL or a description of the changes.
2. **Extract new SCSS variables** (colors, fonts, spacing) and add them to `_variables.scss`.
3. **Create or update component SCSS files** using BEM naming.
4. **Update the main SCSS file** (`main.scss`) to import the new files.
5. **Search for old class names** in templates: `grep -r "old-class" templates/`.
6. **Replace old classes** with new BEM‑compliant ones.
7. **Run `npm run build:css`** (or your SCSS compiler) to generate the final CSS.
8. **Verify** that the new design appears correctly in the browser.
9. **Commit the changes** with a descriptive message.

If the design introduces new components, create a new Wagtail snippet or block for them.