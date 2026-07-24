import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaEnvelope, FaLock, FaUser, FaKey, FaCheck, FaArrowRight, FaShieldAlt, FaEye, FaEyeSlash } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageToggle from '../components/LanguageToggle';
import ThemeToggle from '../components/ThemeToggle';
import { isTauri } from '../utils/tauri';

import { FusionPage } from '../components/FusionPage';
type AuthStep = 'loading' | 'checking' | 'register' | 'verify' | 'login';

export default function Auth() {
  const { t, i18n } = useTranslation();
  const {
    isLoading,
    login,
    setupAccount,
    sendConfirmationCode,
  } = useAuth();

  const [step, setStep] = useState<AuthStep>('loading');
  const [hasExistingUsers, setHasExistingUsers] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [codeSending, setCodeSending] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showLoginPassword, setShowLoginPassword] = useState(false);

  // Determine initial step on mount
  useEffect(() => {
    const init = async () => {
      setStep('checking');
      try {
        if (isTauri) {
          const { invoke } = await import('@tauri-apps/api/core');
          // Check if auth is required
          const required = await invoke<boolean>('check_auth_required');
          if (required) {
            // Check if any users exist
            const hasUsers = await invoke<boolean>('has_users');
            setHasExistingUsers(hasUsers);
            setStep(hasUsers ? 'login' : 'register');

            // Pre-fill superuser email if configured via env vars
            if (hasUsers) {
              const superEmail = await invoke<string | null>('get_superuser_email');
              if (superEmail) {
                setEmail(superEmail);
              }
            }
          } else {
            // Auth not required — this shouldn't render, but just in case
            setStep('login');
          }
        } else {
          // Browser dev mode — skip auth check (AuthContext handles it)
          setStep('login');
        }
      } catch (err) {
        console.error('Auth init error:', err);
        setError('Failed to initialize authentication. Please restart the app.');
        setStep('login');
      }
    };
    init();
  }, []);

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
    if (!name.trim()) {
      setError(t('auth.validationNameRequired'));
      return;
    }
    if (!email.trim()) {
      setError(t('auth.validationEmailRequired'));
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError(t('auth.validationEmailInvalid'));
      return;
    }
    if (!code.trim()) {
      setError(t('auth.validationCodeRequired'));
      return;
    }
    if (!password) {
      setError(t('auth.validationPasswordRequired'));
      return;
    }
    if (password.length < 6) {
      setError(t('auth.validationPasswordLength'));
      return;
    }
    if (password !== confirmPassword) {
      setError(t('auth.validationPasswordMatch'));
      return;
    }

    try {
      await setupAccount(email.trim(), code.trim(), password, name.trim(), rememberMe);
      setSuccess(t('auth.accountCreated'));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const handleLogin = async () => {
    clearMessages();
    if (!email.trim()) {
      setError(t('auth.validationEmailRequired'));
      return;
    }
    if (!password) {
      setError(t('auth.validationPasswordRequired'));
      return;
    }

    try {
      await login(email.trim(), password, rememberMe);
    } catch (err) {
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

  return (
    <div
      className={`min-h-screen bg-linear-to-br from-slate-900 via-teal-900 to-slate-900 flex items-center justify-center p-4 ${isRtl ? 'rtl' : 'ltr'}`}
      dir={isRtl ? 'rtl' : 'ltr'}
    >
      {/* Top-right toggles */}
      <div className="fixed top-4 right-4 flex items-center gap-3 z-50">
        <LanguageToggle />
        <ThemeToggle />
      </div>

      <AnimatePresence mode="wait">
        {step === 'checking' && (
          <motion.div
            key="checking"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            <div className="w-16 h-16 border-4 border-teal-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-white/60 text-lg">{t('auth.checking')}</p>
          </motion.div>
        )}

        {step === 'register' && (
          <motion.div
            key="register"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4 }}
            className="w-full max-w-md"
          >
            {/* Logo / Brand */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                className="bg-white/10 backdrop-blur-sm rounded-full p-4 w-fit mx-auto mb-4"
              >
                <FaShieldAlt className="w-10 h-10 text-teal-400" />
              </motion.div>
              <h1 className="text-3xl font-bold text-white mb-2">{t('auth.createAccount')}</h1>
              <p className="text-white/60">{t('auth.registerDesc')}</p>
            </div>

            {/* Card */}
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 md:p-8 border border-white/10 shadow-2xl">
              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaUser className="inline mr-2 text-teal-400" />
                    {t('auth.fullName')}
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t('auth.namePlaceholder')}
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white 
                      placeholder:text-white/30 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30
                      transition-all duration-200"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaEnvelope className="inline mr-2 text-teal-400" />
                    {t('auth.email')}
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="manager@restaurant.com"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white 
                      placeholder:text-white/30 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30
                      transition-all duration-200"
                  />
                </div>

                {/* Send Code Button */}
                <motion.button
                  onClick={handleSendCode}
                  disabled={codeSending || !email.trim()}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-medium 
                    flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {codeSending ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <><FaKey /> {t('auth.sendCode')}</>
                  )}
                </motion.button>
              </div>

              {/* Bottom link */}
              <div className="mt-6 text-center">
                <p className="text-white/50 text-sm">
                  {t('auth.alreadyHaveAccount')}{' '}
                  <button onClick={switchToLogin} className="text-teal-400 hover:text-teal-300 font-medium transition-colors">
                    {t('auth.signIn')}
                  </button>
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {step === 'verify' && (
          <motion.div
            key="verify"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4 }}
            className="w-full max-w-md"
          >
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                className="bg-white/10 backdrop-blur-sm rounded-full p-4 w-fit mx-auto mb-4"
              >
                <FaKey className="w-10 h-10 text-teal-400" />
              </motion.div>
              <h1 className="text-3xl font-bold text-white mb-2">{t('auth.verifyEmail')}</h1>
              <p className="text-white/60">{t('auth.verifyDesc')} <strong className="text-teal-400">{email}</strong></p>
            </div>

            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 md:p-8 border border-white/10 shadow-2xl">
              <div className="space-y-4">
                {/* Code */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaKey className="inline mr-2 text-teal-400" />
                    {t('auth.confirmationCode')}
                  </label>
                  <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                    placeholder="000000"
                    maxLength={6}
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white 
                      placeholder:text-white/30 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30
                      transition-all duration-200 text-center text-2xl tracking-widest font-mono"
                  />
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaLock className="inline mr-2 text-teal-400" />
                    {t('auth.password')}
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full px-4 py-3 pr-12 rounded-lg bg-white/5 border border-white/20 text-white 
                        placeholder:text-white/30 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30
                        transition-all duration-200"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/80 transition-colors"
                      aria-label={showPassword ? t('auth.hidePassword') : t('auth.showPassword')}
                    >
                      {showPassword ? <FaEyeSlash className="w-4 h-4" /> : <FaEye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaLock className="inline mr-2 text-teal-400" />
                    {t('auth.confirmPassword')}
                  </label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
                      className={`w-full px-4 py-3 pr-12 rounded-lg bg-white/5 border text-white 
                        placeholder:text-white/30 focus:outline-none focus:ring-1 focus:ring-teal-400/30
                        transition-all duration-200 ${
                          confirmPassword && password === confirmPassword
                            ? 'border-green-400/40 focus:border-green-400'
                            : confirmPassword
                              ? 'border-red-400/40 focus:border-red-400'
                              : 'border-white/20 focus:border-teal-400'
                        }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/80 transition-colors"
                      aria-label={showConfirmPassword ? t('auth.hidePassword') : t('auth.showPassword')}
                    >
                      {showConfirmPassword ? <FaEyeSlash className="w-4 h-4" /> : <FaEye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Create Account Button */}
                <motion.button
                  onClick={handleRegister}
                  disabled={isLoading || !code.trim() || !password || !confirmPassword}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-medium 
                    flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <><FaCheck /> {t('auth.createAccountBtn')}</>
                  )}
                </motion.button>

                {/* Resend code */}
                <div className="text-center">
                  <button
                    onClick={handleSendCode}
                    disabled={codeSending}
                    className="text-white/50 hover:text-teal-400 text-sm transition-colors"
                  >
                    {t('auth.resendCode')}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {step === 'login' && (
          <motion.div
            key="login"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4 }}
            className="w-full max-w-md"
          >
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                className="bg-white/10 backdrop-blur-sm rounded-full p-4 w-fit mx-auto mb-4"
              >
                <FaShieldAlt className="w-10 h-10 text-teal-400" />
              </motion.div>
              <h1 className="text-3xl font-bold text-white mb-2">{t('auth.welcomeBack')}</h1>
              <p className="text-white/60">{t('auth.loginDesc')}</p>
            </div>

            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 md:p-8 border border-white/10 shadow-2xl">
              <div className="space-y-4">
                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaEnvelope className="inline mr-2 text-teal-400" />
                    {t('auth.email')}
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="manager@restaurant.com"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white 
                      placeholder:text-white/30 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30
                      transition-all duration-200"
                  />
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-1.5">
                    <FaLock className="inline mr-2 text-teal-400" />
                    {t('auth.password')}
                  </label>
                  <div className="relative">
                    <input
                      type={showLoginPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                      className="w-full px-4 py-3 pr-12 rounded-lg bg-white/5 border border-white/20 text-white 
                        placeholder:text-white/30 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30
                        transition-all duration-200"
                    />
                    <button
                      type="button"
                      onClick={() => setShowLoginPassword(!showLoginPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/80 transition-colors"
                      aria-label={showLoginPassword ? t('auth.hidePassword') : t('auth.showPassword')}
                    >
                      {showLoginPassword ? <FaEyeSlash className="w-4 h-4" /> : <FaEye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me */}
                <label className="flex items-center gap-2.5 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-white/30 bg-white/5 text-teal-500 
                      focus:ring-teal-400 focus:ring-offset-0 cursor-pointer
                      accent-teal-500"
                  />
                  <span className="text-sm text-white/70">{t('auth.rememberMe')}</span>
                </label>

                {/* Login Button */}
                <motion.button
                  onClick={handleLogin}
                  disabled={isLoading || !email.trim() || !password}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-medium 
                    flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <><FaArrowRight /> {t('auth.signIn')}</>
                  )}
                </motion.button>
              </div>

              {/* Show register link if there's no existing user (shouldn't happen normally since we check) */}
              {!hasExistingUsers && (
                <div className="mt-6 text-center">
                  <p className="text-white/50 text-sm">
                    {t('auth.noAccount')}{' '}
                    <button onClick={switchToRegister} className="text-teal-400 hover:text-teal-300 font-medium transition-colors">
                      {t('auth.createOne')}
                    </button>
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-red-500/90 backdrop-blur-sm text-white 
              px-6 py-3 rounded-xl shadow-2xl z-50 max-w-md text-center border border-red-400/30"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success Toast */}
      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-24 left-1/2 -translate-x-1/2 bg-teal-500/90 backdrop-blur-sm text-white 
              px-6 py-3 rounded-xl shadow-2xl z-50 max-w-md text-center border border-teal-400/30"
          >
            {success}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
