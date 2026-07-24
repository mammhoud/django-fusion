'use client';

import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetInstructorDashboardQuery } from '@/store/api/endpoints/instructors';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiAcademicCap, HiUserGroup, HiStar, HiChartBar, HiBookOpen, HiCurrencyDollar } from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

export default function InstructorDashboardPage() {
  const { data: profile } = useGetProfileQuery();
  const { data: dashboard, isLoading } = useGetInstructorDashboardQuery(profile?.id ?? 0, { skip: !profile?.id });

  const stats = [
    { icon: HiBookOpen, label: 'Courses', value: dashboard?.total_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
    { icon: HiUserGroup, label: 'Students', value: dashboard?.total_students ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
    { icon: HiCurrencyDollar, label: 'Revenue', value: dashboard ? `$${dashboard.total_revenue}` : '$0', color: 'text-[rgb(var(--ctc-accent))]', bg: 'bg-[rgb(var(--ctc-accent))]/10' },
    { icon: HiStar, label: 'Rating', value: dashboard?.average_rating ?? 0, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  ];

  if (!profile) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <LoadingSkeleton variant="profile" />
          <div className="mt-8"><LoadingSkeleton variant="card" count={4} /></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Instructor Dashboard</h1>
        <p className="text-gray-500 mt-1">Welcome back, {profile.first_name || profile.username}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {stats.map((stat, idx) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}
            className="card p-5">
            <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}><stat.icon className={`w-6 h-6 ${stat.color}`} /></div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {([
          { href: '/instructor-dashboard/courses' as const, icon: HiBookOpen, label: 'My Courses' },
          { href: '/instructor-dashboard/quiz' as const, icon: HiChartBar, label: 'Quizzes' },
          { href: '/instructor-dashboard/assignment' as const, icon: HiAcademicCap, label: 'Assignments' },
          { href: '/instructor-dashboard/review' as const, icon: HiStar, label: 'Reviews' },
          { href: '/instructor-dashboard/announcement' as const, icon: HiChartBar, label: 'Announcements' },
          { href: '/instructor-dashboard/attempts' as const, icon: HiUserGroup, label: 'Student Attempts' },
          { href: '/instructor-dashboard/enrolled-courses' as const, icon: HiAcademicCap, label: 'Enrollments' },
          { href: '/instructor-dashboard/history' as const, icon: HiChartBar, label: 'History' },
        ] as const).map((link, idx) => (
          <Link key={link.href} href={link.href}
            className="card p-4 flex items-center gap-3 hover:shadow-md transition-shadow group">
            <link.icon className="w-6 h-6 text-[rgb(var(--ctc-primary))] group-hover:text-[rgb(var(--ctc-primary-dark))]" />
            <span className="font-medium text-gray-700 group-hover:text-gray-900">{link.label}</span>
          </Link>
        ))}
      </div>

      {/* Getting Started */}
      {dashboard?.total_courses === 0 && (
        <div className="bg-[rgb(var(--ctc-primary))]/5 border border-[rgb(var(--ctc-primary))]/20 rounded-xl p-6 mb-6 text-center">
          <HiBookOpen className="w-12 h-12 text-[rgb(var(--ctc-primary))]/40 mx-auto mb-3" />
          <h3 className="font-semibold text-gray-900 mb-1">Getting Started</h3>
          <p className="text-sm text-gray-600 mb-3">Create your first course to start teaching students.</p>
          <Link href="/instructor-dashboard/courses/new" className="btn-primary inline-flex text-sm">Create Course</Link>
        </div>
      )}

      {/* Popular Courses */}
      {dashboard?.popular_courses && dashboard.popular_courses.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Popular Courses</h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm min-w-[400px]">
              <thead className="bg-gray-50 border-b">
                <tr><th className="text-left px-6 py-3 font-medium text-gray-500">Course</th><th className="text-right px-6 py-3 font-medium text-gray-500">Students</th><th className="text-right px-6 py-3 font-medium text-gray-500">Revenue</th></tr>
              </thead>
              <tbody className="divide-y">
                {dashboard.popular_courses.map((course) => (
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
