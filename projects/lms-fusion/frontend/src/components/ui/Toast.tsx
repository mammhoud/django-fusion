'use client';

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HiCheckCircle,
  HiXCircle,
  HiExclamationCircle,
  HiInformationCircle,
  HiX,
} from 'react-icons/hi';

// ── Types ──

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  success: (title: string, message?: string, duration?: number) => string;
  error: (title: string, message?: string, duration?: number) => string;
  warning: (title: string, message?: string, duration?: number) => string;
  info: (title: string, message?: string, duration?: number) => string;
  clearAll: () => void;
}

// ── Icons & Colors ──

const toastConfig: Record<ToastType, { icon: React.ReactNode; bg: string; border: string }> = {
  success: {
    icon: <HiCheckCircle className="w-5 h-5 text-green-500" />,
    bg: 'bg-green-50',
    border: 'border-green-200',
  },
  error: {
    icon: <HiXCircle className="w-5 h-5 text-red-500" />,
    bg: 'bg-red-50',
    border: 'border-red-200',
  },
  warning: {
    icon: <HiExclamationCircle className="w-5 h-5 text-amber-500" />,
    bg: 'bg-amber-50',
    border: 'border-amber-200',
  },
  info: {
    icon: <HiInformationCircle className="w-5 h-5 text-blue-500" />,
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
};

// ── Context ──

const ToastContext = createContext<ToastContextValue | null>(null);

let toastCounter = 0;
function generateId() {
  toastCounter += 1;
  return `toast-${Date.now()}-${toastCounter}`;
}

// ── Provider ──

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>): string => {
      const id = generateId();
      const newToast: Toast = { ...toast, id };
      setToasts((prev) => [...prev, newToast]);

      const duration = toast.duration ?? 5000;
      if (duration > 0) {
        setTimeout(() => removeToast(id), duration);
      }
      return id;
    },
    [removeToast],
  );

  const success = useCallback(
    (title: string, message?: string, duration?: number) =>
      addToast({ type: 'success', title, message, duration }),
    [addToast],
  );
  const error = useCallback(
    (title: string, message?: string, duration?: number) =>
      addToast({ type: 'error', title, message, duration }),
    [addToast],
  );
  const warning = useCallback(
    (title: string, message?: string, duration?: number) =>
      addToast({ type: 'warning', title, message, duration }),
    [addToast],
  );
  const info = useCallback(
    (title: string, message?: string, duration?: number) =>
      addToast({ type: 'info', title, message, duration }),
    [addToast],
  );
  const clearAll = useCallback(() => setToasts([]), []);

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, success, error, warning, info, clearAll }}
    >
      {children}
      {/* Toast Container */}
      <div
        className="fixed top-4 right-4 z-[300] flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        aria-live="polite"
        aria-relevant="additions removals"
      >
        <AnimatePresence mode="popLayout">
          {toasts.map((toast) => {
            const config = toastConfig[toast.type];
            return (
              <motion.div
                key={toast.id}
                layout
                initial={{ opacity: 0, x: 100, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 100, scale: 0.95 }}
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                className={`pointer-events-auto ${config.bg} border ${config.border} 
                  rounded-xl shadow-lg p-4 flex items-start gap-3`}
                role="alert"
              >
                <div className="flex-shrink-0 mt-0.5">{config.icon}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900">{toast.title}</p>
                  {toast.message && (
                    <p className="text-xs text-gray-600 mt-0.5">{toast.message}</p>
                  )}
                  {toast.action && (
                    <button
                      onClick={() => {
                        toast.action!.onClick();
                        removeToast(toast.id);
                      }}
                      className="mt-2 text-xs font-medium text-[rgb(var(--ctc-primary))] 
                        hover:text-[rgb(var(--ctc-primary-dark))] underline underline-offset-2"
                    >
                      {toast.action.label}
                    </button>
                  )}
                </div>
                <button
                  onClick={() => removeToast(toast.id)}
                  className="flex-shrink-0 p-0.5 text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Dismiss"
                >
                  <HiX className="w-4 h-4" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

// ── Hook ──

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error('useToast must be used within a <ToastProvider>');
  }
  return ctx;
}

// ── Toast hook shortcut ──

export function useNotify() {
  const toast = useToast();
  return {
    success: toast.success,
    error: toast.error,
    warning: toast.warning,
    info: toast.info,
  };
}
