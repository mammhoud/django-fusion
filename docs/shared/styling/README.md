# Styling Documentation

Complete guide to styling frameworks, conventions, and design tokens.

## Quick Navigation

- **[CSS Frameworks](01-css-frameworks.md)** - Tailwind CSS and CSS Modules
- **[Styling Conventions](02-styling-conventions.md)** - Best practices and patterns
- **[Theme Configuration](03-theme-configuration.md)** - Design tokens and customization
- **[Responsive Design](04-responsive-design.md)** - Mobile-first responsive patterns

### Color System (Legacy Documentation)

- **[Color Analysis](color-analysis.md)** - CSS variable inventory and current color system overview
- **[Color Analysis Complete](color-analysis-complete.md)** - Full task summary with success criteria and next steps
- **[Color Mapping](color-mapping.md)** - Detailed mapping from blue/teal theme to earth-tone palette
- **[Color Analysis Task 1 Summary](color-analysis-task1-summary.md)** - Summary report for the color system analysis task

## Overview

This project uses a combination of styling approaches:

- **Tailwind CSS** - Utility-first CSS framework for rapid development
- **CSS Modules** - Scoped CSS for component-level styling
- **PostCSS** - CSS transformation and optimization

## Key Principles

1. **Utility-First** - Use Tailwind utilities for rapid development
2. **Component-Scoped** - Use CSS Modules for component-specific styles
3. **Mobile-First** - Design for mobile, enhance for larger screens
4. **Accessibility** - Ensure sufficient contrast and focus indicators
5. **Performance** - Optimize images and minimize CSS

## Design System

### Colors
- Primary: Blue (#3B82F6)
- Secondary: Green (#10B981)
- Status: Success, Warning, Error, Info

### Typography
- Primary Font: Inter
- Monospace Font: Menlo
- Responsive font sizes

### Spacing
- Consistent spacing scale
- Responsive padding and margins
- Gap utilities for layouts

### Components
- Buttons
- Cards
- Forms
- Navigation
- Modals

## Getting Started

1. Review [CSS Frameworks](01-css-frameworks.md) to understand available tools
2. Check [Styling Conventions](02-styling-conventions.md) for best practices
3. Explore [Theme Configuration](03-theme-configuration.md) for design tokens
4. Learn [Responsive Design](04-responsive-design.md) for mobile-first approach

## Common Tasks

### Adding a New Component

1. Create component file (e.g., `Button.jsx`)
2. Create styles file (e.g., `Button.module.css`)
3. Import styles in component
4. Use Tailwind utilities or CSS Modules
5. Test responsive behavior

### Customizing Theme

1. Edit `tailwind.config.js`
2. Add custom colors, fonts, or spacing
3. Update CSS variables if needed
4. Test changes across components

### Creating Responsive Layout

1. Start with mobile styles
2. Add breakpoints for larger screens
3. Use Tailwind responsive prefixes (md:, lg:, etc.)
4. Test on multiple devices

## Next Steps

- Read [CSS Frameworks](01-css-frameworks.md)
- Review [Styling Conventions](02-styling-conventions.md)
- Check [Theme Configuration](03-theme-configuration.md)
- Learn [Responsive Design](04-responsive-design.md)
