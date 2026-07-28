import { motion, AnimatePresence } from 'framer-motion';

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
          className={`fixed bottom-8 left-1/2 -translate-x-1/2 z-50 cursor-pointer
            ${type === 'success' ? 'alert alert-success' : 'alert alert-error'}`}
        >
          {type === 'success' 
            ? <span className="icon-[tabler--check] text-xl" /> 
            : <span className="icon-[tabler--alert-triangle] text-xl" />}
          <span>{message}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
