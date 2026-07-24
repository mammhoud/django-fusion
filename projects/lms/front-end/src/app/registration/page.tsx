'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { HiAcademicCap, HiEye, HiEyeOff } from 'react-icons/hi';
import { useRegisterMutation } from '@/store/api/endpoints/auth';

export default function RegistrationPage() {
  const router = useRouter();
  const [form, setForm] = useState<{ username: string; email: string; first_name: string; last_name: string; password: string; password2: string; role: 'student' | 'instructor' }>({ username: '', email: '', first_name: '', last_name: '', password: '', password2: '', role: 'student' });
  const [showPassword, setShowPassword] = useState(false);
  const [register, { isLoading, error }] = useRegisterMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.password2) return;
    try {
      const result = await register(form).unwrap();
      localStorage.setItem('lms_token', result.token);
      router.push(form.role === 'instructor' ? '/instructor-dashboard' : '/student-dashboard');
    } catch { /* handled by RTK */ }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-10">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <HiAcademicCap className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-500 mt-2">Join our learning community</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-8 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {(error as any)?.data?.detail || 'Registration failed. Please try again.'}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
              <input type="text" value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})}
                className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
              <input type="text" value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})}
                className="input-field" required />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input type="text" value={form.username} onChange={(e) => setForm({...form, username: e.target.value})}
              className="input-field" required />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}
              className="input-field" required />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div className="relative">
              <input type={showPassword ? 'text' : 'password'} value={form.password}
                onChange={(e) => setForm({...form, password: e.target.value})}
                className="input-field pr-10" required minLength={8} />
              <button type="button" onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                {showPassword ? <HiEyeOff className="w-5 h-5" /> : <HiEye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
            <input type="password" value={form.password2} onChange={(e) => setForm({...form, password2: e.target.value})}
              className={`input-field ${form.password2 && form.password !== form.password2 ? 'border-red-500' : ''}`} required />
            {form.password2 && form.password !== form.password2 && (
              <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">I want to</label>
            <div className="grid grid-cols-2 gap-3">
              <button type="button" onClick={() => setForm({...form, role: 'student'})}
                className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                  form.role === 'student' ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}>Learn as Student</button>
              <button type="button" onClick={() => setForm({...form, role: 'instructor'})}
                className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                  form.role === 'instructor' ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}>Teach as Instructor</button>
            </div>
          </div>

          <button type="submit" disabled={isLoading || form.password !== form.password2}
            className="btn-primary w-full flex items-center justify-center gap-2">
            {isLoading ? (
              <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Creating Account...</>
            ) : 'Create Account'}
          </button>

          <p className="text-center text-sm text-gray-500">
            Already have an account? <Link href="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
