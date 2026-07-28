'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import type { Route } from 'next';
import { motion } from 'framer-motion';
import { HiAcademicCap, HiUserGroup, HiBookOpen, HiStar, HiChevronRight } from 'react-icons/hi';
import { useGetFeaturedCoursesQuery, useGetCoursesQuery } from '@/store/api/endpoints/courses';
import { useGetInstructorsQuery } from '@/store/api/endpoints/instructors';
import { FusionPage } from '@/components/FusionPage';
import EmptyState from '@/components/ui/EmptyState';
import Carousel from '@/components/ui/Carousel';
import type { CarouselSlide } from '@/components/ui/Carousel';
import ScrollReveal from '@/components/ui/ScrollReveal';
import { useToast } from '@/components/ui/Toast';
import type { CmsPage } from '@/store/api/endpoints/pages';

export default function HomePage() {
  return (
    <FusionPage slug="home">
      {(page, _fallback) => <HomePageContent page={page} />}
    </FusionPage>
  );
}

function HomePageContent({ page }: { page: CmsPage | undefined }) {
  const { data: featuredCourses, isLoading: coursesLoading } = useGetFeaturedCoursesQuery();
  const { data: coursesData } = useGetCoursesQuery({ page: 1 });
  const { data: instructorsData } = useGetInstructorsQuery({ page: 1 });
  const toast = useToast();

  useEffect(() => {
    const timer = setTimeout(() => {
      toast.success(
        'Welcome to LMS',
        'Discover expert-led courses and start learning today.',
        4000,
      );
    }, 1500);
    return () => clearTimeout(timer);
  }, [toast]);

  const pageStats = page?.blocks.find((block) => block.type === 'stats')?.items || [];
  const hero = page?.blocks.find((block) => block.type === 'hero');
  const featuredHeader = page?.blocks.find((block) => block.key === 'featured_courses');
  const cta = page?.blocks.find((block) => block.type === 'cta');

  const stats = [
    { icon: HiBookOpen, label: 'Courses', value: coursesData?.count ?? 0 },
    { icon: HiUserGroup, label: 'Instructors', value: instructorsData?.count ?? 0 },
    { icon: HiAcademicCap, label: pageStats[0]?.label || 'Students', value: pageStats[0]?.value || '5K+' },
    { icon: HiStar, label: pageStats[1]?.label || 'Reviews', value: pageStats[1]?.value || '12K+' },
  ];

  // Build carousel slides from featured courses
  const courseSlides: CarouselSlide[] = (featuredCourses ?? []).slice(0, 8).map((course) => ({
    id: course.id,
    content: (
      <Link href={`/course-details/${course.id}`} className="card block overflow-hidden group h-full">
        <div className="bg-gradient-to-br card-gradient h-36 flex items-center justify-center">
          <HiBookOpen className="w-10 h-10 text-white/60" />
        </div>
        <div className="p-4">
          <span className="badge-primary mb-2 inline-block text-xs">
            {course.category_name || 'General'}
          </span>
          <h3 className="font-semibold text-gray-900 text-sm mb-1 group-hover:text-[rgb(var(--ctc-primary))] transition-colors line-clamp-1">
            {course.title}
          </h3>
          <p className="text-xs text-gray-500 mb-2 line-clamp-2">{course.short_description}</p>
          <div className="flex items-center justify-between mt-auto">
            <span className="text-xs text-gray-500">{course.instructor_name}</span>
            <span className="font-bold text-sm text-[rgb(var(--ctc-primary))]">
              {course.discounted_price ? (
                <>
                  <span className="line-through text-gray-400 text-xs mr-1">${course.price}</span>
                  ${course.discounted_price}
                </>
              ) : (
                `$${course.price}`
              )}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
            <span>{course.students_count} students</span>
            <span>·</span>
            <span className="flex items-center gap-1">
              <HiStar className="w-3 h-3 text-yellow-400" />
              {course.rating}
            </span>
          </div>
        </div>
      </Link>
    ),
  }));

  return (
    <div>
      {/* ── Hero Section ── */}
      <ScrollReveal animation="fadeUp" duration={0.7}>
        <section className="section-hero text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-3xl mx-auto"
            >
              <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                {hero?.heading || 'Learn Without Limits'}
              </h1>
              <p className="text-lg md:text-xl text-white/70 mb-10 leading-relaxed">
                {hero?.intro || 'Master new skills with expert-led courses, interactive content, and a community of learners.'}
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href={(hero?.ctas?.[0]?.href || '/courses') as Route} className="bg-white text-[rgb(var(--ctc-primary-dark))] px-8 py-3 rounded-lg font-semibold hover:bg-[rgb(var(--ctc-primary))]/5 transition-colors">
                  {hero?.ctas?.[0]?.label || 'Explore Courses'}
                </Link>
                <Link href={(hero?.ctas?.[1]?.href || '/registration') as Route} className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
                  {hero?.ctas?.[1]?.label || 'Get Started Free'}
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </ScrollReveal>

      {/* ── Stats Section ── */}
      <ScrollReveal animation="fadeUp" duration={0.6}>
        <section className="bg-white border-b border-gray-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, idx) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  className="text-center"
                >
                  <stat.icon className="w-8 h-8 text-[rgb(var(--ctc-primary))] mx-auto mb-3" />
                  <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                  <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ── Featured Courses Carousel ── */}
      <ScrollReveal animation="fadeUp" duration={0.6} threshold={0.05}>
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">{featuredHeader?.heading || 'Featured Courses'}</h2>
                <p className="text-gray-500 mt-2">{featuredHeader?.intro || 'Most popular courses picked for you'}</p>
              </div>
              <Link href="/courses" className="text-[rgb(var(--ctc-primary))] font-medium flex items-center gap-1 hover:text-[rgb(var(--ctc-primary-dark))] whitespace-nowrap">
                View All <HiChevronRight className="w-4 h-4" />
              </Link>
            </div>

            {coursesLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="card animate-pulse">
                    <div className="bg-gray-200 h-36 rounded-t-lg" />
                    <div className="p-5 space-y-3">
                      <div className="h-4 bg-gray-200 rounded w-1/3" />
                      <div className="h-5 bg-gray-200 rounded w-3/4" />
                      <div className="h-4 bg-gray-200 rounded w-full" />
                    </div>
                  </div>
                ))}
              </div>
            ) : courseSlides.length > 0 ? (
              <Carousel
                slides={courseSlides}
                slidesPerView={{ xs: 1, sm: 2, md: 2, lg: 3, xl: 4 }}
                showArrows={courseSlides.length > 3}
                showDots={false}
                autoplay={5000}
                loop
                animation="slide"
                gap={20}
                className="pb-4"
              />
            ) : (
              <EmptyState icon="courses" title="No featured courses yet" description="Check back soon for new courses." actionLabel="Browse All Courses" actionHref="/courses" />
            )}
          </div>
        </section>
      </ScrollReveal>

      {/* ── CTA Section ── */}
      <ScrollReveal animation="zoomIn" duration={0.7}>
        <section className="py-20 bg-gradient-to-r from-[rgb(var(--ctc-primary))] to-[rgb(var(--ctc-primary-dark))]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              {cta?.heading || 'Start Learning Today'}
            </h2>
            <p className="text-lg text-white/70 mb-8">
              {cta?.intro || 'Join thousands of students and start your learning journey today.'}
            </p>
            <Link
              href={(cta?.ctas?.[0]?.href || '/registration') as Route}
              className="inline-block bg-white text-[rgb(var(--ctc-primary-dark))] px-10 py-4 rounded-lg font-bold text-lg
                         hover:bg-[rgb(var(--ctc-primary))]/5 transition-colors shadow-lg"
            >
              {cta?.ctas?.[0]?.label || 'Create Free Account'}
            </Link>
          </div>
        </section>
      </ScrollReveal>

      {/* ── Instructors Preview ── */}
      <ScrollReveal animation="fadeUp" duration={0.6} threshold={0.05}>
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-10">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Expert Instructors</h2>
                <p className="text-gray-500 mt-2">Learn from industry professionals</p>
              </div>
              <Link href="/instructors" className="text-[rgb(var(--ctc-primary))] font-medium flex items-center gap-1 hover:text-[rgb(var(--ctc-primary-dark))]">
                View All <HiChevronRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {(instructorsData?.results ?? []).slice(0, 4).map((instructor, idx) => (
                <motion.div
                  key={instructor.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  className="card p-6 text-center"
                >
                  <div className="w-20 h-20 bg-gradient-to-br from-[rgb(var(--ctc-primary))] to-[rgb(var(--ctc-accent))] rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
                    {instructor.first_name?.[0]}{instructor.last_name?.[0]}
                  </div>
                  <h3 className="font-semibold text-gray-900">{instructor.first_name} {instructor.last_name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{instructor.title}</p>
                  <div className="flex items-center justify-center gap-3 mt-3 text-sm text-gray-500">
                    <span>{instructor.courses_count} courses</span>
                    <span>·</span>
                    <span className="flex items-center gap-1">
                      <HiStar className="w-4 h-4 text-yellow-400" />
                      {instructor.average_rating}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>
    </div>
  );
}
