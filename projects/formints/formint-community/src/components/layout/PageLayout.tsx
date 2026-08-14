import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import SideNav from '../layout/SideNav';
import AnimatedBackground from './AnimatedBackground';
import { useAuth, AuthUser } from '../../contexts/AuthContext';
import AnimatePresence from '../ui/AnimatePresence';
import { dropdownMenu, toastSlideIn, iconSpring } from '../../utils/pageTransitions';
// Built-in Formint crest logo — always shown in the app chrome.
// Business logos from settings only appear on invoices/receipts.
import defaultLogo from '../../../assets/images/formint-crest.svg';


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
  const { t } = useTranslation();

  return (
    <div className="relative z-[60]">
      <button              onClick={onToggle}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-base-100/70 backdrop-blur-md border border-base-300/30
                hover:shadow-md transition-all active:scale-[0.97]"
        aria-label={t('common.userProfile') || 'User profile'}
        aria-expanded={open}
      >
        <div className={`${compact ? 'w-8 h-8 text-sm' : 'w-7 h-7 sm:w-8 sm:h-8 text-xs sm:text-sm'}
          rounded-full bg-linear-to-br from-primary to-primary/70
          flex items-center justify-center text-white font-bold shrink-0 shadow-sm`}>
          {initials}
        </div>
        <span className="hidden sm:block text-xs font-medium text-base-content/60 max-w-[120px] truncate">
          {user.email}
        </span>
        <span className={`ri-arrow-down-s-line ri-16px text-base-content/50 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {open && (
          <div
            className={`${dropdownMenu} absolute right-0 mt-1 w-64 bg-base-100 rounded-2xl shadow-xl
              border border-base-300/50 overflow-hidden z-50 rtl:right-auto rtl:left-0`}

          >
            {/* User info header */}              <div className="px-4 py-3 border-b border-base-300/30">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-linear-to-br from-primary to-primary/70
                  flex items-center justify-center text-white font-bold shadow-sm shrink-0">
                  {initials}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-base-content truncate">
                    {user.name || 'User'}
                  </p>
                  <p className="text-xs text-base-content/50 truncate">
                    {user.email}
                  </p>
                </div>
              </div>
            </div>

            {/* Logout action */}
            <div className="p-2">
              <button
                onClick={onLogout}
                className="btn btn-ghost btn-block justify-start text-error hover:bg-error/10 rounded-xl"
              >
                <span className="ri-logout-box-r-line ri-16px" />
                {t('auth.signOut')}
              </button>
            </div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── PageLayout ──────────────────────────────────────────────────────────────

interface PageLayoutProps {
  children: React.ReactNode;
  showNav?: boolean;
  /** Full-bleed presentation for dedicated windows —
   *  hides SideNav, the top bar and inactivity toast so the page owns the
   *  whole viewport. */
  standalone?: boolean;
  title?: React.ReactNode;
  background?: string;
  containerWidth?: string;
  padding?: string;
}

export default function PageLayout({
  children,
  showNav = true,
  standalone = false,
  title,
  background = 'bg-texture',
  // Wider default container — all pages get more horizontal room for grids.
  // Capped at ~120rem so table rows don't stretch absurdly on huge monitors.
  containerWidth = 'max-w-[90rem] xl:max-w-[100rem] 3xl:max-w-[110rem] 4xl:max-w-[120rem]',
  // Compact on small screens (py-4) so every viewport shows more content,
  // scaling up only once there is real room (md+).
  padding = 'py-4 sm:py-6 md:py-10 lg:py-12',
}: PageLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  const { user, isAuthRequired, logout, inactivityWarning, dismissInactivityWarning } = useAuth();
  const { t } = useTranslation();

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



  const handleBackNavigation = () => {
    setIsNavigating(true);
    setTimeout(() => navigate('/dashboard'), 300);
  };

  const renderLogo = (size: string) => (      <img
      src={defaultLogo as unknown as string}
      alt="Formint"
      className={`${iconSpring} ${size} object-contain rounded-md shadow-sm bg-base-100/80 p-0.5 border border-base-300/50 shrink-0`}
      onError={(e) => { (e.currentTarget as HTMLImageElement).style.opacity = '0.5'; }}
    />
  );

  // Show profile button when auth is required AND a user is logged in
  const showProfile = isAuthRequired && user;

  return (
    <div className={`min-h-[100dvh] overflow-y-auto transition-colors duration-300 ${background}`}>
      {/* GSAP ambient background — sits behind all content, follows the theme */}
      <AnimatedBackground />

      {!standalone && (
        <>
          {/* Overlay SideNav (mobile/tablet) */}
          <SideNav isOpen={isNavOpen} onClose={() => setIsNavOpen(false)} currentRoute={location.pathname} />

          {/* Persistent hover-expand sidebar (ultra-wide screens) */}
          <SideNav persistent currentRoute={location.pathname} />

          {/* Inactivity warning toast */}
          <AnimatePresence>
            {inactivityWarning && (
              <div
                className={`${toastSlideIn} fixed top-4 left-1/2 -translate-x-1/2 z-50 alert alert-warning shadow-2xl text-sm font-semibold`}
              >
                <span className="ri-alert-line ri-20px shrink-0" />
                <span>Session expiring soon. Click anywhere to stay logged in</span>              <button
                    onClick={dismissInactivityWarning}
                    className="btn btn-ghost btn-xs ml-2 text-white bg-white/20"
                >
                  Stay
                </button>
              </div>
            )}
          </AnimatePresence>
        </>
      )}

      <div className={`${standalone ? '' : '4xl:ml-16 rtl:4xl:mr-16 rtl:4xl:ml-0 '}${containerWidth} mx-auto px-4 sm:px-6 ${standalone ? 'py-3' : padding}`}>
        {standalone ? null : showNav ? (
          /* Full TopBar: [Menu] [Back] [Logo + Title] [Profile] */
          <div className="relative z-30 flex items-center justify-between mb-4 sm:mb-6 gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 sm:py-3 rounded-2xl bg-base-100/60 backdrop-blur-md border border-base-300/20 shadow-sm">
            <div className="flex items-center gap-2 shrink-0">
              {/* Fluid-island hamburger — morphs into an X while the drawer is open */}
              <button
                onClick={() => setIsNavOpen(o => !o)}
                className="relative flex h-10 w-10 items-center justify-center rounded-full
                  transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                  hover:bg-base-200/80 dark:hover:bg-white/10 active:scale-95"
                aria-label={isNavOpen
                  ? (t('common.closeNavigation') || 'Close navigation')
                  : (t('common.openNavigation') || 'Open navigation')}
                aria-expanded={isNavOpen}
              >
                <span
                  className={`absolute h-[1.5px] w-4 rounded-full bg-base-content
                    transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                    ${isNavOpen ? 'rotate-45' : '-translate-y-[4.5px]'}`}
                />
                <span
                  className={`absolute h-[1.5px] w-4 rounded-full bg-base-content
                    transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                    ${isNavOpen ? '-rotate-45' : 'translate-y-[4.5px]'}`}
                />
              </button>
              <button
                onClick={handleBackNavigation}
                disabled={isNavigating}
                className="btn btn-square btn-ghost btn-icon disabled:opacity-50"
                aria-label={t('common.backToHome') || 'Back to home'}
              >
                <span className="ri-arrow-left-line ri-16px rtl:scale-x-[-1]" />
              </button>
            </div>
            <div className="flex items-center gap-3 flex-1 justify-center min-w-0">
              {renderLogo('h-9 w-9 sm:h-10 sm:w-10')}
              {title && (
                <h1 className="text-base sm:text-lg md:text-xl font-semibold text-base-content transition-colors duration-300 flex items-center gap-2 truncate">
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
          <div className="relative z-30 flex justify-between items-center gap-3 mb-8">
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
              {/* Fluid-island hamburger — morphs into an X while the drawer is open */}
              <button
                onClick={() => setIsNavOpen(o => !o)}
                className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full
                  transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                  hover:bg-base-200/80 dark:hover:bg-white/10 active:scale-95"
                aria-label={isNavOpen
                  ? (t('common.closeNavigation') || 'Close navigation')
                  : (t('common.openNavigation') || 'Open navigation')}
                aria-expanded={isNavOpen}
              >
                <span
                  className={`absolute h-[1.5px] w-4 rounded-full bg-base-content
                    transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                    ${isNavOpen ? 'rotate-45' : '-translate-y-[4.5px]'}`}
                />
                <span
                  className={`absolute h-[1.5px] w-4 rounded-full bg-base-content
                    transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                    ${isNavOpen ? '-rotate-45' : 'translate-y-[4.5px]'}`}
                />
              </button>
            </div>
          </div>
        )}

        <div key={location.pathname}>
          {children}
        </div>
      </div>
    </div>
  );
}
