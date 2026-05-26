# SCSS Migration Guide

## Overview
This guide documents the migration of all inline CSS styles to SCSS files using master color variables from `_master.scss`.

## Color Variables Reference

All color variables are defined in `assets/static/styles/colors/_master.scss` and are organized by category:

### Primary Colors
- `--theme-primary`: #0056b3 (Deep accessible blue)
- `--theme-primary-dark`: #003d80 (Darker blue for hover/active)
- `--theme-primary-light`: #1a7fd4 (Lighter blue for accents)
- `--theme-primary-lighter`: #cce0ff (Very light blue for backgrounds)

### Secondary Colors
- `--theme-secondary`: #008080 (True teal)
- `--theme-secondary-dark`: #006D6D (Deep teal)
- `--theme-secondary-light`: #4DB3B3 (Light teal)

### Accent Colors
- `--theme-accent`: #6C63FF (Vibrant purple-blue)
- `--theme-accent-alt`: #FF6B8B (Vibrant coral pink)

### Background Colors
- `--theme-bg-primary`: #FFFFFF (Primary background)
- `--theme-bg-secondary`: #F5F7FA (Secondary background)
- `--theme-bg-tertiary`: #EBEFF5 (Tertiary background)

### Text Colors
- `--color-text-primary`: #1a1a1a (High contrast charcoal)
- `--color-text-secondary`: #3d3d3d (Medium contrast dark gray)
- `--color-text-tertiary`: #5c5c5c (Lower contrast gray)
- `--color-text-heading`: #1a1a1a (Heading text)
- `--color-text-body`: #3d3d3d (Body text)
- `--color-text-muted`: #767676 (Muted text)

### Border Colors
- `--color-card-border`: #d0d7de (Primary border)
- `--color-input-border`: #d0d7de (Input border)
- `--color-input-border-focus`: #0056b3 (Focused input border)

### State Colors
- `--color-success`: #10B981 (Vibrant green)
- `--color-warning`: #F59E0B (Vibrant amber)
- `--color-error`: #EF4444 (Vibrant red)
- `--color-info`: #3B82F6 (Vibrant blue)

### Shadow Variables
- `--theme-shadow`: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
- `--theme-shadow-md`: 0 6px 12px -2px rgba(0, 0, 0, 0.1)
- `--theme-shadow-lg`: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
- `--color-shadow-light`: rgba(0, 0, 0, 0.05)
- `--color-shadow-medium`: rgba(0, 0, 0, 0.1)

## SCSS Files Created

### 1. `_progress.scss`
Styles for progress bars, circular progress, and progress steps.

**Classes:**
- `.progress` - Basic progress bar
- `.progress-bar` - Progress bar fill
- `.progress-circle` - Circular progress indicator
- `.progress-steps` - Step-based progress

**Usage:**
```html
<div class="progress" style="height: 6px;">
  <div class="progress-bar" style="width: 75%"></div>
</div>
```

**SCSS:**
```scss
.progress {
  height: 6px;
  background-color: var(--color-course-progress-bg);
  border-radius: 3px;
}

.progress-bar {
  background-color: var(--color-course-progress-fill);
}
```

### 2. `_notes.scss`
Styles for notes components including note cards, editor, and search.

**Classes:**
- `.notes` - Notes container
- `.note-card` - Individual note card
- `.note-editor` - Note editing form
- `.note-modal` - Note modal dialog
- `.note-search` - Note search component

**Usage:**
```html
<div class="note-card">
  <h3 class="note-card__title">Note Title</h3>
  <p class="note-card__content">Note content here...</p>
</div>
```

### 3. `_profile.scss`
Styles for profile components including profile cards, settings, and modals.

**Classes:**
- `.profile` - Main profile container
- `.profile-card` - Profile card component
- `.profile-settings` - Settings form
- `.profile-modal` - Profile modal
- `.profile-badge` - Badge component
- `.avatar` - Avatar image sizes

**Usage:**
```html
<div class="profile">
  <div class="profile__header">
    <img class="avatar-lg" src="..." alt="Avatar">
  </div>
</div>
```

### 4. `_modals.scss`
Styles for modal dialogs including profile image upload, messaging, and sharing.

**Classes:**
- `.modal` - Modal container
- `.modal-content` - Modal content
- `.modal-header` - Modal header
- `.modal-body` - Modal body
- `.modal-footer` - Modal footer
- `.upload-zone` - File upload area
- `.share-profile-preview` - Profile share preview

**Usage:**
```html
<div class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h5 class="modal-title">Modal Title</h5>
    </div>
    <div class="modal-body">Content here</div>
  </div>
</div>
```

### 5. `_contact.scss`
Styles for contact components including maps, forms, and contact info.

**Classes:**
- `.contact__map` - Contact map container
- `.contact-card-section` - Contact card section
- `.contact-section__form` - Contact form
- `.contact-info` - Contact information
- `.contact-method` - Contact method item

**Usage:**
```html
<div class="contact__map">
  <iframe src="..." style="width: 100%; height: 500px;"></iframe>
</div>
```

**SCSS:**
```scss
.contact__map {
  iframe {
    width: 100%;
    height: 500px;
    border: none;
  }
}
```

