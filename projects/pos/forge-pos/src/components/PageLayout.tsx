import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
// ── Icons use Tabler icon CSS classes via icon-[tabler--*] ──
import { invoke } from '@tauri-apps/api/core';
import SideNav from './SideNav';
import { Settings } from '../types';
import { useAuth, AuthUser } from '../contexts/AuthContext';
// Bundled fallback logo (animated POS Crest SVG).
// settings.logo always takes priority when uploaded.
import defaultLogo from '../assets/pos-crest.svg';

// ── Local helper: Profile dropdown ──────────────────────────────────────────

function ProfileDropdown({
  user,
  open,
  onToggle,
  onLogout,
  compact = false,
}: {
  user: AuthUser;
  open: boolean;
  onToggle: () => void;
  onLogout: () => void;
  compact?: boolean;
}) {
  const initials = (user.name?.charAt(0) || user.email.charAt(0)).toUpperCase();

  return (
    <div className="relative">
      <motion.button
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={onToggle}
        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10
          hover:shadow-md transition-shadow"
        aria-label="User profile"
        aria-expanded={open}
      >
        <div className={`${compact ? 'w-8 h-8 text-sm' : 'w-7 h-7 sm:w-8 sm:h-8 text-xs sm:text-sm'}
          rounded-full bg-gradient-to-br from-teal-500 to-teal-700
          flex items-center justify-center text-white font-bold shrink-0 shadow-sm`}>
          {initials}
        </div>
        <span className="hidden sm:block text-xs font-medium text-slate-600 dark:text-slate-300 max-w-[120px] truncate">
          {user.email}
        </span>
        <span className={`icon-[tabler--chevron-down] w-4 h-4 text-slate-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 4, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-1 w-64 bg-white dark:bg-slate-800 rounded-2xl shadow-xl
              border border-slate-200 dark:border-slate-700 overflow-hidden z-50"
          >
            {/* User info header */}
            <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-teal-700
                  flex items-center justify-center text-white font-bold shadow-sm shrink-0">
                  {initials}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                    {user.name || 'User'}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                    {user.email}
                  </p>
                </div>
              </div>
            </div>

            {/* Logout action */}
            <div className="p-2">
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                onClick={onLogout}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl
                  text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20
                  transition-colors text-sm font-medium"
              >
                <span className="icon-[tabler--logout] w-4 h-4" />
                Sign Out
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── PageLayout ──────────────────────────────────────────────────────────────

interface PageLayoutProps {
  children: React.ReactNode;
  showNav?: boolean;
  title?: React.ReactNode;
  background?: string;
  containerWidth?: string;
  padding?: string;
}

export default function PageLayout({
  children,
  showNav = true,
  title,
  background = 'bg-slate-100 dark:bg-slate-900',
  containerWidth = 'max-w-7xl xl:max-w-[90rem] 3xl:max-w-[110rem] 4xl:max-w-[130rem]',
  padding = 'py-4 md:py-6 lg:py-10',
}: PageLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const [logo, setLogo] = useState<string | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  const { user, isAuthRequired, logout, inactivityWarning, dismissInactivityWarning } = useAuth();

  // Close profile dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false);
      }
    };
    if (profileOpen) {
      document.addEventListener('mousedown', handleClick);
    }
    return () => document.removeEventListener('mousedown', handleClick);
  }, [profileOpen]);

  const handleLogout = () => {
    setProfileOpen(false);
    logout();
  };

  // ── AJAX: load settings once (cached by browser) ──
  useEffect(() => {
    let cancelled = false;
    const loadSettings = async () => {
      try {
        const response = await invoke<Settings>('get_settings');
        if (!cancelled && response?.logo) setLogo(response.logo);
      } catch {
        if (!cancelled) setLogo(null);
      }
    };
    loadSettings();
    return () => { cancelled = true; };
  }, []);

  const handleBackNavigation = () => {
    setIsNavigating(true);
    setTimeout(() => navigate('/'), 300);
  };

  const renderLogo = (size: string) => (
    <motion.img
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 240, damping: 20 }}
      whileHover={{ rotate: 6, scale: 1.06 }}
      src={logo || defaultLogo}
      alt="Restaurant Logo"
      className={`${size} object-contain rounded-md shadow-sm bg-white/60 dark:bg-white/10 p-0.5 border border-slate-200 dark:border-white/10 shrink-0`}
      onError={(e) => { (e.currentTarget as HTMLImageElement).style.opacity = '0.5'; }}
    />
  );

  // Show profile button when auth is required AND a user is logged in
  const showProfile = isAuthRequired && user;

  return (
    <div className={`min-h-screen transition-colors duration-300 ${background}`}>
      {/* Overlay SideNav (mobile/tablet) */}
      <SideNav isOpen={isNavOpen} onClose={() => setIsNavOpen(false)} currentRoute={location.pathname} />

      {/* Persistent hover-expand sidebar (ultra-wide screens) */}
      <SideNav persistent currentRoute={location.pathname} />

      {/* Inactivity warning toast */}
      <AnimatePresence>
        {inactivityWarning && (
          <motion.div
            initial={{ opacity: 0, y: -24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -24 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3
              bg-amber-500 text-white px-5 py-3 rounded-xl shadow-2xl text-sm font-semibold"
          >
            <span className="icon-[tabler--alert-triangle] w-5 h-5 shrink-0" />
            <span>Session expiring soon — click anywhere to stay logged in</span>
            <motion.button
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              onClick={dismissInactivityWarning}
              className="ml-2 px-3 py-1 rounded-lg bg-white/20 hover:bg-white/30 text-white text-xs font-bold transition-colors"
            >
              Stay
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      <div className={`4xl:ml-16 rtl:4xl:mr-16 rtl:4xl:ml-0 ${containerWidth} mx-auto px-4 sm:px-6 ${padding}`}>
        {showNav ? (
          /* Full TopBar: [Menu] [Back] [Logo + Title] [Profile] */
          <div className="flex items-center justify-between mb-6 gap-3">
            <div className="flex items-center gap-2 shrink-0">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.92 }}
                onClick={() => setIsNavOpen(true)}
                className="w-9 h-9 flex items-center justify-center rounded-xl bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10"
                aria-label="Open navigation"
              >
                <span className="icon-[tabler--menu-2] w-5 h-5 text-slate-700 dark:text-slate-300" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.92 }}
                onClick={handleBackNavigation}
                disabled={isNavigating}
                className="w-9 h-9 flex items-center justify-center rounded-xl bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10 disabled:opacity-50"
                aria-label="Back to home"
              >
                <span className="icon-[tabler--arrow-back] w-4 h-4 text-slate-700 dark:text-slate-300 rtl:scale-x-[-1]" />
              </motion.button>
            </div>
            <div className="flex items-center gap-3 flex-1 justify-center min-w-0">
              {renderLogo('h-9 w-9 sm:h-10 sm:w-10')}
              {title && (
                <h1 className="text-base sm:text-lg md:text-xl font-semibold text-slate-900 dark:text-white transition-colors duration-300 flex items-center gap-2 truncate">
                  {title}
                </h1>
              )}
            </div>

            {/* Profile / spacer on right */}
            <div className="shrink-0 flex items-center" ref={profileRef}>
              {showProfile ? (
                <ProfileDropdown
                  user={user}
                  open={profileOpen}
                  onToggle={() => setProfileOpen(o => !o)}
                  onLogout={handleLogout}
                />
              ) : (
                <div className="w-9 hidden sm:block" aria-hidden="true" />
              )}
            </div>
          </div>
        ) : (
          /* Home page: logo + menu + profile */
          <div className="flex justify-between items-center gap-3 mb-8">
            <div className="flex items-center gap-3">
              {renderLogo('h-10 w-10 sm:h-12 sm:w-12')}
            </div>
            <div className="flex items-center gap-2" ref={profileRef}>
              {showProfile && (
                <ProfileDropdown
                  user={user}
                  open={profileOpen}
                  onToggle={() => setProfileOpen(o => !o)}
                  onLogout={handleLogout}
                  compact
                />
              )}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.92 }}
                onClick={() => setIsNavOpen(true)}
                className="w-9 h-9 flex items-center justify-center rounded-xl bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10 shrink-0"
                aria-label="Open navigation"
              >
                <span className="icon-[tabler--menu-2] w-5 h-5 text-slate-700 dark:text-slate-300" />
              </motion.button>
            </div>
          </div>
        )}

        {children}
      </div>
    </div>
  );
}
