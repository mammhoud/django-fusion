import Modal from './Modal';
import { useTranslation } from 'react-i18next';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  itemName: string;
  confirmLabel?: string;
  variant?: 'danger' | 'warning';
  description?: string;
}

export default function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  itemName,
  confirmLabel = 'Deactivate',
  variant = 'danger',
  description,
}: ConfirmDialogProps) {
  const { t } = useTranslation();
  const isDanger = variant === 'danger';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      size="sm"
      variant={variant}
      footer={
        <>
          <button
            onClick={onClose}
            className="btn btn-ghost flex-1"
          >
            {t('confirmDialog.cancel')}
          </button>
          <button
            onClick={onConfirm}
            className={`btn flex-1 ${isDanger ? 'btn-error' : 'btn-warning'}`}
          >
            <span className="ri-delete-bin-line ri-16px" /> {confirmLabel === 'Deactivate' ? t('confirmDialog.deactivate') : confirmLabel}
          </button>
        </>
      }
    >
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className={`modal__body-icon ${isDanger ? 'modal__body-icon--danger' : 'modal__body-icon--warning'}`}>
            <span className="ri-alert-line text-4xl" />
          </div>
        </div>
        <h2 className="modal__title text-xl font-bold mb-2 text-center">{title}</h2>
        <p className="text-base-content/70">{message}</p>
        <p className="text-base-content font-semibold text-lg mt-1 mb-2">{itemName}?</p>
        {description && (
          <p className="text-base-content/50 text-sm mb-2">{description}</p>
        )}
      </div>
    </Modal>
  );
}
