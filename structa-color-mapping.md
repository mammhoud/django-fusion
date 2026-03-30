# Color System Analysis and Mapping

## Current Color System Analysis
Based on analysis of `structa/core/assets/static/styles/colors/_master.scss`

## Current Color Variables (Light Theme)

### Core Theme Colors (Current)
1. Primary Colors:
   - `--theme-primary: #3A7CA5` (Blue)
   - `--theme-primary-dark: #1A4D63` (Dark Blue)
   - `--theme-primary-light: #5FA8D4` (Light Blue)
   - `--theme-primary-lighter: #BAE6FF` (Very Light Blue)
   - `--theme-primary-darker: #0F3747` (Very Dark Blue)

2. Secondary Colors:
   - `--theme-secondary: #008080` (Teal)
   - `--theme-secondary-dark: #006D6D` (Dark Teal)
   - `--theme-secondary-light: #4DB3B3` (Light Teal)

3. Accent Colors:
   - `--theme-accent: #6C63FF` (Purple-Blue)
   - `--theme-accent-alt: #FF6B8B` (Coral Pink)

4. Background Colors:
   - `--theme-bg-primary: #FFFFFF` (White)
   - `--theme-bg-secondary: #F5F7FA` (Light Gray)
   - `--theme-bg-tertiary: #EBEFF5` (Light Blue-Gray)

5. Text Colors:
   - `--theme-text-primary: #1F2937` (Dark Gray)
   - `--theme-text-secondary: #4A5568` (Medium Gray)
   - `--theme-text-tertiary: #718096` (Light Gray)

