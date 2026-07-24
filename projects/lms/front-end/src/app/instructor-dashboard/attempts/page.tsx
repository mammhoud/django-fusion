'use client';

import { motion } from 'framer-motion';
import { HiUser, HiClock, HiCheckCircle, HiXCircle } from 'react-icons/hi';

export default function InstructorAttemptsPage() {
  const attempts = [
    { id: 1, student: 'Alice Johnson', quiz: 'React Basics Quiz', score: 85, total: 100, date: '2026-07-20', passed: true },
    { id: 2, student: 'Bob Smith', quiz: 'Python Data Types', score: 45, total: 100, date: '2026-07-19', passed: false },
    { id: 3, student: 'Carol Williams', quiz: 'React Basics Quiz', score: 92, total: 100, date: '2026-07-18', passed: true },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Student Attempts</h1>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm min-w-[500px]">
          <thead className="bg-gray-50 border-b">
            <tr><th className="text-left px-6 py-3 font-medium text-gray-500">Student</th><th className="text-left px-6 py-3 font-medium text-gray-500">Quiz</th><th className="text-center px-6 py-3 font-medium text-gray-500">Score</th><th className="text-center px-6 py-3 font-medium text-gray-500">Date</th><th className="text-center px-6 py-3 font-medium text-gray-500">Result</th></tr>
          </thead>
          <tbody className="divide-y">
            {attempts.map((a, idx) => (
              <motion.tr key={a.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.05 }} className="hover:bg-gray-50">
                <td className="px-6 py-4"><div className="flex items-center gap-2"><HiUser className="w-4 h-4 text-gray-400" /><span className="font-medium text-gray-900">{a.student}</span></div></td>
                <td className="px-6 py-4 text-gray-500">{a.quiz}</td>
                <td className="px-6 py-4 text-center font-medium">{a.score}/{a.total}</td>
                <td className="px-6 py-4 text-center text-gray-500">{new Date(a.date).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-center">{a.passed ? <HiCheckCircle className="w-5 h-5 text-green-500 mx-auto" /> : <HiXCircle className="w-5 h-5 text-red-500 mx-auto" />}</td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
