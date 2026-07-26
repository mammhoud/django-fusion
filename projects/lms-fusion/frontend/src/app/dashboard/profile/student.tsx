'use client';

import { useState } from 'react';
import { useGetProfileQuery, useUpdateProfileMutation } from '@/store/api/endpoints/auth';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

export default function StudentProfile() {
  const { data: profile, isLoading: profileLoading, isError } = useGetProfileQuery();
  const [update, { isLoading }] = useUpdateProfileMutation();
  const [form, setForm] = useState({ first_name: profile?.first_name || '', last_name: profile?.last_name || '', bio: profile?.bio || '' });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try { await update(form).unwrap(); setSaved(true); setTimeout(() => setSaved(false), 3000); } catch (err: any) { setError(err?.data?.message || 'Failed to update profile'); }
  };

  if (profileLoading) return <div className="max-w-2xl mx-auto px-4 py-10"><LoadingSkeleton variant="profile" /></div>;
  if (isError) return <ErrorState fullPage message="Failed to load profile." />;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile Settings</h1>
      {saved && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm mb-4">Profile saved successfully</div>}
      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="card p-8 space-y-5">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-20 h-20 avatar-sm flex items-center justify-center text-white text-2xl font-bold">{profile?.first_name?.[0]}{profile?.last_name?.[0]}</div>
          <div><h2 className="font-semibold text-gray-900 text-lg">{profile?.first_name} {profile?.last_name}</h2><p className="text-sm text-gray-500">{profile?.email}</p></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium text-gray-700 mb-1">First Name</label><input type="text" value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})} className="input-field" /></div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label><input type="text" value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})} className="input-field" /></div>
        </div>
        <div><label className="block text-sm font-medium text-gray-700 mb-1">Bio</label><textarea rows={4} value={form.bio} onChange={(e) => setForm({...form, bio: e.target.value})} className="input-field" /></div>
        <div className="flex items-center gap-3">
          <button type="submit" disabled={isLoading} className="btn-primary">{isLoading ? 'Saving...' : 'Save Changes'}</button>
          {saved && <span className="text-sm text-green-600 font-medium">✓ Saved</span>}
        </div>
      </form>
    </div>
  );
}
