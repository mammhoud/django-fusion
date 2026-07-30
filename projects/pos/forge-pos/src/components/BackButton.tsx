import { motion } from 'framer-motion';
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
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex items-center gap-2 px-4 py-2 rounded-lg min-w-[120px] justify-center
        bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 font-medium text-sm
        disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.96] transition-all"
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
          <span className="icon-[tabler--arrow-back] w-4 h-4 rtl:scale-x-[-1] shrink-0" />
          <span>{displayText}</span>
        </>
      )}
    </button>
  );
}
