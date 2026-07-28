'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  HiPlus, HiTrash, HiPencil, HiCheck, HiX, HiClipboardList, HiUserGroup, HiStar,
} from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import {
  useGetAssignmentsQuery,
  useCreateAssignmentMutation,
  useUpdateAssignmentMutation,
  useDeleteAssignmentMutation,
  useGetAssignmentSubmissionsQuery,
  useGradeSubmissionMutation,
  type Assignment,
  type AssignmentSubmission,
} from '@/store/api/endpoints/assignments';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

// ── Constants ──

const COURSES_LIST = [
  { id: 1, title: 'React Fundamentals' },
  { id: 2, title: 'Advanced Python' },
  { id: 3, title: 'Machine Learning' },
];

// ── Main Page ──

export default function DashboardAssignmentPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const {
    data: assignmentsData,
    isLoading: assLoading,
    error: assError,
    refetch,
  } = useGetAssignmentsQuery();
  const [createAssignment, { isLoading: isCreating }] = useCreateAssignmentMutation();
  const [updateAssignment, { isLoading: isUpdating }] = useUpdateAssignmentMutation();
  const [deleteAssignment] = useDeleteAssignmentMutation();

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({
    title: '',
    course_id: 1,
    description: '',
    instructions: '',
    due_date: '',
    max_score: 100,
    is_published: true,
  });
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [formError, setFormError] = useState('');

  // Grading modal state
  const [gradingSubmission, setGradingSubmission] = useState<AssignmentSubmission | null>(null);
  const [gradingAssignmentId, setGradingAssignmentId] = useState<number | null>(null);

  const isInstructor = profile?.role === 'instructor';
  const assignments = assignmentsData?.results ?? [];

  const resetForm = useCallback(() => {
    setForm({ title: '', course_id: 1, description: '', instructions: '', due_date: '', max_score: 100, is_published: true });
    setFormError('');
    setEditingId(null);
    setShowForm(false);
  }, []);

  const openEdit = useCallback((a: Assignment) => {
    setForm({
      title: a.title,
      course_id: a.course,
      description: a.description,
      instructions: a.instructions,
      due_date: a.due_date ? a.due_date.slice(0, 16) : '',
      max_score: a.max_score,
      is_published: a.is_published,
    });
    setEditingId(a.id);
    setShowForm(true);
    setFormError('');
  }, []);

  const handleSubmit = async () => {
    if (!form.title.trim()) {
      setFormError('Title is required.');
      return;
    }
    try {
      const payload = {
        ...form,
        due_date: form.due_date ? new Date(form.due_date).toISOString() : undefined,
      };
      if (editingId !== null) {
        await updateAssignment({ id: editingId, data: payload }).unwrap();
      } else {
        await createAssignment(payload as any).unwrap();
      }
      resetForm();
      refetch();
    } catch (err: any) {
      setFormError(err?.data?.message || 'Failed to save assignment.');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAssignment(id).unwrap();
      setDeleteConfirm(null);
      refetch();
    } catch { /* ignore */ }
  };

  if (profileLoading) {
    return (
      <div className="min-h-[40vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!isInstructor) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <ErrorState fullPage message="This page is only available for instructors." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-500 mt-1">Manage course assignments and grade submissions</p>
        </div>
        {!showForm && (
          <button onClick={() => { resetForm(); setShowForm(true); }}
            className="btn-primary flex items-center gap-2">
            <HiPlus className="w-4 h-4" /> New Assignment
          </button>
        )}
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {editingId ? 'Edit Assignment' : 'New Assignment'}
            </h2>
            <button onClick={resetForm} className="text-gray-400 hover:text-gray-600"><HiX className="w-5 h-5" /></button>
          </div>

          {formError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2 mb-4">{formError}</div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input type="text" value={form.title}
                  onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                  placeholder="e.g., Week 3 Homework" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Course</label>
                <select value={form.course_id}
                  onChange={(e) => setForm((f) => ({ ...f, course_id: Number(e.target.value) }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none">
                  {COURSES_LIST.map((c) => (
                    <option key={c.id} value={c.id}>{c.title}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                rows={2}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none resize-none"
                placeholder="Brief description..." />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Instructions</label>
              <textarea value={form.instructions}
                onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))}
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none resize-none"
                placeholder="Detailed instructions for students..." />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                <input type="datetime-local" value={form.due_date}
                  onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Score</label>
                <input type="number" value={form.max_score}
                  onChange={(e) => setForm((f) => ({ ...f, max_score: Number(e.target.value) }))}
                  min={0} max={1000}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none" />
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.is_published}
                    onChange={(e) => setForm((f) => ({ ...f, is_published: e.target.checked }))}
                    className="rounded border-gray-300 text-[rgb(var(--fu-primary))] focus:ring-[rgb(var(--fu-primary))]" />
                  <span className="text-sm text-gray-700">Published</span>
                </label>
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button onClick={resetForm}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg">
                Cancel
              </button>
              <button onClick={handleSubmit} disabled={isCreating || isUpdating}
                className="btn-primary flex items-center gap-2 text-sm">
                {isCreating || isUpdating ? 'Saving...' : editingId ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading */}
      {assLoading && <div className="space-y-4"><LoadingSkeleton variant="card" count={3} /></div>}

      {/* Error */}
      {assError && !assLoading && (
        <ErrorState message="Failed to load assignments." onRetry={() => refetch()} />
      )}

      {/* Assignment List */}
      {!assLoading && !assError && (
        <div className="space-y-4">
          {assignments.length === 0 ? (
            <EmptyState icon="generic" title="No assignments yet"
              description="Create your first assignment for a course."
              actionLabel="Create Assignment"
              onAction={() => { resetForm(); setShowForm(true); }} />
          ) : (
            assignments.map((a, idx) => (
              <motion.div key={a.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }} className="card p-5">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-[rgb(var(--fu-primary))]/10 rounded-full flex items-center justify-center flex-shrink-0">
                    <HiClipboardList className="w-5 h-5 text-[rgb(var(--fu-primary))]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <div>
                        <h3 className="font-semibold text-gray-900">{a.title}</h3>
                        <p className="text-xs text-gray-500 mt-0.5">{a.course_title}</p>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {a.is_published ? (
                          <span className="badge-primary text-xs">Published</span>
                        ) : (
                          <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full font-medium">Draft</span>
                        )}
                        {a.submissions_count > 0 && (
                          <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                            <HiUserGroup className="w-3 h-3" /> {a.submissions_count}
                          </span>
                        )}
                      </div>
                    </div>
                    {a.description && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{a.description}</p>
                    )}
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        {a.due_date && (
                          <span>Due: {new Date(a.due_date).toLocaleDateString('en-US', {
                            year: 'numeric', month: 'short', day: 'numeric',
                          })}</span>
                        )}
                        <span>{a.max_score} pts</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button onClick={() => setGradingAssignmentId(a.id)}
                          className="text-xs text-[rgb(var(--fu-primary))] hover:underline flex items-center gap-1">
                          <HiStar className="w-3.5 h-3.5" /> Grade
                        </button>
                        <button onClick={() => openEdit(a)} className="text-gray-400 hover:text-gray-600" title="Edit">
                          <HiPencil className="w-4 h-4" />
                        </button>
                        {deleteConfirm === a.id ? (
                          <div className="flex items-center gap-1">
                            <button onClick={() => handleDelete(a.id)}
                              className="text-red-500 hover:text-red-700" title="Confirm"><HiCheck className="w-4 h-4" /></button>
                            <button onClick={() => setDeleteConfirm(null)}
                              className="text-gray-400 hover:text-gray-600" title="Cancel"><HiX className="w-4 h-4" /></button>
                          </div>
                        ) : (
                          <button onClick={() => setDeleteConfirm(a.id)}
                            className="text-gray-400 hover:text-red-500" title="Delete"><HiTrash className="w-4 h-4" /></button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}

      {/* Grading Modal */}
      {gradingAssignmentId && (
        <GradingModal
          assignmentId={gradingAssignmentId}
          onClose={() => { setGradingAssignmentId(null); setGradingSubmission(null); }}
        />
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Grading Modal
// ═══════════════════════════════════════════════════════════════════

function GradingModal({
  assignmentId,
  onClose,
}: {
  assignmentId: number;
  onClose: () => void;
}) {
  const { data: submissionsData, isLoading } = useGetAssignmentSubmissionsQuery(assignmentId);
  const [gradeSubmission, { isLoading: isGrading }] = useGradeSubmissionMutation();

  const [gradeForm, setGradeForm] = useState<Record<number, { score: string; feedback: string }>>({});

  const submissions = submissionsData?.results ?? [];

  const handleGrade = async (submissionId: number, maxScore: number) => {
    const entry = gradeForm[submissionId];
    if (!entry) return;

    const score = parseInt(entry.score, 10);
    if (isNaN(score) || score < 0 || score > maxScore) return;

    try {
      await gradeSubmission({
        submissionId,
        data: { score, feedback: entry.feedback },
      }).unwrap();
      setGradeForm((prev) => {
        const next = { ...prev };
        delete next[submissionId];
        return next;
      });
    } catch { /* ignore */ }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto shadow-2xl mx-4"
        onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Grade Submissions</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><HiX className="w-5 h-5" /></button>
        </div>

        <div className="p-6">
          {isLoading ? (
            <LoadingSkeleton variant="card" count={3} />
          ) : submissions.length === 0 ? (
            <EmptyState icon="generic" title="No submissions yet"
              description="Students haven't submitted this assignment yet." />
          ) : (
            <div className="space-y-6">
              {submissions.map((sub) => {
                const gradeEntry = gradeForm[sub.id] || { score: '', feedback: sub.feedback || '' };
                const isGraded = sub.status === 'graded';

                return (
                  <motion.div key={sub.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    className={`border rounded-xl p-4 ${isGraded ? 'border-green-200 bg-green-50/30' : 'border-gray-200'}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-medium text-gray-900 text-sm">{sub.student_name}</h4>
                        <p className="text-xs text-gray-500">
                          Submitted {new Date(sub.submitted_at).toLocaleDateString('en-US', {
                            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                          })}
                          {sub.is_late && <span className="text-red-500 ml-2">Late</span>}
                        </p>
                      </div>
                      {isGraded && (
                        <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full font-medium">
                          Graded: {sub.score}/{sub.max_score}
                        </span>
                      )}
                    </div>

                    {/* Submission Content */}
                    {sub.text_submission && (
                      <div className="bg-gray-50 rounded-lg p-3 mb-3 text-sm text-gray-700 whitespace-pre-wrap max-h-32 overflow-y-auto">
                        {sub.text_submission}
                      </div>
                    )}
                    {sub.file_url && (
                      <a href={sub.file_url} target="_blank" rel="noopener noreferrer"
                        className="text-xs text-[rgb(var(--fu-primary))] hover:underline">
                        📎 {sub.file_name || 'View Attachment'}
                      </a>
                    )}

                    {isGraded && sub.feedback && (
                      <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-xs font-medium text-green-800 mb-1">Feedback:</p>
                        <p className="text-sm text-green-700">{sub.feedback}</p>
                      </div>
                    )}

                    {/* Grade Form */}
                    {!isGraded && (
                      <div className="mt-4 space-y-2">
                        <div className="flex items-center gap-3">
                          <div className="flex-1">
                            <label className="block text-xs font-medium text-gray-600 mb-1">Score (max {sub.max_score})</label>
                            <input type="number" min={0} max={sub.max_score}
                              value={gradeEntry.score}
                              onChange={(e) => setGradeForm((prev) => ({
                                ...prev,
                                [sub.id]: { ...prev[sub.id] || { feedback: '' }, score: e.target.value },
                              }))}
                              className="w-24 border border-gray-300 rounded-lg px-2 py-1.5 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                              placeholder="Score" />
                          </div>
                          <button onClick={() => handleGrade(sub.id, sub.max_score)}
                            disabled={isGrading || !gradeEntry.score}
                            className="btn-primary text-xs px-3 py-1.5">
                            {isGrading ? 'Saving...' : 'Submit Grade'}
                          </button>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Feedback</label>
                          <textarea value={gradeEntry.feedback}
                            onChange={(e) => setGradeForm((prev) => ({
                              ...prev,
                              [sub.id]: { ...prev[sub.id] || { score: '' }, feedback: e.target.value },
                            }))}
                            rows={2}
                            className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none resize-none"
                            placeholder="Write feedback..." />
                        </div>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
