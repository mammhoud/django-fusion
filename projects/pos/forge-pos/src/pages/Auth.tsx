import { useState, useEffect, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// react-icons/fa no longer needed — all icons migrated to Tabler
import { useAuth } from '../contexts/AuthContext';
import { useTheme, type ThemeVariant } from '../contexts/ThemeContext';
import { useTranslation } from 'react-i18next';
import LanguageToggle from '../components/LanguageToggle';
import ThemeToggle from '../components/ThemeToggle';
import { invoke } from '@tauri-apps/api/core';

type AuthStep = 'loading' | 'checking' | 'register' | 'verify' | 'login';

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
  default:   'from-teal-600 via-emerald-700 to-teal-800',
  corporate: 'from-blue-600 via-indigo-700 to-blue-900',
  luxury:    'from-amber-700 via-yellow-800 to-amber-900',
  pastel:    'from-pink-300 via-purple-400 to-pink-500',
  cyberpunk: 'from-fuchsia-700 via-violet-800 to-fuchsia-900',
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
  const [rememberMe, setRememberMe] = useState(() => true);
  const [selectedRole, setSelectedRole] = useState<'manager' | 'employee'>('manager');
  // Password visibility toggles — handled by FlyonUI data-toggle-password
  // (React state removed to avoid conflict with FlyonUI's DOM toggle)


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
      await setupAccount(email.trim(), code.trim(), password, name.trim(), rememberMe);
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
      await login(email.trim(), password, rememberMe);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const handleQuickLogin = async (role: 'manager' | 'employee') => {
    clearMessages();
    // Try the superuser email first, fall back to demo credentials
    let loginEmail = email || (await invoke<string | null>('get_superuser_email')) || 'manager@restaurant.com';
    let loginPassword = password || 'secret123';

    if (role === 'employee') {
      // Employee login — use demo credentials
      loginEmail = 'employee@restaurant.com';
      loginPassword = 'secret123';
    }

    setEmail(loginEmail);
    setPassword(loginPassword);

    try {
      await login(loginEmail, loginPassword, true, role);
    } catch (err) {
      // If quick login fails, just show the form with pre-filled credentials
      setError(err instanceof Error ? err.message : String(err));
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
    setStep('login');
  };

  const isRtl = i18n.language === 'ar';
  const { variant } = useTheme();

  // ── Decorative pattern SVG lines (FlyonUI-inspired) ──
  const renderDecorativePattern = () => (
    <svg
      className="absolute inset-0 w-full h-full opacity-[0.03] pointer-events-none"
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

  // ── FlyonUI card with glassmorphism styling ──
  const CardWrapper = ({ children, className = '' }: { children: ReactNode; className?: string }) => (
    <div className={`card bg-white/10 backdrop-blur-xl border border-white/10 shadow-2xl shadow-white/5 relative overflow-hidden ${className}`}>
      {/* Decorative SVG element */}
      <div className="absolute -top-24 -right-24 w-72 h-72 opacity-[0.04] pointer-events-none text-primary/80">
        <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
          <path d="M100 0C155.228 0 200 44.7715 200 100C200 155.228 155.228 200 100 200C44.7715 200 0 155.228 0 100C0 44.7715 44.7715 0 100 0Z" fill="currentColor" />
          <circle cx="100" cy="100" r="60" fill="currentColor" opacity="0.6" />
          <circle cx="100" cy="100" r="30" fill="currentColor" opacity="0.3" />
        </svg>
      </div>
      {children}
    </div>
  );

  // ── Shared form label ──
  const labelClass = 'block text-sm font-medium text-white/70 mb-1.5';

  // ── FlyonUI input group with glassmorphism ──
  const InputWrapper = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
    <div className={`input flex items-center gap-3 w-full px-4 py-3 rounded-xl bg-white/5 border border-white/20
      focus-within:border-primary/60 focus-within:ring-2 focus-within:ring-teal-400/20
      transition-all duration-200 ${className}`}>
      {children}
    </div>
  );

  // ── FlyonUI checkbox ──
  const Checkbox = ({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) => (
    <label className="flex items-center gap-2.5 cursor-pointer select-none group">
      <input
        type="checkbox"
        className={`checkbox checkbox-sm border-2 rounded-lg transition-all duration-200 ${
          checked
            ? 'checkbox-primary [--checkbox-checked-bg:theme(colors.teal.500)]'
            : 'border-white/20 group-hover:border-white/40'
        }`}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="text-sm text-white/60 group-hover:text-white/80 transition-colors">
        {label}
      </span>
    </label>
  );

  // ── FlyonUI primary button with spring animations ──
  const PrimaryButton = ({ onClick, disabled, loading, children, gradient = 'from-primary to-primary/80' }: {
    onClick: () => void; disabled?: boolean; loading?: boolean; children: React.ReactNode; gradient?: string;
  }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn w-full bg-gradient-to-r ${gradient} hover:from-primary/60 hover:to-primary/40
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
    <div className={`relative hidden lg:flex lg:w-1/2 bg-gradient-to-br ${ILLUSTRATION_GRADIENTS[variant]} p-8 xl:p-12 items-center justify-center overflow-hidden`}>
      {/* Animated background particles */}
      {PARTICLES.map(p => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-white/10"
          style={{
            width: p.size,
            height: p.size,
            left: `${p.x}%`,
            top: `${p.y}%`,
          }}
          animate={{
            opacity: [0.2, 0.6, 0.2],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Floating brand icons */}
      {BRAND_ICONS.map(({ icon: iconName, delay, x, y, size, color }) => (
        <motion.div
          key={delay}
          className={`absolute ${size} ${color}`}
          style={{ left: x, top: y }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay, duration: 0.8, ease: 'easeOut' }}
        >
          <span className={'icon-[tabler--' + iconName + '] w-full h-full'} />
        </motion.div>
      ))}

      {/* Central Branding */}
      <motion.div
        className="relative z-10 text-center max-w-md"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <motion.div
          className="bg-white/15 backdrop-blur-xl rounded-3xl p-6 w-fit mx-auto mb-8 border border-white/20 shadow-2xl"
          whileHover={{ scale: 1.05, rotate: 2 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
        >
          <span className="icon-[tabler--shield] w-16 h-16 text-white" />
        </motion.div>
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
            <motion.div
              key={idx}
              className="flex items-center gap-3 text-white/80"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 + idx * 0.15, duration: 0.5 }}
            >
              <div className="bg-white/15 rounded-lg p-2">
                <span className={'icon-[tabler--' + iconName + '] w-4 h-4'} />
              </div>
              <span className="text-sm font-medium">{text}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  // ── Form Panel step classes ──
  const FORM_PANEL_CLASS = 'w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-6 md:p-8 xl:p-12 relative overflow-y-auto min-h-screen lg:min-h-0';

  // ── Toast Notifications ──
  const renderToasts = () => (
    <>
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-500/95 backdrop-blur-md text-white
              px-5 py-3 rounded-2xl shadow-2xl z-50 max-w-md text-center border border-red-400/30
              flex items-center gap-3 shadow-red-500/20"
          >
            <div className="w-2 h-2 rounded-full bg-white animate-pulse shrink-0" />
            <span className="text-sm font-medium">{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 left-1/2 -translate-x-1/2 bg-primary/95 backdrop-blur-md text-primary-content
              px-5 py-3 rounded-2xl shadow-2xl z-50 max-w-md text-center border border-primary/30
              flex items-center gap-3 shadow-primary/20"
          >
            <span className="icon-[tabler--check] w-4 h-4 shrink-0" />
            <span className="text-sm font-medium">{success}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );

  // ── Brand Logo chip ──
  const BrandLogo = () => (
    <div className="flex items-center gap-2.5 mb-4">
      <div className={`bg-gradient-to-br ${ILLUSTRATION_GRADIENTS[variant]} rounded-lg p-2 shadow-lg`}>
        <span className="icon-[tabler--shield] w-5 h-5 text-white" />
      </div>
      <span className="text-white/80 text-lg font-bold">Forge POS</span>
    </div>
  );

  // ── Auth header ──
  const AuthHeader = ({ title, desc }: { title: string; desc: string }) => (
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-white mb-1">{title}</h2>
      <p className="text-white/50 text-sm">{desc}</p>
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
        <ThemeToggle />
      </div>

      {/* Illustration Panel */}
      <motion.div
        className="hidden lg:flex lg:w-1/2"
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {renderIllustration()}
      </motion.div>

      {/* Form Panel */}
      <AnimatePresence mode="wait">
        {step === 'checking' && (
          <motion.div
            key="checking"
            className="w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-6 md:p-8 xl:p-12 min-h-screen lg:min-h-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="text-center">
              <div className="relative w-20 h-20 mx-auto mb-6">
                <motion.div
                  className="absolute inset-0 border-4 border-primary/30 border-t-teal-400 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                />
                <motion.div
                  className="absolute inset-2 border-4 border-success/20 border-b-emerald-400 rounded-full"
                  animate={{ rotate: -360 }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
                />
              </div>
              <motion.p
                className="text-white/60 text-lg"
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {t('auth.checking')}
              </motion.p>
            </div>
          </motion.div>
        )}

        {step === 'register' && (
          <motion.div
            key="register"
            className={FORM_PANEL_CLASS}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          >
            {/* Background gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-teal-900/20 via-slate-900/50 to-teal-900/20 lg:hidden" />
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
                      <span className="icon-[tabler--user] inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.fullName')}
                    </label>
                    <InputWrapper>
                      <span className="icon-[tabler--user] w-4 h-4 text-white/40 shrink-0" />
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder={t('auth.namePlaceholder')}
                        className="w-full bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                        autoFocus
                      />
                    </InputWrapper>
                  </div>

                  {/* Email */}
                  <div>
                    <label className={labelClass}>
                      <span className="icon-[tabler--mail] inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.email')}
                    </label>
                    <InputWrapper>
                      <span className="icon-[tabler--mail] w-4 h-4 text-white/40 shrink-0" />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="manager@restaurant.com"
                        className="w-full bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
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
                    <span className="icon-[tabler--key] text-sm" />
                    {t('auth.sendCode')}
                  </PrimaryButton>
                </div>

                {/* Switch to Login */}
                <div className="mt-6 text-center">
                  <p className="text-white/40 text-sm">
                    {t('auth.alreadyHaveAccount')}{' '}
                    <button
                      onClick={switchToLogin}
                      className="text-primary/80 hover:text-primary/70 font-medium transition-colors hover:underline"
                    >
                      {t('auth.signIn')}
                    </button>
                  </p>
                </div>
              </CardWrapper>
            </div>
          </motion.div>
        )}

        {step === 'verify' && (
          <motion.div
            key="verify"
            className={FORM_PANEL_CLASS}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          >
            {/* Background gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-teal-900/20 via-slate-900/50 to-teal-900/20 lg:hidden" />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                <BrandLogo />
                <AuthHeader
                  title={t('auth.verifyEmail')}
                  desc={`${t('auth.verifyDesc')} `}
                />
                <p className="text-primary/80 text-sm font-medium -mt-4 mb-6 text-center">{email}</p>

                <div className="space-y-4">
                  {/* Code Input */}
                  <div>
                    <label className={labelClass}>{t('auth.confirmationCode')}</label>
                    <div className="flex justify-center gap-2 sm:gap-3 mb-1">
                      {[0, 1, 2, 3, 4, 5].map((i) => (
                        <div
                          key={i}
                          className={`w-10 h-12 sm:w-12 sm:h-14 rounded-xl border-2 flex items-center justify-center
                            text-white text-xl font-bold font-mono transition-all duration-200
                            ${code.length > i
                              ? 'border-primary bg-primary/20 shadow-lg shadow-teal-500/10'
                              : code.length === i
                                ? 'border-primary/60 bg-white/10 animate-pulse'
                                : 'border-white/10 bg-white/5'
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
                      <span className="icon-[tabler--lock] inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.password')}
                    </label>
                    <InputWrapper>
                      <span className="icon-[tabler--lock] w-4 h-4 text-white/40 shrink-0" />
                      <input
                        id="register-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                      />
                      <button
                        type="button"
                        data-toggle-password='{ "target": "#register-password" }'
                        className="text-white/40 hover:text-white/80 transition-colors shrink-0"
                        aria-label={t('auth.showPassword')}
                      >
                        <span className="icon-[tabler--eye] password-active:block hidden size-4 shrink-0" />
                        <span className="icon-[tabler--eye-off] password-active:hidden block size-4 shrink-0" />
                      </button>
                    </InputWrapper>
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="icon-[tabler--lock] inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.confirmPassword')}
                    </label>
                    <InputWrapper>
                      <span className="icon-[tabler--lock] w-4 h-4 text-white/40 shrink-0" />
                      <input
                        id="register-confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
                        className="w-full bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                      />
                      <button
                        type="button"
                        data-toggle-password='{ "target": "#register-confirm-password" }'
                        className="text-white/40 hover:text-white/80 transition-colors shrink-0"
                        aria-label={t('auth.showPassword')}
                      >
                        <span className="icon-[tabler--eye] password-active:block hidden size-4 shrink-0" />
                        <span className="icon-[tabler--eye-off] password-active:hidden block size-4 shrink-0" />
                      </button>
                    </InputWrapper>
                    {confirmPassword && password === confirmPassword && (
                      <motion.p
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-green-400 text-xs mt-1 flex items-center gap-1"
                      >
                        <span className="icon-[tabler--check] w-3 h-3" /> Passwords match
                      </motion.p>
                    )}
                  </div>

                  {/* Create Account */}
                  <PrimaryButton
                    onClick={handleRegister}
                    disabled={isLoading || !code.trim() || !password || !confirmPassword}
                    loading={isLoading}
                    gradient="from-primary to-primary/80"
                  >
                    <span className="icon-[tabler--check] text-sm" />
                    {t('auth.createAccountBtn')}
                  </PrimaryButton>

                  {/* Resend */}
                  <div className="text-center">
                    <button
                      onClick={handleSendCode}
                      disabled={codeSending}
                      className="text-white/40 hover:text-primary/80 text-sm transition-colors disabled:opacity-40"
                    >
                      {codeSending ? (
                        <span className="flex items-center justify-center gap-2">
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                            className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full inline-block"
                          />
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
          </motion.div>
        )}

        {step === 'login' && (
          <motion.div
            key="login"
            className={FORM_PANEL_CLASS}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          >
            {/* Background gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-teal-900/20 via-slate-900/50 to-teal-900/20 lg:hidden" />
            {renderDecorativePattern()}
            <div className="relative z-10 w-full max-w-md">
              <CardWrapper className="p-5 sm:p-6 md:p-8">
                {/* Brand logo + title */}
                <BrandLogo />

                {/* FlyonUI-style "Sign in" header */}
                <AuthHeader title={t('auth.welcomeBack')} desc={t('auth.loginDesc')} />

                {/* Role-based quick-login segmented switcher */}
                <div className="flex p-1 rounded-xl bg-white/5 border border-white/10 mb-6 gap-1">
                  {(['manager', 'employee'] as const).map((role) => (
                    <button
                      key={role}
                      onClick={() => {
                        setSelectedRole(role);
                        handleQuickLogin(role);
                      }}
                      disabled={isLoading}
                      className={`flex-1 min-w-[120px] px-3 py-2.5 rounded-lg text-sm font-medium
                        flex items-center justify-center gap-2 transition-all duration-200
                        disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97]
                        ${selectedRole === role
                          ? 'bg-gradient-to-r from-primary/30 to-primary/20 shadow-lg shadow-primary/10 text-white border border-primary/40'
                          : 'text-white/50 hover:text-white/70 hover:bg-white/5'
                        }`}
                    >
                      <span className={'icon-[tabler--' + (role === 'manager' ? 'user-check' : 'user-circle') + '] w-4 h-4'} />
                      <span>{role === 'manager' ? 'Manager' : 'Employee'}</span>
                    </button>
                  ))}
                </div>

                {/* Divider */}
                <div className="flex items-center gap-3 mb-5">
                  <div className="flex-1 h-px bg-white/10" />
                  <span className="text-white/30 text-xs font-medium">or</span>
                  <div className="flex-1 h-px bg-white/10" />
                </div>

                {/* Form */}
                <div className="space-y-4">
                  {/* Email */}
                  <div>
                    <label className={labelClass}>
                      <span className="icon-[tabler--mail] inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.email')}
                    </label>
                    <InputWrapper>
                      <span className="icon-[tabler--mail] w-4 h-4 text-white/40 shrink-0" />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="manager@restaurant.com"
                        className="w-full bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                        autoFocus
                      />
                    </InputWrapper>
                  </div>

                  {/* Password */}
                  <div>
                    <label className={labelClass}>
                      <span className="icon-[tabler--lock] inline mr-2 text-primary/80 w-3.5 h-3.5" />
                      {t('auth.password')}
                    </label>
                    <InputWrapper>
                      <span className="icon-[tabler--lock] w-4 h-4 text-white/40 shrink-0" />
                      <input
                        id="login-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                        className="w-full bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                      />
                      <button
                        type="button"
                        data-toggle-password='{ "target": "#login-password" }'
                        className="text-white/40 hover:text-white/80 transition-colors shrink-0"
                        aria-label={t('auth.showPassword')}
                      >
                        <span className="icon-[tabler--eye] password-active:block hidden size-4 shrink-0" />
                        <span className="icon-[tabler--eye-off] password-active:hidden block size-4 shrink-0" />
                      </button>
                    </InputWrapper>
                  </div>

                  {/* Remember Me + Forgot Password */}
                  <div className="flex items-center justify-between gap-y-2">
                    <Checkbox checked={rememberMe} onChange={setRememberMe} label={t('auth.rememberMe')} />
                    <button className="text-primary/80/60 hover:text-primary/70 text-xs font-medium transition-colors hover:underline">
                      Forgot Password?
                    </button>
                  </div>

                  {/* Sign In Button */}
                  <PrimaryButton
                    onClick={handleLogin}
                    disabled={isLoading || !email.trim() || !password}
                    loading={isLoading}
                    gradient="from-primary to-secondary"
                  >
                    <span className="icon-[tabler--arrow-right] text-sm" />
                    {t('auth.signIn')}
                  </PrimaryButton>
                </div>

                {/* Create Account link */}
                {!hasExistingUsers && (
                  <div className="mt-6 text-center">
                    <p className="text-white/40 text-sm">
                      {t('auth.noAccount')}{' '}
                      <button
                        onClick={switchToRegister}
                        className="text-primary/80 hover:text-primary/70 font-medium transition-colors hover:underline"
                      >
                        {t('auth.createOne')}
                      </button>
                    </p>
                  </div>
                )}

                {/* Skip login */}
                {!isAuthRequired && (
                  <div className="mt-4 text-center border-t border-white/10 pt-4">
                    <button
                      onClick={skipAuth}
                      className="text-white/30 hover:text-white/60 text-xs transition-colors hover:underline"
                    >
                      Continue without signing in
                    </button>
                  </div>
                )}
              </CardWrapper>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toasts */}
      {renderToasts()}
    </div>
  );
}
