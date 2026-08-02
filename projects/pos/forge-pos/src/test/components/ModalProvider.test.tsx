import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import { ModalProvider, useModal } from '../../components/ui/ModalProvider';

function Trigger({ config }: { config: Parameters<ReturnType<typeof useModal>['openModal']>[0] }) {
  const { openModal, closeModal, closeAllModals } = useModal();
  return (
    <div>
      <button type="button" onClick={() => openModal(config)}>Open</button>
      <button type="button" onClick={() => closeModal('custom-id')}>Close by id</button>
      <button type="button" onClick={closeAllModals}>Close all</button>
    </div>
  );
}

function renderWithProvider(ui: React.ReactNode) {
  return render(<ModalProvider>{ui}</ModalProvider>);
}

describe('ModalProvider + useModal', () => {
  it('throws when used outside a ModalProvider', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    function Boom() {
      useModal();
      return null;
    }
    expect(() => render(<Boom />)).toThrow('useModal must be used within a <ModalProvider>');
    spy.mockRestore();
  });

  it('opens a modal imperatively', () => {
    renderWithProvider(
      <Trigger config={{ id: 'custom-id', title: 'Hello', content: <p>Body text</p> }} />,
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    expect(screen.getByRole('dialog', { name: 'Hello' })).toBeInTheDocument();
    expect(screen.getByText('Body text')).toBeInTheDocument();
  });

  it('closes a modal by id', () => {
    renderWithProvider(
      <Trigger config={{ id: 'custom-id', title: 'Hello', content: <p>Body</p> }} />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Close by id' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('closes all modals', () => {
    renderWithProvider(
      <>
        <Trigger config={{ id: 'a', title: 'A', content: <p>A body</p> }} />
        <Trigger config={{ id: 'b', title: 'B', content: <p>B body</p> }} />
      </>,
    );
    fireEvent.click(screen.getAllByRole('button', { name: 'Open' })[0]);
    fireEvent.click(screen.getAllByRole('button', { name: 'Open' })[1]);
    expect(screen.getAllByRole('dialog').length).toBe(2);
    // Both Trigger instances render a "Close all" button — click the first.
    fireEvent.click(screen.getAllByRole('button', { name: 'Close all' })[0]);
    expect(screen.queryAllByRole('dialog').length).toBe(0);
  });

  it('supports render-prop content and footer receiving close', () => {
    renderWithProvider(
      <Trigger
        config={{
          id: 'rp',
          title: 'Render Prop',
          content: (close) => (
            <button type="button" data-testid="content-close" onClick={close}>
              close from content
            </button>
          ),
          footer: (close) => (
            <button type="button" data-testid="footer-close" onClick={close}>
              close from footer
            </button>
          ),
        }}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    // Footer render-prop renders inside the modal footer slot.
    fireEvent.click(screen.getByTestId('footer-close'));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('forwards extended Modal props (position + variant)', () => {
    renderWithProvider(
      <Trigger
        config={{ id: 'sheet', title: 'Sheet', position: 'right', variant: 'success', content: <p>x</p> }}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveClass('modal--right', 'modal--variant--success');
  });

  it('auto-generates an id when omitted', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    renderWithProvider(
      <Trigger config={{ title: 'Auto', content: <p>auto id body</p> }} />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    expect(screen.getByRole('dialog', { name: 'Auto' })).toBeInTheDocument();
    spy.mockRestore();
  });
});