### 6. `_content.scss`
Styles for content components including paragraphs, headings, quotes, and rich text.

**Classes:**
- `.paragraph-content` - Paragraph styling
- `.heading-block` - Heading styling
- `.block-quote` - Block quote styling
- `.richtext-block` - Rich text content
- `.page-title` - Page title
- `.page-link` - Page link button
- `.stat-card` - Statistics card

**Usage:**
```html
<div class="paragraph-content">
  <p>Paragraph text here...</p>
</div>
```

## Migration Steps

### Step 1: Remove Inline Styles from HTML
Replace inline `style` attributes with CSS classes.

**Before:**
```html
<div style="width: 100%; height: 500px; border: 0;">
  <iframe src="..."></iframe>
</div>
```

**After:**
```html
<div class="contact__map">
  <iframe src="..."></iframe>
</div>
```

### Step 2: Use CSS Classes
Apply appropriate CSS classes from the SCSS files.

**Before:**
```html
<div style="background-color: #F5F7FA; padding: 2rem; border-radius: 0.5rem;">
  Form content
</div>
```

**After:**
```html
<div class="contact-section__form">
  Form content
</div>
```

### Step 3: Use Color Variables
All colors are now managed through CSS variables in `_master.scss`.

**Before:**
```scss
background-color: #F5F7FA;
color: #1a1a1a;
border-color: #d0d7de;
```

**After:**
```scss
background-color: var(--color-bg-secondary);
color: var(--color-text-primary);
border-color: var(--color-card-border);
```

## Common Patterns

### Progress Bar
```html
<!-- Old -->
<div class="progress" style="height: 6px;">
  <div class="progress-bar bg-warning progress-bar-striped progress-bar-animated"
       style="width: {{ progress }}%"></div>
</div>

<!-- New -->
<div class="progress">
  <div class="progress-bar progress-bar-striped progress-bar-animated"
       style="width: {{ progress }}%"></div>
</div>
```

### Modal
```html
<!-- Old -->
<div class="modal-body p-4">
  <div style="background: rgba(0,0,0,0.4); opacity: 0; transition: opacity 0.3s;">
    Content
  </div>
</div>

<!-- New -->
<div class="modal-body">
  <div class="preview-overlay">
    Content
  </div>
</div>
```

### Contact Form
```html
<!-- Old -->
<div style="background-color: {{ page.form_background_color }}; padding: 2rem; border-radius: 0.5rem;">
  Form
</div>

<!-- New -->
<div class="contact-section__form">
  Form
</div>
```

### Avatar
```html
<!-- Old -->
<img src="..." style="width: 100px; height: 100px; object-fit: cover;">

<!-- New -->
<img src="..." class="avatar-lg">
```

## Responsive Design

All SCSS files include responsive breakpoints:

- **Desktop**: Full width (> 992px)
- **Tablet**: 768px - 992px
- **Mobile**: < 768px
- **Small Mobile**: < 576px

Example:
```scss
@media (max-width: 768px) {
  .component {
    padding: 1rem;
  }
}

@media (max-width: 576px) {
  .component {
    padding: 0.5rem;
  }
}
```

## Best Practices

1. **Use CSS Variables**: Always use CSS variables from `_master.scss` instead of hardcoded colors
2. **Use BEM Naming**: Follow BEM (Block Element Modifier) naming convention
3. **Organize by Component**: Keep related styles in component SCSS files
4. **Responsive First**: Design mobile-first, then enhance for larger screens
5. **Avoid Inline Styles**: Move all inline styles to SCSS files
6. **Use Semantic Classes**: Use meaningful class names that describe the component

## Compilation

The SCSS files are automatically compiled to CSS. The main file `main.scss` imports all component files:

```scss
@import 'components/progress';
@import 'components/notes';
@import 'components/profile';
@import 'components/modals';
@import 'components/contact';
@import 'components/content';
```

## Troubleshooting

### Colors Not Applying
- Ensure the color variable exists in `_master.scss`
- Check that the SCSS file is imported in `main.scss`
- Verify the CSS is compiled to the output file

### Styles Not Showing
- Check that the class name matches the SCSS file
- Verify the HTML element has the correct class
- Check browser DevTools for CSS specificity issues

### Responsive Issues
- Test on different screen sizes
- Check media query breakpoints
- Verify mobile-first approach is used

## File Structure

```
assets/static/styles/
├── main.scss (Main import file)
├── colors/
│   ├── _master.scss (Master color variables)
│   └── _index.scss
├── components/
│   ├── _progress.scss (NEW)
│   ├── _notes.scss (NEW)
│   ├── _profile.scss (NEW)
│   ├── _modals.scss (NEW)
│   ├── _contact.scss (NEW)
│   ├── _content.scss (NEW)
│   └── ... (existing components)
├── base/
├── layout/
├── pages/
├── spacing/
└── utility/
```

## Next Steps

1. Update HTML files to remove inline styles
2. Apply appropriate CSS classes
3. Test responsive design on all breakpoints
4. Verify color consistency across the site
5. Update documentation as needed

## Support

For questions or issues with the SCSS migration:
1. Check this guide first
2. Review the specific component SCSS file
3. Check `_master.scss` for available color variables
4. Test in browser DevTools
