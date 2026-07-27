'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiBookOpen, HiCheckCircle, HiArrowRight } from 'react-icons/hi';

export default function StudentEnrolledCourses() {
  const courses = [
    { id: 1, title: 'React Fundamentals', instructor: 'John Doe', progress: 65, enrolled: '2026-07-01', lessons: 24, completed: 16 },
    { id: 2, title: 'Advanced Python', instructor: 'Jane Smith', progress: 30, enrolled: '2026-07-05', lessons: 20, completed: 6 },
    { id: 3, title: 'UI/UX Design Principles', instructor: 'Bob Johnson', progress: 90, enrolled: '2026-06-15', lessons: 18, completed: 16 },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Courses</h1>
      <div className="space-y-4">
        {courses.map((c, idx) => (
          <motion.div key={c.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}
            className="card p-5 flex items-center gap-5">
            <div className="w-16 h-16 card-gradient rounded-xl flex items-center justify-center flex-shrink-0">
              <HiBookOpen className="w-8 h-8 text-white/60" />
            </div>
            <div className="flex-1 min-w-0">
              <Link href={`/course-details/${c.id}`} className="font-semibold text-gray-900 hover:text-[rgb(var(--ctc-primary))] transition-colors">{c.title}</Link>
              <p className="text-sm text-gray-500">{c.instructor}</p>
              <div className="mt-2">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-500">{c.completed}/{c.lessons} lessons</span>
                  <span className="font-medium text-gray-700">{c.progress}%</span>
                </div>
                <div className="progress-track"><div className="progress-fill" style={{ width: `${c.progress}%` }} /></div>
              </div>
            </div>
            {c.progress === 100 ? <HiCheckCircle className="w-8 h-8 text-green-500 flex-shrink-0" /> : <HiArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
