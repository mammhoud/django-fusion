import { useEffect, useRef } from 'react';
import AnimatePresence from './AnimatePresence';

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';
export type ModalPosition = 'center' | 'top' | 'bottom' | 'left' | 'right';
export type ModalVariant = 'default' | 'danger' | 'warning' | 'success' | 'info';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  /** Optional header icon rendered before the title */
  headerIcon?: React.ReactNode;
  /** Optional subtitle rendered under the title */
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  /** sm | md | lg | xl | full — maps to BEM `.modal--{size}` */
  size?: ModalSize;
  /** center | top | bottom | left | right — maps to BEM `.modal--{position}`.
      Side positions render a full-height sheet; top/bottom stay centered horizontally. */
  position?: ModalPosition;
  /** default | danger | warning | success | info — semantic accent styles */
  variant?: ModalVariant;
  /** Legacy accent border (e.g. from ConfirmDialog) */
  borderColor?: string;
  /** Allow the body to scroll independently (pins header + footer) */
  scroll?: boolean;
  /** Remove default content padding */
  noPad?: boolean;
  /** Align footer: start | between | center | end */
  footerAlign?: 'start' | 'between' | 'center' | 'end';
  /** Close when the backdrop overlay is clicked (default true) */
  closeOnBackdrop?: boolean;
  /** Close when the Escape key is pressed (default true) */
  escapeClosable?: boolean;
  /** Show the header close button (default true) */
  dismissible?: boolean;
  /** Keep keyboard focus inside the dialog while open (default true) */
  focusTrap?: boolean;
  /** Ref to focus when the modal opens (defaults to the first focusable element) */
  initialFocusRef?: React.RefObject<HTMLElement | null>;
  className?: string;
  contentClassName?: string;
  /** data-testid forwarded to the content frame (used by page tests) */
  contentTestId?: string;
}

const footerAlignClass: Record<string, string> = {
  start: 'modal__footer--start',
  between: 'modal__footer--between',
  center: 'modal__footer--center',
  end: '',
};

/** Selector for elements that should receive keyboard focus inside the dialog. */
const FOCUSABLE_SELECTOR =
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

export default function Modal({
  isOpen,
  onClose,
  title,
  headerIcon,
  subtitle,
  children,
  footer,
  size = 'md',
  position = 'center',
  variant = 'default',
  borderColor,
  scroll = false,
  noPad = false,
  footerAlign = 'end',
  closeOnBackdrop = true,
  escapeClosable = true,
  dismissible = true,
  focusTrap = true,
  initialFocusRef,
  className = '',
  contentClassName = '',
  contentTestId,
}: ModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  // Keep the latest onClose in a ref so the keydown listener never goes stale
  // without having to re-subscribe on every parent re-render.
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  // ── ESC close + focus trap ──
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && escapeClosable) {
        e.stopPropagation();
        onCloseRef.current();
        return;
      }
      if (e.key !== 'Tab' || !focusTrap) return;
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

    // Move focus into the dialog on open (respect explicit initialFocusRef).
    const contentEl = contentRef.current;
    if (contentEl) {
      const target =
        initialFocusRef?.current ??
        contentEl.querySelector<HTMLElement>(FOCUSABLE_SELECTOR);
      target?.focus?.();
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, escapeClosable, focusTrap, initialFocusRef]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          className={`modal modal--enter modal--${position} modal--${size} ${variant !== 'default' ? `modal--variant--${variant}` : ''} ${scroll ? 'modal--scroll' : ''} ${noPad ? 'modal--nopad' : ''} ${className}`}
          role="dialog"
          aria-modal="true"
          aria-label={title || 'Dialog'}
        >
          {/* Backdrop */}
          <div
            className="modal__overlay"
            onClick={closeOnBackdrop ? onClose : undefined}
          />
          <div
            ref={contentRef}
            className={`modal__content ${borderColor ? `border-2 ${borderColor}` : ''} ${contentClassName}`}
            {...(contentTestId ? { 'data-testid': contentTestId } : {})}
          >
            {(title !== undefined || headerIcon) && (
              <div className="modal__header">
                <div className="flex items-center gap-2 min-w-0">
                  {headerIcon}
                  <div className="min-w-0">
                    {title && <h2 className="modal__title">{title}</h2>}
                    {subtitle && <p className="modal__subtitle">{subtitle}</p>}
                  </div>
                </div>
                {dismissible && (
                  <button
                    type="button"
                    onClick={onClose}
                    className="modal__close"
                    aria-label="Close"
                  >
                    <span className="ri-close-line modal__close-icon" />
                  </button>
                )}
              </div>
            )}
            <div className="modal__body">{children}</div>
            {footer && (
              <div className={`modal__footer ${footerAlignClass[footerAlign] || ''}`}>
                {footer}
              </div>
            )}
          </div>
        </div>
      )}
    </AnimatePresence>
  );
}
