'use client';

import { motion } from 'framer-motion';
import { HiPlay, HiCheckCircle, HiStar, HiClock } from 'react-icons/hi';

const activities = [
  { id: 1, action: 'Completed Lesson', detail: 'React Hooks - useState Deep Dive', date: '2026-07-20', icon: HiCheckCircle },
  { id: 2, action: 'Quiz Submitted', detail: 'React Basics Quiz - Score: 85%', date: '2026-07-19', icon: HiStar },
  { id: 3, action: 'New Lesson Started', detail: 'Advanced Python - Generators', date: '2026-07-18', icon: HiPlay },
  { id: 4, action: 'Course Enrolled', detail: 'UI/UX Design Principles', date: '2026-07-15', icon: HiClock },
];

export default function StudentHistory() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Activity History</h1>
      <div className="card divide-y">
        {activities.map((a, idx) => (
          <motion.div key={a.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.05 }}
            className="p-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center"><a.icon className="w-5 h-5 text-[rgb(var(--ctc-primary))]" /></div>
            <div className="flex-1"><p className="font-medium text-gray-900">{a.action}</p><p className="text-sm text-gray-500">{a.detail}</p></div>
            <span className="text-xs text-gray-400">{new Date(a.date).toLocaleDateString()}</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
