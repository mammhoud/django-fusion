'use client';

import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import InstructorAttempts from './instructor';
import StudentAttempts from './student';

export default function DashboardAttemptsPage() {
  const { data: profile, isLoading, isError } = useGetProfileQuery();
  if (isLoading) return <div className="min-h-[60vh] flex items-center justify-center"><LoadingSkeleton variant="profile" /></div>;
  if (isError || !profile) return <ErrorState fullPage message="Please sign in to access this page." />;
  if (profile.role === 'instructor') return <InstructorAttempts />;
  return <StudentAttempts />;
}
