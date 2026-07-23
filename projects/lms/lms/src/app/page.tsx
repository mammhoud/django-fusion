'use client';

import Link from 'next/link';
import type { Route } from 'next';
import { motion } from 'framer-motion';
import { HiAcademicCap, HiUserGroup, HiBookOpen, HiStar, HiChevronRight } from 'react-icons/hi';
import { useGetFeaturedCoursesQuery, useGetCoursesQuery } from '@/store/api/endpoints/courses';
import { useGetInstructorsQuery } from '@/store/api/endpoints/instructors';
import { useGetPageQuery } from '@/store/api/endpoints/pages';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function HomePage() {
  const { data: page } = useGetPageQuery('home');
  const { data: featuredCourses, isLoading: coursesLoading } = useGetFeaturedCoursesQuery();
  const { data: coursesData } = useGetCoursesQuery({ page: 1 });
  const { data: instructorsData } = useGetInstructorsQuery({ page: 1 });

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

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 text-white">
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
            <p className="text-lg md:text-xl text-indigo-200 mb-10 leading-relaxed">
              {hero?.intro || 'Master new skills with expert-led courses, interactive content, and a community of learners.'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={(hero?.ctas?.[0]?.href || '/courses') as Route} className="bg-white text-indigo-700 px-8 py-3 rounded-lg font-semibold hover:bg-indigo-50 transition-colors">
                {hero?.ctas?.[0]?.label || 'Explore Courses'}
              </Link>
              <Link href={(hero?.ctas?.[1]?.href || '/registration') as Route} className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
                {hero?.ctas?.[1]?.label || 'Get Started Free'}
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
                <stat.icon className="w-8 h-8 text-indigo-600 mx-auto mb-3" />
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
            <Link href="/courses" className="text-indigo-600 font-medium flex items-center gap-1 hover:text-indigo-700">
              View All <HiChevronRight className="w-4 h-4" />
            </Link>
          </div>

          {coursesLoading ? (
            <LoadingSkeleton variant="card" count={3} />
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
                    <div className="bg-gradient-to-br from-indigo-500 to-purple-600 h-40 flex items-center justify-center">
                      <HiBookOpen className="w-12 h-12 text-white/60" />
                    </div>
                    <div className="p-5">
                      <span className="badge-primary mb-2 inline-block">{course.category_name || 'General'}</span>
                      <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-indigo-600 transition-colors">
                        {course.title}
                      </h3>
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">{course.short_description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">{course.instructor_name}</span>
                        <span className="font-bold text-indigo-600">
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
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            {cta?.heading || 'Start Learning Today'}
          </h2>
          <p className="text-lg text-indigo-200 mb-8">
            {cta?.intro || 'Join thousands of students and start your learning journey today.'}
          </p>
          <Link
            href={(cta?.ctas?.[0]?.href || '/registration') as Route}
            className="inline-block bg-white text-indigo-700 px-10 py-4 rounded-lg font-bold text-lg
                       hover:bg-indigo-50 transition-colors shadow-lg"
          >
            {cta?.ctas?.[0]?.label || 'Create Free Account'}
          </Link>
        </div>
      </section>

      {/* Instructors Preview */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Expert Instructors</h2>
              <p className="text-gray-500 mt-2">Learn from industry professionals</p>
            </div>
            <Link href="/instructors" className="text-indigo-600 font-medium flex items-center gap-1 hover:text-indigo-700">
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
                <div className="w-20 h-20 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
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
