import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import ConfirmDialog from '../../components/ui/ConfirmDialog';

const baseProps = {
  isOpen: true,
  onClose: vi.fn(),
  onConfirm: vi.fn(),
  title: 'Delete Item?',
  message: 'Are you sure?',
  itemName: 'Burger',
};

describe('ConfirmDialog component', () => {
  it('renders title, message, and item name when open', () => {
    render(<ConfirmDialog {...baseProps} />);
    expect(screen.getByText('Delete Item?')).toBeInTheDocument();
    expect(screen.getByText('Are you sure?')).toBeInTheDocument();
    expect(screen.getByText('Burger?')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<ConfirmDialog {...baseProps} description="This cannot be undone." />);
    expect(screen.getByText('This cannot be undone.')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<ConfirmDialog {...baseProps} isOpen={false} />);
    expect(screen.queryByText('Delete Item?')).not.toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', () => {
    const onConfirm = vi.fn();
    render(<ConfirmDialog {...baseProps} onConfirm={onConfirm} confirmLabel="Yes, Delete" />);
    fireEvent.click(screen.getByRole('button', { name: /Yes, Delete/ }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when cancel button is clicked', () => {
    const onClose = vi.fn();
    render(<ConfirmDialog {...baseProps} onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /Cancel/ }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('uses translated deactivate label when confirmLabel is the default', () => {
    render(<ConfirmDialog {...baseProps} confirmLabel="Deactivate" variant="warning" />);
    expect(screen.getByRole('button', { name: /Deactivate/ })).toBeInTheDocument();
  });
});
