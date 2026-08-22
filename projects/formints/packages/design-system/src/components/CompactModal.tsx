/**
 * @formints/design-system — CompactModal Component
 * 
 * Compact modal for CRUD operations with Double-Bezel architecture.
 * Features:
 * - Sticky header and action bar
 * - Smooth spring transitions
 * - Focus trap and keyboard navigation
 * - Responsive sizing
 */

import { useEffect, useRef, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

export interface CompactModalProps {
  /** Modal visibility */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Modal title */
  title: string;
  /** Optional subtitle */
  subtitle?: string;
  /** Modal content */
  children: ReactNode;
  /** Action buttons */
  actions?: ReactNode;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Close on backdrop click */
  closeOnBackdrop?: boolean;
  /** Close on ESC key */
  closeOnEscape?: boolean;
  /** Show close button */
  dismissible?: boolean;
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
};

const FOCUSABLE_SELECTOR =
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

export default function CompactModal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  actions,
  size = 'md',
  closeOnBackdrop = true,
  closeOnEscape = true,
  dismissible = true,
}: CompactModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  // ESC close + focus trap
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closeOnEscape) {
        e.stopPropagation();
        onCloseRef.current();
        return;
      }
      if (e.key !== 'Tab') return;
      const contentEl = contentRef.current;
      if (!contentEl) return;
      const focusables = Array.from(
        contentEl.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
      );
      if (focusables.length === 0) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    // Focus first element
    const contentEl = contentRef.current;
    if (contentEl) {
      const target = contentEl.querySelector<HTMLElement>(FOCUSABLE_SELECTOR);
      target?.focus?.();
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, closeOnEscape]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={closeOnBackdrop ? onClose : undefined}
      />

      {/* Modal */}
      <div
        ref={contentRef}
        className={`
          relative w-full ${sizeClasses[size]}
          bg-base-100 dark:bg-base-900
          rounded-2xl
          shadow-2xl
          animate-scale-in
          overflow-hidden
        `}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        {/* Header */}
        <div className="px-5 py-4 border-b border-base-300/50 dark:border-white/10">
          <div className="flex items-center justify-between">
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-base-content">{title}</h2>
              {subtitle && (
                <p className="text-xs text-base-content/50 mt-0.5">{subtitle}</p>
              )}
            </div>
            {dismissible && (
              <button
                onClick={onClose}
                className="w-7 h-7 rounded-full bg-base-200 dark:bg-base-800 flex items-center justify-center hover:bg-base-300 dark:hover:bg-base-700 transition-colors shrink-0"
                aria-label="Close"
              >
                <span className="ri-close-line text-xs" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="px-5 py-4 max-h-[60vh] overflow-y-auto">
          <div className="space-y-3">
            {children}
          </div>
        </div>

        {/* Actions */}
        {actions && (
          <div className="px-5 py-3 border-t border-base-300/50 dark:border-white/10 bg-base-50 dark:bg-base-800/50">
            <div className="flex items-center justify-end gap-2">
              {actions}
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}
