import { useState, useEffect, type ReactNode } from 'react';
// react-icons/fa no longer needed — all icons migrated to Remix
import { useAuth } from '../../contexts/AuthContext';
import { useTheme, type ThemeVariant } from '../../contexts/ThemeContext';
import { useTranslation } from 'react-i18next';
import LanguageToggle from '../../components/display/LanguageToggle';
import { invoke } from '@tauri-apps/api/core';
import { iconClass, Ic } from '../../lib/icons';
import AnimatePresence from '../../components/ui/AnimatePresence';
import posCrest from '../../../assets/images/pos-crest.svg';

type AuthStep = 'loading' | 'checking' | 'register' | 'verify' | 'login' | 'forgotPassword' | 'resetPassword';

// Heroicon eye icons for the show/hide password toggles
const EyeIcon = Ic('hi:eye');
const EyeSlashIcon = Ic('hi:eye-slash');

// ── Floating brand icons for the illustration panel ──
const BRAND_ICONS = [
  { icon: 'building-store', delay: 0, x: '15%', y: '15%', size: 'w-10 h-10', color: 'text-white/30' },
  { icon: 'chart-line', delay: 0.3, x: '75%', y: '20%', size: 'w-12 h-12', color: 'text-white/20' },
  { icon: 'tools', delay: 0.6, x: '20%', y: '70%', size: 'w-11 h-11', color: 'text-white/25' },
  { icon: 'tools-kitchen-2', delay: 0.9, x: '70%', y: '75%', size: 'w-9 h-9', color: 'text-white/30' },
  { icon: 'clipboard-list', delay: 1.2, x: '45%', y: '10%', size: 'w-8 h-8', color: 'text-white/20' },
];

// ── Floating particles for background ──
const PARTICLES = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  size: Math.random() * 4 + 2,
  x: Math.random() * 100,
  y: Math.random() * 100,
  duration: Math.random() * 3 + 4,
  delay: Math.random() * 5,
}));

// ── Per-variant illustration panel gradients ──
const ILLUSTRATION_GRADIENTS: Record<ThemeVariant, string> = {
  default:   'from-primary via-primary/80 to-primary/70',
  corporate: 'from-info via-primary to-info/80',
  luxury:    'from-warning via-warning/80 to-warning/70',
  pastel:    'from-secondary via-accent to-primary',
  perplexity: 'from-info via-primary to-secondary',
};

