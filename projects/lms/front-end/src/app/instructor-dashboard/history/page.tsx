'use client';

import { motion } from 'framer-motion';
import { HiClock, HiBookOpen, HiUser, HiStar } from 'react-icons/hi';

export default function InstructorHistoryPage() {
  const activities = [
    { id: 1, action: 'Course Published', detail: 'React Fundamentals v2.0', date: '2026-07-20', icon: HiBookOpen },
    { id: 2, action: 'New Review', detail: '5-star rating on Python Course', date: '2026-07-19', icon: HiStar },
    { id: 3, action: 'Student Enrolled', detail: 'Alice joined React Fundamentals', date: '2026-07-18', icon: HiUser },
    { id: 4, action: 'Quiz Updated', detail: 'Week 3 Quiz - Added 5 questions', date: '2026-07-17', icon: HiClock },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Activity History</h1>
      <div className="space-y-4">
        {activities.map((a, idx) => (
          <motion.div key={a.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.05 }}
            className="card p-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center"><a.icon className="w-5 h-5 text-[rgb(var(--ctc-primary))]" /></div>
            <div className="flex-1"><p className="font-medium text-gray-900">{a.action}</p><p className="text-sm text-gray-500">{a.detail}</p></div>
            <span className="text-xs text-gray-400">{new Date(a.date).toLocaleDateString()}</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
