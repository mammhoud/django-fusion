import AnimatePresence from '../../components/ui/AnimatePresence';
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
        <div
          role="alert"
          onClick={onDismiss}
          className={`fixed bottom-8 left-1/2 -translate-x-1/2 z-50 cursor-pointer
            ${type === 'success' ? 'alert alert-success' : 'alert alert-error'}`}
        >
          {type === 'success' 
            ? <span className="ri-check-line text-xl" /> 
            : <span className="ri-alert-line text-xl" />}
          <span>{message}</span>
        </div>
      )}
    </AnimatePresence>
  );
}
