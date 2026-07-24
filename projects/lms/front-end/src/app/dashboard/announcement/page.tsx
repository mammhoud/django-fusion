'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiSpeakerphone, HiPlus } from 'react-icons/hi';
import ErrorState from '@/components/ui/ErrorState';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';

export default function DashboardAnnouncementPage() {
  const { data: profile } = useGetProfileQuery();
  const [announcements] = useState([
    { id: 1, title: 'New Course Coming Soon', content: 'Exciting updates for next semester...', date: '2026-07-20', status: 'published' },
    { id: 2, title: 'Assignment Due Date Extended', content: 'The deadline for assignment 3 has been extended...', date: '2026-07-18', status: 'published' },
  ]);

  if (profile?.role !== 'instructor') {
    return <ErrorState fullPage message="This page is only available for instructors." />;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Announcements</h1>
          <p className="text-gray-500 mt-1">Communicate with your students</p>
        </div>
        <button className="btn-primary flex items-center gap-2"><HiPlus className="w-4 h-4" /> New Announcement</button>
      </div>
      <div className="space-y-4">
        {announcements.map((a, idx) => (
          <motion.div key={a.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }} className="card p-5">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center flex-shrink-0"><HiSpeakerphone className="w-5 h-5 text-[rgb(var(--ctc-primary))]" /></div>
              <div className="flex-1">
                <div className="flex items-center justify-between"><h3 className="font-semibold text-gray-900">{a.title}</h3><span className="badge-primary text-xs">{a.status}</span></div>
                <p className="text-sm text-gray-500 mt-1">{a.content}</p>
                <p className="text-xs text-gray-400 mt-2">{new Date(a.date).toLocaleDateString()}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
