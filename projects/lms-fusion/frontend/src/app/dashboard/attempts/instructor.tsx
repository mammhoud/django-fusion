'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { HiUser, HiCheckCircle, HiXCircle, HiStar } from 'react-icons/hi';
import {
  useGetAttemptsQuery,
  useGetQuizAttemptsQuery,
} from '@/store/api/endpoints/quiz';
import QuizGradingModal from '@/components/quiz/QuizGradingModal';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

export default function InstructorAttempts() {
  const searchParams = useSearchParams();
  const quizId = searchParams.get('quiz_id');
  const [gradingAttemptId, setGradingAttemptId] = useState<number | null>(null);

  const { data: allAttemptsData, isLoading: allLoading } = useGetAttemptsQuery(undefined, {
    skip: !!quizId,
  });
  const { data: quizAttemptsData, isLoading: quizLoading } = useGetQuizAttemptsQuery(
    Number(quizId),
    { skip: !quizId }
  );

  const isLoading = quizId ? quizLoading : allLoading;
  const attempts = quizId
    ? quizAttemptsData?.results ?? []
    : allAttemptsData?.results ?? [];

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        {quizId ? 'Quiz Attempts' : 'Student Attempts'}
      </h1>
      {attempts.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No attempts yet</p>
          <p className="text-sm mt-1">Student submissions will appear here.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm min-w-[650px]">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Student</th>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Quiz</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Score</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Date</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Result</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Actions</th>
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
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <HiUser className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900">{a.username}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{a.quiz_title}</td>
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
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => setGradingAttemptId(a.id)}
                      className="inline-flex items-center gap-1.5 text-xs font-medium text-[rgb(var(--fu-primary))] hover:bg-[rgb(var(--fu-primary))]/5 px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <HiStar className="w-3.5 h-3.5" /> Grade
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Grading Modal */}
      {gradingAttemptId && (
        <QuizGradingModal
          attemptId={gradingAttemptId}
          onClose={() => setGradingAttemptId(null)}
        />
      )}
    </div>
  );
}
