'use client';

import Link from 'next/link';
import { useState } from 'react';
import { HiMenu, HiX, HiUser, HiLogout, HiAcademicCap } from 'react-icons/hi';
import { useGetProfileQuery, useLogoutMutation } from '@/store/api/endpoints/auth';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/courses', label: 'Courses' },
  { href: '/instructors', label: 'Instructors' },
  { href: '/blog', label: 'Blog' },
  { href: '/events', label: 'Events' },
  { href: '/shop', label: 'Shop' },
  { href: '/contact', label: 'Contact' },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { data: profile, isLoading } = useGetProfileQuery(undefined, { skip: typeof window === 'undefined' || !localStorage.getItem('lms_token') });
  const [logout] = useLogoutMutation();

  const handleLogout = async () => {
    await logout();
    localStorage.removeItem('lms_token');
    window.location.href = '/';
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 text-[rgb(var(--fu-primary))] font-bold text-xl">
            <HiAcademicCap className="w-8 h-8" />
            <span>LMS</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">                {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href as any}
                className="text-gray-600 hover:text-[rgb(var(--fu-primary))] font-medium transition-colors duration-200"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Auth Section */}
          <div className="hidden md:flex items-center gap-4">
            {isLoading ? (
              <div className="w-8 h-8 border-2 border-[rgb(var(--fu-primary))] border-t-transparent rounded-full animate-spin" />
            ) : profile ? (
              <div className="flex items-center gap-3">
                <Link
                  href={profile.role === 'instructor' ? '/instructor-dashboard' : '/student-dashboard'}
                  className="flex items-center gap-2 text-gray-700 hover:text-[rgb(var(--fu-primary))]"
                >
                  <HiUser className="w-5 h-5" />
                  <span className="font-medium">{profile.first_name || profile.username}</span>
                </Link>
                <button onClick={handleLogout} className="text-gray-400 hover:text-red-500 transition-colors">
                  <HiLogout className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="text-gray-600 hover:text-[rgb(var(--fu-primary))] font-medium">Log In</Link>
                <Link href="/registration" className="btn-primary text-sm !px-4 !py-2">Sign Up</Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-gray-600 hover:text-[rgb(var(--fu-primary))]"
          >
            {mobileMenuOpen ? <HiX className="w-6 h-6" /> : <HiMenu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <div className="px-4 py-3 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href as any}
                className="block px-3 py-2 text-gray-600 hover:text-[rgb(var(--fu-primary))] hover:bg-[rgb(var(--fu-primary))]/5 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <hr className="my-2" />
            {profile ? (
              <>
                <Link href={profile.role === 'instructor' ? '/instructor-dashboard' : '/student-dashboard'}
                      className="block px-3 py-2 text-[rgb(var(--fu-primary))] font-medium"
                      onClick={() => setMobileMenuOpen(false)}>
                  Dashboard
                </Link>
                <button onClick={handleLogout} className="block w-full text-left px-3 py-2 text-red-600 font-medium">
                  Log Out
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="block px-3 py-2 text-[rgb(var(--fu-primary))] font-medium" onClick={() => setMobileMenuOpen(false)}>Log In</Link>
                <Link href="/registration" className="block px-3 py-2 text-white bg-[rgb(var(--fu-primary))] rounded-lg text-center font-medium" onClick={() => setMobileMenuOpen(false)}>Sign Up</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
