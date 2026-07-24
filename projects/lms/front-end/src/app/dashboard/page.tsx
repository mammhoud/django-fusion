'use client';

import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetInstructorDashboardQuery } from '@/store/api/endpoints/instructors';
import { useGetDashboardQuery, useGetStudentEnrollmentsQuery } from '@/store/api/endpoints/students';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  HiAcademicCap, HiUserGroup, HiStar, HiChartBar, HiBookOpen, HiCurrencyDollar,
  HiClock, HiCheckCircle,
} from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function DashboardPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();

  if (profileLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!profile) {
    return (
      <ErrorState
        message="Please sign in to access your dashboard."
        fullPage
      />
    );
  }

  if (profile.role === 'instructor') {
    return <InstructorDashboard profile={profile} />;
  }

  return <StudentDashboard profile={profile} />;
}

// ═══════════════════════════════════════════════════════════════════
// Instructor Dashboard
// ═══════════════════════════════════════════════════════════════════

function InstructorDashboard({ profile }: { profile: { id: number; first_name?: string; username: string } }) {
  const { data: dashboard, isLoading } = useGetInstructorDashboardQuery(profile.id, { skip: !profile.id });

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="profile" className="mb-8" />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const stats = [
    { icon: HiBookOpen, label: 'Courses', value: dashboard?.total_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
    { icon: HiUserGroup, label: 'Students', value: dashboard?.total_students ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
    { icon: HiCurrencyDollar, label: 'Revenue', value: dashboard ? `$${dashboard.total_revenue}` : '$0', color: 'text-[rgb(var(--ctc-accent))]', bg: 'bg-[rgb(var(--ctc-accent))]/10' },
    { icon: HiStar, label: 'Rating', value: dashboard?.average_rating ?? 0, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  ];

  const quickLinks = [
    { href: '/instructor-dashboard/courses', icon: HiBookOpen, label: 'My Courses' },
    { href: '/instructor-dashboard/quiz', icon: HiChartBar, label: 'Quizzes' },
    { href: '/instructor-dashboard/review', icon: HiStar, label: 'Reviews' },
    { href: '/instructor-dashboard/announcement', icon: HiChartBar, label: 'Announcements' },
    { href: '/instructor-dashboard/enrolled-courses', icon: HiAcademicCap, label: 'Enrollments' },
    { href: '/instructor-dashboard/history', icon: HiChartBar, label: 'History' },
  ] as const;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Instructor Dashboard</h1>
        <p className="text-gray-500 mt-1">Welcome back, {profile.first_name || profile.username}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {stats.map((stat, idx) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}
            className="card p-5">
            <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-10">
        {quickLinks.map((link) => (
          <Link key={link.href} href={link.href}
            className="card p-4 flex items-center gap-3 hover:shadow-md transition-shadow group">
            <link.icon className="w-6 h-6 text-[rgb(var(--ctc-primary))] group-hover:text-[rgb(var(--ctc-primary-dark))]" />
            <span className="font-medium text-gray-700 group-hover:text-gray-900">{link.label}</span>
          </Link>
        ))}
      </div>

      {/* Getting Started CTA */}
      {dashboard?.total_courses === 0 && (
        <div className="bg-[rgb(var(--ctc-primary))]/5 border border-[rgb(var(--ctc-primary))]/20 rounded-xl p-6 mb-6 text-center">
          <HiBookOpen className="w-12 h-12 text-[rgb(var(--ctc-primary))]/40 mx-auto mb-3" />
          <h3 className="font-semibold text-gray-900 mb-1">Getting Started</h3>
          <p className="text-sm text-gray-600 mb-3">Create your first course to start teaching students.</p>
          <Link href="/instructor-dashboard/courses/new" className="btn-primary inline-flex text-sm">Create Course</Link>
        </div>
      )}

      {/* Popular Courses Table */}
      {dashboard?.popular_courses && dashboard.popular_courses.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Popular Courses</h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm min-w-[400px]">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-6 py-3 font-medium text-gray-500">Course</th>
                  <th className="text-right px-6 py-3 font-medium text-gray-500">Students</th>
                  <th className="text-right px-6 py-3 font-medium text-gray-500">Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {dashboard.popular_courses.map((course: { id: number; title: string; students: number; revenue: number }) => (
                  <tr key={course.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{course.title}</td>
                    <td className="px-6 py-4 text-right text-gray-500">{course.students}</td>
                    <td className="px-6 py-4 text-right font-medium text-gray-900">${course.revenue}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Student Dashboard
// ═══════════════════════════════════════════════════════════════════

function StudentDashboard({ profile }: { profile: { id: number; first_name?: string; username: string } }) {
  const { data: dashboard } = useGetDashboardQuery(profile.id, { skip: !profile.id });
  const { data: enrollments, isLoading: enrollLoading } = useGetStudentEnrollmentsQuery(profile.id, { skip: !profile.id });

  const statsCards = [
    { icon: HiAcademicCap, label: 'Enrolled Courses', value: dashboard?.enrolled_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
    { icon: HiCheckCircle, label: 'Completed', value: dashboard?.completed_courses ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
    { icon: HiClock, label: 'Total Hours', value: dashboard?.total_hours ?? 0, color: 'text-[rgb(var(--ctc-accent))]', bg: 'bg-[rgb(var(--ctc-accent))]/10' },
    { icon: HiChartBar, label: 'Progress', value: enrollments?.length ? Math.round(enrollments.reduce((sum, e) => sum + e.progress, 0) / enrollments.length) : 0, suffix: '%', color: 'text-[rgb(var(--ctc-primary))]', bg: 'bg-[rgb(var(--ctc-primary))]/10' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
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
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
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
          <Link href="/courses" className="text-[rgb(var(--ctc-primary))] text-sm font-medium hover:text-[rgb(var(--ctc-primary-dark))]">
            Browse More Courses
          </Link>
        </div>

        {enrollLoading ? (
          <LoadingSkeleton variant="list" count={3} />
        ) : (
          <div className="space-y-4">
            {enrollments?.map((enrollment, idx) => (
              <motion.div
                key={enrollment.id}
                initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.05 }}
                className="card p-5 flex items-center gap-5"
              >
                <div className="w-24 h-24 card-gradient rounded-lg flex items-center justify-center flex-shrink-0">
                  <HiAcademicCap className="w-8 h-8 text-white/60" />
                </div>
                <div className="flex-1 min-w-0">
                  <Link href={`/course-details/${enrollment.course}`}
                    className="font-semibold text-gray-900 hover:text-[rgb(var(--ctc-primary))] transition-colors line-clamp-1">
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
                    <div className="progress-track">
                      <div className="progress-fill"
                        style={{ width: `${enrollment.progress}%` }} />
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
