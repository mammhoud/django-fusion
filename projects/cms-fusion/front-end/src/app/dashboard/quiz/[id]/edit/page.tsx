'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HiArrowLeft, HiPlus, HiTrash, HiPencil, HiSave,
  HiDotsVertical, HiChevronUp, HiChevronDown, HiMenu,
} from 'react-icons/hi';
import {
  useGetQuizQuery,
  useUpdateQuizMutation,
  useCreateQuestionMutation,
  useUpdateQuestionMutation,
  useDeleteQuestionMutation,
  useReorderQuestionsMutation,
  type QuizQuestion,
  type Quiz,
} from '@/store/api/endpoints/quiz';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

const QUESTION_TYPES = [
  { value: 'multiple_choice', label: 'Multiple Choice' },
  { value: 'true_false', label: 'True / False' },
  { value: 'short_answer', label: 'Short Answer / Essay' },
  { value: 'multiple_select', label: 'Multiple Select' },
];

interface QuestionFormData {
  question_type: string;
  question_text: string;
  explanation: string;
  points: number;
  choices: { text: string; is_correct: boolean }[];
}

const emptyQuestion = (): QuestionFormData => ({
  question_type: 'multiple_choice',
  question_text: '',
  explanation: '',
  points: 1,
  choices: [
    { text: '', is_correct: false },
    { text: '', is_correct: false },
  ],
});

