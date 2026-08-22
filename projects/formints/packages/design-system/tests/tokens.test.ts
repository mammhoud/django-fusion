import { describe, it, expect } from 'vitest';
import {
  tokens,
  spacing,
  widgetPadding,
  widgetGap,
  typography,
  radius,
  shadow,
  motion,
  zIndex,
  breakpoints,
  colors,
} from '../src/tokens';

describe('Design Tokens', () => {
  describe('Spacing', () => {
    it('should have 8px base unit spacing scale', () => {
      expect(spacing['1']).toBe('4px');
      expect(spacing['2']).toBe('8px');
      expect(spacing['4']).toBe('16px');
      expect(spacing['8']).toBe('32px');
    });

    it('should have zero spacing', () => {
      expect(spacing['0']).toBe('0px');
    });
  });

  describe('Widget Spacing', () => {
    it('should have compact padding values', () => {
      expect(widgetPadding.xs).toBe('8px');
      expect(widgetPadding.sm).toBe('12px');
      expect(widgetPadding.md).toBe('16px');
    });

    it('should have compact gap values', () => {
      expect(widgetGap.xs).toBe('4px');
      expect(widgetGap.sm).toBe('8px');
      expect(widgetGap.md).toBe('12px');
    });
  });

  describe('Typography', () => {
    it('should have font families', () => {
      expect(typography.fontFamily.sans).toContain('Inter');
      expect(typography.fontFamily.mono).toContain('JetBrains Mono');
    });

    it('should have font sizes', () => {
      expect(typography.fontSize.xs).toBe('0.75rem');
      expect(typography.fontSize.sm).toBe('0.875rem');
      expect(typography.fontSize.base).toBe('1rem');
    });

    it('should have font weights', () => {
      expect(typography.fontWeight.normal).toBe('400');
      expect(typography.fontWeight.medium).toBe('500');
      expect(typography.fontWeight.semibold).toBe('600');
      expect(typography.fontWeight.bold).toBe('700');
    });
  });

  describe('Radius', () => {
    it('should have Double-Bezel radius values', () => {
      expect(radius.bezelOuter).toBe('1.5rem');
      expect(radius.bezelInner).toBe('1.125rem');
    });

    it('should have standard radius values', () => {
      expect(radius.sm).toBe('0.25rem');
      expect(radius.md).toBe('0.375rem');
      expect(radius.lg).toBe('0.5rem');
      expect(radius.xl).toBe('0.75rem');
    });

    it('should have full radius for pills', () => {
      expect(radius.full).toBe('9999px');
      expect(radius.button).toBe('9999px');
      expect(radius.badge).toBe('9999px');
    });
  });

  describe('Shadow', () => {
    it('should have Double-Bezel shadows', () => {
      expect(shadow.bezelOuter).toContain('0 0 0 1px');
      expect(shadow.bezelInner).toContain('inset');
      expect(shadow.bezelHover).toContain('0 8px 24px');
    });

    it('should have standard shadow scale', () => {
      expect(shadow.none).toBe('none');
      expect(shadow.sm).toContain('0 1px 3px');
      expect(shadow.md).toContain('0 4px 6px');
      expect(shadow.lg).toContain('0 10px 15px');
    });
  });

  describe('Motion', () => {
    it('should have premium easing functions', () => {
      expect(motion.easing.fluid).toBe('cubic-bezier(0.32, 0.72, 0, 1)');
      expect(motion.easing.bounce).toBe('cubic-bezier(0.34, 1.56, 0.64, 1)');
      expect(motion.easing.spring).toBe('cubic-bezier(0.175, 0.885, 0.32, 1.275)');
    });

    it('should have duration values', () => {
      expect(motion.duration.fast).toBe('100ms');
      expect(motion.duration.normal).toBe('200ms');
      expect(motion.duration.slow).toBe('300ms');
      expect(motion.duration.slowest).toBe('700ms');
    });

    it('should have stagger delays', () => {
      expect(motion.stagger[1]).toBe('75ms');
      expect(motion.stagger[2]).toBe('150ms');
      expect(motion.stagger[3]).toBe('225ms');
      expect(motion.stagger[4]).toBe('300ms');
    });
  });

  describe('Z-Index', () => {
    it('should have z-index scale', () => {
      expect(zIndex.base).toBe('0');
      expect(zIndex.dropdown).toBe('1000');
      expect(zIndex.modal).toBe('1400');
      expect(zIndex.toast).toBe('1700');
    });
  });

  describe('Breakpoints', () => {
    it('should have standard breakpoints', () => {
      expect(breakpoints.sm).toBe('640px');
      expect(breakpoints.md).toBe('768px');
      expect(breakpoints.lg).toBe('1024px');
      expect(breakpoints.xl).toBe('1280px');
    });
  });

  describe('Colors', () => {
    it('should have primary palette', () => {
      expect(colors.primary).toBeDefined();
      expect(colors.primary[500]).toBeDefined();
    });

    it('should have semantic colors', () => {
      expect(colors.success.DEFAULT).toBe('#059669');
      expect(colors.warning.DEFAULT).toBe('#d97706');
      expect(colors.error.DEFAULT).toBe('#dc2626');
      expect(colors.info.DEFAULT).toBe('#3b82f6');
    });
  });

  describe('Combined Tokens', () => {
    it('should export all token categories', () => {
      expect(tokens.spacing).toBeDefined();
      expect(tokens.widgetPadding).toBeDefined();
      expect(tokens.widgetGap).toBeDefined();
      expect(tokens.typography).toBeDefined();
      expect(tokens.radius).toBeDefined();
      expect(tokens.shadow).toBeDefined();
      expect(tokens.motion).toBeDefined();
      expect(tokens.zIndex).toBeDefined();
      expect(tokens.breakpoints).toBeDefined();
      expect(tokens.colors).toBeDefined();
    });
  });
});
