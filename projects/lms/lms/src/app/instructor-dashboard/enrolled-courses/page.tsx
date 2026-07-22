'use client';

import { motion } from 'framer-motion';
import { HiAcademicCap, HiUser } from 'react-icons/hi';

export default function InstructorEnrolledCoursesPage() {
  const enrollments = [
    { id: 1, course: 'React Fundamentals', student: 'Alice Johnson', enrolled: '2026-07-01', progress: 65 },
    { id: 2, course: 'React Fundamentals', student: 'Bob Smith', enrolled: '2026-07-02', progress: 30 },
    { id: 3, course: 'Advanced Python', student: 'Carol Williams', enrolled: '2026-06-15', progress: 90 },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Enrolled Students</h1>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm min-w-[500px]">
          <thead className="bg-gray-50 border-b">
            <tr><th className="text-left px-6 py-3 font-medium text-gray-500">Student</th><th className="text-left px-6 py-3 font-medium text-gray-500">Course</th><th className="text-left px-6 py-3 font-medium text-gray-500">Enrolled</th><th className="text-left px-6 py-3 font-medium text-gray-500">Progress</th></tr>
          </thead>
          <tbody className="divide-y">
            {enrollments.map((e, idx) => (
              <motion.tr key={e.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.05 }} className="hover:bg-gray-50">
                <td className="px-6 py-4"><div className="flex items-center gap-2"><HiUser className="w-4 h-4 text-gray-400" /><span className="font-medium text-gray-900">{e.student}</span></div></td>
                <td className="px-6 py-4 text-gray-500">{e.course}</td>
                <td className="px-6 py-4 text-gray-500">{new Date(e.enrolled).toLocaleDateString()}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3"><div className="w-full max-w-xs bg-gray-200 rounded-full h-2"><div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${e.progress}%` }} /></div><span className="text-sm font-medium text-gray-700">{e.progress}%</span></div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
