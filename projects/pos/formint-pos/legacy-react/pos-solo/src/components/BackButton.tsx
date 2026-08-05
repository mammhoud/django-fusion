import { motion } from 'framer-motion';
import { MdArrowBack } from 'react-icons/md';
import { useTranslation } from 'react-i18next';

interface BackButtonProps {
  onClick: () => void;
  disabled?: boolean;
  text?: string;
}export default function BackButton({
  onClick,
  disabled = false,
  text,
}: BackButtonProps) {
  const { t } = useTranslation();
  const displayText = text || t('common.back');

  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.96 }}
      onClick={onClick}
      disabled={disabled}
      className="flex items-center gap-2 px-4 py-2 rounded-lg min-w-[120px] justify-center
        card--glass font-medium text-sm
        disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {disabled ? (
        <>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-4 h-4 border-2 border-slate-500 dark:border-slate-300 border-t-transparent rounded-full shrink-0"
          />
          <span>{t('common.loading')}</span>
        </>
      ) : (
        <>
          <MdArrowBack className="w-4 h-4 u-rtl-flip shrink-0" />
          <span>{displayText}</span>
        </>
      )}
    </motion.button>
  );
}
