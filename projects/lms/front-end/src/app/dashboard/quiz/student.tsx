'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { HiClock, HiCheck, HiX, HiFlag, HiArrowLeft } from 'react-icons/hi';
import {
  useGetQuizQuery,
  useStartAttemptMutation,
  useSubmitAttemptMutation,
  type QuizQuestion,
} from '@/store/api/endpoints/quiz';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

type QuizState = 'not_started' | 'in_progress' | 'completed';

export default function StudentQuizPage() {
  const searchParams = useSearchParams();
  const quizId = searchParams.get('quiz_id');

  const { data: quizData, isLoading } = useGetQuizQuery(Number(quizId), { skip: !quizId });
  const [startAttempt] = useStartAttemptMutation();
  const [submitAttempt] = useSubmitAttemptMutation();

  const [quizState, setQuizState] = useState<QuizState>('not_started');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number | string>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [flaggedQuestions, setFlaggedQuestions] = useState<number[]>([]);
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [result, setResult] = useState<{ score: number; passed: boolean; points: number; total: number } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const quiz = quizData?.data;
  const questions = quiz?.questions ?? [];

  const handleStart = async () => {
    if (!quizId) return;
    try {
      const resp = await startAttempt(Number(quizId)).unwrap();
      setAttemptId(resp.data.id);
      setTimeLeft((quiz?.time_limit || 15) * 60);
      setQuizState('in_progress');
    } catch {
      // Error handled by RTK
    }
  };

  const handleSubmit = async () => {
    if (!attemptId) return;
    setSubmitting(true);
    try {
      const answerList = Object.entries(answers).map(([qIdx, value]) => {
        const question = questions[Number(qIdx)];
        if (!question) return null;

        // Short answer / essay question
        if (question.question_type === 'short_answer') {
          return {
            question_id: question.id,
            text_answer: (value as string) || '',
          };
        }

        // MCQ / true-false: send selected choice ID
        const choiceIdx = value as number;
        const selectedChoice = question?.choices?.[choiceIdx];
        return {
          question_id: question.id,
          selected_choice_id: selectedChoice?.id,
        };
      }).filter(Boolean);

      const resp = await submitAttempt({ attempt_id: attemptId, answers: answerList as any }).unwrap();
      const data = resp.data;
      setResult({
        score: data.score ?? 0,
        passed: data.passed ?? false,
        points: data.points_earned,
        total: data.points_possible,
      });
      setQuizState('completed');
    } catch {
      // Error handled by RTK
    }
    setSubmitting(false);
  };

  // Auto-submit when timer hits 0 (stable ref to handleSubmit via a ref)
  const handleSubmitRef = useRef(handleSubmit);
  handleSubmitRef.current = handleSubmit;

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  // Timer effect — uses ref to avoid stale closure
  useEffect(() => {
    if (quizState !== 'in_progress') return;
    if (timeLeft <= 0) { handleSubmitRef.current(); return; }
    const timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    return () => clearInterval(timer);
  }, [quizState, timeLeft]);

  if (isLoading || !quizId) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Quiz Not Found</h2>
        <p className="text-gray-500 mb-4">This quiz may not exist or has been removed.</p>
        <Link href="/dashboard" className="btn-primary">Back to Dashboard</Link>
      </div>
    );
  }

  if (quizState === 'not_started') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16">
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
          <div className="w-16 h-16 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <HiClock className="w-8 h-8 text-[rgb(var(--ctc-primary))]" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{quiz.title}</h1>
          {quiz.course_title && <p className="text-gray-500 mb-2">Course: {quiz.course_title}</p>}
          <div className="flex justify-center gap-6 mt-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{questions.length}</div>
              <div className="text-xs text-gray-500">Questions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{quiz.time_limit || 'No'}min</div>
              <div className="text-xs text-gray-500">Time Limit</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{quiz.passing_score}%</div>
              <div className="text-xs text-gray-500">Pass Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{quiz.total_points}</div>
              <div className="text-xs text-gray-500">Total Points</div>
            </div>
          </div>
          {quiz.description && (
            <p className="text-sm text-gray-600 mb-6 max-w-md mx-auto">{quiz.description}</p>
          )}
          <button onClick={handleStart} className="btn-primary">
            Start Quiz
          </button>
        </div>
      </div>
    );
  }

  if (quizState === 'in_progress') {
    return (
      <div className="max-w-3xl mx-auto px-4 py-6">
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-900">
              Question {currentQuestion + 1} of {questions.length}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() =>
                setFlaggedQuestions((prev) =>
                  prev.includes(currentQuestion)
                    ? prev.filter((q) => q !== currentQuestion)
                    : [...prev, currentQuestion]
                )
              }
              className={`flex items-center gap-1 text-sm transition-colors ${
                flaggedQuestions.includes(currentQuestion)
                  ? 'text-yellow-500'
                  : 'text-gray-400 hover:text-yellow-500'
              }`}
            >
              <HiFlag className="w-4 h-4" /> Flag
            </button>
            <div
              className={`flex items-center gap-1 text-sm font-medium ${
                timeLeft < 60 ? 'text-red-600' : 'text-gray-700'
              }`}
            >
              <HiClock className="w-4 h-4" /> {formatTime(timeLeft)}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1 order-2 lg:order-1">
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 sticky top-24">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Questions</h3>
              <div className="grid grid-cols-5 gap-2">
                {questions.map((q, i) => (
                  <button
                    key={q.id}
                    onClick={() => setCurrentQuestion(i)}
                    className={`w-9 h-9 rounded-lg text-xs font-medium transition-all ${
                      i === currentQuestion
                        ? 'bg-[rgb(var(--ctc-primary))] text-white'
                        : answers[i] !== undefined
                        ? 'bg-green-100 text-green-700'
                        : flaggedQuestions.includes(i)
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-3 order-1 lg:order-2">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">
                {questions[currentQuestion]?.question_text}
              </h2>

              {/* MCQ / True-False: choice buttons */}
              {questions[currentQuestion]?.choices.length > 0 && (
                <div className="space-y-3">
                  {questions[currentQuestion]?.choices.map((choice, idx) => (
                    <button
                      key={choice.id}
                      onClick={() => setAnswers({ ...answers, [currentQuestion]: idx })}
                      className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                        answers[currentQuestion] === idx
                          ? 'border-[rgb(var(--ctc-primary))] bg-[rgb(var(--ctc-primary))]/5 text-[rgb(var(--ctc-primary-dark))]'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <span className="font-medium">{String.fromCharCode(65 + idx)}.</span>{' '}
                      {choice.text}
                    </button>
                  ))}
                </div>
              )}

              {/* Short answer / Essay: text input */}
              {questions[currentQuestion]?.choices.length === 0 && (
                <div>
                  <textarea
                    value={(answers[currentQuestion] as string) || ''}
                    onChange={(e) =>
                      setAnswers({ ...answers, [currentQuestion]: e.target.value })
                    }
                    rows={5}
                    className="input-field w-full resize-y"
                    placeholder="Type your answer here..."
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Short answer question — type your response above
                  </p>
                </div>
              )}
              <div className="flex justify-between mt-8">
                <button
                  onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                  disabled={currentQuestion === 0}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                {currentQuestion < questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentQuestion(currentQuestion + 1)}
                    className="btn-primary"
                  >
                    Next
                  </button>
                ) : (
                  <button onClick={handleSubmit} disabled={submitting} className="btn-primary">
                    {submitting ? 'Submitting...' : 'Submit Quiz'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Completed state
  const percentage = result ? Math.round((result.score / 100) * 100) : 0;
  const passed = result?.passed ?? false;
  const score = result?.points ?? 0;
  const total = result?.total ?? questions.length;

  return (
    <div className="max-w-2xl mx-auto px-4 py-16">
      <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
        <div
          className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 ${
            passed ? 'bg-green-100' : 'bg-red-100'
          }`}
        >
          {passed ? (
            <HiCheck className="w-10 h-10 text-green-600" />
          ) : (
            <HiX className="w-10 h-10 text-red-600" />
          )}
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {passed ? 'Congratulations!' : 'Keep Practicing!'}
        </h2>
        <p className="text-gray-500 mb-6">
          {passed
            ? "You passed the quiz! You're making great progress."
            : `You scored ${percentage}%, but don't give up! Review the material and try again.`}
        </p>
        <div className="relative w-32 h-32 mx-auto mb-6">
          <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 128 128">
            <circle cx="64" cy="64" r="54" fill="none" stroke="#e5e7eb" strokeWidth="8" />
            <circle
              cx="64"
              cy="64"
              r="54"
              fill="none"
              stroke={passed ? '#22c55e' : '#ef4444'}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${(percentage / 100) * 339.292} 339.292`}
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div>
              <div className="text-3xl font-bold text-gray-900">{percentage}%</div>
              <div className="text-xs text-gray-500">Score</div>
            </div>
          </div>
        </div>
        <div className="flex justify-center gap-6 mb-8">
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">{score}</div>
            <div className="text-xs text-gray-500">Earned</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-gray-600">{total}</div>
            <div className="text-xs text-gray-500">Possible</div>
          </div>
        </div>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => {
              setQuizState('not_started');
              setCurrentQuestion(0);
              setAnswers({});
              setTimeLeft(0);
              setFlaggedQuestions([]);
              setAttemptId(null);
              setResult(null);
            }}
            className="btn-secondary"
          >
            Retry Quiz
          </button>
          <Link href="/dashboard" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
