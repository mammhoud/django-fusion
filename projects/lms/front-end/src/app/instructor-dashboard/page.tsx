'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Redirects from the old instructor-dashboard URL to the unified /dashboard page.
 * All instructor sub-pages under /instructor-dashboard/* redirect to /dashboard/*.
 */
export default function InstructorDashboardRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/dashboard');
  }, [router]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <p className="text-gray-500">Redirecting to your dashboard...</p>
    </div>
  );
}
