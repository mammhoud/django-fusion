'use client';

import { ReactNode, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

interface AuthGuardProps {
  children: ReactNode;
  loginPath?: string;
}

const buildLoginRedirect = (loginPath: string, pathname: string | null) => {
  const next = pathname || '/';
  return `${loginPath}?next=${encodeURIComponent(next)}`;
};

export default function AuthGuard({ children, loginPath = '/login' }: AuthGuardProps) {
  const pathname = usePathname();
  const router = useRouter();
  const hasToken = typeof window !== 'undefined' && Boolean(localStorage.getItem('lms_token'));
  const { isLoading, isFetching, isError } = useGetProfileQuery(undefined, {
    skip: !hasToken,
  });

  useEffect(() => {
    if (!hasToken || isError) {
      router.replace(buildLoginRedirect(loginPath, pathname) as never);
    }
  }, [hasToken, isError, loginPath, pathname, router]);

  if (!hasToken || isLoading || isFetching || isError) {
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
