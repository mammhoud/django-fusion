import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { invoke } from '@tauri-apps/api/core';

export interface AuthUser {
  id: number;
  email: string;
  name: string;
  role?: string;
}

/** Timeout options in minutes — 'never' means disabled */
export const INACTIVITY_TIMEOUT_OPTIONS = [
  { value: 'never', label: 'Never' },
  { value: '5', label: '5 min' },
  { value: '15', label: '15 min' },
  { value: '30', label: '30 min' },
  { value: '60', label: '1 hour' },
  { value: '120', label: '2 hours' },
] as const;

interface AuthContextType {
  isAuthenticated: boolean;
  isAuthRequired: boolean | null; // null = still checking
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string, rememberMe?: boolean, roleOverride?: string) => Promise<void>;
  logout: () => void;
  skipAuth: () => void;
  setupAccount: (email: string, code: string, password: string, name: string, rememberMe?: boolean) => Promise<void>;
  sendConfirmationCode: (email: string) => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  // Inactivity timeout
  inactivityTimeout: string;
  setInactivityTimeout: (value: string) => void;
  inactivityWarning: boolean;
  dismissInactivityWarning: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}

function loadUserFromStorage(): AuthUser | null {
  try {
    // Check localStorage first (persistent), then sessionStorage (temporary)
    const stored = localStorage.getItem('auth_user') || sessionStorage.getItem('auth_user');
    const authed = localStorage.getItem('is_authenticated') || sessionStorage.getItem('is_authenticated');
    if (stored && authed === 'true') {
      return JSON.parse(stored);
    }
  } catch {
    // ignore
  }
  return null;
}

function saveUserToStorage(user: AuthUser, persist: boolean = true) {
  const storage = persist ? localStorage : sessionStorage;
  storage.setItem('auth_user', JSON.stringify(user));
  storage.setItem('is_authenticated', 'true');
}

function clearAuthStorage() {
  localStorage.removeItem('auth_user');
  localStorage.removeItem('is_authenticated');
  sessionStorage.removeItem('auth_user');
  sessionStorage.removeItem('is_authenticated');
}

function loadTimeoutFromStorage(): string {
  try {
    return localStorage.getItem('inactivity_timeout') || '30';
  } catch {
    return '30';
  }
}

function saveTimeoutToStorage(value: string) {
  localStorage.setItem('inactivity_timeout', value);
}

