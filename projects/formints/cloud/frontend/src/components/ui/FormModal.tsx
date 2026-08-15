import { type ReactNode } from 'react';
import Modal, { type ModalSize } from './Modal';

/**
 * Reusable add/edit form modal shell.
 *
 * Standardizes the add/edit dialog pattern used across the app: a shared
 * `Modal` frame with a consistent footer (Cancel + Save), a submitting
 * spinner, and a disabled state. Pages pass any entity form as children —
 * the same shell is reused for every CRUD entity (employees, types, …).
 *
 * ```tsx
 * <FormModal
 *   isOpen={!!entityModal}
 *   onClose={closeModal}
 *   title={editing ? t('editTitle') : t('addTitle')}
 *   submitLabel={editing ? t('common.update') : t('common.add')}
 *   submitDisabled={!form.name.trim()}
 *   onSubmit={handleSave}
 * >
 *   <EntityForm value={form} onChange={setForm} />
 * </FormModal>
 * ```
 */
export interface FormModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  /** sm | md | lg | xl | full — width of the dialog */
  size?: ModalSize;
  onSubmit: () => void;
  /** Disable the Save button (e.g. invalid form). */
  submitDisabled?: boolean;
  /** Show the in-button spinner + disable both footer buttons. */
  isSubmitting?: boolean;
  submitLabel: ReactNode;
  cancelLabel?: ReactNode;
  /** Tailwind classes for the Save button — defaults to the primary button. */
  submitClassName?: string;
  /** data-testid forwarded to the dialog content frame. */
  contentTestId?: string;
  children: ReactNode;
}

export default function FormModal({
  isOpen,
  onClose,
  title,
  size = 'md',
  onSubmit,
  submitDisabled = false,
  isSubmitting = false,
  submitLabel,
  cancelLabel = 'Cancel',
  submitClassName = 'btn-primary',
  contentTestId,
  children,
}: FormModalProps) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size={size}
      contentTestId={contentTestId}
      footer={
        <div className="flex gap-2 w-full">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="btn btn-ghost flex-1 disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onSubmit}
            disabled={submitDisabled || isSubmitting}
            data-testid={contentTestId ? `${contentTestId}-submit` : undefined}
            className={`btn flex-1 disabled:opacity-50 gap-2 ${submitClassName}`}
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                {submitLabel}
              </>
            ) : (
              <>
                <span className="ri-save-3-line ri-16px" />
                {submitLabel}
              </>
            )}
          </button>
        </div>
      }
    >
      {children}
    </Modal>
  );
}
