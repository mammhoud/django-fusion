'use client';

import Link from 'next/link';
import type { Route } from 'next';
import { motion } from 'framer-motion';
import { HiBeaker, HiUserGroup, HiClipboardCheck, HiGlobe, HiChevronRight } from 'react-icons/hi2';
import { useGetFeaturedCoursesQuery, useGetCoursesQuery } from '@/store/api/endpoints/courses';
import { useGetInstructorsQuery } from '@/store/api/endpoints/instructors';
import { FusionPage } from '@/components/FusionPage';
import EmptyState from '@/components/ui/EmptyState';
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

  const pageStats = page?.blocks.find((block) => block.type === 'stats')?.items || [];
  const hero = page?.blocks.find((block) => block.type === 'hero');
  const featuredHeader = page?.blocks.find((block) => block.key === 'featured_courses');
  const cta = page?.blocks.find((block) => block.type === 'cta');

  const stats = [
    { icon: HiClipboardCheck, label: 'Clinical Trials', value: pageStats[0]?.value || '200+' },
    { icon: HiUserGroup, label: 'Patients Enrolled', value: pageStats[1]?.value || '15K+' },
    { icon: HiGlobe, label: 'Research Sites', value: pageStats[2]?.value || '50+' },
    { icon: HiBeaker, label: 'Years Experience', value: pageStats[3]?.value || '25+' },
  ];

  return (
    <div>
      {/* Hero Section — CTC Research */}
      <section className="section-hero text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              {hero?.heading || 'Advancing Clinical Trials Through Innovation'}
            </h1>
            <p className="text-lg md:text-xl text-white/80 mb-10 leading-relaxed">
              {hero?.intro || 'CTC Research is a premier clinical research organization dedicated to accelerating the development of new therapies through rigorous scientific methods and patient-centered approaches.'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={(hero?.ctas?.[0]?.href || '/services') as Route} className="bg-white text-[rgb(var(--ctc-primary-dark))] px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg">
                {hero?.ctas?.[0]?.label || 'Explore Our Services'}
              </Link>
              <Link href={(hero?.ctas?.[1]?.href || '/contact') as Route} className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
                {hero?.ctas?.[1]?.label || 'Contact Us'}
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
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

      {/* Featured Courses */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">{featuredHeader?.heading || 'Featured Courses'}</h2>
              <p className="text-gray-500 mt-2">{featuredHeader?.intro || 'Most popular courses picked for you'}</p>
            </div>
            <Link href="/services" className="text-[rgb(var(--ctc-primary))] font-medium flex items-center gap-1 hover:text-[rgb(var(--ctc-primary-dark))]">
              View All <HiChevronRight className="w-4 h-4" />
            </Link>
          </div>

          {coursesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="card animate-pulse">
                  <div className="bg-gray-200 h-40 rounded-t-lg" />
                  <div className="p-5 space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-1/3" />
                    <div className="h-5 bg-gray-200 rounded w-3/4" />
                    <div className="h-4 bg-gray-200 rounded w-full" />
                  </div>
                </div>
              ))}
            </div>
          ) : featuredCourses && featuredCourses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {featuredCourses.slice(0, 6).map((course, idx) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.05 }}
                >
                  <Link href={`/course-details/${course.id}`} className="card block overflow-hidden group">
                    <div className="bg-gradient-to-br from-[rgb(var(--ctc-primary))] to-[rgb(var(--ctc-primary-dark))] h-40 flex items-center justify-center">
                      <HiBookOpen className="w-12 h-12 text-white/60" />
                    </div>
                    <div className="p-5">
                      <span className="badge-primary mb-2 inline-block">{course.category_name || 'General'}</span>
                      <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-[rgb(var(--ctc-primary))] transition-colors">
                        {course.title}
                      </h3>
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">{course.short_description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">{course.instructor_name}</span>
                        <span className="font-bold text-[rgb(var(--ctc-primary))]">
                          {course.discounted_price ? (
                            <>
                              <span className="line-through text-gray-400 text-sm mr-1">${course.price}</span>
                              ${course.discounted_price}
                            </>
                          ) : (
                            `$${course.price}`
                          )}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mt-3 text-sm text-gray-500">
                        <span>{course.students_count} students</span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <HiStar className="w-4 h-4 text-yellow-400" />
                          {course.rating}
                        </span>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          ) : (
            <EmptyState icon="courses" title="No featured courses yet" description="Check back soon for new courses." actionLabel="Browse All Courses" actionHref="/courses" />
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-cta">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            {cta?.heading || 'Partner With Us'}
          </h2>
          <p className="text-lg text-white/80 mb-8">
            {cta?.intro || 'Join leading pharmaceutical companies and research institutions in advancing medical science.'}
          </p>
          <Link
            href={(cta?.ctas?.[0]?.href || '/contact') as Route}
            className="inline-block bg-white text-[rgb(var(--ctc-primary-dark))] px-10 py-4 rounded-lg font-bold text-lg
                       hover:bg-gray-100 transition-colors shadow-lg"
          >
            {cta?.ctas?.[0]?.label || 'Get Started'}
          </Link>
        </div>
      </section>

      {/* Instructors Preview */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Research Team</h2>
              <p className="text-gray-500 mt-2">Meet our clinical research professionals</p>
            </div>
            <Link href="/team" className="text-[rgb(var(--ctc-primary))] font-medium flex items-center gap-1 hover:text-[rgb(var(--ctc-primary-dark))]">
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
                <div className="team-avatar">
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
    </div>
  );
}
