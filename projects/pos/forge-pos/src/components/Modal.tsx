import { motion, AnimatePresence } from 'framer-motion';
import { MdClose } from 'react-icons/md';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  borderColor?: string;
}

const sizeClasses: Record<string, string> = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-xl',
  xl: 'max-w-4xl',
  full: 'max-w-6xl',
};

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  borderColor,
}: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className={`bg-white dark:bg-slate-800 rounded-xl p-6 w-full ${sizeClasses[size]} max-h-[90vh] overflow-y-auto transition-colors duration-300
              ${borderColor ? `border-2 ${borderColor}` : ''}`}
          >
            <div className="flex items-center mb-4">
              {title ? (
                <h2 className="flex-1 text-xl font-bold text-slate-900 dark:text-white">{title}</h2>
              ) : (
                <div className="flex-1" />
              )}
              <button
                onClick={onClose}
                className="text-slate-500 hover:text-slate-700 dark:hover:text-white transition-colors rounded-lg p-1"
              >
                <MdClose className="w-6 h-6" />
              </button>
            </div>
            <div className="space-y-4">{children}</div>
            {footer && <div className="flex gap-3 pt-4 mt-2 border-t border-slate-300 dark:border-white/10">{footer}</div>}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
