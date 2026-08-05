import Modal from './Modal';
import { useTranslation } from 'react-i18next';
import { FaExclamationTriangle } from 'react-icons/fa';
import { MdDelete } from 'react-icons/md';

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
            className="flex-1 py-3 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
          >
            {t('confirmDialog.cancel')}
          </button>
          <button
            onClick={onConfirm}
            className={`flex-1 py-3 rounded-lg text-white font-semibold flex items-center justify-center gap-2 transition-colors ${
              isDanger ? 'bg-red-500 hover:bg-red-600' : 'bg-yellow-500 hover:bg-yellow-600'
            }`}
          >
            <MdDelete className="w-4 h-4" /> {confirmLabel === 'Deactivate' ? t('confirmDialog.deactivate') : confirmLabel}
          </button>
        </>
      }
    >
      <div className="text-center">
        <div className={`flex justify-center mb-4 ${isDanger ? 'text-red-500' : 'text-yellow-500'}`}>
          <div className={`${isDanger ? 'bg-red-500/20' : 'bg-yellow-500/20'} rounded-full p-4`}>
            <FaExclamationTriangle className="text-4xl" />
          </div>
        </div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{title}</h2>
        <p className="text-slate-600 dark:text-gray-300">{message}</p>
        <p className="text-slate-900 dark:text-white font-semibold text-lg mt-1 mb-2">{itemName}?</p>
        {description && (
          <p className="text-slate-500 dark:text-gray-400 text-sm mb-2">{description}</p>
        )}
      </div>
    </Modal>
  );
}
