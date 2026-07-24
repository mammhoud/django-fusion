'use client';

import { useState } from 'react';
import Link from 'next/link';
import { HiSearch, HiMail, HiUserGroup, HiChartBar, HiCheck, HiX, HiDotsVertical } from 'react-icons/hi';

const mockStudents = [
  { id: 's1', name: 'Alex M.', email: 'alex@example.com', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50', course: 'Advanced React Development', enrolled: 'Jan 15, 2026', progress: 78, status: 'Active', lastActive: '2 hours ago' },
  { id: 's2', name: 'Jessica L.', email: 'jessica@example.com', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50', course: 'Full-Stack TypeScript', enrolled: 'Feb 1, 2026', progress: 45, status: 'Active', lastActive: '1 day ago' },
  { id: 's3', name: 'David R.', email: 'david@example.com', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50', course: 'Advanced React Development', enrolled: 'Dec 10, 2025', progress: 92, status: 'Active', lastActive: '3 days ago' },
  { id: 's4', name: 'Sarah K.', email: 'sarah@example.com', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50', course: 'Python for Data Science', enrolled: 'Mar 5, 2026', progress: 30, status: 'At Risk', lastActive: '2 weeks ago' },
  { id: 's5', name: 'Michael B.', email: 'michael@example.com', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50', course: 'Advanced React Development', enrolled: 'Nov 20, 2025', progress: 100, status: 'Completed', lastActive: '1 month ago' },
  { id: 's6', name: 'Emily W.', email: 'emily@example.com', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50', course: 'Full-Stack TypeScript', enrolled: 'Jan 28, 2026', progress: 60, status: 'Active', lastActive: '5 hours ago' },
];

export default function StudentManagePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'Active' | 'At Risk' | 'Completed'>('all');

  const filtered = mockStudents.filter((s) => {
    const matchesSearch = s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.course.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' ? true : s.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const avgProgress = Math.round(mockStudents.reduce((sum, s) => sum + s.progress, 0) / mockStudents.length);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/instructor-dashboard" className="text-sm text-gray-500 hover:text-indigo-600 mb-1 block transition-colors">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Student Management</h1>
          <p className="text-sm text-gray-500 mt-1">{mockStudents.length} students across your courses</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <HiUserGroup className="w-5 h-5 text-indigo-500 mb-1" />
            <div className="text-2xl font-bold text-gray-900">{mockStudents.length}</div>
            <div className="text-xs text-gray-500">Total Students</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <HiChartBar className="w-5 h-5 text-green-500 mb-1" />
            <div className="text-2xl font-bold text-gray-900">{avgProgress}%</div>
            <div className="text-xs text-gray-500">Avg Progress</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <HiCheck className="w-5 h-5 text-blue-500 mb-1" />
            <div className="text-2xl font-bold text-gray-900">{mockStudents.filter((s) => s.status === 'Completed').length}</div>
            <div className="text-xs text-gray-500">Completed</div>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-3 mb-6">
          <div className="relative flex-1">
            <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search students by name, email, or course..."
              className="w-full pl-9 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
            />
          </div>
          {['all', 'Active', 'At Risk', 'Completed'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s as any)}
              className={`px-4 py-2 text-sm rounded-lg transition-all font-medium whitespace-nowrap ${
                statusFilter === s ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {s === 'all' ? 'All' : s}
            </button>
          ))}
        </div>

        {/* Students Table */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Student</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Course</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Progress</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Last Active</th>
                  <th className="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <img src={student.avatar} alt="" className="w-8 h-8 rounded-full object-cover" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{student.name}</div>
                          <div className="text-xs text-gray-500">{student.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{student.course}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-gray-100 rounded-full h-2">
                          <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${student.progress}%` }} />
                        </div>
                        <span className="text-sm text-gray-600">{student.progress}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        student.status === 'Active' ? 'bg-green-100 text-green-700' :
                        student.status === 'At Risk' ? 'bg-red-100 text-red-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>{student.status}</span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{student.lastActive}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-1">
                        <button className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                          <HiMail className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                          <HiDotsVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
