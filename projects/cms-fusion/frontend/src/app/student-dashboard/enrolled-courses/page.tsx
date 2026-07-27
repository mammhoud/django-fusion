'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiBookOpen, HiCheckCircle, HiClock, HiArrowRight, HiAcademicCap, HiFilter, HiSearch } from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetStudentEnrollmentsQuery } from '@/store/api/endpoints/students';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/ui/EmptyState';
import ErrorState from '@/components/ui/ErrorState';

type FilterStatus = 'all' | 'active' | 'completed';

export default function StudentEnrolledCoursesPage() {
  const { data: profile } = useGetProfileQuery();
  const { data: enrollments, isLoading, error, refetch } = useGetStudentEnrollmentsQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });

  const [filter, setFilter] = useState<FilterStatus>('all');
  const [search, setSearch] = useState('');

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="profile" className="mb-8" />
        <LoadingSkeleton variant="list" count={3} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <ErrorState
          message="Could not load your enrolled courses. Please try again."
          onRetry={refetch}
        />
      </div>
    );
  }

  const filteredEnrollments = (enrollments || [])
    .filter((e) => {
      if (filter === 'active') return !e.is_completed && e.status === 'active';
      if (filter === 'completed') return e.is_completed || e.status === 'completed';
      return true;
    })
    .filter((e) =>
      search ? e.course_title.toLowerCase().includes(search.toLowerCase()) : true
    );

  const stats = {
    total: enrollments?.length || 0,
    completed: enrollments?.filter((e) => e.is_completed).length || 0,
    active: enrollments?.filter((e) => !e.is_completed && e.status === 'active').length || 0,
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Courses</h1>
        <p className="text-gray-500 mt-1">Track your learning progress across all courses</p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Total Enrolled', value: stats.total, color: 'text-[rgb(var(--ctc-primary))]', bg: 'bg-[rgb(var(--ctc-primary))]/10' },
          { label: 'In Progress', value: stats.active, color: 'text-blue-600', bg: 'bg-blue-100' },
          { label: 'Completed', value: stats.completed, color: 'text-green-600', bg: 'bg-green-100' },
        ].map((stat) => (
          <div key={stat.label} className="card p-4 text-center">
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex gap-2">
          {(['all', 'active', 'completed'] as FilterStatus[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                filter === f
                  ? 'bg-[rgb(var(--ctc-primary))] text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>
        <div className="relative flex-1 sm:max-w-xs">
          <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search courses..."
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-[rgb(var(--ctc-primary))] focus:border-transparent outline-none"
          />
        </div>
      </div>

      {/* Course List */}
      {isLoading ? (
        <LoadingSkeleton variant="list" count={4} />
      ) : filteredEnrollments.length === 0 ? (
        <EmptyState
          icon="courses"
          title={search || filter !== 'all' ? 'No matching courses' : 'No courses yet'}
          description={
            search || filter !== 'all'
              ? 'Try adjusting your search or filter.'
              : 'Start your learning journey by enrolling in a course.'
          }
          actionLabel="Browse Courses"
          actionHref="/courses"
        />
      ) : (
        <div className="space-y-4">
          {filteredEnrollments.map((enrollment, idx) => (
            <motion.div
              key={enrollment.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              className="card p-5 flex items-center gap-5 hover:shadow-md transition-shadow"
            >
              {/* Thumbnail */}
              <div className="w-24 h-24 bg-gradient-to-br from-[rgb(var(--ctc-primary))] to-[rgb(var(--ctc-accent))] rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden">
                {enrollment.course_thumbnail ? (
                  <img src={enrollment.course_thumbnail} alt="" className="w-full h-full object-cover" />
                ) : (
                  <HiBookOpen className="w-8 h-8 text-white/60" />
                )}
              </div>

              {/* Course Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <Link
                      href={`/course-details/${enrollment.course}`}
                      className="font-semibold text-gray-900 hover:text-[rgb(var(--ctc-primary))] transition-colors line-clamp-1"
                    >
                      {enrollment.course_title}
                    </Link>
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <HiAcademicCap className="w-4 h-4" />
                        {enrollment.instructor_name || 'Instructor'}
                      </span>
                      <span className="flex items-center gap-1">
                        <HiClock className="w-4 h-4" />
                        {enrollment.duration || 'Self-paced'}
                      </span>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 flex-shrink-0">
                    Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="flex items-center justify-between text-sm mb-1.5">
                    <span className="text-gray-500">
                      {enrollment.is_completed ? 'Completed' : 'In Progress'}
                    </span>
                    <span className="font-semibold text-gray-700">{Math.round(enrollment.progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${enrollment.progress}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className={`h-full rounded-full ${
                        enrollment.is_completed ? 'bg-green-500' : 'bg-[rgb(var(--ctc-primary))]'
                      }`}
                    />
                  </div>
                </div>
              </div>

              {/* Action */}
              {enrollment.is_completed ? (
                <div className="flex flex-col items-center gap-1 flex-shrink-0">
                  <HiCheckCircle className="w-8 h-8 text-green-500" />
                  <span className="text-xs text-green-600 font-medium">Done</span>
                </div>
              ) : (                  <Link
                  href={`/course-details/${enrollment.course}`}
                  className="flex flex-col items-center gap-1 flex-shrink-0 group">
                  <div className="w-10 h-10 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center group-hover:bg-[rgb(var(--ctc-primary))]/20 transition-colors">
                    <HiArrowRight className="w-5 h-5 text-[rgb(var(--ctc-primary))]" />
                  </div>
                  <span className="text-xs text-[rgb(var(--ctc-primary))] font-medium">Continue</span>
                </Link>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
