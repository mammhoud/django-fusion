import Modal from '../layout/Modal';
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
  const borderColor = isDanger ? 'border-red-300 dark:border-red-500/30' : 'border-yellow-300 dark:border-yellow-500/30';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      size="sm"
      borderColor={borderColor}
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
            <span className="icon-[tabler--trash] w-4 h-4" /> {confirmLabel === 'Deactivate' ? t('confirmDialog.deactivate') : confirmLabel}
          </button>
        </>
      }
    >
      <div className="text-center">
        <div className={`flex justify-center mb-4 ${isDanger ? 'text-red-500' : 'text-yellow-500'}`}>
          <div className={`${isDanger ? 'bg-red-500/20' : 'bg-yellow-500/20'} rounded-full p-4`}>
            <span className="icon-[tabler--alert-triangle] text-4xl" />
          </div>
        </div>
        <h2 className="text-xl font-bold text-base-content mb-2">{title}</h2>
        <p className="text-base-content/70">{message}</p>
        <p className="text-base-content font-semibold text-lg mt-1 mb-2">{itemName}?</p>
        {description && (
          <p className="text-base-content/50 text-sm mb-2">{description}</p>
        )}
      </div>
    </Modal>
  );
}
