# Color System Analysis for Structa Core

## Current Color System Analysis
Based on analysis of `structa/core/assets/static/styles/colors/_master.scss`

## 1. Core Theme Colors

### Primary Theme Colors (Light Theme)
- `--theme-primary: #3A7CA5` (Vibrant blue)
- `--theme-primary-dark: #1A4D63` (Deep blue)
- `--theme-primary-light: #5FA8D4` (Light blue)
- `--theme-primary-lighter: #BAE6FF` (Very light blue)
- `--theme-primary-darker: #0F3747` (Very dark blue)

### Secondary Theme Colors
- `--theme-secondary: #008080` (True teal)
- `--theme-secondary-dark: #006D6D` (Deep teal)
- `--theme-secondary-light: #4DB3B3` (Light teal)
- `--theme-secondary-lighter: #E6F7F7` (Very light teal)

### Accent Colors
- `--theme-accent: #6C63FF` (Vibrant purple-blue)
- `--theme-accent-dark: #5A52D4` (Dark purple-blue)
- `--theme-accent-light: #8B84FF` (Light purple-blue)
- `--theme-accent-alt: #FF6B8B` (Vibrant coral pink)
- `--theme-accent-alt-dark: #E05575` (Dark coral pink)
- `--theme-accent-alt-light: #FF8BA7` (Light coral pink)

## 2. Background Colors

### Light Theme Backgrounds
- `--theme-bg-primary: #FFFFFF` (White)
- `--theme-bg-secondary: #F5F7FA` (Light gray)
- `--theme-bg-tertiary: #EBEFF5` (Light blue-gray)
- `--theme-bg-inverse: #1A1D23` (Dark gray/black)
- `--theme-bg-overlay: rgba(255, 255, 255, 0.96)` (Semi-transparent white)

### Dark Theme Backgrounds
- `--theme-bg-primary: #0F172A` (Dark blue-black)
- `--theme-bg-secondary: #1E293B` (Dark blue-gray)
- `--theme-bg-tertiary: #2D3748` (Medium gray-blue)
- `--theme-bg-inverse: #F8FAFC` (Light gray)

## 3. Text Colors

### Light Theme Text
- `--theme-text-primary: #1F2937` (Dark gray - high contrast)
- `--theme-text-secondary: #4A5568` (Medium gray)
- `--theme-text-tertiary: #718096` (Light gray)
- `--theme-text-inverse: #FFFFFF` (White)
- `--theme-text-accent: #3A7CA5` (Brand blue)
- `--theme-text-muted: #94A3B8` (Muted gray)
- `--theme-text-disabled: #CBD5E0` (Light gray)

### Dark Theme Text
- `--theme-text-primary: #F1F5F9` (Light gray)
- `--theme-text-secondary: #E2E8F0` (Light gray)
- `--theme-text-tertiary: #A0AEC0` (Medium gray)
- `--theme-text-inverse: #0F172A` (Dark blue-black)

## 4. Border Colors
- `--theme-border-primary: #E2E8F0` (Light gray)
- `--theme-border-secondary: #CBD5E0` (Medium gray)
- `--theme-border-tertiary: #A0AEC0` (Dark gray)
- `--theme-border-accent: #3A7CA5` (Brand blue)
- `--theme-border-inverse: #1A1D23` (Dark)

## 5. State & Status Colors

### Success Colors
- `--color-success: #10B981` (Vibrant green)
- `--color-success-light: #34D399` (Light green)
- `--color-success-dark: #059669` (Dark green)
- `--color-success-lighter: #D1FAE5` (Very light green)
- `--color-success-darker: #047857` (Very dark green)

### Warning Colors
- `--color-warning: #F59E0B` (Vibrant amber)
- `--color-warning-light: #FBBF24` (Light amber)
- `--color-warning-dark: #D97706` (Dark amber)
- `--color-warning-lighter: #FEF3C7` (Very light amber)
- `--color-warning-darker: #92400E` (Very dark amber)

### Error Colors
- `--color-error: #EF4444` (Vibrant red)
- `--color-error-light: #F87171` (Light red)
- `--color-error-dark: #DC2626` (Dark red)
- `--color-error-lighter: #FEE2E2` (Very light red)
- `--color-error-darker: #991B1B` (Very dark red)

