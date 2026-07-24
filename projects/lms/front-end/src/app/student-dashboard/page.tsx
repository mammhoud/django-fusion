'use client';

import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetDashboardQuery, useGetStudentEnrollmentsQuery } from '@/store/api/endpoints/students';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiAcademicCap, HiClock, HiCheckCircle, HiChartBar, HiBookOpen } from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function StudentDashboard() {
  const { data: profile } = useGetProfileQuery();
  const { data: dashboard, isLoading: dashLoading } = useGetDashboardQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });
  const { data: enrollments } = useGetStudentEnrollmentsQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });

  if (!profile) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSkeleton variant="profile" className="mb-8" />
          <LoadingSkeleton variant="card" count={4} />
        </div>
      </div>
    );
  }

  const statsCards = [
    { icon: HiAcademicCap, label: 'Enrolled Courses', value: dashboard?.enrolled_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
    { icon: HiCheckCircle, label: 'Completed', value: dashboard?.completed_courses ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
    { icon: HiClock, label: 'Total Hours', value: dashboard?.total_hours ?? 0, color: 'text-purple-600', bg: 'bg-purple-100' },
    { icon: HiChartBar, label: 'Progress', value: enrollments?.length ? Math.round(enrollments.reduce((sum, e) => sum + e.progress, 0) / enrollments.length) : 0, suffix: '%', color: 'text-indigo-600', bg: 'bg-indigo-100' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {profile.first_name || profile.username}!
        </h1>
        <p className="text-gray-500 mt-1">Here&apos;s your learning progress</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {statsCards.map((stat, idx) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.1 }}
            className="card p-5"
          >
            <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}{stat.suffix || ''}</div>
            <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Enrolled Courses */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">My Courses</h2>
          <Link href="/courses" className="text-indigo-600 text-sm font-medium hover:text-indigo-700">
            Browse More Courses
          </Link>
        </div>

        {dashLoading ? (
          <LoadingSkeleton variant="list" count={3} />
        ) : (
          <div className="space-y-4">
            {enrollments?.map((enrollment, idx) => (
              <motion.div
                key={enrollment.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.05 }}
                className="card p-5 flex items-center gap-5"
              >
                <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <HiAcademicCap className="w-8 h-8 text-white/60" />
                </div>
                <div className="flex-1 min-w-0">
                  <Link href={`/course-details/${enrollment.course}`}
                        className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors line-clamp-1">
                    {enrollment.course_title}
                  </Link>
                  <p className="text-sm text-gray-500 mt-1">
                    Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}
                  </p>
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-500">Progress</span>
                      <span className="font-medium text-gray-700">{enrollment.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${enrollment.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
                {enrollment.is_completed && (
                  <HiCheckCircle className="w-8 h-8 text-green-500 flex-shrink-0" />
                )}
              </motion.div>
            ))}
            {(!enrollments || enrollments.length === 0) && (
              <EmptyState icon="courses" title="No courses yet" description="Start your learning journey by enrolling in a course." actionLabel="Browse Courses" actionHref="/courses" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
