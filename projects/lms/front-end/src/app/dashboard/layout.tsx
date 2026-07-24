'use client';

import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HiHome, HiBookOpen, HiStar, HiChartBar, HiAcademicCap, HiUserGroup } from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

const instructorLinks = [
  { href: '/dashboard', icon: HiHome, label: 'Overview' },
  { href: '/dashboard/courses', icon: HiBookOpen, label: 'Courses' },
  { href: '/dashboard/quiz', icon: HiChartBar, label: 'Quizzes' },
  { href: '/dashboard/review', icon: HiStar, label: 'Reviews' },
  { href: '/dashboard/enrolled-courses', icon: HiUserGroup, label: 'Students' },
];

const studentLinks = [
  { href: '/dashboard', icon: HiHome, label: 'Overview' },
  { href: '/dashboard/enrolled-courses', icon: HiBookOpen, label: 'My Courses' },
  { href: '/dashboard/quiz', icon: HiChartBar, label: 'Quizzes' },
  { href: '/dashboard/profile', icon: HiAcademicCap, label: 'Profile' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data: profile, isLoading } = useGetProfileQuery();
  const pathname = usePathname();

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  const links = profile?.role === 'instructor' ? instructorLinks : studentLinks;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex gap-8">
        {/* Sidebar */}
        <aside className="hidden lg:block w-56 flex-shrink-0 py-10">
          <nav className="space-y-1 sticky top-24">
            {links.map((link) => {
              const isActive = pathname === link.href || (link.href !== '/dashboard' && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href as any}
                  className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors
                    ${isActive
                      ? 'bg-[rgb(var(--ctc-primary))]/10 text-[rgb(var(--ctc-primary))]'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                >
                  <link.icon className="w-5 h-5" />
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>
    </div>
  );
}