const INACTIVITY_EVENTS = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click'];
const WARNING_BEFORE_MS = 60_000; // Show warning 1 minute before timeout

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => loadUserFromStorage() !== null);
  const [user, setUser] = useState<AuthUser | null>(() => loadUserFromStorage());
  const [isAuthRequired, setIsAuthRequired] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Inactivity timeout state
  const [inactivityTimeout, setInactivityTimeoutState] = useState<string>(loadTimeoutFromStorage);
  const [inactivityWarning, setInactivityWarning] = useState(false);
  const lastActivityRef = useRef(Date.now());

  const setInactivityTimeout = useCallback((value: string) => {
    setInactivityTimeoutState(value);
    saveTimeoutToStorage(value);
    setInactivityWarning(false);
    lastActivityRef.current = Date.now();
  }, []);

  const dismissInactivityWarning = useCallback(() => {
    setInactivityWarning(false);
    lastActivityRef.current = Date.now();
  }, []);

  const checkAuthStatus = useCallback(async () => {
    try {
      const required = await invoke<boolean>('check_auth_required');
      let hasUsers = false;
      try {
        hasUsers = await invoke<boolean>('has_users');
      } catch {
        // has_users not available — treat as no users
      }

      // Show Auth page when:
      // 1. Auth is explicitly required (env vars configured), OR
      // 2. There are existing users in the database (accounts were created)
      const showAuth = required || hasUsers;
      setIsAuthRequired(showAuth);

      if (!showAuth) {
        // No auth config AND no users — auto-authenticate for first run
        setIsAuthenticated(true);
        setUser(null);
        clearAuthStorage();
      } else if (required) {
        // Auth is required by config — check stored session
        const stored = loadUserFromStorage();
        if (stored) {
          try {
            await invoke('verify_user', { email: stored.email });
            // User verified — stay authenticated
          } catch {
            clearAuthStorage();
            setIsAuthenticated(false);
            setUser(null);
          }
        }
      } else {
        // hasUsers is true but auth is not 'required' by config
        // Don't auto-authenticate — let the user choose login or skip
        const stored = loadUserFromStorage();
        if (stored) {
          try {
            await invoke('verify_user', { email: stored.email });
          } catch {
            clearAuthStorage();
            setIsAuthenticated(false);
            setUser(null);
          }
        }
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setIsAuthRequired(false);
      setIsAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const login = useCallback(async (email: string, password: string, rememberMe?: boolean, roleOverride?: string) => {
    setIsLoading(true);
    try {
      const result = await invoke<{ id: number; email: string; name: string; role?: string }>('login_user', {
        email,
        password,
      });
      const authUser: AuthUser = {
        id: result.id,
        email: result.email,
        name: result.name,
        role: roleOverride || result.role || 'manager',
      };
      saveUserToStorage(authUser, rememberMe !== false);
      setUser(authUser);
      setIsAuthenticated(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearAuthStorage();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const skipAuth = useCallback(() => {
    setIsAuthenticated(true);
    setIsAuthRequired(false);
    setUser(null);
    clearAuthStorage();
  }, []);

  // Track user activity — only active when logged in and timeout is configured
  useEffect(() => {
    if (!isAuthenticated || !isAuthRequired || inactivityTimeout === 'never') return;

    const handleActivity = () => {
      lastActivityRef.current = Date.now();
      setInactivityWarning(false);
    };

    for (const event of INACTIVITY_EVENTS) {
      window.addEventListener(event, handleActivity, { passive: true });
    }

    return () => {
      for (const event of INACTIVITY_EVENTS) {
        window.removeEventListener(event, handleActivity);
      }
    };
  }, [isAuthenticated, isAuthRequired, inactivityTimeout]);

  // Check inactivity periodically — auto-logout when timeout reached
  useEffect(() => {
    if (!isAuthenticated || !isAuthRequired || inactivityTimeout === 'never') return;

    const timeoutMs = parseInt(inactivityTimeout, 10) * 60 * 1000;
    const checkInterval = 5000;

    const checkInactivity = () => {
      const elapsed = Date.now() - lastActivityRef.current;

      if (!inactivityWarning && elapsed >= timeoutMs - WARNING_BEFORE_MS && elapsed < timeoutMs) {
        setInactivityWarning(true);
      }

      if (elapsed >= timeoutMs) {
        setInactivityWarning(false);
        logout();
      }
    };

    const intervalId = setInterval(checkInactivity, checkInterval);
    return () => clearInterval(intervalId);
  }, [isAuthenticated, isAuthRequired, inactivityTimeout, inactivityWarning, logout]);

  const setupAccount = useCallback(async (
    email: string,
    code: string,
    password: string,
    name: string,
    rememberMe?: boolean
  ) => {
    setIsLoading(true);
    try {
      const result = await invoke<{ id: number; email: string; name: string }>('setup_account', {
        email,
        code,
        password,
        name,
      });
      const authUser: AuthUser = {
        id: result.id,
        email: result.email,
        name: result.name,
      };
      saveUserToStorage(authUser, rememberMe !== false);
      setUser(authUser);
      setIsAuthenticated(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendConfirmationCode = useCallback(async (email: string) => {
    setIsLoading(true);
    try {
      await invoke('send_auth_confirmation_code', { email });
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isAuthRequired,
        user,
        isLoading,
        login,
        logout,
        skipAuth,
        setupAccount,
        sendConfirmationCode,
        checkAuthStatus,
        inactivityTimeout,
        setInactivityTimeout,
        inactivityWarning,
        dismissInactivityWarning,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
