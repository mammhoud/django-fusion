'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { HiArrowLeft, HiCamera, HiCheck, HiXCircle } from 'react-icons/hi';
import { useGetProfileQuery, useUpdateProfileMutation } from '@/store/api/endpoints/auth';

export default function StudentProfilePage() {
  const { data: profile, isLoading } = useGetProfileQuery(undefined, {
    skip: typeof window === 'undefined' || !localStorage.getItem('lms_token'),
  });
  const [updateProfile, { isLoading: isUpdating }] = useUpdateProfileMutation();

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    username: '',
    bio: '',
    phone: '',
    location: '',
    education: '',
  });

  useEffect(() => {
    if (profile) {
      const p = profile as any;
      setForm((prev) => ({
        ...prev,
        first_name: p.first_name || '',
        last_name: p.last_name || '',
        email: p.email || '',
        username: p.username || '',
        bio: p.bio || '',
        phone: p.phone || '',
        location: p.location || '',
        education: p.education || '',
      }));
    }
  }, [profile]);

  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await updateProfile({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        username: form.username,
        bio: form.bio,
      }).unwrap();
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err?.data?.message || 'Failed to update profile');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/student-dashboard" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-indigo-600 mb-2 transition-colors">
              <HiArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
          </div>
          {saved && (
            <div className="flex items-center gap-1 text-green-600 bg-green-50 px-3 py-1.5 rounded-lg text-sm font-medium">
              <HiCheck className="w-4 h-4" />
              Saved
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Avatar */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-6">
              <div className="relative group">
                <div className="w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center">
                  {profile?.avatar ? (
                    <img src={profile.avatar} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <span className="text-3xl font-bold text-indigo-500">
                      {(form.first_name?.[0] || form.username?.[0] || '?').toUpperCase()}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  className="absolute bottom-0 right-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center hover:bg-indigo-700 transition-colors shadow-lg"
                >
                  <HiCamera className="w-4 h-4" />
                </button>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{form.first_name || form.username || 'Student'}</h3>
                <p className="text-sm text-gray-500">{form.email}</p>
              </div>
            </div>
          </section>

          {/* Personal Info */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input type="text" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input type="text" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input type="text" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Education</label>
                <input type="text" value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="e.g., B.Sc. Computer Science" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
                  placeholder="Tell us about yourself..." />
              </div>
            </div>
          </section>

          {error && (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-xl text-sm">
              <HiXCircle className="w-5 h-5 flex-shrink-0" />
              {error}
            </div>
          )}

          <div className="flex justify-end gap-3">
            <Link href="/student-dashboard" className="btn-secondary">Cancel</Link>
            <button type="submit" disabled={isUpdating} className="btn-primary">
              {isUpdating ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