export default function QuizEditorPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = Number(params.id);

  const { data: quizData, isLoading, isError } = useGetQuizQuery(quizId);
  const [updateQuiz] = useUpdateQuizMutation();
  const [createQuestion] = useCreateQuestionMutation();
  const [updateQuestion] = useUpdateQuestionMutation();
  const [deleteQuestion] = useDeleteQuestionMutation();
  const [reorderQuestions] = useReorderQuestionsMutation();

  const [quizSettings, setQuizSettings] = useState<Partial<Quiz>>({});
  const [settingsDirty, setSettingsDirty] = useState(false);
  const [saving, setSaving] = useState(false);

  // Question editing state
  const [editingQuestion, setEditingQuestion] = useState<QuestionFormData | null>(null);
  const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set());

  // Drag-to-reorder state
  const [localQuestions, setLocalQuestions] = useState<QuizQuestion[]>([]);
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const [isReordering, setIsReordering] = useState(false);

  const quiz = quizData?.data;
  const serverQuestions = quiz?.questions ?? [];

  // Sync local questions when server data changes and no drag is in progress
  useEffect(() => {
    if (!dragIndex && serverQuestions.length > 0) {
      setLocalQuestions(serverQuestions);
    }
  }, [serverQuestions, dragIndex]);

  useEffect(() => {
    if (quiz) {
      setQuizSettings({
        title: quiz.title,
        description: quiz.description,
        passing_score: quiz.passing_score,
        time_limit: quiz.time_limit,
        max_attempts: quiz.max_attempts,
        shuffle_questions: quiz.shuffle_questions,
        show_correct_answers: quiz.show_correct_answers,
        is_active: quiz.is_active,
      });
    }
  }, [quiz]);

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await updateQuiz({ id: quizId, data: quizSettings }).unwrap();
      setSettingsDirty(false);
    } catch {
      // handled by RTK
    }
    setSaving(false);
  };

  const handleAddQuestion = () => {
    setEditingQuestion(emptyQuestion());
    setEditingQuestionId(null);
  };

  const handleEditQuestion = (q: QuizQuestion) => {
    setEditingQuestion({
      question_type: q.question_type,
      question_text: q.question_text,
      explanation: q.explanation,
      points: q.points,
      choices: q.choices.map((c) => ({
        text: c.text || '',
        is_correct: c.is_correct ?? false,
      })),
    });
    setEditingQuestionId(q.id);
  };

  const handleSaveQuestion = async () => {
    if (!editingQuestion || !editingQuestion.question_text.trim()) return;

    try {
      if (editingQuestionId) {
        await updateQuestion({
          id: editingQuestionId,
          data: {
            question_type: editingQuestion.question_type as any,
            question_text: editingQuestion.question_text,
            explanation: editingQuestion.explanation,
            points: editingQuestion.points,
            choices: editingQuestion.choices.filter((c) => c.text.trim()),
          } as any,
        }).unwrap();
      } else {
        await createQuestion({
          quiz_id: quizId,
          data: {
            question_type: editingQuestion.question_type as any,
            question_text: editingQuestion.question_text,
            explanation: editingQuestion.explanation,
            points: editingQuestion.points,
            choices: editingQuestion.choices.filter((c) => c.text.trim()),
          } as any,
        }).unwrap();
      }
      setEditingQuestion(null);
      setEditingQuestionId(null);
    } catch {
      // handled by RTK
    }
  };

  const handleDeleteQuestion = async (id: number) => {
    try {
      await deleteQuestion(id).unwrap();
      setDeletingId(null);
    } catch {
      // handled by RTK
    }
  };

  // ── Drag-to-Reorder Handlers ──

  const handleDragStart = useCallback((e: React.DragEvent<Element>, index: number) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', String(index));
    // Delay setting dragIndex so the drag image captures properly
    requestAnimationFrame(() => {
      setDragIndex(index);
    });
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (dragIndex !== index) {
      setDragOverIndex(index);
    }
  }, [dragIndex]);

  const handleDragLeave = useCallback(() => {
    setDragOverIndex(null);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    const sourceIndex = Number(e.dataTransfer.getData('text/plain'));

    if (isNaN(sourceIndex) || sourceIndex === dropIndex) {
      setDragIndex(null);
      setDragOverIndex(null);
      return;
    }

    // Reorder local state optimistically
    const updated = [...localQuestions];
    const [moved] = updated.splice(sourceIndex, 1);
    updated.splice(dropIndex, 0, moved);
    setLocalQuestions(updated);
    setDragIndex(null);
    setDragOverIndex(null);
    setIsReordering(true);

    // Send batch update to server
    try {
      const reordered = updated.map((q, idx) => ({ id: q.id, order: idx + 1 }));
      await reorderQuestions({ quiz_id: quizId, questions: reordered }).unwrap();
    } catch {
      // Revert on failure by resetting to server data
      setLocalQuestions(serverQuestions);
    }
    setIsReordering(false);
  }, [localQuestions, quizId, reorderQuestions, serverQuestions]);

  const handleDragEnd = useCallback(() => {
    setDragIndex(null);
    setDragOverIndex(null);
  }, []);

  const handleMoveUp = useCallback(async (index: number) => {
    if (index === 0) return;
    const updated = [...localQuestions];
    [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
    setLocalQuestions(updated);
    setIsReordering(true);
    try {
      const reordered = updated.map((q, idx) => ({ id: q.id, order: idx + 1 }));
      await reorderQuestions({ quiz_id: quizId, questions: reordered }).unwrap();
    } catch {
      setLocalQuestions(serverQuestions);
    }
    setIsReordering(false);
  }, [localQuestions, quizId, reorderQuestions, serverQuestions]);

  const handleMoveDown = useCallback(async (index: number) => {
    if (index === localQuestions.length - 1) return;
    const updated = [...localQuestions];
    [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
    setLocalQuestions(updated);
    setIsReordering(true);
    try {
      const reordered = updated.map((q, idx) => ({ id: q.id, order: idx + 1 }));
      await reorderQuestions({ quiz_id: quizId, questions: reordered }).unwrap();
    } catch {
      setLocalQuestions(serverQuestions);
    }
    setIsReordering(false);
  }, [localQuestions, quizId, reorderQuestions, serverQuestions]);

  const updateChoice = (idx: number, field: 'text' | 'is_correct', value: string | boolean) => {
    if (!editingQuestion) return;
    const choices = [...editingQuestion.choices];
    choices[idx] = { ...choices[idx], [field]: value };

    if (field === 'is_correct' && value === true &&
        (editingQuestion.question_type === 'multiple_choice' || editingQuestion.question_type === 'true_false')) {
      for (let i = 0; i < choices.length; i++) {
        if (i !== idx) choices[i].is_correct = false;
      }
    }

    setEditingQuestion({ ...editingQuestion, choices });
  };

  const addChoice = () => {
    if (!editingQuestion) return;
    setEditingQuestion({
      ...editingQuestion,
      choices: [...editingQuestion.choices, { text: '', is_correct: false }],
    });
  };

  const removeChoice = (idx: number) => {
    if (!editingQuestion || editingQuestion.choices.length <= 2) return;
    setEditingQuestion({
      ...editingQuestion,
      choices: editingQuestion.choices.filter((_, i) => i !== idx),
    });
  };

  const toggleQuestionExpand = (id: number) => {
    setExpandedQuestions((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <LoadingSkeleton variant="detail" />
        </div>
      </div>
    );
  }

  if (isError || !quiz) {
    return <ErrorState fullPage message="Quiz not found." />;
  }

  const questions = localQuestions;
  const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link
            href="/dashboard/quiz"
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <HiArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
            <p className="text-sm text-gray-500">
              {questions.length} question{questions.length !== 1 && 's'} · {totalPoints} total points
            </p>
          </div>
          {settingsDirty && (
            <button
              onClick={handleSaveSettings}
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              <HiSave className="w-4 h-4" /> {saving ? 'Saving...' : 'Save Changes'}
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Quiz Settings */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 sticky top-24">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quiz Settings</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input
                    type="text"
                    value={quizSettings.title || ''}
                    onChange={(e) => { setQuizSettings((p) => ({ ...p, title: e.target.value })); setSettingsDirty(true); }}
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={quizSettings.description || ''}
                    onChange={(e) => { setQuizSettings((p) => ({ ...p, description: e.target.value })); setSettingsDirty(true); }}
                    rows={3}
                    className="input-field w-full resize-y"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Passing Score (%)</label>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={quizSettings.passing_score ?? 70}
                      onChange={(e) => { setQuizSettings((p) => ({ ...p, passing_score: Number(e.target.value) })); setSettingsDirty(true); }}
                      className="input-field w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Time Limit (min)</label>
                    <input
                      type="number"
                      min={0}
                      value={quizSettings.time_limit ?? 0}
                      onChange={(e) => { setQuizSettings((p) => ({ ...p, time_limit: Number(e.target.value) })); setSettingsDirty(true); }}
                      className="input-field w-full"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Attempts</label>
                  <input
                    type="number"
                    min={0}
                    value={quizSettings.max_attempts ?? 0}
                    onChange={(e) => { setQuizSettings((p) => ({ ...p, max_attempts: Number(e.target.value) })); setSettingsDirty(true); }}
                    className="input-field w-full"
                  />
                  <p className="text-xs text-gray-400 mt-1">0 = unlimited</p>
                </div>

                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={quizSettings.shuffle_questions ?? false}
                      onChange={(e) => { setQuizSettings((p) => ({ ...p, shuffle_questions: e.target.checked })); setSettingsDirty(true); }}
                      className="rounded border-gray-300 text-[rgb(var(--ctc-primary))] focus:ring-[rgb(var(--ctc-primary))]"
                    />
                    <span className="text-sm text-gray-700">Shuffle questions</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={quizSettings.show_correct_answers ?? true}
                      onChange={(e) => { setQuizSettings((p) => ({ ...p, show_correct_answers: e.target.checked })); setSettingsDirty(true); }}
                      className="rounded border-gray-300 text-[rgb(var(--ctc-primary))] focus:ring-[rgb(var(--ctc-primary))]"
                    />
                    <span className="text-sm text-gray-700">Show correct answers</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={quizSettings.is_active ?? true}
                      onChange={(e) => { setQuizSettings((p) => ({ ...p, is_active: e.target.checked })); setSettingsDirty(true); }}
                      className="rounded border-gray-300 text-[rgb(var(--ctc-primary))] focus:ring-[rgb(var(--ctc-primary))]"
                    />
                    <span className="text-sm text-gray-700">Active (visible to students)</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Questions */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Questions</h2>
              <div className="flex items-center gap-2">
                {isReordering && (
                  <span className="text-xs text-gray-400 animate-pulse">Saving order...</span>
                )}
                <button onClick={handleAddQuestion} className="btn-primary flex items-center gap-2 text-sm">
                  <HiPlus className="w-4 h-4" /> Add Question
                </button>
              </div>
            </div>

            {/* Question Editor Modal */}
            <AnimatePresence>
              {editingQuestion && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4"
                  onClick={() => setEditingQuestion(null)}
                >
                  <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                    className="bg-white rounded-2xl p-6 shadow-xl max-w-2xl w-full max-h-[85vh] overflow-y-auto"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      {editingQuestionId ? 'Edit Question' : 'New Question'}
                    </h3>

                    <div className="space-y-4">
                      {/* Question Type */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Question Type</label>
                        <select
                          value={editingQuestion.question_type}
                          onChange={(e) => {
                            const qType = e.target.value;
                            let choices = editingQuestion.choices;
                            if (qType === 'true_false') {
                              choices = [
                                { text: 'True', is_correct: false },
                                { text: 'False', is_correct: false },
                              ];
                            } else if (qType === 'short_answer') {
                              choices = [];
                            } else if (choices.length < 2) {
                              choices = [
                                { text: '', is_correct: false },
                                { text: '', is_correct: false },
                              ];
                            }
                            setEditingQuestion({ ...editingQuestion, question_type: qType, choices });
                          }}
                          className="input-field w-full"
                        >
                          {QUESTION_TYPES.map((t) => (
                            <option key={t.value} value={t.value}>{t.label}</option>
                          ))}
                        </select>
                      </div>

                      {/* Question Text */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Question</label>
                        <textarea
                          value={editingQuestion.question_text}
                          onChange={(e) => setEditingQuestion({ ...editingQuestion, question_text: e.target.value })}
                          rows={3}
                          className="input-field w-full resize-y"
                          placeholder="Enter your question..."
                        />
                      </div>

                      {/* Choices */}
                      {editingQuestion.choices.length > 0 && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Answer Choices
                            {editingQuestion.question_type === 'multiple_choice' && (
                              <span className="text-xs text-gray-400 ml-2">(select one correct answer)</span>
                            )}
                            {editingQuestion.question_type === 'multiple_select' && (
                              <span className="text-xs text-gray-400 ml-2">(select all correct answers)</span>
                            )}
                          </label>
                          <div className="space-y-2">
                            {editingQuestion.choices.map((choice, idx) => (
                              <div key={idx} className="flex items-center gap-2">
                                <input
                                  type={
                                    editingQuestion.question_type === 'multiple_select'
                                      ? 'checkbox'
                                      : 'radio'
                                  }
                                  name={`choice-correct-${idx}`}
                                  checked={choice.is_correct}
                                  onChange={(e) => updateChoice(idx, 'is_correct', e.target.checked)}
                                  className="rounded border-gray-300 text-[rgb(var(--ctc-primary))] focus:ring-[rgb(var(--ctc-primary))]"
                                />
                                <input
                                  type="text"
                                  value={choice.text}
                                  onChange={(e) => updateChoice(idx, 'text', e.target.value)}
                                  placeholder={`Choice ${idx + 1}`}
                                  className="input-field flex-1"
                                />
                                {editingQuestion.choices.length > 2 && (
                                  <button
                                    onClick={() => removeChoice(idx)}
                                    className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                  >
                                    <HiTrash className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            ))}
                          </div>
                          <button
                            onClick={addChoice}
                            className="mt-2 text-sm text-[rgb(var(--ctc-primary))] hover:underline flex items-center gap-1"
                          >
                            <HiPlus className="w-3 h-3" /> Add choice
                          </button>
                        </div>
                      )}

                      {/* Points & Explanation */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Points</label>
                          <input
                            type="number"
                            min={1}
                            value={editingQuestion.points}
                            onChange={(e) => setEditingQuestion({ ...editingQuestion, points: Math.max(1, Number(e.target.value)) })}
                            className="input-field w-full"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Explanation
                          <span className="text-xs text-gray-400 ml-2">(shown after answering)</span>
                        </label>
                        <textarea
                          value={editingQuestion.explanation}
                          onChange={(e) => setEditingQuestion({ ...editingQuestion, explanation: e.target.value })}
                          rows={2}
                          className="input-field w-full resize-y"
                          placeholder="Explain the correct answer..."
                        />
                      </div>
                    </div>

                    <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
                      <button
                        onClick={() => { setEditingQuestion(null); setEditingQuestionId(null); }}
                        className="btn-secondary"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSaveQuestion}
                        disabled={!editingQuestion.question_text.trim()}
                        className="btn-primary disabled:opacity-50"
                      >
                        {editingQuestionId ? 'Update Question' : 'Add Question'}
                      </button>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Delete Confirm Modal */}
            <AnimatePresence>
              {deletingId && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4"
                  onClick={() => setDeletingId(null)}
                >
                  <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                    className="bg-white rounded-2xl p-6 shadow-xl max-w-sm w-full"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Question?</h3>
                    <p className="text-sm text-gray-600 mb-6">This cannot be undone.</p>
                    <div className="flex justify-end gap-3">
                      <button onClick={() => setDeletingId(null)} className="btn-secondary">Cancel</button>
                      <button onClick={() => handleDeleteQuestion(deletingId)} className="btn-danger bg-red-600 text-white px-4 py-2 rounded-xl hover:bg-red-700 transition-colors font-medium">
                        Delete
                      </button>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Question List with Drag-to-Reorder */}
            <div className="space-y-3">
              {questions.length === 0 ? (
                <div className="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <HiDotsVertical className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">No questions yet</h3>
                  <p className="text-sm text-gray-500 mb-4">Add your first question to get started.</p>
                  <button onClick={handleAddQuestion} className="btn-primary">
                    <HiPlus className="w-4 h-4 inline mr-1" /> Add Question
                  </button>
                </div>
              ) : (
                questions.map((q, idx) => {
                  const isDragging = dragIndex === idx;
                  const isDragOver = dragOverIndex === idx;

                  return (
                    <motion.div
                      key={q.id}
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{
                        opacity: isDragging ? 0.5 : 1,
                        y: 0,
                        scale: isDragging ? 1.02 : 1,
                        borderColor: isDragOver ? 'rgb(var(--ctc-primary))' : undefined,
                      }}
                      transition={{ delay: dragIndex !== null ? 0 : idx * 0.03, duration: 0.2 }}
                      className={`bg-white rounded-xl shadow-sm border ${
                        isDragOver ? 'border-2 border-dashed' : 'border-gray-100'
                      } overflow-hidden cursor-default`}
                      draggable
                      onDragStart={(e) => handleDragStart(e as unknown as React.DragEvent<Element>, idx)}
                      onDragOver={(e) => handleDragOver(e, idx)}
                      onDragLeave={handleDragLeave}
                      onDrop={(e) => handleDrop(e, idx)}
                      onDragEnd={handleDragEnd}
                      style={{
                        ...(isDragOver && dragIndex !== idx
                          ? { transform: 'translateY(4px)', transition: 'transform 0.15s ease' }
                          : {}),
                      }}
                    >
                      <div
                        className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                        onClick={() => toggleQuestionExpand(q.id)}
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {/* Drag Handle */}
                          <span
                            className="flex-shrink-0 text-gray-300 hover:text-gray-500 cursor-grab active:cursor-grabbing transition-colors select-none"
                            title="Drag to reorder"
                          >
                            <HiMenu className="w-5 h-5" />
                          </span>

                          {/* Number Badge */}
                          <span className="w-8 h-8 rounded-lg bg-[rgb(var(--ctc-primary))]/10 text-[rgb(var(--ctc-primary))] flex items-center justify-center text-sm font-bold flex-shrink-0">
                            {idx + 1}
                          </span>
                          <div className="min-w-0">
                            <p className="font-medium text-gray-900 truncate">{q.question_text}</p>
                            <p className="text-xs text-gray-500">
                              {q.question_type.replace('_', ' ')} · {q.points} pt{q.points !== 1 && 's'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                          {/* Move Up */}
                          <button
                            onClick={() => handleMoveUp(idx)}
                            disabled={idx === 0}
                            className="p-1.5 text-gray-300 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                            title="Move up"
                          >
                            <HiChevronUp className="w-4 h-4" />
                          </button>
                          {/* Move Down */}
                          <button
                            onClick={() => handleMoveDown(idx)}
                            disabled={idx === questions.length - 1}
                            className="p-1.5 text-gray-300 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                            title="Move down"
                          >
                            <HiChevronDown className="w-4 h-4" />
                          </button>
                          {/* Edit */}
                          <button
                            onClick={() => handleEditQuestion(q)}
                            className="p-1.5 text-gray-400 hover:text-[rgb(var(--ctc-primary))] hover:bg-[rgb(var(--ctc-primary))]/5 rounded-lg transition-colors"
                            title="Edit question"
                          >
                            <HiPencil className="w-4 h-4" />
                          </button>
                          {/* Delete */}
                          <button
                            onClick={() => setDeletingId(q.id)}
                            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete question"
                          >
                            <HiTrash className="w-4 h-4" />
                          </button>
                          {/* Expand/Collapse */}
                          <button
                            onClick={(e) => { e.stopPropagation(); toggleQuestionExpand(q.id); }}
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
                            title={expandedQuestions.has(q.id) ? 'Collapse details' : 'Expand details'}
                          >
                            {expandedQuestions.has(q.id) ? (
                              <HiChevronUp className="w-4 h-4" />
                            ) : (
                              <HiChevronDown className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                      </div>

                      <AnimatePresence>
                        {expandedQuestions.has(q.id) && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="border-t border-gray-100"
                          >
                            <div className="p-4 space-y-3 bg-gray-50/50">
                              {q.explanation && (
                                <div>
                                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Explanation</span>
                                  <p className="text-sm text-gray-700 mt-1">{q.explanation}</p>
                                </div>
                              )}
                              {q.choices.length > 0 && (
                                <div>
                                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Choices</span>
                                  <div className="mt-1 space-y-1">
                                    {q.choices.map((c) => (
                                      <div key={c.id} className={`text-sm px-3 py-1.5 rounded-lg ${c.is_correct ? 'bg-green-50 text-green-700 font-medium' : 'text-gray-600'}`}>
                                        {c.is_correct && <span className="mr-1.5">✓</span>}
                                        {c.text}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
