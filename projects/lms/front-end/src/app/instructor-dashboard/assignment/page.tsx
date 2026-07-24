'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiAcademicCap, HiPlus, HiClock, HiUser } from 'react-icons/hi';

export default function InstructorAssignmentPage() {
  const [assignments] = useState([
    { id: 1, title: 'Week 3 Assignment', course: 'React Fundamentals', submissions: 24, due: '2026-08-01', status: 'active' },
    { id: 2, title: 'Final Project', course: 'Advanced Python', submissions: 15, due: '2026-08-15', status: 'active' },
  ]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
        <button className="btn-primary flex items-center gap-2"><HiPlus className="w-4 h-4" /> New Assignment</button>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm min-w-[500px]">
          <thead className="bg-gray-50 border-b">
            <tr><th className="text-left px-6 py-3 font-medium text-gray-500">Assignment</th><th className="text-left px-6 py-3 font-medium text-gray-500">Course</th><th className="text-center px-6 py-3 font-medium text-gray-500">Submissions</th><th className="text-left px-6 py-3 font-medium text-gray-500">Due Date</th><th className="text-center px-6 py-3 font-medium text-gray-500">Status</th></tr>
          </thead>
          <tbody className="divide-y">
            {assignments.map(a => (
              <tr key={a.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-gray-900">{a.title}</td>
                <td className="px-6 py-4 text-gray-500">{a.course}</td>
                <td className="px-6 py-4 text-center text-gray-500">{a.submissions}</td>
                <td className="px-6 py-4 text-gray-500">{new Date(a.due).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-center"><span className="badge bg-green-100 text-green-700">Active</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