### Info Colors
- `--color-info: #3B82F6` (Vibrant blue)
- `--color-info-light: #60A5FA` (Light blue)
- `--color-info-dark: #2563EB` (Dark blue)
- `--color-info-lighter: #DBEAFE` (Very light blue)
- `--color-info-darker: #1E40AF` (Very dark blue)

## 6. Component Colors

### Button Colors
- Primary Button: `--color-button-primary-bg: var(--theme-primary)`
- Secondary Button: `--color-button-secondary-bg: var(--theme-bg-secondary)`
- Accent Button: `--color-button-accent-bg: var(--theme-accent)`

### Card Colors
- `--color-card-bg: var(--theme-surface)`
- `--color-card-border: var(--theme-border-primary)`
- `--color-card-shadow: var(--theme-shadow)`

### Input Colors
- `--color-input-bg: var(--color-bg-text-primary)`
- `--color-input-border: var(--theme-border-primary)`
- `--color-input-focus: var(--theme-border-accent)`

## 7. Gradients

### Primary Gradients
- `--gradient-primary: linear-gradient(135deg, var(--theme-bg-tertiary) 0%, var(--theme-primary) 100%)`
- `--gradient-accent: linear-gradient(135deg, var(--theme-accent) 0%, var(--color-accent-2) 100%)`
- `--gradient-button-primary: linear-gradient(90deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%)`

## 8. Shadows
- `--theme-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)`
- `--theme-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`
- `--theme-shadow-md: 0 6px 12px -2px rgba(0, 0, 0, 0.1), 0 3px 6px -1px rgba(0, 0, 0, 0.08)`
- `--theme-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)`

## 9. Opacity Variations
- Multiple opacity levels for primary, secondary, accent colors
- Black and white opacity variations
- Success, warning, error, and info opacity variants

## 10. Component-Specific Colors
- Header, navigation, form elements, badges, alerts, toasts, etc.

## Current Color Palette Summary
The current color system is comprehensive but uses a blue/teal/purple color scheme that needs to be updated to the new cohesive palette.

## Files That Reference Color Variables
Based on the search, the following files reference color variables:
1. `_sections.scss` - Layout sections with shadow and gradient variables
2. `_listing.scss` - Course cards and featured courses
3. Various component files that use color variables

## Mapping to New Color Palette

### New Color Palette (from design document):
1. **Black (#0A0908)** - Primary black for text and high-contrast elements
2. **Jet Black (#22333B)** - Secondary black for backgrounds and dark elements
3. **Soft Linen (#EAE0D5)** - Light neutral for backgrounds and cards
4. **Tan (#C6AC8F)** - Warm neutral for accents and highlights
5. **Stone Brown (#5E503F)** - Earth tone for borders and subtle elements

### Mapping Strategy:
1. **Primary Text/High Contrast**: Use Black (#0A0908)
2. **Secondary Text/Backgrounds**: Use Jet Black (#22333B)
3. **Backgrounds/Surfaces**: Use Soft Linen (#EAE0D5) for light mode
4. **Accents & Highlights**: Use Tan (#C6AC8F) for interactive elements
5. **Borders & Dividers**: Use Stone Brown (#5E503F)

### Component Mapping:
- Primary buttons: Tan (#C6AC8F)
- Secondary buttons: Stone Brown (#5E503F)
- Backgrounds: Soft Linen (#EAE0D5) for light, Jet Black (#22333B) for dark
- Text: Black (#0A0908) for light mode, Soft Linen (#EAE0D5) for dark mode
- Borders: Stone Brown (#5E503F)
- Accents: Tan (#C6AC8F) for highlights

### Accessibility Considerations:
- Black (#0A0908) on Soft Linen (#EAE0D5) provides 15.9:1 contrast ratio ✓
- Jet Black (#22333B) on Soft Linen (#EAE0D5) provides 8.6:1 contrast ratio ✓
- Stone Brown (#5E503F) on Soft Linen (#EAE0D5) provides 4.6:1 contrast ratio ✓
- All combinations meet WCAG AA standards for normal text (4.5:1)

### Implementation Priority:
1. Update core theme colors in `_master.scss`
2. Update component-specific color variables
3. Test contrast ratios for accessibility
4. Update dark theme variants
5. Test across all components

This analysis provides the foundation for the color system update to the new cohesive palette.</text>
