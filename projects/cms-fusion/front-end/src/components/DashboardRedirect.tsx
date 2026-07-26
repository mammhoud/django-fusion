'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Redirects from /instructor-dashboard/* to /dashboard/* paths.
 * Usage: sub-page files import and render this with the path they should redirect to.
 */
export default function DashboardRedirect({ to }: { to: string }) {
  const router = useRouter();
  useEffect(() => { router.replace(to); }, [router, to]);
  return <div className="min-h-[60vh] flex items-center justify-center"><p className="text-gray-500">Redirecting to dashboard...</p></div>;
}