export default function Auth() {
  const { t, i18n } = useTranslation();
  const {
    isLoading,
    login,
    setupAccount,
    sendConfirmationCode,
    skipAuth,
    isAuthRequired,
  } = useAuth();

  const [step, setStep] = useState<AuthStep>('loading');
  const [hasExistingUsers, setHasExistingUsers] = useState(() => false);
  const [email, setEmail] = useState(() => '');
  const [name, setName] = useState(() => '');
  const [password, setPassword] = useState(() => '');
  const [confirmPassword, setConfirmPassword] = useState(() => '');
  const [code, setCode] = useState(() => '');
  const [error, setError] = useState(() => '');
  const [success, setSuccess] = useState(() => '');
  const [codeSending, setCodeSending] = useState(() => false);
  const [resetCode, setResetCode] = useState(() => '');
  const [resetPassword, setResetPassword] = useState(() => '');
  const [resetConfirmPassword, setResetConfirmPassword] = useState(() => '');
  const [selectedRole, setSelectedRole] = useState<'manager' | 'employee'>('manager');
  // Password visibility toggles — React state (reliable, works with the
  // dynamically-rendered form panels; FlyonUI's data-toggle-password JS
  // binding never fires for these inputs).
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showRegisterConfirm, setShowRegisterConfirm] = useState(false);
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);


  // Determine initial step on mount
  useEffect(() => {
    const isBrowserMode = typeof window !== 'undefined' && !('__TAURI_INTERNALS__' in window);

    if (isBrowserMode) {
      // Running in a browser without Tauri backend — skip auth gracefully
      console.log('Auth: browser mode detected, skipping auth');
      try { skipAuth(); } catch { /* ignore */ }
      return;
    }

    const init = async () => {
      setStep('checking');
      try {
        const required = await invoke<boolean>('check_auth_required');
        if (required) {
          const hasUsers = await invoke<boolean>('has_users');
          setHasExistingUsers(hasUsers);
          setStep(hasUsers ? 'login' : 'register');

          if (hasUsers) {
            const superEmail = await invoke<string | null>('get_superuser_email');
            if (superEmail) {
              setEmail(superEmail);
            }
          }
        } else {
          setStep('login');
        }
      } catch (err) {
        console.error('Auth init error (Tauri backend unavailable):', err);
        // Tauri backend unavailable — fall back to skip mode
        try { skipAuth(); } catch { /* ignore */ }
      }
    };
    init();
  }, [skipAuth]);

  // Auto-dismiss errors after 6 seconds
  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(''), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  const handleSendCode = async () => {
    clearMessages();
    if (!email.trim()) {
      setError(t('auth.validationEmailRequired'));
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError(t('auth.validationEmailInvalid'));
      return;
    }

    setCodeSending(true);
    try {
      await sendConfirmationCode(email.trim());
      setStep('verify');
      setSuccess(t('auth.codeSent'));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setCodeSending(false);
    }
  };

  const handleRegister = async () => {
    clearMessages();
    if (!name.trim()) { setError(t('auth.validationNameRequired')); return; }
    if (!email.trim()) { setError(t('auth.validationEmailRequired')); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setError(t('auth.validationEmailInvalid')); return; }
    if (!code.trim()) { setError(t('auth.validationCodeRequired')); return; }
    if (!password) { setError(t('auth.validationPasswordRequired')); return; }
    if (password.length < 6) { setError(t('auth.validationPasswordLength')); return; }
    if (password !== confirmPassword) { setError(t('auth.validationPasswordMatch')); return; }

    try {
      await setupAccount(email.trim(), code.trim(), password, name.trim(), true);
      setSuccess(t('auth.accountCreated'));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const handleLogin = async () => {
    clearMessages();
    if (!email.trim()) { setError(t('auth.validationEmailRequired')); return; }
    if (!password) { setError(t('auth.validationPasswordRequired')); return; }

    try {
      await login(email.trim(), password, true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  // Selecting a role only pre-fills demo credentials — the actual login
  // happens via the Sign In button, so the page never reloads/navigates away.
  const selectRole = (role: 'manager' | 'employee') => {
    clearMessages();
    setSelectedRole(role);
    if (role === 'employee') {
      // Employee — use demo credentials
      setEmail('employee@restaurant.com');
      setPassword('secret123');
    } else {
      // Manager — keep the current email (or superuser email if already loaded)
      setEmail(email || 'manager@restaurant.com');
      setPassword(password || 'secret123');
    }
  };

  const switchToRegister = () => {
    clearMessages();
    setCode('');
    setPassword('');
    setConfirmPassword('');
    setStep('register');
  };

  const switchToLogin = () => {
    clearMessages();
    setResetCode('');
    setResetPassword('');
    setResetConfirmPassword('');
    setStep('login');
  };

  const handleForgotPassword = () => {
    clearMessages();
    setResetCode('');
    setResetPassword('');
    setResetConfirmPassword('');
    setStep('forgotPassword');
  };

  const handleRequestReset = async () => {
    clearMessages();
    if (!email.trim()) {
      setError(t('auth.validationEmailRequired'));
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError(t('auth.validationEmailInvalid'));
      return;
    }

    setCodeSending(true);
    try {
      await invoke('request_password_reset', { email: email.trim() });
      setSuccess(t('auth.resetCodeSent'));
      setStep('resetPassword');
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setCodeSending(false);
    }
  };

  const handleResetPassword = async () => {
    clearMessages();
    if (!resetCode.trim()) { setError(t('auth.validationCodeRequired')); return; }
    if (!resetPassword) { setError(t('auth.validationPasswordRequired')); return; }
    if (resetPassword.length < 6) { setError(t('auth.validationPasswordLength')); return; }
    if (resetPassword !== resetConfirmPassword) { setError(t('auth.validationPasswordMatch')); return; }

    try {
      await invoke('reset_password_cmd', {
        email: email.trim(),
        code: resetCode.trim(),
        newPassword: resetPassword,
      });
      setSuccess(t('auth.passwordResetSuccess'));
      // Auto-switch to login after successful reset
      setTimeout(() => switchToLogin(), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const isRtl = i18n.language === 'ar';
  const { variant, mode } = useTheme();
  const isDark = mode === 'dark';

  // ── Decorative pattern SVG lines (visible in both light and dark) ──
  const renderDecorativePattern = (opacityClass = 'opacity-[0.04]') => (
    <svg
      className={`absolute inset-0 w-full h-full pointer-events-none ${opacityClass} ${isDark ? 'text-white' : 'text-slate-300'}`}
      viewBox="0 0 800 600"
      preserveAspectRatio="none"
    >
      <defs>
        <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
          <path d="M 60 0 L 0 0 0 60" fill="none" stroke="currentColor" strokeWidth="0.5" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>
  );

  // ── Card with theme-responsive styling ──
  const CardWrapper = ({ children, className = '' }: { children: ReactNode; className?: string }) => {
    const cardBase = isDark
      ? 'card bg-white/10 backdrop-blur-xl border border-white/10 shadow-2xl shadow-white/5'
      : 'card bg-white border border-slate-200 shadow-xl shadow-slate-200/50';
    const decoColor = isDark ? 'text-primary/80' : 'text-primary/10';
    return (
      <div className={`${cardBase} relative overflow-hidden ${className}`}>
        <div className={`absolute -top-24 -right-24 w-72 h-72 opacity-[0.06] pointer-events-none ${decoColor}`}>
          <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
            <path d="M100 0C155.228 0 200 44.7715 200 100C200 155.228 155.228 200 100 200C44.7715 200 0 155.228 0 100C0 44.7715 44.7715 0 100 0Z" fill="currentColor" />
            <circle cx="100" cy="100" r="60" fill="currentColor" opacity="0.6" />
            <circle cx="100" cy="100" r="30" fill="currentColor" opacity="0.3" />
          </svg>
        </div>
        {children}
      </div>
    );
  };

  // ── Shared form label ──
  const labelClass = `block text-sm font-medium mb-1.5 ${isDark ? 'text-white/70' : 'text-slate-600'}`;

  // ── Input group with theme-responsive styling ──
  const inputBg = isDark ? 'bg-white/5 border-white/20' : 'bg-slate-50 border-slate-200';
  const inputPlaceholder = isDark ? 'placeholder:text-white/30' : 'placeholder:text-slate-400';
  const inputText = isDark ? 'text-white' : 'text-slate-900';
  const inputIcon = isDark ? 'text-white/40' : 'text-slate-400';
  const inputFocus = isDark ? 'focus-within:border-primary/60 focus-within:ring-teal-400/20' : 'focus-within:border-primary focus-within:ring-primary/10';
  
  const InputWrapper = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
    <div className={`input flex items-center gap-3 w-full px-4 py-3 rounded-xl border
      ${inputBg} ${inputFocus} focus-within:ring-2 transition-all duration-200 ${className}`}>
      {children}
    </div>
  );

  // ── FlyonUI primary button with spring animations ──
  const PrimaryButton = ({ onClick, disabled, loading, children, gradient = 'from-primary to-primary/80' }: {
    onClick: () => void; disabled?: boolean; loading?: boolean; children: React.ReactNode; gradient?: string;
  }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn w-full bg-linear-to-r ${gradient} hover:from-primary/60 hover:to-primary/40
        text-white rounded-xl font-semibold border-0
        flex items-center justify-center gap-2 h-12
        disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] transition-all`}
    >
      {loading ? (
        <span className="loading loading-spinner loading-sm" />
      ) : children}
    </button>
  );

  // ── Illustration Panel ──
  const renderIllustration = () => (
    <div className={`relative hidden lg:flex lg:w-1/2 bg-linear-to-br ${ILLUSTRATION_GRADIENTS[variant]} p-8 xl:p-12 items-center justify-center overflow-hidden`}>
      {/* Animated background particles */}
      {PARTICLES.map(p => (
        <div
          key={p.id}
          className="absolute rounded-full bg-white/10"
          style={{
            width: p.size,
            height: p.size,
            left: `${p.x}%`,
            top: `${p.y}%`,
          }}
        />
      ))}

      {/* Floating brand icons */}
      {BRAND_ICONS.map(({ icon: iconName, delay, x, y, size, color }) => (
        <div
          key={delay}
          className={`absolute ${size} ${color}`}
          style={{ left: x, top: y }}
        >
          <span className={iconClass(iconName, 'w-full h-full')} />
        </div>
      ))}

      {/* Central Branding */}
      <div
        className="relative z-10 text-center max-w-md"
      >
        <div className="bg-white/15 backdrop-blur-xl rounded-3xl p-6 w-fit mx-auto mb-8 border border-white/20 shadow-2xl">
          <span className="ri-shield-line w-16 h-16 text-white" />
        </div>
        <h1 className="text-4xl xl:text-5xl font-bold text-white mb-4 leading-tight">
          Forge POS
        </h1>
        <p className="text-lg text-white/70 leading-relaxed">
          {step === 'login' ? t('auth.loginDesc') : t('auth.registerDesc')}
        </p>

        {/* Feature highlights */}
        <div className="mt-10 space-y-4 text-left">
          {[
            { icon: 'building-store', text: 'Point of Sale & Order Management' },
            { icon: 'chart-line', text: 'Real-time Analytics & Reports' },
            { icon: 'tools-kitchen-2', text: 'Inventory & Recipe Tracking' },
          ].map(({ icon: iconName, text }, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 text-white/80"
            >
              <div className="bg-white/15 rounded-lg p-2">
                <span className={iconClass(iconName, 'w-4 h-4')} />
              </div>
              <span className="text-sm font-medium">{text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // ── Form Panel step classes ──
  const FORM_PANEL_CLASS = 'w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-6 md:p-8 xl:p-12 relative overflow-y-auto min-h-screen lg:min-h-0';

  // ── Toast backgrounds (moved near other computed classes for consistency) ──
  const toastBg = isDark ? 'bg-red-500/95' : 'bg-red-500';
  const toastSuccessBg = isDark ? 'bg-primary/95' : 'bg-primary';
  
  const renderToasts = () => (
    <>
      <AnimatePresence>
        {error && (
          <div
            className={`fixed bottom-6 left-1/2 -translate-x-1/2 backdrop-blur-md text-white
              px-5 py-3 rounded-2xl shadow-2xl z-50 max-w-md text-center border border-red-400/30
              flex items-center gap-3 shadow-red-500/20 ${toastBg}`}
          >
            <div className="w-2 h-2 rounded-full bg-white animate-pulse shrink-0" />
            <span className="text-sm font-medium">{error}</span>
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {success && (
          <div
            className={`fixed bottom-24 left-1/2 -translate-x-1/2 backdrop-blur-md text-primary-content
              px-5 py-3 rounded-2xl shadow-2xl z-50 max-w-md text-center border border-primary/30
              flex items-center gap-3 shadow-primary/20 ${toastSuccessBg}`}
          >
            <span className="ri-check-line ri-16px shrink-0" />
            <span className="text-sm font-medium">{success}</span>
          </div>
        )}
      </AnimatePresence>
    </>
  );

  // ── Brand Logo chip — uses the pos-crest.svg crest (same as app chrome) ──
  const BrandLogo = () => (
    <div className="flex items-center gap-2.5 mb-4">
      <div className={`bg-linear-to-br ${ILLUSTRATION_GRADIENTS[variant]} rounded-lg p-1.5 shadow-lg`}>
        <img src={posCrest} alt="Forge POS" className="w-6 h-6 object-contain rounded-md" />
      </div>
      <span className={`text-lg font-bold ${isDark ? 'text-white/80' : 'text-slate-800'}`}>Forge POS</span>
    </div>
  );

  // ── Theme-responsive computed classes ──
  const textHeading = isDark ? 'text-white' : 'text-slate-900';
  const textMuted = isDark ? 'text-white/50' : 'text-slate-400';
  const textLink = isDark ? 'text-primary/80 hover:text-primary/70' : 'text-primary hover:text-primary/600';
  const formPanelOverlay = isDark
    ? 'bg-linear-to-br from-primary/20 via-base-200 to-primary/20'
    : 'bg-linear-to-br from-primary/5 via-base-200 to-primary/5';

  // ── Auth header ──
  const AuthHeader = ({ title, desc }: { title: string; desc: string }) => (
    <div className="mb-6">
      <h2 className={`text-2xl font-bold mb-1 ${textHeading}`}>{title}</h2>
      <p className={`text-sm ${textMuted}`}>{desc}</p>
    </div>
  );

  return (
    <div
      className={`min-h-screen flex ${isRtl ? 'rtl flex-row-reverse' : 'ltr'}`}
      dir={isRtl ? 'rtl' : 'ltr'}
    >
      {/* Top-right toggles */}
      <div className="fixed top-4 right-4 flex items-center gap-3 z-50">
        <LanguageToggle dropdownUp={false} />
      </div>

      {/* Illustration Panel */}
      <div
        className="hidden lg:flex lg:w-1/2"
      >
        {renderIllustration()}
      </div>

      {/* Form Panel */}
      <AnimatePresence mode="wait">
        {step === 'checking' && (
          <div
            key="checking"
            className="w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-6 md:p-8 xl:p-12 min-h-screen lg:min-h-0"
          >
            <div className="text-center">
              <div className="relative w-20 h-20 mx-auto mb-6">
                <div className="absolute inset-0 border-4 border-primary/30 border-t-teal-400 rounded-full animate-spin" />
                <div className="absolute inset-2 border-4 border-success/20 border-b-emerald-400 rounded-full animate-spin [animation-direction:reverse]" />
              </div>
              <p
                className={`text-lg ${isDark ? 'text-white/60' : 'text-slate-500'} animate-pulse`}
              >
                {t('auth.checking')}
              </p>
            </div>
          </div>
        )}

        {step === 'register' && (
          <div
            key="register"
            className={FORM_PANEL_CLASS}
          >
            {/* Background overlay — theme-responsive */}
            <div className={`absolute inset-0 ${formPanelOverlay} lg:hidden`} />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              {/* Register — Step 1: Send Code */}
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                <BrandLogo />
                <AuthHeader title={t('auth.createAccount')} desc={t('auth.registerDesc')} />

                <div className="space-y-4">
                  {/* Name */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-user-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.fullName')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-user-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder={t('auth.namePlaceholder')}
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                        autoFocus
                      />
                    </InputWrapper>
                  </div>

                  {/* Email */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-mail-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.email')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-mail-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="manager@restaurant.com"
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendCode()}
                      />
                    </InputWrapper>
                  </div>

                  {/* Send Code */}
                  <PrimaryButton
                    onClick={handleSendCode}
                    disabled={codeSending || !email.trim()}
                    loading={codeSending}
                    gradient="from-primary to-primary/80"
                  >
                    <span className="ri-key-line text-sm" />
                    {t('auth.sendCode')}
                  </PrimaryButton>
                </div>

                {/* Switch to Login */}
                <div className="mt-6 text-center">
                  <p className={`text-sm ${textMuted}`}>
                    {t('auth.alreadyHaveAccount')}{' '}
                    <button
                      onClick={switchToLogin}
                      className={`font-medium transition-colors hover:underline ${textLink}`}
                    >
                      {t('auth.signIn')}
                    </button>
                  </p>
                </div>
              </CardWrapper>
            </div>
          </div>
        )}

        {step === 'verify' && (
          <div
            key="verify"
            className={FORM_PANEL_CLASS}
          >
            {/* Background overlay — theme-responsive */}
            <div className={`absolute inset-0 ${formPanelOverlay} lg:hidden`} />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                <BrandLogo />
                <AuthHeader
                  title={t('auth.verifyEmail')}
                  desc={`${t('auth.verifyDesc')} `}
                />
                <p className={`text-sm font-medium -mt-4 mb-6 text-center ${isDark ? 'text-primary/80' : 'text-primary'}`}>{email}</p>

                <div className="space-y-4">
                  {/* Code Input */}
                  <div>
                    <label className={labelClass}>{t('auth.confirmationCode')}</label>
                    <div className="flex justify-center gap-2 sm:gap-3 mb-1">
                      {[0, 1, 2, 3, 4, 5].map((i) => (
                        <div
                          key={i}
                          className={`w-10 h-12 sm:w-12 sm:h-14 rounded-xl border-2 flex items-center justify-center
                            text-xl font-bold font-mono transition-all duration-200
                            ${code.length > i
                              ? 'border-primary bg-primary/20 shadow-lg shadow-teal-500/10 text-white'
                              : code.length === i
                                ? 'border-primary/60 animate-pulse ' + (isDark ? 'bg-white/10 text-white' : 'bg-primary/5 text-slate-700')
                                : (isDark ? 'border-white/10 bg-white/5 text-white' : 'border-slate-200 bg-slate-50 text-slate-400')
                            }`}
                        >
                          {code[i] || ''}
                        </div>
                      ))}
                    </div>
                    <input
                      type="text"
                      value={code}
                      onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                      placeholder="000000"
                      maxLength={6}
                      className="sr-only"
                      autoFocus
                      aria-label="Confirmation code"
                    />
                  </div>

                  {/* Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-lock-2-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.password')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-lock-2-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        id="register-password"
                        type={showRegisterPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowRegisterPassword(s => !s)}
                        aria-pressed={showRegisterPassword}
                        className={`transition-colors shrink-0 ${isDark ? 'text-white/40 hover:text-white/80' : 'text-slate-400 hover:text-slate-600'}`}
                        aria-label={t('auth.showPassword')}
                      >
                        {showRegisterPassword
                          ? <EyeSlashIcon className="size-4 shrink-0" />
                          : <EyeIcon className="size-4 shrink-0" />}
                      </button>
                    </InputWrapper>
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-lock-2-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.confirmPassword')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-lock-2-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        id="register-confirm-password"
                        type={showRegisterConfirm ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowRegisterConfirm(s => !s)}
                        aria-pressed={showRegisterConfirm}
                        className={`transition-colors shrink-0 ${isDark ? 'text-white/40 hover:text-white/80' : 'text-slate-400 hover:text-slate-600'}`}
                        aria-label={t('auth.showPassword')}
                      >
                        {showRegisterConfirm
                          ? <EyeSlashIcon className="size-4 shrink-0" />
                          : <EyeIcon className="size-4 shrink-0" />}
                      </button>
                    </InputWrapper>
                    {confirmPassword && password === confirmPassword && (
                      <p
                        className={`text-xs mt-1 flex items-center gap-1 ${isDark ? 'text-green-400' : 'text-green-600'}`}
                      >
                        <span className="ri-check-line ri-12px" /> Passwords match
                      </p>
                    )}
                  </div>

                  {/* Create Account */}
                  <PrimaryButton
                    onClick={handleRegister}
                    disabled={isLoading || !code.trim() || !password || !confirmPassword}
                    loading={isLoading}
                    gradient="from-primary to-primary/80"
                  >
                    <span className="ri-check-line text-sm" />
                    {t('auth.createAccountBtn')}
                  </PrimaryButton>

                  {/* Resend */}
                  <div className="text-center">
                    <button
                      onClick={handleSendCode}
                      disabled={codeSending}
                      className={`text-sm transition-colors disabled:opacity-40 ${isDark ? 'text-white/40 hover:text-primary/80' : 'text-slate-400 hover:text-primary'}`}
                    >
                      {codeSending ? (
                        <span className="flex items-center justify-center gap-2">
                          <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full inline-block animate-spin" />
                          {t('common.loading')}
                        </span>
                      ) : (
                        t('auth.resendCode')
                      )}
                    </button>
                  </div>
                </div>
              </CardWrapper>
            </div>
          </div>
        )}

        {step === 'login' && (
          <div
            key="login"
            className={FORM_PANEL_CLASS}
          >
            {/* Background overlay — theme-responsive */}
            <div className={`absolute inset-0 ${formPanelOverlay} lg:hidden`} />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                {/* Brand logo + title */}
                <BrandLogo />

                {/* FlyonUI-style "Sign in" header */}
                <AuthHeader title={t('auth.welcomeBack')} desc={t('auth.loginDesc')} />

                {/* Role choice cards — select manager or employee; the active role is lit up */}
                <div className="grid grid-cols-2 gap-2 mb-6" role="group" aria-label={t('auth.roleLabel') || 'Sign in as'}>
                  {(['manager', 'employee'] as const).map((role) => {
                    const isActive = selectedRole === role;
                    return (
                      <button
                        key={role}
                        type="button"
                        onClick={() => selectRole(role)}
                        disabled={isLoading}
                        aria-pressed={isActive}
                        className={`relative flex items-center justify-center gap-2 px-3 py-3 rounded-xl border text-sm font-medium transition-all duration-200
                          disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97]
                          ${isActive
                            ? 'bg-linear-to-r from-primary to-primary/80 text-white border-primary shadow-lg shadow-primary/25 ring-1 ring-primary/40'
                            : isDark
                              ? 'border-white/10 bg-white/5 text-white/60 hover:text-white/80 hover:border-white/25'
                              : 'border-slate-200 bg-slate-50 text-slate-500 hover:text-slate-700 hover:border-slate-300'
                          }`}
                      >
                        <span className={iconClass(role === 'manager' ? 'user-check' : 'user-circle', 'w-4 h-4')} />
                        <span>{role === 'manager' ? (t('auth.roleManager') || 'Manager') : (t('auth.roleEmployee') || 'Employee')}</span>
                        {isActive && (
                          <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-white flex items-center justify-center shadow-md">
                            <span className="ri-check-line ri-12px text-primary" />
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Divider */}
                <div className="flex items-center gap-3 mb-5">
                  <div className={`flex-1 h-px ${isDark ? 'bg-white/10' : 'bg-slate-200'}`} />
                  <span className={`text-xs font-medium ${isDark ? 'text-white/30' : 'text-slate-400'}`}>or</span>
                  <div className={`flex-1 h-px ${isDark ? 'bg-white/10' : 'bg-slate-200'}`} />
                </div>

                {/* Form */}
                <div className="space-y-4">
                  {/* Email */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-mail-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.email')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-mail-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="manager@restaurant.com"
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                        autoFocus
                      />
                    </InputWrapper>
                  </div>

                  {/* Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-lock-2-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.password')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-lock-2-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        id="login-password"
                        type={showLoginPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowLoginPassword(s => !s)}
                        aria-pressed={showLoginPassword}
                        className={`transition-colors shrink-0 ${isDark ? 'text-white/40 hover:text-white/80' : 'text-slate-400 hover:text-slate-600'}`}
                        aria-label={t('auth.showPassword')}
                      >
                        {showLoginPassword
                          ? <EyeSlashIcon className="size-4 shrink-0" />
                          : <EyeIcon className="size-4 shrink-0" />}
                      </button>
                    </InputWrapper>
                  </div>

                  {/* Sign In Button */}
                  <PrimaryButton
                    onClick={handleLogin}
                    disabled={isLoading || !email.trim() || !password}
                    loading={isLoading}
                    gradient="from-primary to-secondary"
                  >
                    <span className="ri-arrow-right-line text-sm rtl:rotate-180" />
                    {t('auth.signIn')}
                  </PrimaryButton>
                </div>

                {/* Forgot Password + Create Account links */}
                <div className="mt-4 text-center">
                  <button
                    onClick={handleForgotPassword}
                    className={`text-xs transition-colors hover:underline ${isDark ? 'text-white/40 hover:text-primary/80' : 'text-slate-400 hover:text-primary'}`}
                  >
                    {t('auth.forgotPassword')}
                  </button>
                </div>

                {!hasExistingUsers && (
                  <div className="mt-6 text-center">
                    <p className={`text-sm ${textMuted}`}>
                      {t('auth.noAccount')}{' '}
                      <button
                        onClick={switchToRegister}
                        className={`font-medium transition-colors hover:underline ${textLink}`}
                      >
                        {t('auth.createOne')}
                      </button>
                    </p>
                  </div>
                )}

                {/* Skip login */}
                {!isAuthRequired && (
                  <div className={`mt-4 text-center border-t pt-4 ${isDark ? 'border-white/10' : 'border-slate-200'}`}>
                    <button
                      onClick={skipAuth}
                      className={`text-xs transition-colors hover:underline ${isDark ? 'text-white/30 hover:text-white/60' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                      Continue without signing in
                    </button>
                  </div>
                )}
              </CardWrapper>
            </div>
          </div>
        )}
        {/* ── Forgot Password: Enter Email ── */}
        {step === 'forgotPassword' && (
          <div
            key="forgotPassword"
            className={FORM_PANEL_CLASS}
          >
            <div className={`absolute inset-0 ${formPanelOverlay} lg:hidden`} />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                <BrandLogo />
                <AuthHeader title={t('auth.forgotPassword')} desc={t('auth.forgotPasswordDesc')} />

                <div className="space-y-4">
                  {/* Email */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-mail-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.email')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-mail-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="manager@restaurant.com"
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                        autoFocus
                        onKeyDown={(e) => e.key === 'Enter' && handleRequestReset()}
                      />
                    </InputWrapper>
                  </div>

                  {/* Send Reset Code */}
                  <PrimaryButton
                    onClick={handleRequestReset}
                    disabled={codeSending || !email.trim()}
                    loading={codeSending}
                    gradient="from-primary to-primary/80"
                  >
                    <span className="ri-key-line text-sm" />
                    {t('auth.sendResetCode')}
                  </PrimaryButton>
                </div>

                {/* Back to Login */}
                <div className="mt-6 text-center">
                  <button
                    onClick={switchToLogin}
                    className={`text-sm transition-colors hover:underline ${isDark ? 'text-white/40 hover:text-primary/80' : 'text-slate-400 hover:text-primary'}`}
                  >
                    <span className="inline-block rtl:rotate-180">←</span> {t('auth.backToLogin')}
                  </button>
                </div>
              </CardWrapper>
            </div>
          </div>
        )}

        {/* ── Reset Password: Enter Code + New Password ── */}
        {step === 'resetPassword' && (
          <div
            key="resetPassword"
            className={FORM_PANEL_CLASS}
          >
            <div className={`absolute inset-0 ${formPanelOverlay} lg:hidden`} />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                <BrandLogo />
                <AuthHeader title={t('auth.resetPassword')} desc={`${t('auth.resetPasswordDesc')} ${email}`} />

                <div className="space-y-4">
                  {/* Reset Code */}
                  <div>
                    <label className={labelClass}>{t('auth.confirmationCode')}</label>
                    <div className="flex justify-center gap-2 sm:gap-3 mb-1">
                      {[0, 1, 2, 3, 4, 5].map((i) => (
                        <div
                          key={i}
                          className={`w-10 h-12 sm:w-12 sm:h-14 rounded-xl border-2 flex items-center justify-center
                            text-xl font-bold font-mono transition-all duration-200
                            ${resetCode.length > i
                              ? 'border-primary bg-primary/20 shadow-lg shadow-teal-500/10 text-white'
                              : resetCode.length === i
                                ? 'border-primary/60 animate-pulse ' + (isDark ? 'bg-white/10 text-white' : 'bg-primary/5 text-slate-700')
                                : (isDark ? 'border-white/10 bg-white/5 text-white' : 'border-slate-200 bg-slate-50 text-slate-400')
                            }`}
                        >
                          {resetCode[i] || ''}
                        </div>
                      ))}
                    </div>
                    <input
                      type="text"
                      value={resetCode}
                      onChange={(e) => setResetCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                      placeholder="000000"
                      maxLength={6}
                      className="sr-only"
                      autoFocus
                      aria-label="Reset code"
                    />
                  </div>

                  {/* New Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-lock-2-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.newPassword')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-lock-2-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        id="reset-new-password"
                        type={showResetPassword ? 'text' : 'password'}
                        value={resetPassword}
                        onChange={(e) => setResetPassword(e.target.value)}
                        placeholder="••••••••"
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowResetPassword(s => !s)}
                        aria-pressed={showResetPassword}
                        className={`transition-colors shrink-0 ${isDark ? 'text-white/40 hover:text-white/80' : 'text-slate-400 hover:text-slate-600'}`}
                        aria-label={t('auth.showPassword')}
                      >
                        {showResetPassword
                          ? <EyeSlashIcon className="size-4 shrink-0" />
                          : <EyeIcon className="size-4 shrink-0" />}
                      </button>
                    </InputWrapper>
                  </div>

                  {/* Confirm New Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="ri-lock-2-line inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.confirmPassword')}
                    </label>
                    <InputWrapper>
                      <span className={`ri-lock-2-line ri-16px shrink-0 ${inputIcon}`} />
                      <input
                        id="reset-confirm-password"
                        type={showResetConfirm ? 'text' : 'password'}
                        value={resetConfirmPassword}
                        onChange={(e) => setResetConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        onKeyDown={(e) => e.key === 'Enter' && handleResetPassword()}
                        className={`w-full bg-transparent focus:outline-none text-sm ${inputText} ${inputPlaceholder}`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowResetConfirm(s => !s)}
                        aria-pressed={showResetConfirm}
                        className={`transition-colors shrink-0 ${isDark ? 'text-white/40 hover:text-white/80' : 'text-slate-400 hover:text-slate-600'}`}
                        aria-label={t('auth.showPassword')}
                      >
                        {showResetConfirm
                          ? <EyeSlashIcon className="size-4 shrink-0" />
                          : <EyeIcon className="size-4 shrink-0" />}
                      </button>
                    </InputWrapper>
                    {resetConfirmPassword && resetPassword === resetConfirmPassword && (
                      <p
                        className={`text-xs mt-1 flex items-center gap-1 ${isDark ? 'text-green-400' : 'text-green-600'}`}
                      >
                        <span className="ri-check-line ri-12px" /> Passwords match
                      </p>
                    )}
                  </div>

                  {/* Reset Password Button */}
                  <PrimaryButton
                    onClick={handleResetPassword}
                    disabled={isLoading || !resetCode.trim() || !resetPassword || !resetConfirmPassword}
                    loading={isLoading}
                    gradient="from-primary to-secondary"
                  >
                    <span className="ri-check-line text-sm" />
                    {t('auth.resetPasswordBtn')}
                  </PrimaryButton>

                  {/* Resend Code */}
                  <div className="text-center">
                    <button
                      onClick={handleRequestReset}
                      disabled={codeSending}
                      className={`text-sm transition-colors disabled:opacity-40 ${isDark ? 'text-white/40 hover:text-primary/80' : 'text-slate-400 hover:text-primary'}`}
                    >
                      {codeSending ? (
                        <span className="flex items-center justify-center gap-2">
                          <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full inline-block animate-spin" />
                          {t('common.loading')}
                        </span>
                      ) : (
                        t('auth.resendCode')
                      )}
                    </button>
                  </div>
                </div>

                {/* Back to Login */}
                <div className="mt-4 text-center">
                  <button
                    onClick={switchToLogin}
                    className={`text-sm transition-colors hover:underline ${isDark ? 'text-white/40 hover:text-primary/80' : 'text-slate-400 hover:text-primary'}`}
                  >
                    <span className="inline-block rtl:rotate-180">←</span> {t('auth.backToLogin')}
                  </button>
                </div>
              </CardWrapper>
            </div>
          </div>
        )}
      </AnimatePresence>

      {/* Toasts */}
      {renderToasts()}
    </div>
  );
}
