'use client';

import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  HiArrowLeft, HiClock, HiChartBar, HiAcademicCap,
  HiCheckCircle, HiXCircle, HiPlay, HiPencil, HiUsers,
} from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import {
  useGetQuizQuery,
} from '@/store/api/endpoints/quiz';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

export default function QuizDetailPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = Number(params.id);

  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const { data: quizData, isLoading, isError } = useGetQuizQuery(quizId);
  const quiz = quizData?.data;
  const questions = quiz?.questions ?? [];
  const totalPoints = questions.reduce((s, q) => s + q.points, 0);
  const isInstructor = profile?.role === 'instructor';
  const isStudent = profile?.role === 'student';

  const handleStartQuiz = () => {
    if (!quizId) return;
    router.push(`/dashboard/quiz?quiz_id=${quizId}`);
  };

  if (isLoading || profileLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <LoadingSkeleton variant="detail" />
        </div>
      </div>
    );
  }

  if (isError || !quiz) {
    return <ErrorState fullPage message="Quiz not found." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Back nav */}
        <Link
          href="/dashboard/quiz"
          className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-6 transition-colors"
        >
          <HiArrowLeft className="w-4 h-4" /> Back to Quizzes
        </Link>

        {/* Header */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 mb-8">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                    quiz.is_active
                      ? 'bg-green-100 text-green-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}
                >
                  {quiz.is_active ? 'Active' : 'Draft'}
                </span>
              </div>
              {quiz.description && (
                <p className="text-gray-600 max-w-2xl">{quiz.description}</p>
              )}
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{questions.length}</div>
              <div className="text-xs text-gray-500 mt-1">Questions</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{quiz.time_limit || '∞'}</div>
              <div className="text-xs text-gray-500 mt-1">Minutes</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{quiz.passing_score}%</div>
              <div className="text-xs text-gray-500 mt-1">Pass Score</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{totalPoints}</div>
              <div className="text-xs text-gray-500 mt-1">Total Points</div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-3 mt-6 pt-6 border-t border-gray-100">
            {isStudent && (
              <button
                onClick={handleStartQuiz}
                className="btn-primary flex items-center gap-2"
              >
                <HiPlay className="w-4 h-4" /> Start Quiz
              </button>
            )}
            {isInstructor && (
              <>
                <Link
                  href={`/dashboard/quiz/${quiz.id}/edit` as any}
                  className="btn-primary flex items-center gap-2"
                >
                  <HiPencil className="w-4 h-4" /> Edit Quiz
                </Link>
                <Link
                  href={`/dashboard/attempts?quiz_id=${quiz.id}` as any}
                  className="btn-secondary flex items-center gap-2"
                >
                  <HiUsers className="w-4 h-4" /> View Attempts
                </Link>
              </>
            )}
            {isStudent && quiz.user_attempts > 0 && (
              <Link
                href="/dashboard/attempts"
                className="btn-secondary flex items-center gap-2"
              >
                <HiChartBar className="w-4 h-4" /> My Attempts ({quiz.user_attempts})
              </Link>
            )}
          </div>

          {/* Student: Best Score */}
          {isStudent && quiz.best_score !== null && (
            <div className="mt-4 flex items-center gap-2 text-sm">
              {quiz.best_score >= quiz.passing_score ? (
                <HiCheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <HiXCircle className="w-4 h-4 text-yellow-500" />
              )}
              <span className="text-gray-600">Best score: </span>
              <span className={`font-semibold ${quiz.best_score >= quiz.passing_score ? 'text-green-600' : 'text-yellow-600'}`}>
                {Math.round(quiz.best_score)}%
              </span>
            </div>
          )}
        </div>

        {/* Questions Preview (for students) */}
        {isStudent && questions.length > 0 && (
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Question Preview</h2>
            <div className="space-y-2">
              {questions.map((q, idx) => (
                <motion.div
                  key={q.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.03 }}
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <span className="w-7 h-7 rounded-lg bg-gray-100 text-gray-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 truncate">{q.question_text}</p>
                    <p className="text-xs text-gray-500">
                      {q.question_type === 'multiple_choice' && 'Multiple Choice'}
                      {q.question_type === 'true_false' && 'True / False'}
                      {q.question_type === 'short_answer' && 'Short Answer'}
                      {q.question_type === 'multiple_select' && 'Multiple Select'}
                      {' · '}{q.points} pt{q.points !== 1 && 's'}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                    {q.question_type === 'short_answer' ? 'Essay' : 'Auto-graded'}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Instructor: Settings Summary */}
        {isInstructor && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <HiClock className="w-4 h-4 text-gray-400" /> Quiz Settings
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Max Attempts</span>
                  <span className="font-medium text-gray-900">{quiz.max_attempts || 'Unlimited'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Shuffle Questions</span>
                  <span className="font-medium text-gray-900">{quiz.shuffle_questions ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Show Correct Answers</span>
                  <span className="font-medium text-gray-900">{quiz.show_correct_answers ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">User Attempts Count</span>
                  <span className="font-medium text-gray-900">{quiz.user_attempts}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <HiAcademicCap className="w-4 h-4 text-gray-400" /> Quick Actions
              </h3>
              <div className="space-y-2">
                <Link
                  href={`/dashboard/quiz/${quiz.id}/edit` as any}
                  className="block w-full text-left px-4 py-2.5 rounded-xl bg-[rgb(var(--ctc-primary))]/5 text-[rgb(var(--ctc-primary))] hover:bg-[rgb(var(--ctc-primary))]/10 transition-colors font-medium text-sm"
                >
                  ✏️ Edit questions & settings
                </Link>
                <Link
                  href={`/dashboard/attempts?quiz_id=${quiz.id}`}
                  className="block w-full text-left px-4 py-2.5 rounded-xl bg-gray-50 text-gray-700 hover:bg-gray-100 transition-colors font-medium text-sm"
                >
                  👥 Review student attempts
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
