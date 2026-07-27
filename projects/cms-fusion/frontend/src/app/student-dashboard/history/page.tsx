'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiPlay, HiCheckCircle, HiStar, HiClock, HiBookOpen, HiAcademicCap, HiFilter } from 'react-icons/hi';
import type { IconType } from 'react-icons';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetDashboardQuery } from '@/store/api/endpoints/students';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/ui/EmptyState';

const activityIcons: Record<string, { icon: IconType; color: string; bg: string }> = {
  completed: { icon: HiCheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
  enrolled: { icon: HiAcademicCap, color: 'text-blue-600', bg: 'bg-blue-100' },
  started: { icon: HiPlay, color: 'text-[rgb(var(--ctc-accent))]', bg: 'bg-[rgb(var(--ctc-accent))]/10' },
  quiz: { icon: HiStar, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  review: { icon: HiBookOpen, color: 'text-[rgb(var(--ctc-primary))]', bg: 'bg-[rgb(var(--ctc-primary))]/10' },
};

function getActivityMeta(action: string) {
  const lower = action.toLowerCase();
  if (lower.includes('complete')) return activityIcons.completed;
  if (lower.includes('enroll')) return activityIcons.enrolled;
  if (lower.includes('start') || lower.includes('begin')) return activityIcons.started;
  if (lower.includes('quiz') || lower.includes('score')) return activityIcons.quiz;
  if (lower.includes('review')) return activityIcons.review;
  return { icon: HiClock, color: 'text-gray-600', bg: 'bg-gray-100' };
}

export default function StudentHistoryPage() {
  const { data: profile } = useGetProfileQuery();
  const { data: dashboard, isLoading } = useGetDashboardQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });
  const [filter, setFilter] = useState<string>('all');

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="profile" className="mb-8" />
        <LoadingSkeleton variant="list" count={5} />
      </div>
    );
  }

  const activities = (dashboard?.recent_activity || []).map((a: any) => ({
    id: a.id || Math.random(),
    action: a.course__title ? `Activity in "${a.course__title}"` : 'Course activity',
    detail: a.progress !== undefined ? `Progress: ${Math.round(a.progress)}%` : '',
    date: a.last_accessed_at || new Date().toISOString(),
    percentage: a.progress || 0,
  }));

  const filtered = filter === 'all' ? activities : activities.filter((a) => a.action.includes(filter));

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Activity History</h1>
          <p className="text-gray-500 mt-1">Track your learning journey</p>
        </div>
        <div className="flex items-center gap-2">
          <HiFilter className="w-4 h-4 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[rgb(var(--ctc-primary))] outline-none"
          >
            <option value="all">All Activity</option>
            <option value="complete">Completed</option>
            <option value="enroll">Enrolled</option>
            <option value="quiz">Quizzes</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Courses Enrolled', value: dashboard?.enrolled_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
          { label: 'Completed', value: dashboard?.completed_courses ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
          { label: 'Hours Learned', value: dashboard?.total_hours ?? 0, color: 'text-[rgb(var(--ctc-accent))]', bg: 'bg-[rgb(var(--ctc-accent))]/10', suffix: 'h' },
        ].map((stat) => (
          <div key={stat.label} className="card p-4 text-center">
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}{stat.suffix || ''}</div>
            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Timeline */}
      {isLoading ? (
        <LoadingSkeleton variant="list" count={5} />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon="inbox"
          title="No activity yet"
          description="Your learning activity will appear here as you study."
          actionLabel="Browse Courses"
          actionHref="/courses"
        />
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

          <div className="space-y-4">
            {filtered.map((activity, idx) => {
              const meta = getActivityMeta(activity.action);
              return (
                <motion.div
                  key={activity.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  className="relative pl-14"
                >
                  {/* Timeline dot */}
                  <div className={`absolute left-3 top-4 w-4 h-4 rounded-full border-2 border-white ${meta.bg} ${meta.color} ring-2 ring-white`} style={{ backgroundColor: 'currentColor' }} />

                  {/* Card */}
                  <div className="card p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 ${meta.bg} rounded-full flex items-center justify-center flex-shrink-0`}>
                        <meta.icon className={`w-5 h-5 ${meta.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900">{activity.action}</p>
                        {activity.detail && (
                          <p className="text-sm text-gray-500 mt-0.5">{activity.detail}</p>
                        )}
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-xs text-gray-400">
                            {new Date(activity.date).toLocaleDateString('en-US', {
                              month: 'short', day: 'numeric', year: 'numeric',
                              hour: '2-digit', minute: '2-digit',
                            })}
                          </span>
                          {activity.percentage > 0 && (
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-gray-200 rounded-full h-1.5">
                                <div
                                  className="bg-[rgb(var(--ctc-primary))]/50 h-1.5 rounded-full"
                                  style={{ width: `${activity.percentage}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500">{Math.round(activity.percentage)}%</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
