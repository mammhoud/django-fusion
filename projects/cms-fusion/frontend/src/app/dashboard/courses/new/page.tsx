'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateCourseMutation } from '@/store/api/endpoints/courses';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import Link from 'next/link';
import { HiArrowLeft } from 'react-icons/hi';
import ErrorState from '@/components/ui/ErrorState';

export default function DashboardNewCoursePage() {
  const { data: profile } = useGetProfileQuery();
  const router = useRouter();
  const [createCourse, { isLoading }] = useCreateCourseMutation();

  if (profile?.role !== 'instructor') {
    return <ErrorState fullPage message="This page is only available for instructors." />;
  }
  const [form, setForm] = useState({ title: '', description: '', price: '', category: '' });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await createCourse({
        title: form.title,
        description: form.description,
        price: parseFloat(form.price) || 0,
        category: form.category,
      }).unwrap();
      router.push('/dashboard/courses');
    } catch (err: any) {
      setError(err?.data?.message || 'Failed to create course');
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link href="/dashboard/courses" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-[rgb(var(--ctc-primary))] mb-6 transition-colors">
        <HiArrowLeft className="w-4 h-4" /> Back to Courses
      </Link>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Create New Course</h1>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-4">{error}</div>}

      <form onSubmit={handleSubmit} className="card p-8 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Course Title</label>
          <input type="text" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input-field" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Price ($)</label>
            <input type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} className="input-field" min="0" step="0.01" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <input type="text" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="input-field" />
          </div>
        </div>
        <button type="submit" disabled={isLoading} className="btn-primary">
          {isLoading ? 'Creating...' : 'Create Course'}
        </button>
      </form>
    </div>
  );
}
