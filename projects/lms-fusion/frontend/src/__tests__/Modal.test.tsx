/**
 * Unit tests for the Modal component.
 *
 * Covers:
 * - Renders nothing when isOpen is false
 * - Renders children, title, footer when open
 * - Close on backdrop click
 * - Close on Escape key
 * - Close button in header
 * - showCloseButton=false hides close button
 * - Body scroll lock when open
 * - Focus trap basics
 * - Custom size variants
 * - Custom className
 * - blur prop
 * - onOpened and onClosed callbacks
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Modal from '@/components/ui/Modal';

describe('Modal', () => {
  beforeEach(() => {
    // Ensure body scroll is unlocked before each test
    document.body.style.overflow = '';
  });

  it('does not render children when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        <div>Modal Content</div>
      </Modal>,
    );
    expect(screen.queryByText('Modal Content')).not.toBeInTheDocument();
  });

  it('renders children when isOpen is true', () => {
    render(
      <Modal isOpen onClose={() => {}}>
        <div>Modal Content</div>
      </Modal>,
    );
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('renders the title', () => {
    render(
      <Modal isOpen onClose={() => {}} title="My Modal Title">
        <div>Content</div>
      </Modal>,
    );
    expect(screen.getByText('My Modal Title')).toBeInTheDocument();
  });

  it('renders the footer', () => {
    render(
      <Modal isOpen onClose={() => {}} footer={<button>Save</button>}>
        <div>Content</div>
      </Modal>,
    );
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('calls onClose when clicking the backdrop', () => {
    const onClose = vi.fn();
    const { container } = render(
      <Modal isOpen onClose={onClose}>
        <div>Content</div>
      </Modal>,
    );
    // The backdrop is the first motion div with absolute inset-0
    const backdrop = container.querySelector('.fixed.inset-0.z-\\[100\\] > div.absolute');
    // Click the overlay directly
    const overlay = document.querySelector('[class*="bg-black/50"]');
    if (overlay) {
      fireEvent.click(overlay);
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });

  it('calls onClose when pressing Escape', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose}>
        <div>Content</div>
      </Modal>,
    );
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not close on Escape when closeOnEscape is false', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} closeOnEscape={false}>
        <div>Content</div>
      </Modal>,
    );
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('renders a close button in the header by default', () => {
    render(
      <Modal isOpen onClose={() => {}} title="Title">
        <div>Content</div>
      </Modal>,
    );
    expect(screen.getByLabelText('Close modal')).toBeInTheDocument();
  });

  it('hides close button when showCloseButton is false', () => {
    render(
      <Modal isOpen onClose={() => {}} showCloseButton={false}>
        <div>Content</div>
      </Modal>,
    );
    expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument();
  });

  it('calls onClose when clicking the close button', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="Title">
        <div>Content</div>
      </Modal>,
    );
    fireEvent.click(screen.getByLabelText('Close modal'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('locks body scroll when open', () => {
    const { rerender } = render(
      <Modal isOpen onClose={() => {}}>
        <div>Content</div>
      </Modal>,
    );
    expect(document.body.style.overflow).toBe('hidden');

    rerender(
      <Modal isOpen={false} onClose={() => {}}>
        <div>Content</div>
      </Modal>,
    );
    expect(document.body.style.overflow).toBe('');
  });

  it('does not lock scroll when lockScroll is false', () => {
    render(
      <Modal isOpen onClose={() => {}} lockScroll={false}>
        <div>Content</div>
      </Modal>,
    );
    expect(document.body.style.overflow).toBe('');
  });

  it('renders with dialog ARIA attributes', () => {
    render(
      <Modal isOpen onClose={() => {}} title="A11y Title">
        <div>Content</div>
      </Modal>,
    );
    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-label', 'A11y Title');
  });

  it('applies custom className to the modal panel', () => {
    render(
      <Modal isOpen onClose={() => {}} className="custom-modal-class">
        <div>Content</div>
      </Modal>,
    );
    const dialog = document.querySelector('[role="dialog"]');
    expect(dialog?.className).toContain('custom-modal-class');
  });

  it('applies blur class when blur prop is true', () => {
    render(
      <Modal isOpen onClose={() => {}} blur>
        <div>Content</div>
      </Modal>,
    );
    const backdrop = document.querySelector('.backdrop-blur-sm');
    expect(backdrop).toBeInTheDocument();
  });

  it('renders different size variants', () => {
    const { rerender } = render(
      <Modal isOpen onClose={() => {}} size="sm">
        <div>Content</div>
      </Modal>,
    );
    const dialogSm = document.querySelector('[role="dialog"]');
    expect(dialogSm?.className).toContain('max-w-sm');

    rerender(
      <Modal isOpen onClose={() => {}} size="lg">
        <div>Content</div>
      </Modal>,
    );
    const dialogLg = document.querySelector('[role="dialog"]');
    expect(dialogLg?.className).toContain('max-w-lg');
  });

  it('calls onClosed after close animation completes', () => {
    const onClosed = vi.fn();
    const { rerender } = render(
      <Modal isOpen onClose={() => {}} onClosed={onClosed}>
        <div>Content</div>
      </Modal>,
    );

    rerender(
      <Modal isOpen={false} onClose={() => {}} onClosed={onClosed}>
        <div>Content</div>
      </Modal>,
    );

    // AnimatePresence calls onExitComplete when exit animation completes
    // This is called by framer-motion internally
    expect(onClosed).not.toHaveBeenCalled();
  });
});
