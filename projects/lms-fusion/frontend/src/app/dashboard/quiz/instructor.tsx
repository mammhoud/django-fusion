'use client';

import { useState } from 'react';
import Link from 'next/link';
import { HiPlus, HiPencil, HiTrash, HiClock, HiChartBar, HiDotsVertical } from 'react-icons/hi';
import {
  useGetQuizzesQuery,
  useCreateQuizMutation,
  useDeleteQuizMutation,
} from '@/store/api/endpoints/quiz';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

export default function InstructorQuizPage() {
  const [filter, setFilter] = useState<'all' | 'is_active' | '!is_active'>('all');
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState('');

  const { data: quizzesData, isLoading } = useGetQuizzesQuery({});
  const [createQuiz] = useCreateQuizMutation();
  const [deleteQuiz] = useDeleteQuizMutation();

  const allQuizzes = quizzesData?.results ?? [];
  const filtered =
    filter === 'all'
      ? allQuizzes
      : allQuizzes.filter((q) => (filter === 'is_active' ? q.is_active : !q.is_active));

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    await createQuiz({ title: newTitle.trim() } as any);
    setNewTitle('');
    setShowCreate(false);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this quiz?')) {
      await deleteQuiz(id);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <LoadingSkeleton variant="card" count={3} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Quiz Management</h1>
            <p className="text-sm text-gray-500 mt-1">{allQuizzes.length} quizzes</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="btn-primary flex items-center gap-2"
          >
            <HiPlus className="w-4 h-4" /> Create Quiz
          </button>
        </div>

        {/* Create Quiz Inline Form */}
        {showCreate && (
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200 mb-4 flex items-center gap-3">
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Enter quiz title..."
              className="input-field flex-1"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            />
            <button onClick={handleCreate} className="btn-primary text-sm px-4 py-2">
              Create
            </button>
            <button
              onClick={() => { setShowCreate(false); setNewTitle(''); }}
              className="btn-secondary text-sm px-4 py-2"
            >
              Cancel
            </button>
          </div>
        )}

        {/* Filter */}
        <div className="flex gap-2 mb-6">
          {[
            { key: 'all', label: 'All' },
            { key: 'is_active', label: 'Active' },
            { key: '!is_active', label: 'Draft' },
          ].map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key as any)}
              className={`px-4 py-2 text-sm rounded-lg transition-all font-medium ${
                filter === f.key
                  ? 'bg-[rgb(var(--fu-primary))] text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Quiz List */}
        <div className="space-y-3">
          {filtered.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg mb-2">No quizzes yet</p>
              <p className="text-sm">Create your first quiz to get started.</p>
            </div>
          ) : (
            filtered.map((quiz) => (
              <div
                key={quiz.id}
                className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <Link
                        href={`/dashboard/quiz/${quiz.id}` as any}
                        className="font-semibold text-gray-900 hover:text-[rgb(var(--fu-primary))] transition-colors"
                      >
                        {quiz.title}
                      </Link>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          quiz.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {quiz.is_active ? 'Active' : 'Draft'}
                      </span>
                    </div>
                    {quiz.course_title && (
                      <p className="text-sm text-gray-500">{quiz.course_title}</p>
                    )}
                    <div className="flex items-center gap-6 mt-3 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <HiClock className="w-4 h-4" /> {quiz.question_count} questions
                      </span>
                      <span className="flex items-center gap-1">
                        <HiClock className="w-4 h-4" /> {quiz.time_limit || 'No'} min
                      </span>
                      <span className="flex items-center gap-1">
                        <HiChartBar className="w-4 h-4" /> {quiz.total_points} pts
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/dashboard/quiz/${quiz.id}/edit` as any}
                      className="p-2 text-gray-400 hover:text-[rgb(var(--fu-primary))] hover:bg-[rgb(var(--fu-primary))]/5 rounded-lg transition-colors"
                    >
                      <HiPencil className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => handleDelete(quiz.id)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <HiTrash className="w-4 h-4" />
                    </button>
                    <Link
                      href={`/dashboard/quiz/${quiz.id}/attempts` as any}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <HiDotsVertical className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
