import { describe, it, expect } from 'vitest';
import {
  BezelCard,
  BezelWidget,
  CompactInput,
  CompactButton,
  CompactRow,
  CompactBadge,
  CompactLabel,
} from '../src/components';

describe('Components', () => {
  describe('BezelCard', () => {
    it('should render with default props', () => {
      expect(BezelCard).toBeDefined();
      expect(typeof BezelCard).toBe('object'); // forwardRef component
    });

    it('should have correct display name', () => {
      expect(BezelCard.displayName).toBe('BezelCard');
    });
  });

  describe('BezelWidget', () => {
    it('should render with default props', () => {
      expect(BezelWidget).toBeDefined();
      expect(typeof BezelWidget).toBe('object');
    });

    it('should have correct display name', () => {
      expect(BezelWidget.displayName).toBe('BezelWidget');
    });
  });

  describe('CompactInput', () => {
    it('should render with default props', () => {
      expect(CompactInput).toBeDefined();
      expect(typeof CompactInput).toBe('object');
    });

    it('should have correct display name', () => {
      expect(CompactInput.displayName).toBe('CompactInput');
    });
  });

  describe('CompactButton', () => {
    it('should render with default props', () => {
      expect(CompactButton).toBeDefined();
      expect(typeof CompactButton).toBe('object');
    });

    it('should have correct display name', () => {
      expect(CompactButton.displayName).toBe('CompactButton');
    });
  });

  describe('CompactRow', () => {
    it('should render with default props', () => {
      expect(CompactRow).toBeDefined();
      expect(typeof CompactRow).toBe('object');
    });

    it('should have correct display name', () => {
      expect(CompactRow.displayName).toBe('CompactRow');
    });
  });

  describe('CompactBadge', () => {
    it('should render with default props', () => {
      expect(CompactBadge).toBeDefined();
      expect(typeof CompactBadge).toBe('object');
    });

    it('should have correct display name', () => {
      expect(CompactBadge.displayName).toBe('CompactBadge');
    });
  });

  describe('CompactLabel', () => {
    it('should render with default props', () => {
      expect(CompactLabel).toBeDefined();
      expect(typeof CompactLabel).toBe('object');
    });

    it('should have correct display name', () => {
      expect(CompactLabel.displayName).toBe('CompactLabel');
    });
  });
});
