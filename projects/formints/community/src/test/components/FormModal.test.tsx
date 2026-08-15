import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../test-utils';
import FormModal from '../../components/ui/FormModal';

describe('FormModal', () => {
  const baseProps = {
    isOpen: true,
    onClose: vi.fn(),
    title: 'Add Item',
    onSubmit: vi.fn(),
    submitLabel: 'Save',
    cancelLabel: 'Cancel',
  };

  it('renders the title, body children, and footer actions', () => {
    render(
      <FormModal {...baseProps}>
        <input data-testid="form-field" />
      </FormModal>,
    );
    expect(screen.getByText('Add Item')).toBeInTheDocument();
    expect(screen.getByTestId('form-field')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Save/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/ })).toBeInTheDocument();
  });

  it('triggers onSubmit and onClose from the footer buttons', async () => {
    render(<FormModal {...baseProps} contentTestId="frm"><div>body</div></FormModal>);
    await userEvent.click(screen.getByRole('button', { name: /Save/ }));
    expect(baseProps.onSubmit).toHaveBeenCalledTimes(1);
    await userEvent.click(screen.getByRole('button', { name: /Cancel/ }));
    expect(baseProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('disables the submit button when the form is invalid or submitting', () => {
    const { rerender } = render(
      <FormModal {...baseProps} submitDisabled><div>body</div></FormModal>,
    );
    expect(screen.getByRole('button', { name: /Save/ })).toBeDisabled();

    rerender(<FormModal {...baseProps} isSubmitting><div>body</div></FormModal>);
    // Both footer buttons are locked while a save is in flight.
    expect(screen.getByRole('button', { name: /Save/ })).toBeDisabled();
    expect(screen.getByRole('button', { name: /Cancel/ })).toBeDisabled();
  });

  it('forwards the content test id and exposes a submit test id', () => {
    render(<FormModal {...baseProps} contentTestId="employee-form-modal"><div>body</div></FormModal>);
    expect(screen.getByTestId('employee-form-modal')).toBeInTheDocument();
    expect(screen.getByTestId('employee-form-modal-submit')).toBeInTheDocument();
  });

  it('renders nothing when closed', () => {
    render(<FormModal {...baseProps} isOpen={false}><div>body</div></FormModal>);
    expect(screen.queryByText('Add Item')).not.toBeInTheDocument();
  });
});
