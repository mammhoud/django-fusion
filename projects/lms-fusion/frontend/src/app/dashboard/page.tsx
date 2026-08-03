'use client';

import { useEffect, useMemo } from 'react';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetInstructorDashboardQuery } from '@/store/api/endpoints/instructors';
import { useGetDashboardQuery, useGetStudentEnrollmentsQuery } from '@/store/api/endpoints/students';
import { useGetDashboardContentQuery } from '@/store/api/endpoints/dashboard';
import { useGetWithdrawalsQuery } from '@/store/api/endpoints/withdrawals';
import { fusionDecoder } from '@/lib/fusion-decoder';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  HiAcademicCap, HiUserGroup, HiStar, HiChartBar, HiBookOpen, HiCurrencyDollar,
  HiClock, HiCheckCircle, HiTrendingUp, HiLightBulb, HiSpeakerphone, HiLink, HiInformationCircle,
} from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import StatSkeleton from '@/components/ui/StatSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';
import RevenueChart from '@/components/dashboard/RevenueChart';
import EnrollmentTrendChart from '@/components/dashboard/EnrollmentTrendChart';
import CompletionRateChart from '@/components/dashboard/CompletionRateChart';
import Carousel from '@/components/ui/Carousel';
import type { CarouselSlide } from '@/components/ui/Carousel';
import Accordion from '@/components/ui/Accordion';
import type { AccordionItem } from '@/components/ui/Accordion';
import Tabs from '@/components/ui/Tabs';
import type { Tab } from '@/components/ui/Tabs';
import ScrollReveal from '@/components/ui/ScrollReveal';
import { useToast } from '@/components/ui/Toast';

export default function DashboardPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();

  if (profileLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!profile) {
    return (
      <ErrorState
        message="Please sign in to access your dashboard."
        fullPage
      />
    );
  }

  if (profile.role === 'instructor') {
    return <InstructorDashboard profile={profile} />;
  }

  if (profile.role === 'admin') {
    return <AdminDashboard profile={profile} />;
  }

  return <StudentDashboard profile={profile} />;
}

// ═══════════════════════════════════════════════════════════════════
// Admin Dashboard
// ═══════════════════════════════════════════════════════════════════

