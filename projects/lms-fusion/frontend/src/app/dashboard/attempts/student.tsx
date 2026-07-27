'use client';

import { motion } from 'framer-motion';
import { HiCheckCircle, HiXCircle } from 'react-icons/hi';
import { useGetAttemptsQuery } from '@/store/api/endpoints/quiz';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

export default function StudentAttempts() {
  const { data: attemptsData, isLoading } = useGetAttemptsQuery();
  const attempts = attemptsData?.results ?? [];

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <LoadingSkeleton variant="list" count={3} />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Quiz Attempts</h1>
      {attempts.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No quiz attempts yet</p>
          <p className="text-sm mt-1">Take a quiz to see your results here.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm min-w-[400px]">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Quiz</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Score</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Date</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {attempts.map((a, idx) => (
                <motion.tr
                  key={a.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="hover:bg-gray-50"
                >
                  <td className="px-6 py-4 font-medium text-gray-900">{a.quiz_title}</td>
                  <td className="px-6 py-4 text-center font-medium">
                    {a.score !== null ? `${Math.round(a.score)}%` : '—'}
                  </td>
                  <td className="px-6 py-4 text-center text-gray-500">
                    {new Date(a.started_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {a.passed === true ? (
                      <HiCheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                    ) : a.passed === false ? (
                      <HiXCircle className="w-5 h-5 text-red-500 mx-auto" />
                    ) : (
                      <span className="text-xs text-gray-400">Pending</span>
                    )}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
