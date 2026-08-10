import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import Modal from '../../components/ui/Modal';

describe('Modal component', () => {
  it('does not render content when closed', () => {
    render(
      <Modal isOpen={false} onClose={() => {}} title="Test Title">
        <p>Modal Body</p>
      </Modal>,
    );
    expect(screen.queryByText('Modal Body')).not.toBeInTheDocument();
  });

  it('renders title, subtitle, and body when open', () => {
    render(
      <Modal isOpen onClose={() => {}} title="Test Title" subtitle="A subtitle">
        <p>Modal Body</p>
      </Modal>,
    );
    expect(screen.getByRole('dialog', { name: 'Test Title' })).toBeInTheDocument();
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('A subtitle')).toBeInTheDocument();
    expect(screen.getByText('Modal Body')).toBeInTheDocument();
  });

  it('renders footer content', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" footer={<button type="button">Save</button>}>
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
  });

  it('applies size modifier classes', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" size="lg">
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByRole('dialog')).toHaveClass('modal--lg');
  });

  it('applies scroll and nopad modifiers', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" scroll noPad>
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByRole('dialog')).toHaveClass('modal--scroll', 'modal--nopad');
  });

  it('forwards contentTestId to the content frame', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" contentTestId="my-modal">
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByTestId('my-modal')).toBeInTheDocument();
  });

  it('calls onClose when the backdrop is clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="T">
        <p>Body</p>
      </Modal>,
    );
    fireEvent.click(screen.getByRole('dialog').querySelector('.modal__overlay')!);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not close on backdrop click when closeOnBackdrop is false', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="T" closeOnBackdrop={false}>
        <p>Body</p>
      </Modal>,
    );
    fireEvent.click(screen.getByRole('dialog').querySelector('.modal__overlay')!);
    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onClose via the header close button', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="T">
        <p>Body</p>
      </Modal>,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Close' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('renders header icon when provided', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" headerIcon={<span data-testid="head-icon" />}>
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByTestId('head-icon')).toBeInTheDocument();
  });

  it('applies the position modifier class (side sheet)', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" position="right">
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByRole('dialog')).toHaveClass('modal--right');
  });

  it('applies the semantic variant modifier class', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" variant="danger">
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByRole('dialog')).toHaveClass('modal--variant--danger');
  });

  it('hides the close button when dismissible is false', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T" dismissible={false}>
        <p>Body</p>
      </Modal>,
    );
    expect(screen.queryByRole('button', { name: 'Close' })).not.toBeInTheDocument();
  });

  it('closes on Escape by default', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="T">
        <p>Body</p>
      </Modal>,
    );
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not close on Escape when escapeClosable is false', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="T" escapeClosable={false}>
        <p>Body</p>
      </Modal>,
    );
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('does not attach the keydown listener while closed', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={false} onClose={onClose} title="T">
        <p>Body</p>
      </Modal>,
    );
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('moves focus into the dialog on open (focus trap)', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T">
        <button type="button">First</button>
        <button type="button">Last</button>
      </Modal>,
    );
    // The close button is the first focusable element inside the dialog.
    expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Close' }));
  });

  it('honours initialFocusRef when provided', () => {
    const ref = { current: null as HTMLButtonElement | null };
    render(
      <Modal isOpen onClose={() => {}} title="T" initialFocusRef={ref}>
        <div>
          <button type="button" data-testid="target" ref={ref as React.RefObject<HTMLButtonElement | null>}>
            Target
          </button>
        </div>
      </Modal>,
    );
    expect(document.activeElement).toBe(screen.getByTestId('target'));
  });

  it('focus trap wraps Tab focus from the last back to the first focusable', () => {
    render(
      <Modal isOpen onClose={() => {}} title="T">
        <button type="button" data-testid="a">A</button>
        <button type="button" data-testid="b">B</button>
      </Modal>,
    );
    // Focusables in DOM order: [Close, A, B].
    const closeBtn = screen.getByRole('button', { name: 'Close' });
    const btnB = screen.getByTestId('b');
    // On open, focus moves to the first focusable (close button).
    expect(document.activeElement).toBe(closeBtn);
    // jsdom has no native Tab navigation, so manually place focus to test the
    // trap's wrap-around logic (the code under test):
    //   Tab on the LAST focusable → wraps to the FIRST (close button).
    btnB.focus();
    fireEvent.keyDown(window, { key: 'Tab' });
    expect(document.activeElement).toBe(closeBtn);
    //   Shift+Tab on the FIRST → wraps to the LAST (B).
    closeBtn.focus();
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(btnB);
  });
});
