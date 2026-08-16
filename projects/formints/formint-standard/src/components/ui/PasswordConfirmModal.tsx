import { useState, useEffect, useRef } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import Modal from './Modal';

export type ImportMode = 'append' | 'replace';

interface PasswordConfirmModalProps {
  isOpen: boolean;
  /** Modal title — e.g. "Import Database" */
  title: string;
  /** Body description — explains what the action will do */
  description: string;
  /** Label for the confirm button */
  confirmLabel: string;
  variant?: 'default' | 'danger';
  /** When true and a user is signed in, the password is required and verified
      (via login_user) before onConfirm fires. When no account exists the
      confirm button acts directly. */
  requirePassword?: boolean;
  /** Show the append/replace import-mode selector */
  showModeSelector?: boolean;
  mode?: ImportMode;
  onModeChange?: (mode: ImportMode) => void;
  onClose: () => void;
  /** Called after the password is verified (or immediately when not required) */
  onConfirm: () => void;
}

const MODE_OPTIONS: { id: ImportMode; icon: string; titleKey: string; descKey: string }[] = [
  { id: 'append', icon: 'ri-add-circle-line', titleKey: 'passwordConfirm.modeAppend', descKey: 'passwordConfirm.modeAppendDesc' },
  { id: 'replace', icon: 'ri-database-2-line', titleKey: 'passwordConfirm.modeReplace', descKey: 'passwordConfirm.modeReplaceDesc' },
];

export default function PasswordConfirmModal({
  isOpen,
  title,
  description,
  confirmLabel,
  variant = 'default',
  requirePassword = true,
  showModeSelector = false,
  mode = 'replace',
  onModeChange,
  onClose,
  onConfirm,
}: PasswordConfirmModalProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState('');
  const passwordRef = useRef<HTMLInputElement>(null);
  const isOpenRef = useRef(isOpen);

  const needsPassword = requirePassword && !!user;

  // Reset internal state every time the dialog opens.
  useEffect(() => {
    isOpenRef.current = isOpen;
    if (isOpen) {
      setPassword('');
      setShowPassword(false);
      setError('');
      setIsVerifying(false);
    }
  }, [isOpen]);

  const handleConfirm = async () => {
    if (isVerifying) return;
    if (needsPassword) {
      if (!password) {
        setError(t('passwordConfirm.passwordRequired'));
        return;
      }
      setIsVerifying(true);
      setError('');
      try {
        await invoke('login_user', { email: user!.email, password });
        // Ignore the result if the dialog was dismissed mid-verification.
        if (!isOpenRef.current) return;
        onConfirm();
      } catch {
        if (!isOpenRef.current) return;
        setError(t('passwordConfirm.incorrectPassword'));
      } finally {
        if (isOpenRef.current) setIsVerifying(false);
      }
      return;
    }
    onConfirm();
  };

  const isDanger = variant === 'danger';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      size="sm"
      variant={variant}
      initialFocusRef={needsPassword ? passwordRef : undefined}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="btn btn-ghost flex-1"
            disabled={isVerifying}
          >
            {t('confirmDialog.cancel')}
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={isVerifying}
            className={`btn flex-1 ${isDanger ? 'btn-error' : 'btn-primary'}`}
          >
            {isVerifying ? (
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : (
              <span className="ri-lock-2-line ri-16px" />
            )}
            <span>{confirmLabel}</span>
          </button>
        </>
      }
    >
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className={`modal__body-icon ${isDanger ? 'modal__body-icon--danger' : ''}`}>
            <span className={showModeSelector ? 'ri-database-2-line text-4xl' : 'ri-lock-2-line text-4xl'} />
          </div>
        </div>
        <h2 className="modal__title text-xl font-bold mb-2">{title}</h2>
        <p className="text-base-content/70">{description}</p>
      </div>

      {showModeSelector && (
        <div className="mt-5">
          <p className="text-sm font-semibold text-base-content mb-2 text-center">
            {t('passwordConfirm.importModeTitle')}
          </p>
          <div className="grid grid-cols-1 gap-2">
            {MODE_OPTIONS.map((opt) => {
              const isActive = mode === opt.id;
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => onModeChange?.(opt.id)}
                  aria-pressed={isActive}
                  className={`flex items-start gap-3 p-3 rounded-xl text-left transition-all duration-200 border-2 ${
                    isActive
                      ? 'border-primary bg-primary/10'
                      : 'border-base-300/60 bg-base-100/50 hover:border-base-300'
                  }`}
                >
                  <span className={`${opt.icon} ri-20px mt-0.5 ${isActive ? 'text-primary' : 'text-base-content/50'}`} />
                  <span className="min-w-0">
                    <span className={`block text-sm font-semibold ${isActive ? 'text-primary' : 'text-base-content'}`}>
                      {t(opt.titleKey)}
                    </span>
                    <span className="block text-xs text-base-content/50 mt-0.5">{t(opt.descKey)}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {needsPassword && (
        <div className="mt-5">
          <label htmlFor="password-confirm-input" className="label-text block text-sm mb-1.5">{t('passwordConfirm.passwordLabel')}</label>
          <div className="relative">
            <input
              id="password-confirm-input"
              ref={passwordRef}
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError('');
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleConfirm();
                }
              }}
              placeholder="••••••••"
              autoComplete="current-password"
              className="input w-full pe-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword((s) => !s)}
              aria-pressed={showPassword}
              aria-label={t('auth.showPassword')}
              className="absolute inset-y-0 end-2 my-auto flex items-center justify-center text-base-content/50 hover:text-base-content transition-colors"
            >
              <span className={showPassword ? 'ri-eye-off-line ri-18px' : 'ri-eye-line ri-18px'} />
            </button>
          </div>
          {error && (
            <p role="alert" className="mt-2 text-sm text-error flex items-center gap-1.5">
              <span className="ri-alert-line ri-14px" />
              {error}
            </p>
          )}
        </div>
      )}
    </Modal>
  );
}
