'use client';

import { useState } from 'react';
import Link from 'next/link';
import { HiPlus, HiPencil, HiTrash, HiClock, HiChartBar, HiDotsVertical } from 'react-icons/hi';

const mockQuizzes = [
  { id: 'q1', title: 'React Fundamentals Quiz', course: 'Advanced React Development', questions: 10, timeLimit: 15, attempts: 234, avgScore: 78, status: 'Active' },
  { id: 'q2', title: 'TypeScript Basics', course: 'Full-Stack TypeScript', questions: 8, timeLimit: 10, attempts: 189, avgScore: 82, status: 'Active' },
  { id: 'q3', title: 'Python Data Structures', course: 'Python for Data Science', questions: 12, timeLimit: 20, attempts: 312, avgScore: 71, status: 'Active' },
  { id: 'q4', title: 'Final Assessment', course: 'Advanced React Development', questions: 25, timeLimit: 45, attempts: 98, avgScore: 74, status: 'Draft' },
  { id: 'q5', title: 'Machine Learning Basics', course: 'ML Foundations', questions: 10, timeLimit: 15, attempts: 156, avgScore: 68, status: 'Archived' },
];

export default function InstructorQuizPage() {
  const [filter, setFilter] = useState<'all' | 'Active' | 'Draft' | 'Archived'>('all');

  const filtered = filter === 'all' ? mockQuizzes : mockQuizzes.filter((q) => q.status === filter);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/instructor-dashboard" className="text-sm text-gray-500 hover:text-indigo-600 mb-1 block transition-colors">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Quiz Management</h1>
            <p className="text-sm text-gray-500 mt-1">{mockQuizzes.length} quizzes across your courses</p>
          </div>
          <button className="btn-primary flex items-center gap-2">
            <HiPlus className="w-4 h-4" />
            Create Quiz
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          {['all', 'Active', 'Draft', 'Archived'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f as any)}
              className={`px-4 py-2 text-sm rounded-lg transition-all font-medium ${
                filter === f ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>

        {/* Quiz List */}
        <div className="space-y-3">
          {filtered.map((quiz) => (
            <div key={quiz.id} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-semibold text-gray-900">{quiz.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      quiz.status === 'Active' ? 'bg-green-100 text-green-700' :
                      quiz.status === 'Draft' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>{quiz.status}</span>
                  </div>
                  <p className="text-sm text-gray-500">{quiz.course}</p>

                  <div className="flex items-center gap-6 mt-3 text-sm text-gray-600">
                    <span className="flex items-center gap-1"><HiClock className="w-4 h-4" /> {quiz.questions} questions</span>
                    <span className="flex items-center gap-1"><HiClock className="w-4 h-4" /> {quiz.timeLimit} min</span>
                    <span className="flex items-center gap-1"><HiChartBar className="w-4 h-4" /> {quiz.attempts} attempts</span>
                    <span className="flex items-center gap-1">
                      Avg: <span className="font-medium">{quiz.avgScore}%</span>
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                    <HiPencil className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                    <HiTrash className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                    <HiDotsVertical className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
