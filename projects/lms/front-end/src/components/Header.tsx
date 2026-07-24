'use client';

import Link from 'next/link';
import { useState } from 'react';
import { HiMenu, HiX, HiUser, HiLogout } from 'react-icons/hi';
import { HiBeaker } from 'react-icons/hi2';
import { useGetProfileQuery, useLogoutMutation } from '@/store/api/endpoints/auth';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/about-us', label: 'About' },
  { href: '/services', label: 'Services' },
  { href: '/team', label: 'Team' },
  { href: '/courses', label: 'Courses' },
  { href: '/blog', label: 'Blog' },
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
    <header className="section-hero text-white sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo — CTC Research brand */}
          <Link href="/" className="flex items-center gap-2 text-white font-bold text-xl">
            <HiBeaker className="w-8 h-8" />
            <span>CTC Research</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href as any}
                className="text-white/80 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg font-medium transition-all duration-200"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Auth Section */}
          <div className="hidden md:flex items-center gap-4">
            {isLoading ? (
              <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : profile ? (
              <div className="flex items-center gap-3">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
                >
                  <HiUser className="w-5 h-5" />
                  <span className="font-medium">{profile.first_name || profile.username}</span>
                </Link>
                <button onClick={handleLogout} className="text-white/60 hover:text-red-300 transition-colors">
                  <HiLogout className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="text-white/80 hover:text-white font-medium transition-colors">Log In</Link>
                <Link href="/registration" className="btn-white px-4 py-2 rounded-lg font-medium text-sm">Sign Up</Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-white"
          >
            {mobileMenuOpen ? <HiX className="w-6 h-6" /> : <HiMenu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-white/10 bg-[rgb(var(--ctc-primary-dark))]">
          <div className="px-4 py-3 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href as any}
                className="block px-3 py-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <hr className="my-2 border-white/10" />
            {profile ? (
              <>
                <Link href="/dashboard"
                      className="block px-3 py-2 text-white font-medium"
                      onClick={() => setMobileMenuOpen(false)}>
                  Dashboard
                </Link>
                <button onClick={handleLogout} className="block w-full text-left px-3 py-2 text-red-300 font-medium">
                  Log Out
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="block px-3 py-2 text-white font-medium" onClick={() => setMobileMenuOpen(false)}>Log In</Link>
                <Link href="/registration" className="block px-3 py-2 text-white bg-white/20 rounded-lg text-center font-medium" onClick={() => setMobileMenuOpen(false)}>Sign Up</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
