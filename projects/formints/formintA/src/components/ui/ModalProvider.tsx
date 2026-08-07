import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import Modal, { type ModalPosition, type ModalSize, type ModalVariant } from './Modal';

/**
 * Imperative modal management for Formint.
 *
 * Wrap the app (or a subtree) in `<ModalProvider>`, then call `useModal()`
 * anywhere inside to open/close dialogs without lifting state or duplicating
 * `<Modal isOpen={...}>` wrappers on every page:
 *
 * ```tsx
 * const { openModal } = useModal();
 *
 * openModal({
 *   title: t('productManager.deleteTitle'),
 *   variant: 'danger',
 *   size: 'sm',
 *   content: (close) => (
 *     <p>Are you sure you want to delete this?</p>
 *   ),
 *   footer: (close) => (
 *     <>
 *       <button onClick={close}>Cancel</button>
 *       <button onClick={handleDelete}>Delete</button>
 *     </>
 *   ),
 * });
 * ```
 *
 * The rendered dialog is the shared extended `Modal` component (BEM frame),
 * so every feature (positions, variants, focus trap, ESC, sizes) works here too.
 *
 * @see docs/modals.md — including the FlyonUI htmx / Alpine.js option for
 *      server-rendered web deployments.
 */
export interface ModalConfig {
  /** Optional stable id — auto-generated when omitted. */
  id?: string;
  title?: string;
  subtitle?: string;
  headerIcon?: ReactNode;
  /** Dialog body. Can be a render-prop receiving a `close` function. */
  content?: ReactNode | ((close: () => void) => ReactNode);
  /** Footer actions. Can be a render-prop receiving a `close` function. */
  footer?: ReactNode | ((close: () => void) => ReactNode);
  size?: ModalSize;
  position?: ModalPosition;
  variant?: ModalVariant;
  borderColor?: string;
  scroll?: boolean;
  noPad?: boolean;
  closeOnBackdrop?: boolean;
  escapeClosable?: boolean;
  dismissible?: boolean;
  contentTestId?: string;
}

interface ModalProviderValue {
  /** Open a dialog. Returns its id (useful for `closeModal(id)`). */
  openModal: (config: ModalConfig) => string;
  /** Close a specific dialog by id. */
  closeModal: (id: string) => void;
  /** Close every open dialog. */
  closeAllModals: () => void;
}

const ModalContext = createContext<ModalProviderValue | undefined>(undefined);

let nextModalId = 0;

export function ModalProvider({ children }: { children: ReactNode }) {
  const [modals, setModals] = useState<{ id: string; config: ModalConfig }[]>([]);
  const idRef = useRef(nextModalId);

  const openModal = useCallback((config: ModalConfig): string => {
    const id = config.id ?? `modal-${++idRef.current}`;
    setModals(prev => [...prev, { id, config }]);
    return id;
  }, []);

  const closeModal = useCallback((id: string) => {
    setModals(prev => prev.filter(m => m.id !== id));
  }, []);

  const closeAllModals = useCallback(() => setModals([]), []);

  const value = useMemo(
    () => ({ openModal, closeModal, closeAllModals }),
    [openModal, closeModal, closeAllModals],
  );

  return (
    <ModalContext.Provider value={value}>
      {children}
      {modals.map(({ id, config }) => {
        const { id: _configId, content, footer, ...rest } = config;
        const close = () => closeModal(id);
        return (
          <Modal
            key={id}
            isOpen
            onClose={close}
            {...rest}
            footer={
              footer !== undefined
                ? (typeof footer === 'function' ? footer(close) : footer)
                : undefined
            }
          >
            {typeof content === 'function' ? content(close) : content}
          </Modal>
        );
      })}
    </ModalContext.Provider>
  );
}

export function useModal(): ModalProviderValue {
  const ctx = useContext(ModalContext);
  if (!ctx) {
    throw new Error('useModal must be used within a <ModalProvider>');
  }
  return ctx;
}
