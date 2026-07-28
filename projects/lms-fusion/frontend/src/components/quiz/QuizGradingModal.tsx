'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  HiX, HiCheck, HiXCircle, HiDocumentText, HiExternalLink,
  HiStar, HiUser,
} from 'react-icons/hi';
import {
  useGetAttemptQuery,
  useGradeAttemptMutation,
  type QuizAttemptAnswer,
} from '@/store/api/endpoints/quiz';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

// ── Types ──

interface GradeEntry {
  answer_id: number;
  points_awarded: number;
  is_correct: boolean;
}

// ── Props ──

interface QuizGradingModalProps {
  attemptId: number;
  onClose: () => void;
}

// ── Component ──

export default function QuizGradingModal({ attemptId, onClose }: QuizGradingModalProps) {
  const { data: attemptData, isLoading, isError } = useGetAttemptQuery(attemptId);
  const [gradeAttempt, { isLoading: isGrading }] = useGradeAttemptMutation();
  const [grades, setGrades] = useState<Record<number, GradeEntry>>({});
  const [gradeSubmitted, setGradeSubmitted] = useState(false);

  const attempt = attemptData?.data;
  const answers = attempt?.answers ?? [];

  // Build initial grades from already-graded answers when data loads
  useEffect(() => {
    if (answers.length > 0 && Object.keys(grades).length === 0) {
      const initial: Record<number, GradeEntry> = {};
      for (const a of answers) {
        if (a.question_type === 'short_answer') {
          initial[a.id] = {
            answer_id: a.id,
            points_awarded: a.points_awarded,
            is_correct: a.is_correct ?? false,
          };
        }
      }
      setGrades(initial);
    }
  }, [answers]);

  const handleGradeChange = (answerId: number, field: 'points_awarded' | 'is_correct', value: number | boolean) => {
    setGrades((prev) => ({
      ...prev,
      [answerId]: {
        ...prev[answerId],
        answer_id: answerId,
        [field]: value,
      },
    }));
  };

  const handleSubmit = async () => {
    const graded_answers = Object.values(grades);
    if (graded_answers.length === 0) return;

    try {
      await gradeAttempt({ attempt_id: attemptId, graded_answers }).unwrap();
      setGradeSubmitted(true);
    } catch {
      // handled by RTK
    }
  };

  // ── Render States ──

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
        <div className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] overflow-y-auto shadow-2xl mx-4 p-6" onClick={(e) => e.stopPropagation()}>
          <LoadingSkeleton variant="detail" />
        </div>
      </div>
    );
  }

  if (isError || !attempt) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
        <div className="bg-white rounded-2xl w-full max-w-3xl shadow-2xl mx-4 p-6" onClick={(e) => e.stopPropagation()}>
          <div className="text-center py-8 text-gray-500">
            <p className="text-lg mb-2">Unable to load attempt details</p>
            <button onClick={onClose} className="btn-secondary text-sm">Close</button>
          </div>
        </div>
      </div>
    );
  }

  const shortAnswerAnswers = answers.filter((a) => a.question_type === 'short_answer');
  const autoGradedAnswers = answers.filter((a) => a.question_type !== 'short_answer');
  const needsGrading = shortAnswerAnswers.some((a) => a.is_correct === null);

  // Calculate scores
  const autoPoints = autoGradedAnswers.reduce((sum, a) => sum + (a.points_awarded || 0), 0);
  const manualPoints = Object.values(grades).reduce((sum, g) => sum + g.points_awarded, 0);
  const totalPossible = answers.reduce((sum, a) => sum + a.points_possible, 0);
  const totalPoints = autoPoints + manualPoints;
  const scorePercentage = totalPossible > 0 ? Math.round((totalPoints / totalPossible) * 100) : 0;

  // ── Grading Done State (after submit) ──

  if (gradeSubmitted) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
        <div className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] overflow-y-auto shadow-2xl mx-4" onClick={(e) => e.stopPropagation()}>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <HiCheck className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Grades Submitted</h2>
            <p className="text-gray-500 mb-6">
              Score: {totalPoints}/{totalPossible} ({scorePercentage}%)
            </p>
            <button onClick={onClose} className="btn-primary">
              Done
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div
        className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] overflow-y-auto shadow-2xl mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-100 rounded-t-2xl px-6 py-4 flex items-center justify-between z-10">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Grade Quiz Attempt</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              <HiUser className="w-3 h-3 inline mr-1" />
              {attempt.username} · {attempt.quiz_title}
              {attempt.completed_at && (
                <>
                  {' · '}
                  {new Date(attempt.completed_at).toLocaleDateString('en-US', {
                    month: 'short', day: 'numeric', year: 'numeric',
                  })}
                </>
              )}
            </p>
          </div>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <HiX className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Score Summary */}
          <div className="bg-gray-50 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className={`text-2xl font-bold ${scorePercentage >= 70 ? 'text-green-600' : 'text-yellow-600'}`}>
                  {scorePercentage}%
                </div>
                <div className="text-xs text-gray-500">Score</div>
              </div>
              <div className="h-10 w-px bg-gray-200" />
              <div>
                <div className="text-sm text-gray-900">
                  <span className="font-semibold">{totalPoints}</span> / {totalPossible} points
                </div>
                <div className="text-xs text-gray-500">
                  {autoGradedAnswers.length > 0 && (
                    <span>{autoPoints} auto-graded · </span>
                  )}
                  {shortAnswerAnswers.length} short answer
                  {shortAnswerAnswers.length !== 1 && 's'}
                  {needsGrading ? ' (needs grading)' : ''}
                </div>
              </div>
            </div>
            {needsGrading && (
              <button
                onClick={handleSubmit}
                disabled={isGrading}
                className="btn-primary flex items-center gap-2 text-sm"
              >
                <HiStar className="w-4 h-4" />
                {isGrading ? 'Saving...' : 'Submit Grades'}
              </button>
            )}
          </div>

          {/* Auto-graded Questions (read-only) */}
          {autoGradedAnswers.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <HiCheck className="w-4 h-4 text-green-500" />
                Auto-Graded Questions
              </h3>
              <div className="space-y-2">
                {autoGradedAnswers.map((answer) => (
                  <AnswerCard key={answer.id} answer={answer} readOnly />
                ))}
              </div>
            </div>
          )}

          {/* Short Answer Questions (gradable) */}
          {shortAnswerAnswers.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <HiDocumentText className="w-4 h-4 text-[rgb(var(--fu-primary))]" />
                Short Answer / Essay Questions
                {!needsGrading && (
                  <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full font-medium">All graded</span>
                )}
              </h3>
              <div className="space-y-4">
                {shortAnswerAnswers.map((answer) => {
                  const gradeEntry = grades[answer.id] || {
                    answer_id: answer.id,
                    points_awarded: answer.points_awarded,
                    is_correct: answer.is_correct ?? false,
                  };
                  const alreadyGraded = answer.is_correct !== null && !needsGrading;

                  return (
                    <AnswerCard
                      key={answer.id}
                      answer={answer}
                      readOnly={alreadyGraded}
                      gradeEntry={gradeEntry}
                      onGradeChange={(field, value) => handleGradeChange(answer.id, field, value)}
                    />
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t border-gray-100 rounded-b-2xl px-6 py-4 flex items-center justify-between">
          <button onClick={onClose} className="btn-secondary text-sm">
            Cancel
          </button>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              Score: {totalPoints}/{totalPossible}
            </span>
            {needsGrading && (
              <button
                onClick={handleSubmit}
                disabled={isGrading}
                className="btn-primary flex items-center gap-2 text-sm"
              >
                <HiStar className="w-4 h-4" />
                {isGrading ? 'Saving...' : 'Submit Grades'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Answer Card Sub-component
// ═══════════════════════════════════════════════════════════════════

function AnswerCard({
  answer,
  readOnly,
  gradeEntry,
  onGradeChange,
}: {
  answer: QuizAttemptAnswer;
  readOnly?: boolean;
  gradeEntry?: GradeEntry;
  onGradeChange?: (field: 'points_awarded' | 'is_correct', value: number | boolean) => void;
}) {
  const isShortAnswer = answer.question_type === 'short_answer';
  const isGraded = answer.is_correct !== null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border rounded-xl p-4 transition-all ${
        isGraded && !readOnly
          ? 'border-green-200 bg-green-50/30'
          : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      {/* Question Text & Type Badge */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">{answer.question_text}</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-400">
              {answer.question_type === 'multiple_choice' && 'Multiple Choice'}
              {answer.question_type === 'true_false' && 'True / False'}
              {answer.question_type === 'short_answer' && 'Short Answer'}
              {answer.question_type === 'multiple_select' && 'Multiple Select'}
            </span>
            <span className="text-xs text-gray-300">·</span>
            <span className="text-xs text-gray-400">{answer.points_possible} pts</span>
            {isGraded && (
              <>
                <span className="text-xs text-gray-300">·</span>
                <span className={`text-xs font-medium ${answer.is_correct ? 'text-green-600' : 'text-red-500'}`}>
                  {answer.is_correct ? 'Correct' : 'Incorrect'}
                </span>
              </>
            )}
          </div>
        </div>
        {/* Score badge */}
        {readOnly && (
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ml-2 ${
            answer.is_correct
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-600'
          }`}>
            {answer.points_awarded}/{answer.points_possible}
          </span>
        )}
      </div>

      {/* Student's Answer */}
      {isShortAnswer && answer.text_answer && (
        <div className="bg-gray-50 rounded-lg p-3 mb-3">
          <p className="text-xs font-medium text-gray-500 mb-1">Student's Answer:</p>
          <p className="text-sm text-gray-800 whitespace-pre-wrap">{answer.text_answer}</p>
        </div>
      )}

      {isShortAnswer && !answer.text_answer && (
        <div className="bg-gray-50 rounded-lg p-3 mb-3">
          <p className="text-xs text-gray-400 italic">No text answer provided</p>
        </div>
      )}

      {/* File Attachment */}
      {answer.file_url && (
        <a
          href={answer.file_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-xs text-[rgb(var(--fu-primary))] hover:underline mb-3"
        >
          <HiExternalLink className="w-3.5 h-3.5" />
          {answer.file_name || 'View Attachment'}
        </a>
      )}

      {/* Grading Controls (for short answer, not read-only) */}
      {isShortAnswer && !readOnly && onGradeChange && gradeEntry && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-4">
            {/* Points Input */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Points (max {answer.points_possible})
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={0}
                  max={answer.points_possible}
                  value={gradeEntry.points_awarded}
                  onChange={(e) => onGradeChange('points_awarded', Math.min(
                    answer.points_possible,
                    Math.max(0, Number(e.target.value))
                  ))}
                  className="w-20 border border-gray-300 rounded-lg px-2 py-1.5 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                />
                <span className="text-xs text-gray-400">/ {answer.points_possible}</span>
              </div>
            </div>

            {/* Correct/Incorrect Toggle */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onGradeChange('is_correct', true)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                    gradeEntry.is_correct
                      ? 'bg-green-100 text-green-700 border border-green-300'
                      : 'bg-gray-100 text-gray-500 border border-gray-200 hover:bg-gray-200'
                  }`}
                >
                  <HiCheck className="w-3.5 h-3.5 inline mr-1" />
                  Correct
                </button>
                <button
                  onClick={() => onGradeChange('is_correct', false)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                    !gradeEntry.is_correct
                      ? 'bg-red-100 text-red-600 border border-red-300'
                      : 'bg-gray-100 text-gray-500 border border-gray-200 hover:bg-gray-200'
                  }`}
                >
                  <HiXCircle className="w-3.5 h-3.5 inline mr-1" />
                  Incorrect
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