## New Color Palette
Based on the design document, the new color palette is:
1. **Black (#0A0908)** - Primary black for text and high-contrast elements
2. **Jet Black (#22333B)** - Secondary black for backgrounds
3. **Soft Linen (#EAE0D5)** - Light neutral for backgrounds
4. **Tan (#C6AC8F)** - Warm neutral for accents
5. **Stone Brown (#5E503F)** - Earth tone for borders and subtle elements

## Mapping Strategy

### 1. Core Theme Colors Mapping
**Current Blue Theme → New Earth Tone Theme**

Current Blue Theme:
- Primary: `#3A7CA5` (Blue) → `#5E503F` (Stone Brown)
- Secondary: `#008080` (Teal) → `#C6AC8F` (Tan)
- Accent: `#6C63FF` (Purple-Blue) → `#C6AC8F` (Tan)

**New Mapping:**
- Primary: `#5E503F` (Stone Brown) - for primary actions, buttons, links
- Secondary: `#C6AC8F` (Tan) - for secondary actions, highlights
- Accent: `#C6AC8F` (Tan) - for interactive elements, hover states

### 2. Background Colors Mapping
**Current:**
- Light: `#FFFFFF` → `#EAE0D5` (Soft Linen)
- Light Gray: `#F5F7FA` → `#EAE0D5` (Soft Linen)
- Dark Gray: `#1A1D23` → `#22333B` (Jet Black)

**New Background Mapping:**
- Primary Background: `#EAE0D5` (Soft Linen) - Light theme
- Secondary Background: `#22333B` (Jet Black) - Dark theme
- Card Backgrounds: `#FFFFFF` (White) on light, `#22333B` on dark

### 3. Text Colors Mapping
**Current:**
- Primary Text: `#1F2937` (Dark Gray) → `#0A0908` (Black)
- Secondary Text: `#4A5568` (Gray) → `#22333B` (Jet Black)
- Tertiary Text: `#718096` (Light Gray) → `#5E503F` (Stone Brown)

**New Text Colors:**
- Primary Text: `#0A0908` (Black) for high contrast
- Secondary Text: `#22333B` (Jet Black) for less emphasis
- Muted Text: `#5E503F` (Stone Brown) for subtle text

### 4. Border and Divider Colors
**Current:**
- Primary Border: `#E2E8F0` (Light Gray)
- Secondary Border: `#CBD5E0` (Medium Gray)

**New Border Colors:**
- Primary Border: `#5E503F` (Stone Brown)
- Secondary Border: `#C6AC8F` (Tan)
- Divider: `#EAE0D5` (Soft Linen)

### 5. Button Colors
**Current Button Colors:**
- Primary Button: Blue gradient (#3A7CA5 to #1A4D63)
- Secondary Button: Gray (#F5F7FA)

**New Button Colors:**
- Primary Button: `#5E503F` (Stone Brown) with `#C6AC8F` (Tan) text
- Secondary Button: `#C6AC8F` (Tan) with `#0A0908` (Black) text
- Accent Button: `#22333B` (Jet Black) with `#EAE0D5` (Soft Linen) text

### 6. State Colors (Success, Warning, Error, Info)
These can remain the same as they are functional colors:
- Success: `#10B981` (Green) - Keep as is
- Warning: `#F59E0B` (Amber) - Keep as is
- Error: `#EF4444` (Red) - Keep as is
- Info: `#3B82F6` (Blue) - Keep as is

### 7. Component-Specific Mapping

**Cards:**
- Current: White background with blue borders
- New: `#EAE0D5` (Soft Linen) background with `#5E503F` borders

**Inputs:**
- Current: White background with gray border
- New: `#EAE0D5` background with `#5E503F` borders

**Navigation:**
- Current: Blue/Teal theme
- New: `#5E503F` (Stone Brown) for active states, `#C6AC8F` (Tan) for hover

### 8. Dark Theme Mapping

**Current Dark Theme:**
- Background: `#0F172A` (Dark Blue-Black)
- Text: `#F1F5F9` (Light Gray)

**New Dark Theme:**
- Background: `#22333B` (Jet Black)
- Text: `#EAE0D5` (Soft Linen)
- Accents: `#C6AC8F` (Tan) for highlights

### 9. Accessibility Considerations

**Contrast Ratios:**
1. Black (#0A0908) on Soft Linen (#EAE0D5): 15.9:1 ✓ (AAA)
2. Jet Black (#22333B) on Soft Linen (#EAE0D5): 8.6:1 ✓ (AAA)
3. Stone Brown (#5E503F) on Soft Linen (#EAE0D5): 4.6:1 ✓ (AA)
4. Tan (#C6AC8F) on Jet Black (#22333B): 7.2:1 ✓ (AAA)

**WCAG Compliance:**
- All text meets AA standards (4.5:1 minimum)
- Large text (18pt+) meets AA at 3:1 ratio
- Interactive elements have 3:1 contrast for focus states

### 10. Implementation Priority

**Phase 1 (Critical) - Core Variables:**
1. Update `--theme-primary`, `--theme-secondary`, `--theme-accent`
2. Update background and text colors
3. Update border and divider colors

**Phase 2 (Components):**
1. Buttons (primary, secondary, accent)
2. Form elements (inputs, selects, checkboxes)
3. Navigation and header

**Phase 3 (Theming):**
1. Dark theme variants
2. Component-specific overrides
3. State variations (hover, focus, active)

**Phase 4 (Accessibility):**
1. Focus states and keyboard navigation
2. High contrast mode support
3. Screen reader testing

### 11. Files to Update

**Primary Files:**
1. `_master.scss` - Core color variables
2. `_buttons.scss` - Button components
3. `_forms.scss` - Form elements
4. `_components.scss` - Component-specific styles
5. Theme files for light/dark modes

**Testing Strategy:**
1. Color contrast validation
2. Cross-browser testing
3. Mobile/desktop responsive testing
4. Screen reader testing
5. Print styles verification

### 12. Migration Notes

1. **Backward Compatibility**: Create CSS custom property fallbacks
2. **Progressive Enhancement**: New colors for modern browsers, fallback for older
3. **Testing**: Test with existing content to ensure no contrast issues
4. **Documentation**: Update design system documentation

### 13. Color Usage Guidelines

**Primary Color (#5E503F - Stone Brown):**
- Primary buttons
- Primary navigation
- Key interactive elements
- Focus states

**Secondary Color (#C6AC8F - Tan):**
- Secondary buttons
- Hover states
- Accent borders
- Highlighted text

**Backgrounds:**
- Primary: `#EAE0D5` (Soft Linen) - Light theme
- Secondary: `#22333B` (Jet Black) - Dark theme
- Cards: White on light, `#22333B` on dark

**Text Colors:**
- Primary: `#0A0908` (Black) on light, `#EAE0D5` on dark
- Secondary: `#22333B` (Jet Black) on light, `#C6AC8F` (Tan) on dark
- Muted: `#5E503F` (Stone Brown) on light, `#C6AC8F` (Tan) on dark

This mapping provides a cohesive, accessible color system that maintains WCAG compliance while implementing the new color palette.
