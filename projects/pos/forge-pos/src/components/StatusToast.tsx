import { motion, AnimatePresence } from 'framer-motion';
import { FaCheck, FaExclamationTriangle } from 'react-icons/fa';

interface StatusToastProps {
  type: 'success' | 'error';
  message: string;
  visible: boolean;
  onDismiss?: () => void;
}

export default function StatusToast({ type, message, visible, onDismiss }: StatusToastProps) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          onClick={onDismiss}
          className={`fixed bottom-8 left-1/2 -translate-x-1/2 px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg z-50 cursor-pointer
            ${type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'}`}
        >
          {type === 'success' ? <FaCheck className="text-xl" /> : <FaExclamationTriangle className="text-xl" />}
          <span>{message}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