function AdminDashboard({ profile }: { profile: { id: number; first_name?: string; username: string } }) {
  const { data: withdrawals, isLoading } = useGetWithdrawalsQuery({ status: 'pending', page: 1 });
  const toast = useToast();

  useEffect(() => {
    if (isLoading) return;
    const timer = setTimeout(() => {
      toast.info('Admin Dashboard', 'Welcome back, administrator!');
    }, 800);
    return () => clearTimeout(timer);
  }, [toast, isLoading]);

  return (
    <ScrollReveal animation="fadeUp" duration={0.5}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome, {profile.first_name || profile.username}</p>
        </div>

        <ScrollReveal animation="fadeUp" delay={0.1} duration={0.4}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
            <Link href="/dashboard/admin/withdrawals"
              className="card p-5 flex items-center gap-4 hover:shadow-md transition-shadow group">
              <div className="bg-[rgb(var(--fu-primary))]/10 w-12 h-12 rounded-lg flex items-center justify-center">
                <HiCurrencyDollar className="w-6 h-6 text-[rgb(var(--fu-primary))]" />
              </div>
              <div>
                <div className="font-semibold text-gray-900 group-hover:text-[rgb(var(--fu-primary))]">
                  Pending Withdrawals
                </div>
                <div className="text-sm text-gray-500">
                  {isLoading ? '...' : withdrawals?.count ?? 0} pending
                </div>
              </div>
            </Link>
          </div>
        </ScrollReveal>
      </div>
    </ScrollReveal>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Instructor Dashboard
// ═══════════════════════════════════════════════════════════════════

function InstructorDashboard({ profile }: { profile: { id: number; first_name?: string; username: string } }) {
  const { data: dashboard, isLoading } = useGetInstructorDashboardQuery(profile.id, { skip: !profile.id });
  const toast = useToast();

  // Must be declared before any early return (React hooks rule)
  useEffect(() => {
    if (isLoading) return;
    const timer = setTimeout(() => {
      toast.success(
        `Welcome back, ${profile.first_name || profile.username}!`,
        'Here\'s your instructor dashboard overview.',
        4000,
      );
    }, 800);
    return () => clearTimeout(timer);
  }, [toast, profile, isLoading]);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="profile" className="mb-8" />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const stats = [
    { icon: HiBookOpen, label: 'Courses', value: dashboard?.total_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
    { icon: HiUserGroup, label: 'Students', value: dashboard?.total_students ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
    { icon: HiCurrencyDollar, label: 'Revenue', value: dashboard ? `$${dashboard.total_revenue.toLocaleString()}` : '$0', color: 'text-[rgb(var(--fu-accent))]', bg: 'bg-[rgb(var(--fu-accent))]/10' },
    { icon: HiTrendingUp, label: 'Completion', value: dashboard ? `${dashboard.completion_rate}%` : '0%', color: 'text-emerald-600', bg: 'bg-emerald-100' },
  ];

  // Build carousel slides from stats
  const statSlides: CarouselSlide[] = stats.map((stat) => ({
    id: stat.label,
    content: (
      <div className="card p-5 mx-1">
        <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}>
          <stat.icon className={`w-6 h-6 ${stat.color}`} />
        </div>
        <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
        <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
      </div>
    ),
  }));

  const quickLinks = [
    { href: '/dashboard/courses', icon: HiBookOpen, label: 'My Courses' },
    { href: '/dashboard/quiz', icon: HiChartBar, label: 'Quizzes' },
    { href: '/dashboard/review', icon: HiStar, label: 'Reviews' },
    { href: '/dashboard/announcement', icon: HiChartBar, label: 'Announcements' },
    { href: '/dashboard/enrolled-courses', icon: HiAcademicCap, label: 'Enrollments' },
    { href: '/dashboard/history', icon: HiChartBar, label: 'History' },
  ] as const;

  return (
    <ScrollReveal animation="fadeUp" duration={0.5}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* CMS-backed welcome + tips */}
        <CmsDashboardContentBlocks profileName={profile.first_name || profile.username} />

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Instructor Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome back, {profile.first_name || profile.username}</p>
        </div>

        {/* Stats — Carousel on mobile, grid on desktop */}
        <div className="mb-10">
          {/* Mobile/Tablet carousel */}
          <div className="block sm:hidden">
            <Carousel
              slides={statSlides}
              slidesPerView={1.5}
              showArrows={false}
              showDots
              autoplay={4000}
              loop={false}
              animation="slide"
              gap={8}
              className="pb-2"
            />
          </div>
          {/* Desktop grid */}
          <div className="hidden sm:grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats.map((stat, idx) => (
              <ScrollReveal key={stat.label} animation="fadeUp" delay={idx * 0.08} duration={0.4}>
                <div className="card p-5">
                  <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}>
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                  <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>

        {/* Quick Links */}
        <ScrollReveal animation="fadeUp" delay={0.15} duration={0.4}>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-10">
            {quickLinks.map((link) => (
              <Link key={link.href} href={link.href}
                className="card p-4 flex items-center gap-3 hover:shadow-md transition-shadow group">
                <link.icon className="w-6 h-6 text-[rgb(var(--fu-primary))] group-hover:text-[rgb(var(--fu-primary-dark))]" />
                <span className="font-medium text-gray-700 group-hover:text-gray-900">{link.label}</span>
              </Link>
            ))}
          </div>
        </ScrollReveal>

        {/* Getting Started CTA */}
        {dashboard?.total_courses === 0 && (
          <ScrollReveal animation="fadeUp" delay={0.2} duration={0.4}>
            <div className="bg-[rgb(var(--fu-primary))]/5 border border-[rgb(var(--fu-primary))]/20 rounded-xl p-6 mb-6 text-center">
              <HiBookOpen className="w-12 h-12 text-[rgb(var(--fu-primary))]/40 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Getting Started</h3>
              <p className="text-sm text-gray-600 mb-3">Create your first course to start teaching students.</p>
              <Link href="/dashboard/courses/new" className="btn-primary inline-flex text-sm">Create Course</Link>
            </div>
          </ScrollReveal>
        )}

        {/* Analytics Charts */}
        {(dashboard?.monthly_earnings?.length || dashboard?.enrollment_trends?.length) && (
          <ScrollReveal animation="fadeUp" delay={0.2} duration={0.4}>
            <div className="mb-10">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <HiTrendingUp className="w-5 h-5 text-[rgb(var(--fu-primary))]" />
                Analytics
              </h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Revenue Chart */}
                {dashboard?.monthly_earnings && dashboard.monthly_earnings.length > 0 && (
                  <div className="card p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900 text-sm">Monthly Revenue</h3>
                      <span className="text-xs text-gray-400">Last 12 months</span>
                    </div>
                    <RevenueChart data={dashboard.monthly_earnings} />
                  </div>
                )}
                {/* Enrollment Trends */}
                {dashboard?.enrollment_trends && dashboard.enrollment_trends.length > 0 && (
                  <div className="card p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900 text-sm">Enrollment Trends</h3>
                      <span className="text-xs text-gray-400">Last 12 months</span>
                    </div>
                    <EnrollmentTrendChart data={dashboard.enrollment_trends} />
                  </div>
                )}
              </div>
              {/* Completion Rate */}
              {dashboard && dashboard.total_enrollments > 0 && (
                <div className="card p-5 max-w-md mx-auto lg:mx-0">
                  <h3 className="font-semibold text-gray-900 text-sm mb-2 text-center">
                    Course Completion Rate
                  </h3>
                  <CompletionRateChart
                    completionRate={dashboard.completion_rate}
                    completedEnrollments={dashboard.completed_enrollments}
                    activeEnrollments={dashboard.active_enrollments}
                    totalEnrollments={dashboard.total_enrollments}
                  />
                </div>
              )}
            </div>
          </ScrollReveal>
        )}

        {/* Popular Courses Table */}
        {dashboard?.popular_courses && dashboard.popular_courses.length > 0 && (
          <ScrollReveal animation="fadeUp" delay={0.25} duration={0.4}>
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Popular Courses</h2>
              <div className="card overflow-x-auto">
                <table className="w-full text-sm min-w-[400px]">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="text-left px-6 py-3 font-medium text-gray-500">Course</th>
                      <th className="text-right px-6 py-3 font-medium text-gray-500">Students</th>
                      <th className="text-right px-6 py-3 font-medium text-gray-500">Revenue</th>
                      <th className="text-right px-6 py-3 font-medium text-gray-500">Completed</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {dashboard.popular_courses.map((course: any) => (
                      <tr key={course.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{course.title}</td>
                        <td className="px-6 py-4 text-right text-gray-500">{course.student_count}</td>
                        <td className="px-6 py-4 text-right font-medium text-gray-900">${course.course_revenue?.toLocaleString() || '0'}</td>
                        <td className="px-6 py-4 text-right">
                          <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded-full">
                            {course.course_completed || 0}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </ScrollReveal>
        )}
      </div>
    </ScrollReveal>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Student Dashboard
// ═══════════════════════════════════════════════════════════════════

function StudentDashboard({ profile }: { profile: { id: number; first_name?: string; username: string } }) {
  const { data: dashboard, isLoading: dashLoading } = useGetDashboardQuery(profile.id, { skip: !profile.id });
  const { data: enrollments, isLoading: enrollLoading } = useGetStudentEnrollmentsQuery(profile.id, { skip: !profile.id });
  const toast = useToast();

  useEffect(() => {
    const timer = setTimeout(() => {
      toast.success(
        `Welcome back, ${profile.first_name || profile.username}!`,
        'Pick up where you left off.',
        4000,
      );
    }, 800);
    return () => clearTimeout(timer);
  }, [toast, profile]);

  const statsLoading = dashLoading || enrollLoading;
  const statsCards = [
    { icon: HiAcademicCap, label: 'Enrolled Courses', value: dashboard?.enrolled_courses ?? 0, color: 'text-blue-600', bg: 'bg-blue-100' },
    { icon: HiCheckCircle, label: 'Completed', value: dashboard?.completed_courses ?? 0, color: 'text-green-600', bg: 'bg-green-100' },
    { icon: HiClock, label: 'Total Hours', value: dashboard?.total_hours ?? 0, color: 'text-[rgb(var(--fu-accent))]', bg: 'bg-[rgb(var(--fu-accent))]/10' },
    { icon: HiChartBar, label: 'Progress', value: enrollments?.length ? Math.round(enrollments.reduce((sum, e) => sum + e.progress, 0) / enrollments.length) : 0, suffix: '%', color: 'text-[rgb(var(--fu-primary))]', bg: 'bg-[rgb(var(--fu-primary))]/10' },
  ];

  // Build carousel slides from stats
  const statSlides: CarouselSlide[] = statsCards.map((stat) => ({
    id: stat.label,
    content: (
      <div className="card p-5 mx-1">
        <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}>
          <stat.icon className={`w-6 h-6 ${stat.color}`} />
        </div>
        <div className="text-2xl font-bold text-gray-900">
          {statsLoading ? <StatSkeleton /> : stat.value}{!statsLoading && (stat.suffix || '')}
        </div>
        <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
      </div>
    ),
  }));

  return (
    <ScrollReveal animation="fadeUp" duration={0.5}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* CMS-backed welcome + tips */}
        <CmsDashboardContentBlocks profileName={profile.first_name || profile.username} />

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {profile.first_name || profile.username}!
          </h1>
          <p className="text-gray-500 mt-1">Here&apos;s your learning progress</p>
        </div>

        {/* Stats Grid — Carousel on mobile, grid on desktop */}
        <div className="mb-10">
          {/* Mobile/Tablet carousel */}
          <div className="block sm:hidden">
            <Carousel
              slides={statSlides}
              slidesPerView={1.5}
              showArrows={false}
              showDots
              autoplay={4000}
              loop={false}
              animation="slide"
              gap={8}
              className="pb-2"
            />
          </div>
          {/* Desktop grid */}
          <div className="hidden sm:grid grid-cols-2 md:grid-cols-4 gap-4">
            {statsCards.map((stat, idx) => (
              <ScrollReveal key={stat.label} animation="fadeUp" delay={idx * 0.08} duration={0.4}>
                <div className="card p-5">
                  <div className={`${stat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-3`}>
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {statsLoading ? <StatSkeleton /> : stat.value}{!statsLoading && (stat.suffix || '')}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>

        {/* Enrolled Courses */}
        <ScrollReveal animation="fadeUp" delay={0.15} duration={0.4}>
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">My Courses</h2>
              <Link href="/courses" className="text-[rgb(var(--fu-primary))] text-sm font-medium hover:text-[rgb(var(--fu-primary-dark))]">
                Browse More Courses
              </Link>
            </div>

            {enrollLoading ? (
              <LoadingSkeleton variant="list" count={3} />
            ) : (
              <div className="space-y-4">
                {enrollments?.map((enrollment, idx) => (
                  <motion.div
                    key={enrollment.id}
                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.05 }}
                    className="card p-5 flex items-center gap-5"
                  >
                    <div className="w-24 h-24 card-gradient rounded-lg flex items-center justify-center flex-shrink-0">
                      <HiAcademicCap className="w-8 h-8 text-white/60" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <Link href={`/course-details/${enrollment.course}`}
                        className="font-semibold text-gray-900 hover:text-[rgb(var(--fu-primary))] transition-colors line-clamp-1">
                        {enrollment.course_title}
                      </Link>
                      <p className="text-sm text-gray-500 mt-1">
                        Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </p>
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-500">Progress</span>
                          <span className="font-medium text-gray-700">{enrollment.progress}%</span>
                        </div>
                        <div className="progress-track">
                          <div className="progress-fill"
                            style={{ width: `${enrollment.progress}%` }} />
                        </div>
                      </div>
                    </div>
                    {enrollment.is_completed && (
                      <HiCheckCircle className="w-8 h-8 text-green-500 flex-shrink-0" />
                    )}
                  </motion.div>
                ))}
                {(!enrollments || enrollments.length === 0) && (
                  <EmptyState icon="courses" title="No courses yet" description="Start your learning journey by enrolling in a course." actionLabel="Browse Courses" actionHref="/courses" />
                )}
              </div>
            )}
          </div>
        </ScrollReveal>
      </div>
    </ScrollReveal>
  );
}

// ═══════════════════════════════════════════════════════════════════
// CMS Dashboard Content Blocks
// ═══════════════════════════════════════════════════════════════════

/** Renders CMS-managed dashboard content blocks (welcome, tips, quick links).
 *
 * Uses:
 * - Accordion for expandable tips
 * - Tabs for switching between quick links and announcements
 * - Prominent welcome card at top
 */
function CmsDashboardContentBlocks({ profileName }: { profileName: string }) {
  const { data: contentData, isLoading } = useGetDashboardContentQuery();

  const { welcome, tips, quickLinks, announcements } = useMemo(() => {
    if (!contentData?.encoded) return { welcome: null, tips: [], quickLinks: null, announcements: [] };
    try {
      const page = fusionDecoder.decodeAs<{ blocks: any[] }>(contentData.encoded);
      const blocks = page?.blocks ?? [];
      return {
        welcome: blocks.find((b) => b.type === 'dashboard_welcome') || null,
        tips: blocks.filter((b) => b.type === 'dashboard_tip'),
        quickLinks: blocks.find((b) => b.type === 'dashboard_quick_links') || null,
        announcements: blocks.filter((b) => b.type === 'dashboard_announcement'),
      };
    } catch {
      return { welcome: null, tips: [], quickLinks: null, announcements: [] };
    }
  }, [contentData]);

  const hasContent = welcome || tips.length > 0 || quickLinks || announcements.length > 0;
  if (isLoading || !hasContent) return null;

  // ── Build accordion items from tips ──
  const tipAccordionItems: AccordionItem[] = tips.map((tip, idx) => ({
    id: `tip-${idx}`,
    title: tip.heading || 'Tip',
    content: <p className="text-sm text-gray-600">{tip.content}</p>,
    icon: <HiLightBulb className="w-4 h-4 text-amber-500" />,
  }));

  // ── Build quick links content ──
  const hasQuickLinks = quickLinks && quickLinks.links?.length > 0;
  const quickLinksContent = hasQuickLinks ? (
    <div>
      {quickLinks.heading && (
        <h3 className="text-sm font-semibold text-gray-600 mb-3 uppercase tracking-wider">
          {quickLinks.heading}
        </h3>
      )}
      <div className="flex flex-wrap gap-2">
        {(quickLinks.links || []).map((link: any, li: number) => (
          <Link
            key={li}
            href={link.href}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-[rgb(var(--fu-primary))]/30 hover:text-[rgb(var(--fu-primary))] transition-colors"
          >
            <HiLink className="w-3.5 h-3.5" />
            {link.label}
          </Link>
        ))}
      </div>
    </div>
  ) : null;

  // ── Build announcements content ──
  const hasAnnouncements = announcements.length > 0;
  const announcementContent = hasAnnouncements ? (
    announcements.length > 1 ? (
      <Accordion
        items={announcements.map((ann, idx) => ({
          id: `ann-${idx}`,
          title: ann.heading || 'Announcement',
          content: (
            <div>
              <p className="text-sm text-gray-600">{ann.content}</p>
              {ann.link && (
                <a
                  href={ann.link}
                  className="inline-flex items-center gap-1 mt-2 text-sm font-medium text-[rgb(var(--fu-primary))] hover:underline"
                >
                  {ann.link_label || 'Learn More'}
                </a>
              )}
            </div>
          ),
          icon: (
            <HiInformationCircle
              className={`w-4 h-4 ${
                ann.variant === 'warning'
                  ? 'text-red-500'
                  : ann.variant === 'success'
                  ? 'text-green-500'
                  : 'text-blue-500'
              }`}
            />
          ),
        }))}
        multiple
        size="sm"
        compact
      />
    ) : (
      <div
        className={`flex items-start gap-3 rounded-xl p-4 ${
          announcements[0].variant === 'warning'
            ? 'bg-red-50 border border-red-200'
            : announcements[0].variant === 'success'
            ? 'bg-green-50 border border-green-200'
            : 'bg-blue-50 border border-blue-200'
        }`}
      >
        <HiInformationCircle
          className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
            announcements[0].variant === 'warning'
              ? 'text-red-500'
              : announcements[0].variant === 'success'
              ? 'text-green-500'
              : 'text-blue-500'
          }`}
        />
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-900">
            {announcements[0].heading || 'Announcement'}
          </p>
          <p className="text-sm text-gray-600 mt-0.5">{announcements[0].content}</p>
          {announcements[0].link && (
            <a
              href={announcements[0].link}
              className="inline-flex items-center gap-1 mt-2 text-sm font-medium text-[rgb(var(--fu-primary))] hover:underline"
            >
              {announcements[0].link_label || 'Learn More'}
            </a>
          )}
        </div>
      </div>
    )
  ) : null;

  // ── Build tabs for quick links + announcements ──
  const shouldUseTabs = hasQuickLinks && hasAnnouncements;
  const dashboardTabs: Tab[] = [];
  if (hasQuickLinks) {
    dashboardTabs.push({
      id: 'quick-links',
      label: 'Quick Links',
      content: quickLinksContent,
      icon: <HiLink className="w-4 h-4" />,
    });
  }
  if (hasAnnouncements) {
    dashboardTabs.push({
      id: 'announcements',
      label: `Announcements${announcements.length > 0 ? ` (${announcements.length})` : ''}`,
      content: announcementContent,
      icon: <HiInformationCircle className="w-4 h-4" />,
    });
  }

  return (
    <div className="space-y-4 mb-6">
      {/* Welcome — always prominent */}
      {welcome && (
        <ScrollReveal animation="fadeUp" duration={0.4}>
          <div className="bg-gradient-to-r from-[rgb(var(--fu-primary))]/5 to-transparent rounded-xl p-5">
            <h2 className="text-xl font-bold text-gray-900">
              {welcome.heading?.replace('{name}', profileName) || `Welcome back, ${profileName}!`}
            </h2>
            {welcome.intro && <p className="text-sm text-gray-500 mt-1">{welcome.intro}</p>}
          </div>
        </ScrollReveal>
      )}

      {/* Tips — expandable accordion */}
      {tipAccordionItems.length > 0 && (
        <ScrollReveal animation="fadeUp" delay={0.1} duration={0.4}>
          <Accordion items={tipAccordionItems} multiple size="sm" compact />
        </ScrollReveal>
      )}

      {/* Quick Links + Announcements — tabs or standalone */}
      {shouldUseTabs ? (
        <ScrollReveal animation="fadeUp" delay={0.15} duration={0.4}>
          <Tabs tabs={dashboardTabs} variant="pills" size="sm" animation="fade" />
        </ScrollReveal>
      ) : (
        <>
          {!hasQuickLinks && hasAnnouncements && (
            <ScrollReveal animation="fadeUp" delay={0.15} duration={0.4}>
              {announcementContent}
            </ScrollReveal>
          )}
          {!hasAnnouncements && hasQuickLinks && (
            <ScrollReveal animation="fadeUp" delay={0.15} duration={0.4}>
              {quickLinksContent}
            </ScrollReveal>
          )}
        </>
      )}
    </div>
  );
}
