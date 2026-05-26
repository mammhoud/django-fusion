# Design Document: Color Palette Update

**Category Context: Modernization & Updates**
- **Category**: Modernization
- **Scope**: System upgrades, technology updates, performance optimizations, refactoring
- **Related Specs**: project-modernization, structa-color-update
- **Common Patterns**: Technology stack updates, UI/UX improvements, performance optimization
- **Avoid Duplicates**: Check existing modernization specs before creating new update features


## Overview
Update the color palette in the structa/core project to use a more cohesive and accessible color scheme based on the provided color palette.

## Color Palette
1. **Black (#0A0908)** - Primary black for text and high-contrast elements
2. **Jet Black (#22333B)** - Secondary black for backgrounds and dark elements
3. **Soft Linen (#EAE0D5)** - Light neutral for backgrounds and cards
4. **Tan (#C6AC8F)** - Warm neutral for accents and highlights
5. **Stone Brown (#5E503F)** - Earth tone for borders and subtle elements

## Design System Updates

### Color Variables
The following color variables will be updated in the SCSS files:

**Core Colors:**
- `--color-black: #0A0908;` (Black)
- `--color-jet-black: #22333B;` (Jet Black)
- `--color-soft-linen: #EAE0D5;` (Soft Linen)
- `--color-tan: #C6AC8F;` (Tan)
- `--color-stone-brown: #5E503F;` (Stone Brown)

**Semantic Colors:**
- Primary: Use Stone Brown (#5E503F) for primary actions
- Secondary: Use Tan (#C6AC8F) for secondary actions
- Background: Use Soft Linen (#EAE0D5) for backgrounds
- Text: Use Black (#0A0908) for primary text, Jet Black (#22333B) for secondary text
- Borders: Use Stone Brown (#5E503F) for borders and dividers

## Implementation Plan

### 1. Update Color Variables
Update all color variables in `_master.scss` to use the new color palette.

### 2. Theme Updates
- Update light theme to use the new color palette
- Update dark theme to use darker variants of the palette
- Ensure proper contrast ratios for accessibility

### 3. Component Updates
- Update button colors to use the new palette
- Update form elements with new color scheme
- Update card and container backgrounds
- Update typography colors

### 4. Accessibility
- Ensure all color combinations meet WCAG AA standards
- Test contrast ratios for all text/background combinations
- Provide sufficient color contrast for all interactive elements

### 5. HTML Content Review
- Review all HTML templates for color usage
- Update inline styles to use CSS custom properties
- Ensure all text has sufficient contrast

## Files to Update
1. `structa/core/assets/static/styles/colors/_master.scss`
2. All component SCSS files that reference color variables
3. HTML templates with inline styles
4. Any JavaScript that manipulates colors

## Success Criteria
1. All color variables updated to new palette
2. WCAG AA compliance for all text/background combinations
3. Consistent color usage across all components
4. Proper dark theme support
5. All existing functionality preserved
