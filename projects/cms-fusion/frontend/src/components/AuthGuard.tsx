'use client';

import { ReactNode, useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import LoadingSkeleton from './ui/LoadingSkeleton';

interface AuthGuardProps {
  children: ReactNode;
  loginPath?: string;
}

const buildLoginRedirect = (loginPath: string, pathname: string | null) => {
  const next = pathname || '/';
  return `${loginPath}?next=${encodeURIComponent(next)}`;
};

/**
 * AuthGuard — protects routes by checking authentication status.
 * Checks for session cookie or localStorage token.
 */
export default function AuthGuard({ children, loginPath = '/login' }: AuthGuardProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [authState, setAuthState] = useState<'loading' | 'authenticated' | 'unauthenticated'>('loading');

  useEffect(() => {
    const hasSessionCookie = typeof document !== 'undefined' &&
      document.cookie.split(';').some(c => c.trim().startsWith('sessionid='));
    const hasLocalToken = typeof window !== 'undefined' &&
      Boolean(localStorage.getItem('auth_token') || localStorage.getItem('lms_token'));

    setAuthState(hasSessionCookie || hasLocalToken ? 'authenticated' : 'unauthenticated');
  }, []);

  useEffect(() => {
    if (authState === 'unauthenticated') {
      router.replace(buildLoginRedirect(loginPath, pathname) as never);
    }
  }, [authState, loginPath, pathname, router]);

  if (authState !== 'authenticated') {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4 py-10">
        <div className="w-full max-w-xl text-center">
          <LoadingSkeleton variant="profile" className="mb-8" />
          <LoadingSkeleton variant="card" count={2} />
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
