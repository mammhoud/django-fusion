'use client';

import { motion } from 'framer-motion';
import { HiCheckCircle, HiXCircle, HiClock } from 'react-icons/hi';

export default function StudentAttemptsPage() {
  const attempts = [
    { id: 1, quiz: 'React Basics Quiz', course: 'React Fundamentals', score: 85, total: 100, date: '2026-07-20', passed: true },
    { id: 2, quiz: 'Python Data Types', course: 'Advanced Python', score: 45, total: 100, date: '2026-07-15', passed: false },
    { id: 3, quiz: 'Week 2 Quiz', course: 'React Fundamentals', score: 92, total: 100, date: '2026-07-10', passed: true },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Quiz Attempts</h1>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm min-w-[400px]">
          <thead className="bg-gray-50 border-b">
            <tr><th className="text-left px-6 py-3 font-medium text-gray-500">Quiz</th><th className="text-left px-6 py-3 font-medium text-gray-500">Course</th><th className="text-center px-6 py-3 font-medium text-gray-500">Score</th><th className="text-center px-6 py-3 font-medium text-gray-500">Date</th><th className="text-center px-6 py-3 font-medium text-gray-500">Result</th></tr>
          </thead>
          <tbody className="divide-y">
            {attempts.map((a, idx) => (
              <motion.tr key={a.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.05 }} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-gray-900">{a.quiz}</td>
                <td className="px-6 py-4 text-gray-500">{a.course}</td>
                <td className="px-6 py-4 text-center font-medium">{a.score}/{a.total} ({Math.round(a.score / a.total * 100)}%)</td>
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
